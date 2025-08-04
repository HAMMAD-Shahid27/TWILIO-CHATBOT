"""
Helper Utilities
Common utility functions for the LLM Twilio Callbot
"""

import re
import hashlib
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

def sanitize_phone_number(phone_number: str) -> str:
    """
    Sanitize and format phone number
    
    Args:
        phone_number (str): Raw phone number
        
    Returns:
        str: Formatted phone number
    """
    if not phone_number:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    
    # Handle different formats
    if len(digits) == 10:
        return f"+1{digits}"  # US number
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"   # US number with country code
    elif len(digits) >= 10:
        return f"+{digits}"   # International number
    
    return phone_number

def validate_webhook_signature(request_body: str, signature: str, auth_token: str, url: str) -> bool:
    """
    Validate Twilio webhook signature
    
    Args:
        request_body (str): Raw request body
        signature (str): Twilio signature header
        auth_token (str): Twilio auth token
        url (str): Webhook URL
        
    Returns:
        bool: True if signature is valid
    """
    try:
        # This is a simplified validation - in production, use Twilio's validation library
        expected_signature = hashlib.sha256(
            (url + request_body + auth_token).encode('utf-8')
        ).hexdigest()
        
        return signature == expected_signature
    except Exception:
        return False

def extract_call_metadata(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and clean call metadata from Twilio request
    
    Args:
        request_data (Dict): Twilio webhook request data
        
    Returns:
        Dict: Cleaned call metadata
    """
    metadata = {
        'call_sid': request_data.get('CallSid', ''),
        'from_number': sanitize_phone_number(request_data.get('From', '')),
        'to_number': sanitize_phone_number(request_data.get('To', '')),
        'direction': request_data.get('Direction', ''),
        'call_status': request_data.get('CallStatus', ''),
        'speech_result': request_data.get('SpeechResult', ''),
        'confidence': float(request_data.get('Confidence', 0)),
        'timestamp': datetime.now().isoformat()
    }
    
    return metadata

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def generate_conversation_id(call_sid: str, timestamp: datetime = None) -> str:
    """
    Generate a unique conversation ID
    
    Args:
        call_sid (str): Twilio call SID
        timestamp (datetime): Timestamp for the conversation
        
    Returns:
        str: Unique conversation ID
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create a hash from call_sid and timestamp
    hash_input = f"{call_sid}_{timestamp.isoformat()}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:12]

def parse_intent_from_text(text: str) -> Dict[str, Any]:
    """
    Simple intent parsing from text
    
    Args:
        text (str): Input text
        
    Returns:
        Dict: Intent analysis
    """
    text_lower = text.lower()
    
    # Define intent patterns
    intent_patterns = {
        'greeting': r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
        'goodbye': r'\b(goodbye|bye|see you|talk to you later|have a good day)\b',
        'question': r'\b(what|when|where|who|why|how|can you|could you|would you)\b',
        'complaint': r'\b(problem|issue|wrong|broken|not working|complaint|angry|upset)\b',
        'request': r'\b(help|assist|support|need|want|please)\b',
        'confirmation': r'\b(yes|yeah|sure|okay|ok|correct|right)\b',
        'negation': r'\b(no|nope|not|never|wrong|incorrect)\b',
        'thanks': r'\b(thank you|thanks|appreciate it|grateful)\b',
        'apology': r'\b(sorry|apologize|excuse me|pardon)\b',
        'urgency': r'\b(urgent|asap|immediately|right now|emergency|critical)\b'
    }
    
    detected_intents = []
    for intent, pattern in intent_patterns.items():
        if re.search(pattern, text_lower):
            detected_intents.append(intent)
    
    # Determine primary intent
    primary_intent = detected_intents[0] if detected_intents else 'general'
    
    return {
        'primary_intent': primary_intent,
        'all_intents': detected_intents,
        'confidence': 0.8 if detected_intents else 0.3
    }

def analyze_sentiment_simple(text: str) -> Dict[str, Any]:
    """
    Simple sentiment analysis
    
    Args:
        text (str): Input text
        
    Returns:
        Dict: Sentiment analysis
    """
    text_lower = text.lower()
    
    # Positive words
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'happy', 'pleased', 'satisfied', 'love', 'like', 'awesome', 'perfect'
    ]
    
    # Negative words
    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'disappointed', 'angry',
        'upset', 'frustrated', 'hate', 'dislike', 'worst', 'broken', 'problem'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Determine sentiment
    if positive_count > negative_count:
        sentiment = 'positive'
        confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
    elif negative_count > positive_count:
        sentiment = 'negative'
        confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
    else:
        sentiment = 'neutral'
        confidence = 0.5
    
    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'positive_score': positive_count,
        'negative_score': negative_count
    }

