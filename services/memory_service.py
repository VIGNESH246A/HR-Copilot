"""
Memory service for conversation and context management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class MemoryService:
    """Service for managing conversation memory and context"""
    
    def __init__(self):
        self.short_term_memory: Dict[str, List[Dict]] = {}
        self.long_term_memory: Dict[str, Dict] = {}
        self.context_cache: Dict[str, Dict] = {}
    
    def store_short_term(
        self, 
        session_id: str, 
        key: str, 
        value: Any,
        ttl_minutes: int = 60
    ):
        """Store short-term memory with TTL"""
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        
        entry = {
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=ttl_minutes)
        }
        
        self.short_term_memory[session_id].append(entry)
        self._cleanup_expired(session_id)
    
    def get_short_term(
        self, 
        session_id: str, 
        key: Optional[str] = None
    ) -> Any:
        """Retrieve short-term memory"""
        if session_id not in self.short_term_memory:
            return None if key else []
        
        self._cleanup_expired(session_id)
        
        if key:
            for entry in reversed(self.short_term_memory[session_id]):
                if entry["key"] == key:
                    return entry["value"]
            return None
        
        return [
            {"key": e["key"], "value": e["value"]} 
            for e in self.short_term_memory[session_id]
        ]
    
    def store_long_term(
        self, 
        entity_id: str, 
        data: Dict[str, Any]
    ):
        """Store long-term memory (persists across sessions)"""
        if entity_id not in self.long_term_memory:
            self.long_term_memory[entity_id] = {}
        
        self.long_term_memory[entity_id].update(data)
        self.long_term_memory[entity_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def get_long_term(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve long-term memory"""
        return self.long_term_memory.get(entity_id)
    
    def store_context(
        self, 
        session_id: str, 
        context_type: str, 
        data: Dict[str, Any]
    ):
        """Store contextual information"""
        if session_id not in self.context_cache:
            self.context_cache[session_id] = {}
        
        self.context_cache[session_id][context_type] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
    
    def get_context(
        self, 
        session_id: str, 
        context_type: Optional[str] = None
    ) -> Any:
        """Retrieve contextual information"""
        if session_id not in self.context_cache:
            return None
        
        if context_type:
            ctx = self.context_cache[session_id].get(context_type)
            return ctx["data"] if ctx else None
        
        return {
            k: v["data"] 
            for k, v in self.context_cache[session_id].items()
        }
    
    def get_relevant_context(
        self, 
        session_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """Get relevant context based on query"""
        context = {}
        
        # Get recent short-term memory
        recent_memory = self.get_short_term(session_id)
        if recent_memory:
            context["recent_interactions"] = recent_memory[-5:]
        
        # Get all context
        session_context = self.get_context(session_id)
        if session_context:
            context.update(session_context)
        
        return context
    
    def summarize_session(self, session_id: str) -> str:
        """Generate session summary"""
        short_term = self.get_short_term(session_id)
        context = self.get_context(session_id)
        
        summary_parts = []
        
        if short_term:
            summary_parts.append(
                f"Recent actions: {len(short_term)} items stored"
            )
        
        if context:
            summary_parts.append(
                f"Active contexts: {', '.join(context.keys())}"
            )
        
        return " | ".join(summary_parts) if summary_parts else "No active session"
    
    def clear_session(self, session_id: str):
        """Clear all memory for a session"""
        if session_id in self.short_term_memory:
            del self.short_term_memory[session_id]
        if session_id in self.context_cache:
            del self.context_cache[session_id]
    
    def _cleanup_expired(self, session_id: str):
        """Remove expired entries from short-term memory"""
        if session_id not in self.short_term_memory:
            return
        
        now = datetime.utcnow()
        self.short_term_memory[session_id] = [
            entry for entry in self.short_term_memory[session_id]
            if entry["expires_at"] > now
        ]


# Global memory service instance
memory_service = MemoryService()