"""
LLM Handler - OpenAI Integration
Handles communication with OpenAI's GPT models
"""

import os
import logging
import openai
from typing import List, Dict, Any
from config.settings import BOT_PERSONALITY, LLM_SETTINGS

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles interactions with OpenAI's language models"""
    
    def __init__(self):
        """Initialize the LLM handler"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        openai.api_key = self.api_key
        self.model = LLM_SETTINGS.get('model', 'gpt-3.5-turbo')
        self.max_tokens = LLM_SETTINGS.get('max_tokens', 150)
        self.temperature = LLM_SETTINGS.get('temperature', 0.7)
        
        logger.info(f"LLM Handler initialized with model: {self.model}")
    
    def generate_response(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response using OpenAI's GPT model
        
        Args:
            user_input (str): The user's input text
            conversation_history (List[Dict]): Previous conversation messages
            
        Returns:
            str: Generated response from the AI
        """
        try:
            # Build the conversation context
            messages = self._build_messages(user_input, conversation_history)
            
            # Make API call to OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract the response
            ai_response = response.choices[0].message.content.strip()
            
            logger.info(f"Generated response: {ai_response[:100]}...")
            return ai_response
            
        except openai.error.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return "I'm receiving too many requests right now. Please try again in a moment."
            
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid request to OpenAI: {str(e)}")
            return "I'm having trouble processing your request. Could you please rephrase that?"
            
        except openai.error.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return "I'm experiencing technical difficulties. Please try again later."
            
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {str(e)}")
            return "I'm sorry, I'm having trouble understanding. Could you please repeat that?"
    
    def _build_messages(self, user_input: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Build the messages array for OpenAI API
        
        Args:
            user_input (str): Current user input
            conversation_history (List[Dict]): Previous conversation
            
        Returns:
            List[Dict]: Formatted messages for OpenAI API
        """
        messages = []
        
        # System message with bot personality
        system_message = self._create_system_message()
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history[-10:]:  # Keep last 10 messages for context
                role = "user" if message.get("role") == "user" else "assistant"
                content = message.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _create_system_message(self) -> str:
        """
        Create the system message with bot personality
        
        Returns:
            str: System message for OpenAI
        """
        personality = BOT_PERSONALITY
        
        system_message = f"""You are {personality['name']}, an AI assistant with the following characteristics:

- Tone: {personality['tone']}
- Specialties: {', '.join(personality['specialties'])}
- Language: {personality['language']}

Guidelines:
1. Keep responses concise and natural for voice conversation
2. Be helpful, friendly, and professional
3. If you don't understand something, ask for clarification
4. For customer service issues, gather necessary information
5. Avoid technical jargon unless specifically asked
6. Respond as if you're having a natural phone conversation

Remember: You're speaking over the phone, so keep responses conversational and not too long."""

        return system_message
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of user input
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict: Sentiment analysis results
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following text. Return only: positive, negative, or neutral."},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            return {
                "sentiment": sentiment,
                "confidence": 0.8  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0}
    
    def extract_intent(self, text: str) -> Dict[str, Any]:
        """
        Extract the intent from user input
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict: Intent analysis results
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the main intent from the following text. Return only: greeting, question, complaint, request, goodbye, or other."},
                    {"role": "user", "content": text}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            return {
                "intent": intent,
                "confidence": 0.8  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Error in intent extraction: {str(e)}")
            return {"intent": "other", "confidence": 0.0} 