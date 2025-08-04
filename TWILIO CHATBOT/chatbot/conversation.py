"""
Conversation Manager - Conversation State Management
Handles conversation state, history, and context management
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class Conversation:
    """Represents a conversation session"""
    call_sid: str
    from_number: str
    to_number: str
    start_time: datetime
    messages: List[Message]
    is_active: bool
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.metadata is None:
            self.metadata = {}
        if self.start_time is None:
            self.start_time = datetime.now()

class ConversationManager:
    """Manages conversation state and history"""
    
    def __init__(self, max_conversations: int = 1000, cleanup_interval: int = 3600):
        """
        Initialize the conversation manager
        
        Args:
            max_conversations (int): Maximum number of conversations to keep in memory
            cleanup_interval (int): Interval in seconds to clean up old conversations
        """
        self.conversations: Dict[str, Conversation] = {}
        self.max_conversations = max_conversations
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        
        logger.info(f"Conversation Manager initialized with max {max_conversations} conversations")
    
    def get_conversation(self, call_sid: str, from_number: str = None, to_number: str = None) -> Conversation:
        """
        Get or create a conversation for a call
        
        Args:
            call_sid (str): Twilio call SID
            from_number (str): Caller's phone number
            to_number (str): Called phone number
            
        Returns:
            Conversation: The conversation object
        """
        # Clean up old conversations if needed
        self._cleanup_old_conversations()
        
        if call_sid not in self.conversations:
            # Create new conversation
            conversation = Conversation(
                call_sid=call_sid,
                from_number=from_number or "unknown",
                to_number=to_number or "unknown",
                start_time=datetime.now(),
                messages=[],
                is_active=True
            )
            self.conversations[call_sid] = conversation
            logger.info(f"Created new conversation for call {call_sid}")
        else:
            conversation = self.conversations[call_sid]
        
        return conversation
    
    def add_message(self, call_sid: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a message to a conversation
        
        Args:
            call_sid (str): Twilio call SID
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
            metadata (Dict): Additional message metadata
            
        Returns:
            bool: True if message was added successfully
        """
        try:
            conversation = self.get_conversation(call_sid)
            
            message = Message(
                role=role,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            conversation.messages.append(message)
            
            # Update conversation metadata
            conversation.metadata['last_activity'] = datetime.now().isoformat()
            conversation.metadata['message_count'] = len(conversation.messages)
            
            logger.debug(f"Added {role} message to conversation {call_sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message to conversation {call_sid}: {str(e)}")
            return False
    
    def get_history(self, call_sid: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a call
        
        Args:
            call_sid (str): Twilio call SID
            limit (int): Maximum number of messages to return
            
        Returns:
            List[Dict]: List of message dictionaries
        """
        try:
            conversation = self.get_conversation(call_sid)
            
            # Get recent messages
            recent_messages = conversation.messages[-limit:] if limit > 0 else conversation.messages
            
            # Convert to dictionary format
            history = []
            for message in recent_messages:
                history.append({
                    'role': message.role,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'metadata': message.metadata
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting history for conversation {call_sid}: {str(e)}")
            return []
    
    def end_conversation(self, call_sid: str) -> bool:
        """
        Mark a conversation as ended
        
        Args:
            call_sid (str): Twilio call SID
            
        Returns:
            bool: True if conversation was ended successfully
        """
        try:
            if call_sid in self.conversations:
                conversation = self.conversations[call_sid]
                conversation.is_active = False
                conversation.metadata['end_time'] = datetime.now().isoformat()
                conversation.metadata['duration'] = (
                    datetime.now() - conversation.start_time
                ).total_seconds()
                
                logger.info(f"Ended conversation {call_sid}")
                return True
            else:
                logger.warning(f"Conversation {call_sid} not found for ending")
                return False
                
        except Exception as e:
            logger.error(f"Error ending conversation {call_sid}: {str(e)}")
            return False
    
    def get_conversation_stats(self, call_sid: str) -> Dict[str, Any]:
        """
        Get statistics for a conversation
        
        Args:
            call_sid (str): Twilio call SID
            
        Returns:
            Dict: Conversation statistics
        """
        try:
            conversation = self.get_conversation(call_sid)
            
            user_messages = [msg for msg in conversation.messages if msg.role == 'user']
            assistant_messages = [msg for msg in conversation.messages if msg.role == 'assistant']
            
            stats = {
                'call_sid': call_sid,
                'from_number': conversation.from_number,
                'to_number': conversation.to_number,
                'start_time': conversation.start_time.isoformat(),
                'is_active': conversation.is_active,
                'total_messages': len(conversation.messages),
                'user_messages': len(user_messages),
                'assistant_messages': len(assistant_messages),
                'duration_seconds': (datetime.now() - conversation.start_time).total_seconds(),
                'metadata': conversation.metadata
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for conversation {call_sid}: {str(e)}")
            return {}
    
    def get_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all conversations (for admin dashboard)
        
        Args:
            limit (int): Maximum number of conversations to return
            
        Returns:
            List[Dict]: List of conversation summaries
        """
        try:
            conversations = []
            
            # Sort by start time (newest first)
            sorted_conversations = sorted(
                self.conversations.values(),
                key=lambda c: c.start_time,
                reverse=True
            )
            
            for conversation in sorted_conversations[:limit]:
                stats = self.get_conversation_stats(conversation.call_sid)
                conversations.append(stats)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting all conversations: {str(e)}")
            return []
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversations by content
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: Matching conversations
        """
        try:
            results = []
            query_lower = query.lower()
            
            for conversation in self.conversations.values():
                # Search in message content
                for message in conversation.messages:
                    if query_lower in message.content.lower():
                        stats = self.get_conversation_stats(conversation.call_sid)
                        stats['matching_message'] = message.content
                        results.append(stats)
                        break
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []
    
    def _cleanup_old_conversations(self):
        """Clean up old conversations to prevent memory issues"""
        current_time = time.time()
        
        # Only cleanup if enough time has passed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        try:
            # Remove conversations older than 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            old_conversations = []
            
            for call_sid, conversation in self.conversations.items():
                if conversation.start_time < cutoff_time and not conversation.is_active:
                    old_conversations.append(call_sid)
            
            # Remove old conversations
            for call_sid in old_conversations:
                del self.conversations[call_sid]
            
            # If still too many conversations, remove oldest inactive ones
            if len(self.conversations) > self.max_conversations:
                sorted_conversations = sorted(
                    self.conversations.items(),
                    key=lambda x: x[1].start_time
                )
                
                # Keep active conversations and remove oldest inactive ones
                active_conversations = {k: v for k, v in self.conversations.items() if v.is_active}
                inactive_conversations = {k: v for k, v in self.conversations.items() if not v.is_active}
                
                # Remove oldest inactive conversations
                for call_sid, _ in sorted_conversations:
                    if call_sid in inactive_conversations and len(self.conversations) > self.max_conversations:
                        del self.conversations[call_sid]
            
            self.last_cleanup = current_time
            logger.info(f"Cleaned up {len(old_conversations)} old conversations")
            
        except Exception as e:
            logger.error(f"Error during conversation cleanup: {str(e)}")
    
    def export_conversation(self, call_sid: str) -> Dict[str, Any]:
        """
        Export a conversation for backup or analysis
        
        Args:
            call_sid (str): Twilio call SID
            
        Returns:
            Dict: Complete conversation data
        """
        try:
            conversation = self.get_conversation(call_sid)
            
            export_data = {
                'call_sid': conversation.call_sid,
                'from_number': conversation.from_number,
                'to_number': conversation.to_number,
                'start_time': conversation.start_time.isoformat(),
                'is_active': conversation.is_active,
                'metadata': conversation.metadata,
                'messages': []
            }
            
            for message in conversation.messages:
                export_data['messages'].append({
                    'role': message.role,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat(),
                    'metadata': message.metadata
                })
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting conversation {call_sid}: {str(e)}")
            return {} 