def rate_limit_check(call_sid: str, rate_limits: Dict[str, int], call_history: Dict[str, List[datetime]]) -> bool:
    """
    Check if a call should be rate limited
    
    Args:
        call_sid (str): Call SID
        rate_limits (Dict): Rate limit configuration
        call_history (Dict): Call history by phone number
        
    Returns:
        bool: True if call should be allowed
    """
    current_time = datetime.now()
    
    # Get phone number from call_sid (simplified)
    phone_number = call_sid.split('_')[0] if '_' in call_sid else call_sid
    
    if phone_number not in call_history:
        call_history[phone_number] = []
    
    # Remove old calls outside the time windows
    call_history[phone_number] = [
        call_time for call_time in call_history[phone_number]
        if current_time - call_time < timedelta(days=1)
    ]
    
    # Check rate limits
    calls_per_minute = len([
        call_time for call_time in call_history[phone_number]
        if current_time - call_time < timedelta(minutes=1)
    ])
    
    calls_per_hour = len([
        call_time for call_time in call_history[phone_number]
        if current_time - call_time < timedelta(hours=1)
    ])
    
    calls_per_day = len(call_history[phone_number])
    
    # Check if any limits are exceeded
    if (calls_per_minute > rate_limits.get('calls_per_minute', 10) or
        calls_per_hour > rate_limits.get('calls_per_hour', 100) or
        calls_per_day > rate_limits.get('calls_per_day', 1000)):
        return False
    
    # Add current call to history
    call_history[phone_number].append(current_time)
    return True

def create_error_response(error_type: str, message: str = None) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error_type (str): Type of error
        message (str): Error message
        
    Returns:
        Dict: Error response
    """
    error_messages = {
        'rate_limit': 'Too many requests. Please try again later.',
        'invalid_request': 'Invalid request format.',
        'authentication': 'Authentication failed.',
        'timeout': 'Request timed out.',
        'general': 'An error occurred. Please try again.'
    }
    
    return {
        'error': True,
        'error_type': error_type,
        'message': message or error_messages.get(error_type, 'Unknown error'),
        'timestamp': datetime.now().isoformat()
    }

def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid
    """
    if not phone_number:
        return False
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    
    # Check if it's a valid length
    return 10 <= len(digits) <= 15

def mask_phone_number(phone_number: str) -> str:
    """
    Mask phone number for privacy
    
    Args:
        phone_number (str): Phone number to mask
        
    Returns:
        str: Masked phone number
    """
    if not phone_number:
        return ""
    
    # Keep only last 4 digits visible
    digits = re.sub(r'\D', '', phone_number)
    if len(digits) >= 4:
        return f"***-***-{digits[-4:]}"
    
    return "***-***-****"

def json_serializer(obj):
    """
    JSON serializer for objects not serializable by default json code
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_dumps(data: Any) -> str:
    """
    Safely serialize data to JSON
    
    Args:
        data (Any): Data to serialize
        
    Returns:
        str: JSON string
    """
    try:
        return json.dumps(data, default=json_serializer, indent=2)
    except Exception:
        return json.dumps({'error': 'Failed to serialize data'}) 