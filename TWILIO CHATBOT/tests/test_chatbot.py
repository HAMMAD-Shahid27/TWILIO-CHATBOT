"""
Test suite for chatbot functionality
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.llm_handler import LLMHandler
from chatbot.voice_handler import VoiceHandler
from chatbot.conversation import ConversationManager, Conversation, Message
from utils.helpers import (
    sanitize_phone_number, 
    parse_intent_from_text, 
    analyze_sentiment_simple,
    validate_phone_number,
    mask_phone_number
)

class TestLLMHandler:
    """Test LLM Handler functionality"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_llm_handler_initialization(self):
        """Test LLM handler initialization"""
        handler = LLMHandler()
        assert handler.api_key == 'test-key'
        assert handler.model == 'gpt-3.5-turbo'
        assert handler.max_tokens == 150
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.ChatCompletion.create')
    def test_generate_response(self, mock_openai):
        """Test response generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_openai.return_value = mock_response
        
        handler = LLMHandler()
        response = handler.generate_response("Hello", [])
        
        assert response == "Hello! How can I help you?"
        mock_openai.assert_called_once()
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.ChatCompletion.create')
    def test_generate_response_with_history(self, mock_openai):
        """Test response generation with conversation history"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "I understand your issue."
        mock_openai.return_value = mock_response
        
        handler = LLMHandler()
        history = [
            {'role': 'user', 'content': 'I have a problem'},
            {'role': 'assistant', 'content': 'What kind of problem?'}
        ]
        
        response = handler.generate_response("My order is wrong", history)
        
        assert response == "I understand your issue."
        # Verify that history was included in the API call
        call_args = mock_openai.call_args[1]['messages']
        assert len(call_args) > 2  # System message + history + current input

class TestVoiceHandler:
    """Test Voice Handler functionality"""
    
    def test_voice_handler_initialization(self):
        """Test voice handler initialization"""
        handler = VoiceHandler()
        assert handler.voice_settings is not None
        assert 'voice' in handler.voice_settings
    
    def test_process_speech_input(self):
        """Test speech input processing"""
        handler = VoiceHandler()
        result = handler.process_speech_input("Hello there", 0.8)
        
        assert result['original_text'] == "Hello there"
        assert result['cleaned_text'] == "hello there"
        assert result['confidence'] == 0.8
        assert result['is_valid'] == True
    
    def test_clean_speech_text(self):
        """Test speech text cleaning"""
        handler = VoiceHandler()
        
        # Test basic cleaning
        cleaned = handler._clean_speech_text("  Hello   World  ")
        assert cleaned == "hello world"
        
        # Test removal of speech artifacts
        cleaned = handler._clean_speech_text("Um hello uh there")
        assert cleaned == "hello there"
        
        # Test empty input
        cleaned = handler._clean_speech_text("")
        assert cleaned == ""
    
    def test_detect_speech_patterns(self):
        """Test speech pattern detection"""
        handler = VoiceHandler()
        
        # Test greeting detection
        patterns = handler._detect_speech_patterns("hello there")
        assert "greeting" in patterns
        
        # Test question detection
        patterns = handler._detect_speech_patterns("what is this")
        assert "question" in patterns
        
        # Test complaint detection
        patterns = handler._detect_speech_patterns("I have a problem")
        assert "complaint" in patterns
    
    def test_validate_speech_confidence(self):
        """Test speech confidence validation"""
        handler = VoiceHandler()
        
        assert handler.validate_speech_confidence(0.8) == True
        assert handler.validate_speech_confidence(0.3) == False
        assert handler.validate_speech_confidence(0.6, threshold=0.7) == False

class TestConversationManager:
    """Test Conversation Manager functionality"""
    
    def test_conversation_manager_initialization(self):
        """Test conversation manager initialization"""
        manager = ConversationManager()
        assert manager.conversations == {}
        assert manager.max_conversations == 1000
    
    def test_get_conversation_new(self):
        """Test getting a new conversation"""
        manager = ConversationManager()
        conversation = manager.get_conversation("test-call-sid", "+1234567890", "+0987654321")
        
        assert conversation.call_sid == "test-call-sid"
        assert conversation.from_number == "+1234567890"
        assert conversation.to_number == "+0987654321"
        assert conversation.is_active == True
        assert len(conversation.messages) == 0
    
    def test_get_conversation_existing(self):
        """Test getting an existing conversation"""
        manager = ConversationManager()
        
        # Create conversation
        conv1 = manager.get_conversation("test-call-sid")
        
        # Get same conversation
        conv2 = manager.get_conversation("test-call-sid")
        
        assert conv1 is conv2  # Same object reference
    
    def test_add_message(self):
        """Test adding messages to conversation"""
        manager = ConversationManager()
        
        # Add user message
        success = manager.add_message("test-call-sid", "user", "Hello")
        assert success == True
        
        # Add assistant message
        success = manager.add_message("test-call-sid", "assistant", "Hi there!")
        assert success == True
        
        # Check messages
        conversation = manager.get_conversation("test-call-sid")
        assert len(conversation.messages) == 2
        assert conversation.messages[0].content == "Hello"
        assert conversation.messages[1].content == "Hi there!"
    
    def test_get_history(self):
        """Test getting conversation history"""
        manager = ConversationManager()
        
        # Add some messages
        manager.add_message("test-call-sid", "user", "Hello")
        manager.add_message("test-call-sid", "assistant", "Hi!")
        manager.add_message("test-call-sid", "user", "How are you?")
        
        # Get history
        history = manager.get_history("test-call-sid", limit=2)
        
        assert len(history) == 2
        assert history[0]['role'] == 'assistant'
        assert history[1]['role'] == 'user'
    
    def test_end_conversation(self):
        """Test ending a conversation"""
        manager = ConversationManager()
        
        # Create and end conversation
        conversation = manager.get_conversation("test-call-sid")
        success = manager.end_conversation("test-call-sid")
        
        assert success == True
        assert conversation.is_active == False
        assert 'end_time' in conversation.metadata
    
    def test_get_conversation_stats(self):
        """Test getting conversation statistics"""
        manager = ConversationManager()
        
        # Add messages
        manager.add_message("test-call-sid", "user", "Hello")
        manager.add_message("test-call-sid", "assistant", "Hi!")
        manager.add_message("test-call-sid", "user", "How are you?")
        
        # Get stats
        stats = manager.get_conversation_stats("test-call-sid")
        
        assert stats['total_messages'] == 3
        assert stats['user_messages'] == 2
        assert stats['assistant_messages'] == 1
        assert stats['is_active'] == True

