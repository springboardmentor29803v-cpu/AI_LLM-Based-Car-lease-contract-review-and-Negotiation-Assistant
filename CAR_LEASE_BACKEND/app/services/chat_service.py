"""
Chat service for the AI Negotiation Assistant.

Handles:
- Chat memory storage (PostgreSQL per contract)
- LLM integration with negotiation prompts
- Context building from contract data and detected issues
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from sqlalchemy import text

# Import database engine from the main database module
import sys
sys.path.insert(0, str(__file__).replace("\\", "/").rsplit("/app/", 1)[0])
from database import engine

load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment")

MODEL_ID = "gemini-2.5-flash"

# Number of previous messages to include in context
MAX_CHAT_HISTORY = 10

# Default greeting message
DEFAULT_GREETING = (
    "I'm your negotiation assistant. How can I help you prepare for your "
    "conversation with the dealer? You can ask for talking points, questions "
    "to ask, or ways to respond to common dealer tactics."
)

# ============================================================================
# NEGOTIATION PROMPT TEMPLATE
# ============================================================================

NEGOTIATION_SYSTEM_PROMPT = """You are a professional car lease negotiation assistant helping a customer prepare for a dealer conversation.

Your role:
- Provide practical negotiation guidance and strategies
- Suggest talking points based on detected contract issues
- Generate professional, polite messages when requested
- Reference specific contract clauses and terms
- Help the customer understand their leverage points

Guidelines:
- Be concise and actionable
- Focus on the customer's best interests
- Stay professional - never aggressive or confrontational
- Use the contract details to support recommendations
- When drafting messages, keep them to 2-3 sentences
"""

NEGOTIATION_USER_PROMPT = """Context:
Vehicle: {vehicle}
Contract terms: {sla}
Detected issues: {issues}
Negotiation goals: {intents}

Previous conversation:
{chat_history}

User question:
{user_query}

