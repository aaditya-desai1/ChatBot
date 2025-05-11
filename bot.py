import os
import logging
import google.generativeai as genai
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Gemini client
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
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
        f"Hi {user.first_name}! I'm a chatbot powered by Google Gemini AI. How can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
I'm a chatbot powered by Google Gemini AI. Here are some things you can do:
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
    """Handle incoming messages and respond using Gemini AI."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation history if it doesn't exist
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # Format messages for Gemini's chat API
    chat = model.start_chat(history=[])
    
    # Add conversation history
    for msg in conversation_history[user_id][-5:]:
        if msg["role"] == "USER":
            chat.history.append({"role": "user", "parts": [msg["message"]]})
        else:
            chat.history.append({"role": "model", "parts": [msg["message"]]})
    
    # Let the user know the bot is processing
    processing_message = await update.message.reply_text("Thinking...")
    
    try:
        # Generate a response using Gemini
        response = chat.send_message(user_message)
        
        # Add messages to history
        conversation_history[user_id].append({"role": "USER", "message": user_message})
        conversation_history[user_id].append({"role": "ASSISTANT", "message": response.text})
        
        # Delete the "Thinking..." message and send the response
        await processing_message.delete()
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        await processing_message.delete()
        await update.message.reply_text(
            "I'm having trouble connecting to my AI service. Please try again in a moment."
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