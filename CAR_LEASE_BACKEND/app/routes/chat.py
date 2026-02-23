"""
Unified Chat API endpoint for the Negotiation Chatbot.

Single endpoint handles all chat operations:
- greeting: Get welcome message
- message: Send message & get AI response
- history: Get past messages
- clear: Delete chat history
- suggestions: Get suggestion chips
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from enum import Enum

from database import get_db
from app.services.chat_service import get_chat_service, NegotiationChatService
from app.services.rule_processor import RuleProcessor
from app.services.rules_cache import get_cached_rules

router = APIRouter()

# Initialize rule processor for issue detection
rule_processor = RuleProcessor()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatAction(str, Enum):
    """Available chat actions."""
    GREETING = "greeting"
    MESSAGE = "message"
    HISTORY = "history"
    CLEAR = "clear"
    SUGGESTIONS = "suggestions"


class ChatRequest(BaseModel):
    """Unified chat request model."""
    action: ChatAction = Field(..., description="Action: greeting, message, history, clear, suggestions")
    contract_id: Optional[int] = Field(None, description="Contract ID (required for all except greeting)")
    message: Optional[str] = Field(None, description="User's message (required for 'message' action)")


class ChatMessageData(BaseModel):
    """Message data in responses."""
    id: int
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    """Unified chat response model."""
    action: str
    success: bool = True
    contract_id: Optional[int] = None
    
    # For greeting
    greeting: Optional[str] = None
    
    # For message
    user_message: Optional[str] = None
    assistant_response: Optional[str] = None
    timestamp: Optional[str] = None
    
    # For history
    messages: Optional[List[ChatMessageData]] = None
    total_messages: Optional[int] = None
    
    # For clear
    deleted_count: Optional[int] = None
    
    # For suggestions (also included with message and greeting)
    suggestions: Optional[List[str]] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_contract_data(db: Session, contract_id: int) -> Dict[str, Any]:
    """
    Fetch contract data from database.
    
    Returns:
        Dict with vehicle_data, sla_data, and detected issues
    """
    result = db.execute(
        text("""
            SELECT combined_data
            FROM contracts
            WHERE id = :id
        """),
        {"id": contract_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    
    # Parse combined_data which contains both sla and vehicle
    combined_data = result[0] if result[0] else {}
    sla_data = combined_data.get("sla", {})
    vehicle_data = combined_data.get("vehicle", {})
    
    # Detect issues using cached rules
    issues = []
    if sla_data:
        try:
            rules = get_cached_rules()
            issues = rule_processor.detect_issues(sla_data, rules)
        except Exception as e:
            print(f"Warning: Could not detect issues: {e}")
    
    return {
        "vehicle_data": vehicle_data,
        "sla_data": sla_data,
        "issues": issues
    }


# ============================================================================
# UNIFIED CHAT ENDPOINT
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def unified_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    **Unified chat endpoint for all chat operations.**
    
    Actions:
    - `greeting`: Get welcome message (no contract_id needed)
    - `message`: Send a message and get AI response
    - `history`: Get chat history
    - `clear`: Clear chat history  
    - `suggestions`: Get quick suggestions
    
    Examples:
    ```json
    {"action": "greeting"}
    {"action": "message", "contract_id": 5, "message": "What are my negotiation points?"}
    {"action": "history", "contract_id": 5}
    {"action": "clear", "contract_id": 5}
    {"action": "suggestions", "contract_id": 5}
    ```
    """
    chat_service = get_chat_service()
    
    # ========== GREETING ==========
    if request.action == ChatAction.GREETING:
        return ChatResponse(
            action="greeting",
            greeting=chat_service.get_greeting(),
            suggestions=[
                "What are my main negotiation points?",
                "How do I respond if the dealer says the price is firm?",
                "Help me understand my contract terms"
            ]
        )
    
    # All other actions require contract_id
    if request.contract_id is None:
        raise HTTPException(
            status_code=400, 
            detail=f"contract_id is required for action '{request.action.value}'"
        )
    
    # ========== MESSAGE ==========
    if request.action == ChatAction.MESSAGE:
        if not request.message:
            raise HTTPException(
                status_code=400,
                detail="message is required for action 'message'"
            )
        
        # Fetch contract context
        try:
            context = get_contract_data(db, request.contract_id)
        except HTTPException:
            context = {"vehicle_data": None, "sla_data": None, "issues": []}
        
        # Get response from LLM
        response, history = chat_service.chat(
            contract_id=request.contract_id,
            user_message=request.message,
            vehicle_data=context.get("vehicle_data"),
            sla_data=context.get("sla_data"),
            issues=context.get("issues", [])
        )
        
        # Get updated suggestions
        suggestions = chat_service.get_quick_suggestions(context.get("issues", []))
        
        return ChatResponse(
            action="message",
            contract_id=request.contract_id,
            user_message=request.message,
            assistant_response=response,
            timestamp=datetime.now().isoformat(),
            suggestions=suggestions
        )
    
    # ========== HISTORY ==========
    if request.action == ChatAction.HISTORY:
        messages = chat_service.get_history(request.contract_id)
        
        formatted_messages = [
            ChatMessageData(
                id=msg.get("id", 0),
                role=msg["role"],
                content=msg["content"],
                timestamp=str(msg.get("timestamp", ""))
            )
            for msg in messages
        ]
        
        return ChatResponse(
            action="history",
            contract_id=request.contract_id,
            messages=formatted_messages,
            total_messages=len(formatted_messages)
        )
    
    # ========== CLEAR ==========
    if request.action == ChatAction.CLEAR:
        deleted_count = chat_service.clear_history(request.contract_id)
        
        return ChatResponse(
            action="clear",
            contract_id=request.contract_id,
            deleted_count=deleted_count
        )
    
    # ========== SUGGESTIONS ==========
    if request.action == ChatAction.SUGGESTIONS:
        try:
            context = get_contract_data(db, request.contract_id)
            issues = context.get("issues", [])
        except HTTPException:
            issues = []
        
        suggestions = chat_service.get_quick_suggestions(issues)
        
        return ChatResponse(
            action="suggestions",
            contract_id=request.contract_id,
            suggestions=suggestions
        )
    
    # Should not reach here
    raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
