# app/services/db_memory.py - SIMPLE DATABASE MEMORY
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import ChatMessage, NegotiationSession


class DatabaseMemory:
    """Simple database memory - stores conversations in database"""
    
    def __init__(self, db: Session, contract_id: int, session_id: str = None):
        self.db = db
        self.contract_id = contract_id
        self.session_id = session_id or f"session_{contract_id}_{int(datetime.now().timestamp())}"
        
        # Load existing conversation
        self.messages = self._load_messages()
        print(f"✅ DatabaseMemory loaded {len(self.messages)} messages")
    
    def _load_messages(self) -> List[Dict[str, str]]:
        """Load messages from database"""
        try:
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.contract_id == self.contract_id,
                ChatMessage.session_id == self.session_id
            ).order_by(ChatMessage.timestamp).all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"⚠️ Failed to load messages: {e}")
            return []
    
    def add_message(self, role: str, content: str, intent: str = None):
        """Add a message to memory and database"""
        try:
            # Create message object
            message = ChatMessage(
                contract_id=self.contract_id,
                session_id=self.session_id,
                role=role,
                content=content,
                intent=intent,
                timestamp=datetime.utcnow()
            )
            
            # Add to database
            self.db.add(message)
            
            # Update or create session
            session = self.db.query(NegotiationSession).filter(
                NegotiationSession.session_id == self.session_id
            ).first()
            
            if not session:
                session = NegotiationSession(
                    contract_id=self.contract_id,
                    session_id=self.session_id,
                    created_at=datetime.utcnow()
                )
                self.db.add(session)
            
            session.updated_at = datetime.utcnow()
            session.last_message = content[:200]  # Store snippet
            
            # Commit changes
            self.db.commit()
            
            # Add to local memory
            self.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            })
            
            print(f"💾 Saved {role} message to database")
            
        except Exception as e:
            print(f"❌ Failed to save message: {e}")
            self.db.rollback()
    
    def get_messages(self, limit: int = None) -> List[Dict[str, str]]:
        """Get messages from memory"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_conversation_history(self) -> str:
        """Format conversation history as text"""
        history_lines = []
        for msg in self.messages[-10:]:  # Last 10 messages
            speaker = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{speaker}: {msg['content']}")
        
        return "\n".join(history_lines)
    
    def clear(self):
        """Clear memory and database"""
        try:
            # Clear local memory
            self.messages = []
            
            # Delete from database
            self.db.query(ChatMessage).filter(
                ChatMessage.contract_id == self.contract_id,
                ChatMessage.session_id == self.session_id
            ).delete()
            
            self.db.query(NegotiationSession).filter(
                NegotiationSession.session_id == self.session_id
            ).delete()
            
            self.db.commit()
            print("🗑️  Cleared database memory")
            
        except Exception as e:
            print(f"❌ Failed to clear memory: {e}")
            self.db.rollback()
    
    def get_message_count(self) -> int:
        """Get number of messages"""
        return len(self.messages)


# Simple factory function
def create_database_memory(db: Session, contract_id: int, session_id: str = None) -> DatabaseMemory:
    """Create a database memory instance"""
    return DatabaseMemory(db, contract_id, session_id)
