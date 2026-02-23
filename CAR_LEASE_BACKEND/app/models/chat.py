"""
Chat message models for the negotiation chatbot.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    contract_id: int = Field(..., description="Contract ID to chat about")
    message: str = Field(..., description="User's message")


class ChatResponse(BaseModel):
    """Response from the chatbot."""
    contract_id: int
    user_message: str
    assistant_response: str
    timestamp: datetime
    issues_referenced: Optional[List[str]] = None


class ChatHistoryResponse(BaseModel):
    """Full chat history for a contract."""
    contract_id: int
    messages: List[ChatMessage]
    total_messages: int


class NegotiationContext(BaseModel):
    """Context passed to the LLM for negotiation assistance."""
    vehicle: Optional[Dict[str, Any]] = Field(None, description="Vehicle details from VIN decode")
    sla: Optional[Dict[str, Any]] = Field(None, description="Extracted SLA contract terms")
    issues: Optional[List[Dict[str, Any]]] = Field(None, description="Detected issues with negotiation intents")
    chat_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous chat messages")
