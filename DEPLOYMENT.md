# Deploying the Telegram Bot to Render.com

This guide explains how to deploy your Telegram bot to Render.com's free tier.

## Prerequisites

1. A Render.com account (sign up at https://render.com)
2. Your Telegram bot token (from BotFather)
3. Your Cohere API key

## Deployment Steps

### 1. Push your code to a Git repository

First, push your code to GitHub, GitLab, or any other Git provider supported by Render.

### 2. Create a new Web Service on Render

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Connect your Git repository
4. Configure your web service:
   - **Name**: Choose a name for your service (e.g., "my-telegram-bot")
   - **Environment**: Select "Python"
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### 3. Add Environment Variables

In the "Environment" section, add the following environment variables:
- `COHERE_API_KEY`: Your Cohere API key
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token

### 4. Deploy

Click "Create Web Service" to deploy your bot.

## Monitoring and Logs

After deployment, you can monitor your bot's performance and view logs directly from the Render dashboard.

## Free Tier Limitations

Render's free tier has some limitations:
- The service will spin down after 15 minutes of inactivity
- Limited to 750 hours of runtime per month
- Limited to 512 MB of RAM

Your bot will automatically restart when it receives a new request after being spun down.

## Troubleshooting

If your bot isn't working properly:

1. Check the logs in the Render dashboard
2. Verify your environment variables are set correctly
3. Make sure your bot is properly registered with BotFather
4. Ensure your Cohere API key is valid 