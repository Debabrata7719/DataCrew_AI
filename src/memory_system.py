"""
DebAI Email Assistant - Enhanced Memory System (Phase 1)

Upgraded conversation buffer with:
- Larger message window (50 messages instead of 10)
- Conversation summarization
- Smart context retention
- Message prioritization
"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationMemory:
    """Enhanced conversation memory with smart context management."""
    
    def __init__(self, max_messages: int = 50, summary_threshold: int = 40):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of messages to keep
            summary_threshold: When to trigger summarization
        """
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.conversations: Dict[str, List[Dict]] = {}
        self.summaries: Dict[str, str] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.metadata[session_id] = {
                "created_at": datetime.now(),
                "message_count": 0,
                "emails_sent": 0,
                "documents_created": 0
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "index": len(self.conversations[session_id])
        }
        
        self.conversations[session_id].append(message)
        self.metadata[session_id]["message_count"] += 1
        
        # Track email sends
        if role == "assistant" and "✅ Email sent" in content:
            self.metadata[session_id]["emails_sent"] += 1
        
        # Track document creation
        if role == "assistant" and "document created" in content.lower():
            self.metadata[session_id]["documents_created"] += 1
        
        # Apply window limit with smart retention
        self._apply_window_limit(session_id)
    
    def get_messages(self, session_id: str, include_summary: bool = True) -> List[Dict]:
        """
        Get conversation messages for a session.
        
        Args:
            session_id: Session identifier
            include_summary: Whether to include session summary
            
        Returns:
            List of messages with optional summary
        """
        if session_id not in self.conversations:
            return []
        
        messages = []
        
        # Add summary if available and requested
        if include_summary and session_id in self.summaries:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summaries[session_id]}"
            })
        
        # Add actual messages
        messages.extend(self.conversations[session_id])
        
        return messages
    
    def get_conversation_context(self, session_id: str) -> str:
        """
        Get a text summary of the conversation for the AI.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted conversation context
        """
        if session_id not in self.conversations:
            return "No previous conversation."
        
        meta = self.metadata.get(session_id, {})
        messages = self.conversations[session_id]
        
        context_parts = []
        
        # Add metadata summary
        context_parts.append(f"Conversation started: {meta.get('created_at', 'Unknown')}")
        context_parts.append(f"Messages exchanged: {meta.get('message_count', 0)}")
        context_parts.append(f"Emails sent: {meta.get('emails_sent', 0)}")
        context_parts.append(f"Documents created: {meta.get('documents_created', 0)}")
        
        # Add recent important messages
        important_messages = self._get_important_messages(messages[-20:])  # Last 20 messages
        if important_messages:
            context_parts.append("\nRecent important exchanges:")
            for msg in important_messages:
                role_label = "You" if msg["role"] == "user" else "AI"
                snippet = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context_parts.append(f"- {role_label}: {snippet}")
        
        return "\n".join(context_parts)
    
    def _get_important_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Extract important messages (email sends, document creation, questions).
        
        Args:
            messages: List of messages to filter
            
        Returns:
            List of important messages
        """
        important = []
        keywords = ["email", "send", "create", "document", "attach", "report", "?"]
        
        for msg in messages:
            content_lower = msg["content"].lower()
            if any(keyword in content_lower for keyword in keywords):
                important.append(msg)
        
        return important[-10:]  # Return last 10 important messages
    
    def _apply_window_limit(self, session_id: str) -> None:
        """
        Apply message window limit with smart retention.
        
        Args:
            session_id: Session identifier
        """
        if len(self.conversations[session_id]) > self.max_messages:
            # Keep the most recent messages
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages:]
        
        # Create summary if threshold reached
        if len(self.conversations[session_id]) >= self.summary_threshold:
            self._create_summary(session_id)
    
    def _create_summary(self, session_id: str) -> None:
        """
        Create a summary of older messages.
        
        Args:
            session_id: Session identifier
        """
        messages = self.conversations[session_id]
        
        # Summarize the older half of messages
        midpoint = len(messages) // 2
        old_messages = messages[:midpoint]
        
        # Extract key information
        emails_sent = []
        docs_created = []
        topics = []
        
        for msg in old_messages:
            content = msg["content"]
            
            # Track emails
            if "✅ Email sent" in content:
                # Extract recipient if possible
                if "to " in content.lower():
                    emails_sent.append(content)
            
            # Track documents
            if "document created" in content.lower() or "PDF created" in content.lower():
                docs_created.append(content)
            
            # Extract topics (simple keyword extraction)
            if msg["role"] == "user" and len(msg["content"]) > 20:
                topics.append(msg["content"][:50] + "...")
        
        # Build summary
        summary_parts = []
        
        if emails_sent:
            summary_parts.append(f"Sent {len(emails_sent)} emails")
        
        if docs_created:
            summary_parts.append(f"Created {len(docs_created)} documents")
        
        if topics:
            summary_parts.append(f"Discussed: {', '.join(topics[:3])}")
        
        self.summaries[session_id] = "; ".join(summary_parts) if summary_parts else "General conversation"
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.summaries:
            del self.summaries[session_id]
        if session_id in self.metadata:
            del self.metadata[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics
        """
        if session_id not in self.metadata:
            return {
                "exists": False,
                "message_count": 0,
                "emails_sent": 0,
                "documents_created": 0
            }
        
        meta = self.metadata[session_id]
        return {
            "exists": True,
            "message_count": meta.get("message_count", 0),
            "emails_sent": meta.get("emails_sent", 0),
            "documents_created": meta.get("documents_created", 0),
            "created_at": meta.get("created_at"),
            "has_summary": session_id in self.summaries
        }
    
    def search_messages(self, session_id: str, query: str) -> List[Dict]:
        """
        Search for messages containing a query string.
        
        Args:
            session_id: Session identifier
            query: Search query
            
        Returns:
            List of matching messages
        """
        if session_id not in self.conversations:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for msg in self.conversations[session_id]:
            if query_lower in msg["content"].lower():
                matches.append(msg)
        
        return matches


# Global memory instance
conversation_memory = ConversationMemory(max_messages=50, summary_threshold=40)


# Helper functions for easy integration

def add_user_message(session_id: str, content: str) -> None:
    """Add a user message to memory."""
    conversation_memory.add_message(session_id, "user", content)


def add_ai_message(session_id: str, content: str) -> None:
    """Add an AI message to memory."""
    conversation_memory.add_message(session_id, "assistant", content)


def get_conversation_history(session_id: str) -> List[Dict]:
    """Get full conversation history with summaries."""
    return conversation_memory.get_messages(session_id, include_summary=True)


def get_context_for_ai(session_id: str) -> str:
    """Get formatted context string for AI."""
    return conversation_memory.get_conversation_context(session_id)


def clear_conversation(session_id: str) -> None:
    """Clear conversation memory."""
    conversation_memory.clear_session(session_id)


def get_stats(session_id: str) -> Dict:
    """Get session statistics."""
    return conversation_memory.get_session_stats(session_id)


def search_conversation(session_id: str, query: str) -> List[Dict]:
    """Search conversation history."""
    return conversation_memory.search_messages(session_id, query)