class TestHelpers:
    """Test helper utility functions"""
    
    def test_sanitize_phone_number(self):
        """Test phone number sanitization"""
        # Test US number
        assert sanitize_phone_number("123-456-7890") == "+11234567890"
        
        # Test number with country code
        assert sanitize_phone_number("+1-123-456-7890") == "+11234567890"
        
        # Test international number
        assert sanitize_phone_number("+44-20-7946-0958") == "+442079460958"
        
        # Test empty input
        assert sanitize_phone_number("") == ""
    
    def test_parse_intent_from_text(self):
        """Test intent parsing"""
        # Test greeting
        intent = parse_intent_from_text("Hello there")
        assert intent['primary_intent'] == 'greeting'
        assert 'greeting' in intent['all_intents']
        
        # Test question
        intent = parse_intent_from_text("What is this?")
        assert intent['primary_intent'] == 'question'
        assert 'question' in intent['all_intents']
        
        # Test complaint
        intent = parse_intent_from_text("I have a problem")
        assert intent['primary_intent'] == 'complaint'
        assert 'complaint' in intent['all_intents']
        
        # Test general text
        intent = parse_intent_from_text("Random text here")
        assert intent['primary_intent'] == 'general'
    
    def test_analyze_sentiment_simple(self):
        """Test simple sentiment analysis"""
        # Test positive sentiment
        sentiment = analyze_sentiment_simple("This is great and amazing!")
        assert sentiment['sentiment'] == 'positive'
        assert sentiment['positive_score'] > sentiment['negative_score']
        
        # Test negative sentiment
        sentiment = analyze_sentiment_simple("This is terrible and awful!")
        assert sentiment['sentiment'] == 'negative'
        assert sentiment['negative_score'] > sentiment['positive_score']
        
        # Test neutral sentiment
        sentiment = analyze_sentiment_simple("This is just a regular message")
        assert sentiment['sentiment'] == 'neutral'
    
    def test_validate_phone_number(self):
        """Test phone number validation"""
        assert validate_phone_number("123-456-7890") == True
        assert validate_phone_number("+1-123-456-7890") == True
        assert validate_phone_number("123") == False
        assert validate_phone_number("") == False
    
    def test_mask_phone_number(self):
        """Test phone number masking"""
        assert mask_phone_number("123-456-7890") == "***-***-7890"
        assert mask_phone_number("+1-123-456-7890") == "***-***-7890"
        assert mask_phone_number("") == ""

class TestIntegration:
    """Integration tests"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.ChatCompletion.create')
    def test_full_conversation_flow(self, mock_openai):
        """Test complete conversation flow"""
        # Mock OpenAI responses
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_openai.return_value = mock_response
        
        # Initialize components
        llm_handler = LLMHandler()
        voice_handler = VoiceHandler()
        conversation_manager = ConversationManager()
        
        # Simulate conversation
        call_sid = "test-call-123"
        
        # Process user input
        speech_data = voice_handler.process_speech_input("Hello", 0.9)
        assert speech_data['is_valid'] == True
        
        # Get AI response
        response = llm_handler.generate_response(speech_data['cleaned_text'], [])
        assert response == "Hello! How can I help you?"
        
        # Add to conversation
        conversation_manager.add_message(call_sid, "user", speech_data['cleaned_text'])
        conversation_manager.add_message(call_sid, "assistant", response)
        
        # Verify conversation
        conversation = conversation_manager.get_conversation(call_sid)
        assert len(conversation.messages) == 2
        assert conversation.messages[0].role == "user"
        assert conversation.messages[1].role == "assistant"

if __name__ == "__main__":
    pytest.main([__file__]) 