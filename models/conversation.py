"""
Conversation state management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from models.schemas import ConversationMessage, ConversationState


class ConversationManager:
    """Manages conversation state and history"""
    
    def __init__(self, max_history: int = 20):
        self.sessions: Dict[str, ConversationState] = {}
        self.max_history = max_history
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationState(session_id=session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationState]:
        """Get conversation session"""
        return self.sessions.get(session_id)
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(
                session_id=session_id
            )
        
        session = self.sessions[session_id]
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        # Limit history
        if len(session.messages) > self.max_history:
            session.messages = session.messages[-self.max_history:]
    
    def get_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """Get conversation messages"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def update_context(
        self, 
        session_id: str, 
        key: str, 
        value: Any
    ):
        """Update conversation context"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(
                session_id=session_id
            )
        
        self.sessions[session_id].context[key] = value
        self.sessions[session_id].updated_at = datetime.utcnow()
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context"""
        session = self.get_session(session_id)
        return session.context if session else {}
    
    def add_active_task(self, session_id: str, task_id: str):
        """Add active task to session"""
        session = self.get_session(session_id)
        if session and task_id not in session.active_tasks:
            session.active_tasks.append(task_id)
    
    def remove_active_task(self, session_id: str, task_id: str):
        """Remove completed task from session"""
        session = self.get_session(session_id)
        if session and task_id in session.active_tasks:
            session.active_tasks.remove(task_id)
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Generate conversation summary"""
        messages = self.get_messages(session_id)
        if not messages:
            return "No conversation history."
        
        summary_parts = []
        for msg in messages[-5:]:  # Last 5 messages
            role_label = "User" if msg.role == "user" else "Assistant"
            summary_parts.append(f"{role_label}: {msg.content[:100]}...")
        
        return "\n".join(summary_parts)
    
    def clear_session(self, session_id: str):
        """Clear conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """Export session data"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in session.messages
            ],
            "context": session.context,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }


# Global conversation manager instance
conversation_manager = ConversationManager()