"""
Voice Handler - Speech Processing
Handles voice-related operations and speech processing
"""

import logging
import re
from typing import Dict, Any, Optional
from config.settings import VOICE_SETTINGS

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles voice processing and speech-related operations"""
    
    def __init__(self):
        """Initialize the voice handler"""
        self.voice_settings = VOICE_SETTINGS
        self.speech_patterns = self._load_speech_patterns()
        
        logger.info("Voice Handler initialized")
    
    def process_speech_input(self, speech_text: str, confidence: float = 0.0) -> Dict[str, Any]:
        """
        Process and clean speech input
        
        Args:
            speech_text (str): Raw speech text from Twilio
            confidence (float): Speech recognition confidence
            
        Returns:
            Dict: Processed speech data
        """
        try:
            # Clean the speech text
            cleaned_text = self._clean_speech_text(speech_text)
            
            # Analyze speech characteristics
            analysis = self._analyze_speech(cleaned_text, confidence)
            
            # Detect speech patterns
            patterns = self._detect_speech_patterns(cleaned_text)
            
            return {
                "original_text": speech_text,
                "cleaned_text": cleaned_text,
                "confidence": confidence,
                "analysis": analysis,
                "patterns": patterns,
                "is_valid": len(cleaned_text.strip()) > 0
            }
            
        except Exception as e:
            logger.error(f"Error processing speech input: {str(e)}")
            return {
                "original_text": speech_text,
                "cleaned_text": "",
                "confidence": 0.0,
                "analysis": {},
                "patterns": [],
                "is_valid": False,
                "error": str(e)
            }
    
    def _clean_speech_text(self, text: str) -> str:
        """
        Clean and normalize speech text
        
        Args:
            text (str): Raw speech text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common speech artifacts
        text = re.sub(r'\b(um|uh|ah|er|hmm)\b', '', text)
        
        # Remove punctuation that might interfere
        text = re.sub(r'[^\w\s]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _analyze_speech(self, text: str, confidence: float) -> Dict[str, Any]:
        """
        Analyze speech characteristics
        
        Args:
            text (str): Cleaned speech text
            confidence (float): Recognition confidence
            
        Returns:
            Dict: Speech analysis results
        """
        analysis = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "confidence": confidence,
            "language": self.voice_settings.get("language", "en-US"),
            "is_question": self._is_question(text),
            "has_greeting": self._has_greeting(text),
            "has_goodbye": self._has_goodbye(text),
            "urgency_level": self._detect_urgency(text)
        }
        
        return analysis
    
    def _detect_speech_patterns(self, text: str) -> list:
        """
        Detect common speech patterns
        
        Args:
            text (str): Cleaned speech text
            
        Returns:
            list: Detected patterns
        """
        patterns = []
        
        for pattern_name, pattern_regex in self.speech_patterns.items():
            if re.search(pattern_regex, text, re.IGNORECASE):
                patterns.append(pattern_name)
        
        return patterns
    
    def _load_speech_patterns(self) -> Dict[str, str]:
        """
        Load common speech patterns for detection
        
        Returns:
            Dict: Pattern name to regex mapping
        """
        return {
            "greeting": r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
            "goodbye": r'\b(goodbye|bye|see you|talk to you later|have a good day)\b',
            "question": r'\b(what|when|where|who|why|how|can you|could you|would you)\b',
            "complaint": r'\b(problem|issue|wrong|broken|not working|complaint)\b',
            "request": r'\b(help|assist|support|need|want|please)\b',
            "confirmation": r'\b(yes|yeah|sure|okay|ok|correct|right)\b',
            "negation": r'\b(no|nope|not|never|wrong|incorrect)\b',
            "thanks": r'\b(thank you|thanks|appreciate it|grateful)\b',
            "apology": r'\b(sorry|apologize|excuse me|pardon)\b',
            "urgency": r'\b(urgent|asap|immediately|right now|emergency)\b'
        }
    
    def _is_question(self, text: str) -> bool:
        """Check if text contains a question"""
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which']
        return any(word in text.lower() for word in question_words) or text.strip().endswith('?')
    
    def _has_greeting(self, text: str) -> bool:
        """Check if text contains a greeting"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in text.lower() for greeting in greetings)
    
    def _has_goodbye(self, text: str) -> bool:
        """Check if text contains a goodbye"""
        goodbyes = ['goodbye', 'bye', 'see you', 'talk to you later', 'have a good day']
        return any(goodbye in text.lower() for goodbye in goodbyes)
    
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level in text"""
        urgent_words = ['urgent', 'asap', 'immediately', 'right now', 'emergency', 'critical']
        moderate_words = ['soon', 'quickly', 'fast', 'hurry']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in urgent_words):
            return "high"
        elif any(word in text_lower for word in moderate_words):
            return "moderate"
        else:
            return "low"
    
    def format_response_for_speech(self, text: str) -> str:
        """
        Format text response for optimal speech synthesis
        
        Args:
            text (str): Text to format
            
        Returns:
            str: Formatted text for speech
        """
        if not text:
            return ""
        
        # Remove markdown and formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Add pauses for better speech flow
        text = re.sub(r'([.!?])\s+', r'\1 <break time="0.5s"/> ', text)
        
        # Handle abbreviations
        text = re.sub(r'\b(etc\.|vs\.|i\.e\.|e\.g\.)\b', lambda m: m.group(1).replace('.', ''), text)
        
        # Ensure proper spacing
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def get_voice_parameters(self) -> Dict[str, Any]:
        """
        Get voice parameters for Twilio
        
        Returns:
            Dict: Voice parameters
        """
        return {
            "voice": self.voice_settings.get("voice", "en-US-Neural2-F"),
            "language": self.voice_settings.get("language", "en-US"),
            "speech_rate": self.voice_settings.get("speech_rate", 1.0)
        }
    
    def validate_speech_confidence(self, confidence: float, threshold: float = 0.5) -> bool:
        """
        Validate if speech recognition confidence is acceptable
        
        Args:
            confidence (float): Recognition confidence
            threshold (float): Minimum confidence threshold
            
        Returns:
            bool: True if confidence is acceptable
        """
        return confidence >= threshold
    
    def get_fallback_response(self, confidence: float) -> str:
        """
        Get appropriate fallback response based on confidence
        
        Args:
            confidence (float): Speech recognition confidence
            
        Returns:
            str: Fallback response
        """
        if confidence < 0.3:
            return "I'm having trouble understanding. Could you please speak more clearly?"
        elif confidence < 0.6:
            return "I didn't catch that completely. Could you please repeat?"
        else:
            return "I'm sorry, I didn't understand. Could you please rephrase that?" 