Tasks:
1. Provide negotiation guidance and insights based on the context.
2. Suggest talking points or strategies if asked.
3. If user requests a message, generate a polite professional negotiation message in 2-3 sentences.
4. Keep responses concise and practical.
5. Reference contract clauses when relevant."""


# ============================================================================
# CHAT DATABASE MANAGER
# ============================================================================

class ChatDatabase:
    """PostgreSQL-based chat history storage."""
    
    def __init__(self):
        self.engine = engine
        logger.info("✓ Chat database using PostgreSQL")
    
    def add_message(self, contract_id: int, role: str, content: str, 
                    metadata: Dict = None) -> int:
        """
        Add a message to chat history.
        
        Args:
            contract_id: Contract ID
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata dict
            
        Returns:
            Message ID
        """
        with self.engine.begin() as conn:
            result = conn.execute(
                text("""
                INSERT INTO chat_messages (contract_id, role, content, metadata)
                VALUES (:contract_id, :role, :content, :metadata)
                RETURNING id
                """),
                {
                    "contract_id": contract_id,
                    "role": role,
                    "content": content,
                    "metadata": json.dumps(metadata) if metadata else None
                }
            )
            return result.fetchone()[0]
    
    def get_history(self, contract_id: int, limit: int = MAX_CHAT_HISTORY) -> List[Dict]:
        """
        Get chat history for a contract.
        
        Args:
            contract_id: Contract ID
            limit: Max number of messages to retrieve
            
        Returns:
            List of message dicts (oldest first)
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                SELECT id, role, content, created_at, metadata
                FROM chat_messages
                WHERE contract_id = :contract_id
                ORDER BY created_at DESC
                LIMIT :limit
                """),
                {"contract_id": contract_id, "limit": limit}
            )
            rows = result.fetchall()
        
        # Reverse to get oldest first
        messages = []
        for row in reversed(rows):
            msg = {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3].isoformat() if row[3] else None,
            }
            if row[4]:
                msg["metadata"] = row[4] if isinstance(row[4], dict) else json.loads(row[4])
            messages.append(msg)
        
        return messages
    
    def clear_history(self, contract_id: int) -> int:
        """
        Clear all chat history for a contract.
        
        Returns:
            Number of messages deleted
        """
        with self.engine.begin() as conn:
            result = conn.execute(
                text("DELETE FROM chat_messages WHERE contract_id = :contract_id"),
                {"contract_id": contract_id}
            )
            return result.rowcount
    
    def get_message_count(self, contract_id: int) -> int:
        """Get total message count for a contract."""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM chat_messages WHERE contract_id = :contract_id"),
                {"contract_id": contract_id}
            )
            return result.fetchone()[0]


# ============================================================================
# CHAT SERVICE
# ============================================================================

class NegotiationChatService:
    """
    AI Negotiation Assistant chat service.
    
    Handles LLM interactions with context from:
    - Vehicle details (from VIN decode)
    - SLA contract terms
    - Detected issues with negotiation intents
    - Chat history
    """
    
    def __init__(self):
        self.db = ChatDatabase()
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_ID,
            google_api_key=GEMINI_API_KEY,
            temperature=0.7
        )
        logger.info("✓ Negotiation chat service initialized")
    
    def get_greeting(self) -> str:
        """Get the default chatbot greeting."""
        return DEFAULT_GREETING
    
    def build_context(self, 
                      vehicle_data: Optional[Dict] = None,
                      sla_data: Optional[Dict] = None,
                      issues: Optional[List[Dict]] = None,
                      chat_history: Optional[List[Dict]] = None,
                      user_query: str = "") -> str:
        """
        Build the context prompt for the LLM.
        
        Args:
            vehicle_data: Vehicle details from VIN decode
            sla_data: Extracted SLA contract terms
            issues: Detected issues with negotiation intents
            chat_history: Previous chat messages
            user_query: Current user question
            
        Returns:
            Formatted prompt string
        """
        # Format vehicle info
        if vehicle_data:
            vehicle_str = f"{vehicle_data.get('year', 'N/A')} {vehicle_data.get('make', 'N/A')} {vehicle_data.get('model', 'N/A')}"
            if vehicle_data.get('msrp'):
                vehicle_str += f" (MSRP: ${vehicle_data['msrp']:,})"
        else:
            vehicle_str = "Not specified"
        
        # Format SLA data
        if sla_data:
            sla_items = []
            for key, value in sla_data.items():
                if value is not None:
                    sla_items.append(f"- {key}: {value}")
            sla_str = "\n".join(sla_items) if sla_items else "No contract terms extracted"
        else:
            sla_str = "No contract data available"
        
        # Format issues with negotiation intents
        if issues:
            issues_items = []
            intents_items = []
            for issue in issues:
                severity = issue.get("severity", "unknown")
                field = issue.get("field", "unknown")
                issue_text = issue.get("issue", "Unknown issue")
                intent = issue.get("negotiation_intent")
                reason = issue.get("reason", "")
                
                issues_items.append(
                    f"- [{severity.upper()}] {field}: {issue_text}"
                    + (f" ({reason})" if reason else "")
                )
                if intent:
                    intents_items.append(f"- {field}: {intent}")
            
            issues_str = "\n".join(issues_items) if issues_items else "No issues detected"
            intents_str = "\n".join(intents_items) if intents_items else "No specific negotiation actions needed"
        else:
            issues_str = "No issues analyzed yet"
            intents_str = "No negotiation intents available"
        
        # Format chat history
        if chat_history:
            history_items = []
            for msg in chat_history[-MAX_CHAT_HISTORY:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_items.append(f"{role}: {msg['content']}")
            history_str = "\n".join(history_items)
        else:
            history_str = "No previous conversation"
        
        # Build final prompt
        return NEGOTIATION_USER_PROMPT.format(
            vehicle=vehicle_str,
            sla=sla_str,
            issues=issues_str,
            intents=intents_str,
            chat_history=history_str,
            user_query=user_query
        )
    
    def chat(self,
             contract_id: int,
             user_message: str,
             vehicle_data: Optional[Dict] = None,
             sla_data: Optional[Dict] = None,
             issues: Optional[List[Dict]] = None) -> Tuple[str, List[Dict]]:
        """
        Process a chat message and get LLM response.
        
        Args:
            contract_id: Contract ID for chat context
            user_message: User's message
            vehicle_data: Vehicle details from VIN decode
            sla_data: Extracted SLA contract terms
            issues: Detected issues with negotiation intents
            
        Returns:
            Tuple of (assistant_response, chat_history)
        """
        # Get existing chat history
        chat_history = self.db.get_history(contract_id)
        
        # Build context prompt
        context_prompt = self.build_context(
            vehicle_data=vehicle_data,
            sla_data=sla_data,
            issues=issues,
            chat_history=chat_history,
            user_query=user_message
        )
        
        # Prepare messages for LLM
        messages = [
            SystemMessage(content=NEGOTIATION_SYSTEM_PROMPT),
            HumanMessage(content=context_prompt)
        ]
        
        try:
            # Get LLM response
            response = self.llm.invoke(messages)
            assistant_response = response.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            assistant_response = (
                "I apologize, but I'm having trouble processing your request. "
                "Please try again or rephrase your question."
            )
        
        # Save messages to history
        self.db.add_message(contract_id, "user", user_message)
        self.db.add_message(contract_id, "assistant", assistant_response)
        
        # Return response and updated history
        updated_history = self.db.get_history(contract_id)
        
        return assistant_response, updated_history
    
    def get_history(self, contract_id: int) -> List[Dict]:
        """Get chat history for a contract."""
        return self.db.get_history(contract_id)
    
    def clear_history(self, contract_id: int) -> int:
        """Clear chat history for a contract."""
        return self.db.clear_history(contract_id)
    
    def get_quick_suggestions(self, issues: Optional[List[Dict]] = None) -> List[str]:
        """
        Get quick suggestion buttons based on detected issues.
        
        Args:
            issues: Detected issues with negotiation intents
            
        Returns:
            List of suggested questions/actions
        """
        suggestions = [
            "What are my main negotiation points?",
            "How should I respond if the dealer says the price is firm?",
            "Draft a message to request better terms"
        ]
        
        if issues:
            # Add issue-specific suggestions
            high_severity = [i for i in issues if i.get("severity") == "high"]
            if high_severity:
                field = high_severity[0].get("field", "issue")
                suggestions.insert(0, f"How can I negotiate the {field}?")
            
            # Add intent-based suggestions
            intents = [i.get("negotiation_intent") for i in issues if i.get("negotiation_intent")]
            if intents:
                suggestions.insert(1, f"Help me with: {intents[0]}")
        
        return suggestions[:5]  # Return max 5 suggestions


# ============================================================================
# GLOBAL SERVICE INSTANCE
# ============================================================================

_chat_service: Optional[NegotiationChatService] = None


def get_chat_service() -> NegotiationChatService:
    """Get or create the chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = NegotiationChatService()
    return _chat_service


def initialize_chat_service():
    """Initialize the chat service at startup."""
    global _chat_service
    _chat_service = NegotiationChatService()
    return _chat_service
