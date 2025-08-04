# 🤖 LLM Twilio Callbot Chatbot

A sophisticated AI-powered voice chatbot built with Twilio, OpenAI, and Python that can handle natural conversations over phone calls.

## ✨ Features

- **Natural Voice Conversations**: Powered by OpenAI's GPT models for human-like responses
- **Text-to-Speech**: Converts AI responses to natural-sounding speech
- **Speech-to-Text**: Accurately transcribes user speech to text
- **Multi-language Support**: Supports multiple languages and accents
- **Conversation Memory**: Maintains context throughout the conversation
- **Customizable Personality**: Easy to configure bot personality and responses
- **Error Handling**: Robust error handling and fallback responses
- **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Twilio Account (with phone number)
- OpenAI API Key
- ngrok (for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HAMMAD-Shahid27/llm-twilio-callbot.git
   cd llm-twilio-callbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   OPENAI_API_KEY=your_openai_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Set up webhook URL**
   - Install ngrok: `ngrok http 5000`
   - Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
   - In your Twilio console, set the webhook URL to: `https://abc123.ngrok.io/webhook`

## 📁 Project Structure

```
TWILIO CHATBOT/
├── app.py                 # Main Flask application
├── chatbot/
│   ├── __init__.py
│   ├── llm_handler.py     # OpenAI integration
│   ├── voice_handler.py   # Voice processing
│   └── conversation.py    # Conversation management
├── config/
│   └── settings.py        # Configuration settings
├── utils/
│   ├── __init__.py
│   ├── logger.py          # Logging utilities
│   └── helpers.py         # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_chatbot.py
│   └── test_voice.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── index.html
│   └── dashboard.html
├── requirements.txt
├── env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

## 🔧 Configuration

### Bot Personality

Edit `config/settings.py` to customize the bot's personality:

```python
BOT_PERSONALITY = {
    "name": "Alex",
    "tone": "friendly and professional",
    "specialties": ["customer service", "general knowledge", "small talk"],
    "language": "English"
}
```

### Voice Settings

Configure voice parameters in the same file:

```python
VOICE_SETTINGS = {
    "voice": "en-US-Neural2-F",  # Twilio voice
    "language": "en-US",
    "speech_rate": 1.0
}
```

## 📞 Usage

### Making a Call

1. Call your Twilio phone number
2. The bot will answer and introduce itself
3. Start speaking naturally
4. The bot will respond with AI-generated responses

### Example Conversation

**User**: "Hello, can you help me with customer service?"

**Bot**: "Hello! I'm Alex, your AI assistant. I'd be happy to help you with customer service. What specific issue can I assist you with today?"

**User**: "I have a problem with my order"

**Bot**: "I understand you're having an issue with your order. To help you better, could you please provide your order number and describe what problem you're experiencing?"

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

## 📊 Monitoring

The application includes comprehensive logging. Check logs in the `logs/` directory for:

- Conversation transcripts
- Error logs
- Performance metrics
- API usage statistics

## 🔒 Security

- All API keys are stored in environment variables
- HTTPS required for production
- Input validation and sanitization
- Rate limiting on API calls

## 🚀 Deployment

### Heroku

1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy: `git push heroku main`

### Docker

```bash
docker build -t llm-twilio-callbot .
docker run -p 5000:5000 llm-twilio-callbot
```

### Docker Compose

```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- Twilio for voice communication infrastructure
- Flask for the web framework
- The open-source community for various utilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/HAMMAD-Shahid27/llm-twilio-callbot/issues) page
2. Create a new issue with detailed information
3. Contact: hammadshahid980@gmail.com

---


**Made with ❤️ by Hammad Shahid** 
