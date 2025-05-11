import os
import logging
import cohere
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import threading
from flask import Flask, request

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("config.env")

# Get API keys
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Cohere client
try:
    co = cohere.Client(COHERE_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Cohere client: {e}")
    raise

# Store conversation history
conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize conversation history for new users
    conversation_history[user_id] = []
    
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm a chatbot powered by Cohere AI. How can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
I'm a chatbot powered by Cohere AI. Here are some things you can do:
- Just chat with me naturally
- Use /start to start a new conversation
- Use /clear to clear conversation history
- Use /help to see this message again
    """
    await update.message.reply_text(help_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the conversation history for the user."""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("Conversation history cleared! Let's start fresh.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and respond using Cohere AI."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation history if it doesn't exist
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Format messages for Cohere's chat API
    chat_history = [
        {"role": "System", "message": "You are a helpful and friendly chatbot. Be concise and clear in your responses."}
    ]
    
    # Add conversation history
    for msg in conversation_history[user_id][-5:]:
        if msg["role"] == "USER":
            chat_history.append({"role": "User", "message": msg["message"]})
        else:
            chat_history.append({"role": "Chatbot", "message": msg["message"]})
    
    # Let the user know the bot is processing
    processing_message = await update.message.reply_text("Thinking...")
    
    try:
        # Generate a response using Cohere
        response = co.chat(
            message=user_message,
            model="command",
            temperature=0.7,
            chat_history=chat_history
        )
        
        # Add messages to history
        conversation_history[user_id].append({"role": "USER", "message": user_message})
        conversation_history[user_id].append({"role": "ASSISTANT", "message": response.text})
        
        # Delete the "Thinking..." message and send the response
        await processing_message.delete()
        await update.message.reply_text(response.text)
        
    except cohere.error.CohereError as ce:
        logger.error(f"Cohere API error: {ce}")
        await processing_message.delete()
        await update.message.reply_text(
            "I'm having trouble connecting to my AI service. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await processing_message.delete()
        await update.message.reply_text(
            "I encountered an unexpected error. My developers have been notified."
        )

# Create a simple Flask web server to keep the app alive on Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    return "Webhook received!"

def run_flask():
    # Get the port from the environment variable or use 8080 as default
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def run_bot():
    """Start the bot."""
    try:
        # Create the Application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

def main():
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the bot in the main thread
    run_bot()

if __name__ == "__main__":
    main() 