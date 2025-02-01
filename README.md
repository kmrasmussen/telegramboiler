# Telegram Bot with REST Backend

A simple Telegram bot that forwards messages to a REST endpoint and can transcribe voice messages using OpenAI Whisper.

## Setup

1. Get a Telegram bot token from [@BotFather](https://t.me/botfather)
2. Get an OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)
3. Copy `.env-example` to `.env` and add your tokens
4. Run the hellowworld example:
```
docker compose -f docker-compose.helloworld.yml up
```
When you want to use your own endpoint, edit the `docker-compose.yourendpoint.yml` file to point to your endpoint, and use:
```
docker compose -f docker-compose.yourendpoint.yml up
```

## REST Endpoint Interface

### Request

```json
{
"message": "Text from user or transcribed voice message",
"chat_id": 123456789
}
```

### Response

```json
{
    "status": "success",
    "message": "Processing status message",
    "messageToUser": "Message to send back to Telegram user (optional)",
    "includeVoiceMessage": true  // Optional: Convert messageToUser to voice using TTS
}
```

The example backend endpoint will echo received messages back to the user.

## Example real endpoint
I will try to maintain a real external endpoint here: http://aws.kmrasmussen.com/telegramboilerservice1/myendpoint   