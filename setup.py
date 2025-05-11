#!/usr/bin/env python3
import os
import sys

def setup_bot():
    """Interactive setup for the Cohere AI Telegram bot."""
    print("Welcome to the Cohere AI Telegram Bot Setup!")
    print("===========================================")
    
    # Check if config.env exists
    if os.path.exists("config.env"):
        print("Found existing config.env file.")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup aborted. Using existing configuration.")
            return
    
    # Get API keys
    cohere_api_key = input("Enter your Cohere API key: ").strip()
    telegram_token = input("Enter your Telegram Bot Token: ").strip()
    
    # Validate inputs
    if not cohere_api_key:
        print("Error: Cohere API key cannot be empty.")
        return
    
    if not telegram_token:
        print("Error: Telegram Bot Token cannot be empty.")
        return
    
    # Write to config.env
    with open("config.env", "w") as f:
        f.write(f"COHERE_API_KEY={cohere_api_key}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")
    
    print("\nConfiguration saved to config.env")
    print("\nTo run the basic bot: python bot.py")
    print("To run the advanced bot with conversation history: python advanced_bot.py")

if __name__ == "__main__":
    setup_bot() 