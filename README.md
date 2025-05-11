# Telegram Chatbot with Google Gemini AI

A Telegram chatbot powered by Google's Gemini AI that can engage in natural conversations with users. This bot is designed to be deployed on Render.com's free tier.

## Features

- Natural conversation with Google Gemini AI
- Command handling for /start, /help, and /clear
- Conversation history tracking for context-aware responses
- Easy deployment to Render.com

## Requirements

- Python 3.10+
- A Telegram bot token (from [BotFather](https://t.me/botfather))
- A Google Gemini API key (from [Google AI Studio](https://ai.google.dev/))

## Installation

1. Clone this repository:
```
git clone <your-repository-url>
cd <repository-directory>
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `config.env` file with your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

## Running Locally

To run the bot locally:

```
python bot.py
```

The bot will start and listen for messages from Telegram users.

## Deployment

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Usage

Once the bot is running, users can interact with it through Telegram:

1. Start a conversation with `/start`
2. Ask questions or chat naturally
3. Clear conversation history with `/clear`
4. Get help with `/help`

## How It Works

The bot uses Google's Gemini AI to generate responses to user messages. It maintains conversation history to provide context-aware responses. The bot is built using the python-telegram-bot library and uses Flask to create a simple web server to keep the app alive on Render.com.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram bot framework
- [Google Gemini AI](https://ai.google.dev/) for the AI capabilities
- [Flask](https://flask.palletsprojects.com/) for the web server 