# Telegram Bot with REST Backend

A simple Telegram bot that forwards messages to a REST endpoint and can transcribe voice messages using OpenAI Whisper.

## Setup

1. Get a Telegram bot token from [@BotFather](https://t.me/botfather)
2. Get an OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)
3. Copy `.env-example` to `.env` and add your tokens
4. Run `docker compose up`

The example backend endpoint will echo received messages back to the user.