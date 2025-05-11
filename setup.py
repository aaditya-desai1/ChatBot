#!/usr/bin/env python3
import os
import sys

def setup_bot():
    """Interactive setup for the Google Gemini AI Telegram bot."""
    print("Welcome to the Google Gemini AI Telegram Bot Setup!")
    print("=================================================")
    
    # Check if config.env exists
    if os.path.exists("config.env"):
        print("Found existing config.env file.")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup aborted. Using existing configuration.")
            return
    
    # Get API keys
    gemini_api_key = input("Enter your Google Gemini API key: ").strip()
    telegram_token = input("Enter your Telegram Bot Token: ").strip()
    
    # Validate inputs
    if not gemini_api_key:
        print("Error: Google Gemini API key cannot be empty.")
        return
    
    if not telegram_token:
        print("Error: Telegram Bot Token cannot be empty.")
        return
    
    # Write to config.env
    with open("config.env", "w") as f:
        f.write(f"GEMINI_API_KEY={gemini_api_key}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")
    
    print("\nConfiguration saved to config.env")
    print("\nTo run the bot: python bot.py")

if __name__ == "__main__":
    setup_bot() 