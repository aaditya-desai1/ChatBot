import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, Response
import threading

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

# Get port from environment variable
PORT = int(os.environ.get('PORT', 8080))

# Initialize Gemini client
try:
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY environment variable is not set")
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    logger.info(f"Configuring Gemini with API key: {GEMINI_API_KEY[:5]}...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # List available models for debugging
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        logger.info(f"Available models: {model_names}")
    except Exception as model_list_error:
        logger.warning(f"Could not list available models: {model_list_error}")
    
    logger.info("Initializing Gemini 2.0 Flash model...")
    model = genai.GenerativeModel(
        'gemini-2.0-flash',
        # Use a lower temperature for more concise responses
        generation_config={"temperature": 0.3, "max_output_tokens": 2048}
    )
    logger.info("Gemini model initialized successfully")
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
    
    # Add system instruction for concise responses
    chat.send_message("You are a helpful assistant that provides clear, concise responses. Keep your answers brief and to the point. Avoid lengthy explanations unless specifically asked.")
    
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
        response_text = response.text
        
        # Add messages to history
        conversation_history[user_id].append({"role": "USER", "message": user_message})
        conversation_history[user_id].append({"role": "ASSISTANT", "message": response_text})
        
        # Delete the "Thinking..." message
        try:
            await processing_message.delete()
        except Exception as e:
            logger.warning(f"Could not delete processing message: {e}")
        
        # Split the response if it's too long (Telegram has 4096 character limit)
        if len(response_text) <= 4000:
            await update.message.reply_text(response_text)
        else:
            # Split the response into chunks of 4000 characters
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(f"(continued {i+1}/{len(chunks)})\n{chunk}")
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        try:
            await processing_message.delete()
        except Exception as delete_error:
            logger.warning(f"Could not delete processing message: {delete_error}")
            
        error_message = f"I'm having trouble connecting to my AI service. Error: {str(e)[:100]}"
        await update.message.reply_text(error_message)

# Create Flask app
app = Flask(__name__)

# Create the bot application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("clear", clear_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask routes
@app.route('/')
def home():
    return "Bot is running!"

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle webhook requests from Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return Response(status=200)

def main():
    """Start the bot."""
    try:
        # Get the URL from environment or use a default for local development
        webhook_url = os.environ.get('RENDER_EXTERNAL_URL', f'https://your-app-name.onrender.com')
        webhook_path = f'/{TELEGRAM_BOT_TOKEN}'
        
        # Set up the webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=webhook_path,
            webhook_url=f"{webhook_url}{webhook_path}"
        )
        
        # Run Flask in a separate thread (not needed with webhook mode)
        # But we'll keep a simplified version for the health check endpoint
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT+1))
        flask_thread.daemon = True
        flask_thread.start()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main() 