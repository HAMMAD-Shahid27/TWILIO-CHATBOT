"""
Configuration Settings
Central configuration for the LLM Twilio Callbot
"""

import os
from typing import Dict, Any

# Bot Personality Configuration
BOT_PERSONALITY = {
    "name": "Alex",
    "tone": "friendly and professional",
    "specialties": ["customer service", "general knowledge", "small talk", "problem solving"],
    "language": "English",
    "greeting": "Hello! I'm Alex, your AI assistant. How can I help you today?",
    "goodbye": "Thank you for calling. Have a great day!",
    "fallback": "I'm sorry, I didn't understand that. Could you please repeat?"
}

# Voice Settings
VOICE_SETTINGS = {
    "voice": "en-US-Neural2-F",  # Twilio Neural voice
    "language": "en-US",
    "speech_rate": 1.0,
    "timeout": 10,
    "speech_timeout": "auto",
    "confidence_threshold": 0.5
}

# LLM Settings
LLM_SETTINGS = {
    "model": "gpt-3.5-turbo",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "max_history": 10
}

# Twilio Settings
TWILIO_SETTINGS = {
    "webhook_timeout": 30,
    "max_call_duration": 3600,  # 1 hour
    "retry_attempts": 3
}

# Application Settings
APP_SETTINGS = {
    "debug": os.getenv('FLASK_ENV') == 'development',
    "host": "0.0.0.0",
    "port": int(os.getenv('PORT', 5000)),
    "secret_key": os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here'),
    "max_conversations": 1000,
    "cleanup_interval": 3600  # 1 hour
}

# Logging Settings
LOGGING_SETTINGS = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/callbot.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Security Settings
SECURITY_SETTINGS = {
    "rate_limit": {
        "calls_per_minute": 10,
        "calls_per_hour": 100,
        "calls_per_day": 1000
    },
    "allowed_ips": [],  # Empty list means all IPs allowed
    "require_https": True
}

# Error Messages
ERROR_MESSAGES = {
    "rate_limit": "I'm receiving too many requests right now. Please try again in a moment.",
    "invalid_request": "I'm having trouble processing your request. Could you please rephrase that?",
    "authentication": "I'm experiencing technical difficulties. Please try again later.",
    "timeout": "I'm sorry, the request is taking too long. Please try again.",
    "general": "I'm sorry, I'm having trouble understanding. Could you please repeat that?"
}

# Conversation Templates
CONVERSATION_TEMPLATES = {
    "welcome": [
        "Hello! I'm {name}, your AI assistant. How can I help you today?",
        "Hi there! I'm {name}. What can I assist you with?",
        "Welcome! I'm {name}, ready to help. What do you need?"
    ],
    "goodbye": [
        "Thank you for calling. Have a great day!",
        "Thanks for chatting with me. Take care!",
        "It was nice talking to you. Goodbye!"
    ],
    "clarification": [
        "I didn't catch that. Could you please repeat?",
        "Could you please speak more clearly?",
        "I'm having trouble understanding. Could you rephrase that?"
    ],
    "confirmation": [
        "Did I understand you correctly?",
        "Is that right?",
        "Let me make sure I got that right."
    ]
}

# Feature Flags
FEATURE_FLAGS = {
    "sentiment_analysis": True,
    "intent_extraction": True,
    "conversation_search": True,
    "call_analytics": True,
    "multi_language": False,
    "voice_customization": True
}

# API Endpoints
API_ENDPOINTS = {
    "webhook": "/webhook",
    "status": "/api/status",
    "calls": "/api/calls",
    "conversations": "/api/conversations",
    "dashboard": "/dashboard"
}

# Database Settings (for future use)
DATABASE_SETTINGS = {
    "enabled": False,
    "type": "sqlite",  # sqlite, postgresql, mysql
    "url": "sqlite:///callbot.db",
    "pool_size": 10,
    "max_overflow": 20
}

# Monitoring Settings
MONITORING_SETTINGS = {
    "enabled": True,
    "metrics": {
        "call_duration": True,
        "response_time": True,
        "error_rate": True,
        "user_satisfaction": True
    },
    "alerts": {
        "high_error_rate": 0.1,  # 10%
        "long_response_time": 5.0,  # 5 seconds
        "low_confidence": 0.3
    }
}

def get_setting(category: str, key: str, default: Any = None) -> Any:
    """
    Get a setting value with fallback to default
    
    Args:
        category (str): Setting category (e.g., 'BOT_PERSONALITY')
        key (str): Setting key
        default (Any): Default value if not found
        
    Returns:
        Any: Setting value
    """
    settings_map = {
        'bot_personality': BOT_PERSONALITY,
        'voice_settings': VOICE_SETTINGS,
        'llm_settings': LLM_SETTINGS,
        'twilio_settings': TWILIO_SETTINGS,
        'app_settings': APP_SETTINGS,
        'logging_settings': LOGGING_SETTINGS,
        'security_settings': SECURITY_SETTINGS,
        'error_messages': ERROR_MESSAGES,
        'conversation_templates': CONVERSATION_TEMPLATES,
        'feature_flags': FEATURE_FLAGS,
        'api_endpoints': API_ENDPOINTS,
        'database_settings': DATABASE_SETTINGS,
        'monitoring_settings': MONITORING_SETTINGS
    }
    
    category_lower = category.lower()
    if category_lower in settings_map:
        return settings_map[category_lower].get(key, default)
    
    return default

def update_setting(category: str, key: str, value: Any) -> bool:
    """
    Update a setting value
    
    Args:
        category (str): Setting category
        key (str): Setting key
        value (Any): New value
        
    Returns:
        bool: True if updated successfully
    """
    settings_map = {
        'bot_personality': BOT_PERSONALITY,
        'voice_settings': VOICE_SETTINGS,
        'llm_settings': LLM_SETTINGS,
        'twilio_settings': TWILIO_SETTINGS,
        'app_settings': APP_SETTINGS,
        'logging_settings': LOGGING_SETTINGS,
        'security_settings': SECURITY_SETTINGS,
        'error_messages': ERROR_MESSAGES,
        'conversation_templates': CONVERSATION_TEMPLATES,
        'feature_flags': FEATURE_FLAGS,
        'api_endpoints': API_ENDPOINTS,
        'database_settings': DATABASE_SETTINGS,
        'monitoring_settings': MONITORING_SETTINGS
    }
    
    category_lower = category.lower()
    if category_lower in settings_map:
        settings_map[category_lower][key] = value
        return True
    
    return False 