# YouTube Auto-Summarizer Bot

This bot checks a list of YouTube channels for new uploads, retrieves transcripts (with Whisper fallback), summarizes them using GPT-4o, and posts them to a Discord channel.

## 🧱 Features

- Supports multiple YouTube channels
- Whisper API fallback when transcript is unavailable
- Uses GPT-4o for bullet-point summaries
- Sends formatted messages to Discord
- Fully Dockerized for server deployment

## 🛠 Setup

1. Clone this repo.
2. Add a `.env` file with:
   ```
   DISCORD_WEBHOOK=your_webhook
   OPENAI_API_KEY=your_api_key
   ```
3. Build and run:
   ```bash
   docker build -t yt-summary-bot .
   docker run --env-file .env yt-summary-bot
   ```

## ✅ Dependencies

- Python 3.10
- OpenAI API (GPT-4o + Whisper)
- Docker (recommended)