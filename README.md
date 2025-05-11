# Cohere AI Telegram Chatbot

A simple Telegram chatbot powered by Cohere AI.

## Setup

### Automatic Setup
1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the setup script:
   ```
   python setup.py
   ```
4. Follow the prompts to enter your API keys

### Manual Setup
1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit the `config.env` file with your API keys:
   - Get a Cohere API key from [cohere.com](https://cohere.com)
   - Create a Telegram bot and get a token from [BotFather](https://t.me/botfather)

## Running the Bot

### Basic Bot
Run the basic bot with:
```
python bot.py
```

### Advanced Bot (with conversation history)
Run the advanced bot with:
```
python advanced_bot.py
```

## Usage

- Start the bot: `/start`
- Get help: `/help`
- Reset conversation (advanced bot only): `/reset`
- End conversation (advanced bot only): `/end`
- Chat with the bot by sending any message

## Features

### Basic Bot
- Responds to messages using Cohere's AI models
- Simple and easy to customize
- Handles errors gracefully

### Advanced Bot
- All features of the basic bot
- Maintains conversation history for each user
- Allows resetting or ending conversations
- Uses conversation history for more contextual responses 