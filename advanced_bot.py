import os
import logging
import cohere
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

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
co = cohere.Client(COHERE_API_KEY)

# Define conversation states
CHATTING = 0

# Store conversation history for each user
user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize conversation history for this user
    user_conversations[user_id] = []
    
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm a chatbot powered by Cohere AI. How can I help you today?"
    )
    return CHATTING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "I'm a chatbot powered by Cohere AI. Just send me a message and I'll respond!\n\n"
        "Commands:\n"
        "/start - Start a new conversation\n"
        "/help - Show this help message\n"
        "/reset - Reset your conversation history\n"
        "/end - End the conversation"
    )
    return CHATTING

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Reset the conversation history."""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    await update.message.reply_text("Conversation history has been reset.")
    return CHATTING

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle incoming messages and respond using Cohere AI with conversation history."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation history if it doesn't exist
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    # Add user message to conversation history
    user_conversations[user_id].append({"role": "USER", "message": user_message})
    
    # Let the user know the bot is processing
    await update.message.reply_text("Thinking...")
    
    try:
        # Generate a response using Cohere with conversation history
        response = co.chat(
            message=user_message,
            model="command",
            chat_history=user_conversations[user_id][:-1],  # Exclude the latest message
            preamble="You are a helpful assistant chatbot. Provide concise and informative responses."
        )
        
        # Add bot response to conversation history
        user_conversations[user_id].append({"role": "CHATBOT", "message": response.text})
        
        # Send the response back to the user
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your request. Please try again later."
        )
    
    # Keep the conversation going
    return CHATTING

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation."""
    user_id = update.effective_user.id
    
    # Clear conversation history
    if user_id in user_conversations:
        user_conversations.pop(user_id)
    
    await update.message.reply_text(
        "Conversation ended. Type /start to begin a new conversation."
    )
    return ConversationHandler.END

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fallback handler for unexpected commands."""
    await update.message.reply_text(
        "I didn't understand that command. Type /help for available commands."
    )
    return CHATTING

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHATTING: [
                CommandHandler("help", help_command),
                CommandHandler("reset", reset_command),
                CommandHandler("end", end_conversation),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, fallback)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 