#!/usr/bin/env python3
"""
LLM Twilio Callbot - Main Application
A sophisticated AI-powered voice chatbot using Twilio and OpenAI

Author: Hammad Shahid
Email: hammadshahid980@gmail.com
GitHub: https://github.com/HAMMAD-Shahid27
LinkedIn: https://www.linkedin.com/in/hammad-shahid-23a560350/
"""

import os
import logging
from flask import Flask, request, jsonify, render_template
from twilio.twiml import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv

from chatbot.llm_handler import LLMHandler
from chatbot.voice_handler import VoiceHandler
from chatbot.conversation import ConversationManager
from utils.logger import setup_logger
from config.settings import *

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Initialize Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# Initialize chatbot components
llm_handler = LLMHandler()
voice_handler = VoiceHandler()
conversation_manager = ConversationManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Admin dashboard for monitoring calls"""
    return render_template('dashboard.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Twilio webhook endpoint for handling incoming calls
    """
    try:
        # Get call details from Twilio
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        speech_result = request.form.get('SpeechResult', '')
        confidence = request.form.get('Confidence', 0)
        
        logger.info(f"Received call from {from_number} to {to_number}")
        logger.info(f"Speech result: {speech_result} (confidence: {confidence})")
        
        # Initialize or get conversation
        conversation = conversation_manager.get_conversation(call_sid)
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Handle first-time call
        if not conversation.is_started():
            # Welcome message
            welcome_message = f"Hello! I'm {BOT_PERSONALITY['name']}, your AI assistant. How can I help you today?"
            response.say(welcome_message, voice=VOICE_SETTINGS['voice'])
            conversation.start()
            
            # Set up speech recognition
            gather = response.gather(
                input='speech',
                timeout=10,
                speech_timeout='auto',
                language=VOICE_SETTINGS['language'],
                action='/webhook',
                method='POST'
            )
            gather.say("I'm listening...", voice=VOICE_SETTINGS['voice'])
            
        else:
            # Process user input
            if speech_result:
                # Get AI response
                ai_response = llm_handler.generate_response(
                    user_input=speech_result,
                    conversation_history=conversation.get_history()
                )
                
                # Add to conversation history
                conversation.add_message('user', speech_result)
                conversation.add_message('assistant', ai_response)
                
                # Convert to speech and respond
                response.say(ai_response, voice=VOICE_SETTINGS['voice'])
                
                # Continue listening
                gather = response.gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    language=VOICE_SETTINGS['language'],
                    action='/webhook',
                    method='POST'
                )
                gather.say("What else can I help you with?", voice=VOICE_SETTINGS['voice'])
                
            else:
                # No speech detected
                response.say("I didn't catch that. Could you please repeat?", voice=VOICE_SETTINGS['voice'])
                gather = response.gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    language=VOICE_SETTINGS['language'],
                    action='/webhook',
                    method='POST'
                )
        
        # Handle hangup
        response.say("Thank you for calling. Have a great day!", voice=VOICE_SETTINGS['voice'])
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, I'm experiencing technical difficulties. Please try again later.", 
                    voice=VOICE_SETTINGS['voice'])
        return str(response)

@app.route('/api/status')
def api_status():
    """API endpoint to check service status"""
    return jsonify({
        'status': 'healthy',
        'service': 'LLM Twilio Callbot',
        'version': '1.0.0'
    })

@app.route('/api/calls')
def api_calls():
    """API endpoint to get recent calls"""
    try:
        calls = twilio_client.calls.list(limit=10)
        call_data = []
        for call in calls:
            call_data.append({
                'sid': call.sid,
                'from': call.from_,
                'to': call.to,
                'status': call.status,
                'start_time': call.start_time.isoformat() if call.start_time else None,
                'duration': call.duration
            })
        return jsonify(call_data)
    except Exception as e:
        logger.error(f"Error fetching calls: {str(e)}")
        return jsonify({'error': 'Failed to fetch calls'}), 500

@app.route('/api/conversations')
def api_conversations():
    """API endpoint to get conversation history"""
    try:
        conversations = conversation_manager.get_all_conversations()
        return jsonify(conversations)
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Validate environment variables
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your .env file")
        exit(1)
    
    logger.info("Starting LLM Twilio Callbot...")
    logger.info(f"Bot personality: {BOT_PERSONALITY['name']}")
    logger.info(f"Voice settings: {VOICE_SETTINGS['voice']}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    ) 