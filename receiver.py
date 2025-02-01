# Standard library imports
import os
from os.path import join
from dotenv import load_dotenv
import yaml

# Load environment variables (only for sensitive data)
load_dotenv()

# Load application config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Third-party imports
import aiohttp
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import openai
# Local imports
from receive_voice_msg import get_transcript
from send_voice_msg import send_voice_message

# Get sensitive environment variables
TELEGRAM_BOT_KEY = os.getenv('TELEGRAM_BOT_KEY')
BACKEND_ENDPOINT = os.getenv('BACKEND_ENDPOINT')
VOICE_STORE_DIR = config['voice']['store_dir']
REQUIRE_TELEGRAM_USERNAME = config['telegram']['require_username']
DELETE_VOICE_AFTER_TRANSCRIPTION = config['voice']['delete_after_transcription']
OUTGOING_VOICE_STORE_DIR = config['voice']['outgoing_dir']
VOICE_MODEL = config['voice']['voice_model']
VOICE_NAME = config['voice']['voice_name']
DELETE_TTS_AFTER_SENDING = config['voice']['delete_tts_after_sending']
# Initialize OpenAI client
openai_client = openai.OpenAI()

async def send_message_async(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Message sent successfully to chat_id: {chat_id}")
    except Exception as e:
        print(f"Failed to send message: {e}")

async def forward_message_to_backend(message: str, chat_id: int):
    print('forwarding message to backend', message, chat_id)
    """Send message and chat_id to backend endpoint via POST request.
    
    Args:
        message (str): Message content to forward
        chat_id (int): Telegram chat ID
    """
    print('forwarding message to backend', message, chat_id)
    payload = {
        'message': message,
        'chat_id': chat_id
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BACKEND_ENDPOINT, json=payload) as response:
                if response.status == 200:
                    print(f"Successfully forwarded message to backend")
                    response_data = await response.json()
                    if response_data.get('messageToUser'):
                        if response_data.get('includeVoiceMessage'):
                            await send_voice_message(response_data['messageToUser'], chat_id, TELEGRAM_BOT_KEY, OUTGOING_VOICE_STORE_DIR, openai_client, voice_model=VOICE_MODEL, voice_name=VOICE_NAME, delete_tts_after_sending=DELETE_TTS_AFTER_SENDING)
                        await send_message_async(TELEGRAM_BOT_KEY, chat_id, response_data['messageToUser'])
                    print(f"Backend response had status {response.status}")
                else:
                    print(f"Backend response had status {response.status}")
                    await send_message_async(TELEGRAM_BOT_KEY, chat_id, f"Backend response had status {response.status}")
        except Exception as e:
            print(f"Error forwarding message to backend: {e}")

def telegram_message_to_dict(update: Update) -> dict:
    """Convert Telegram message to a dictionary format.
    
    Args:
        update (Update): Telegram update object
        
    Returns:
        dict: Dictionary containing message metadata
    """
    return {
        'chat_id': update.message.chat.id,
        'message_id': update.message.message_id,
        'username': update.message.from_user.username,
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'timestamp': update.message.date.strftime('%Y-%m-%d %H:%M:%S')
    }

async def download_file(url: str, path: str) -> None:
    """Download a file from URL and save to specified path.
    
    Args:
        url (str): URL of the file to download
        path (str): Local path to save the file
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(path, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages.
    
    Args:
        update (Update): Telegram update object
        context (ContextTypes.DEFAULT_TYPE): Callback context
    """
    try:
        if REQUIRE_TELEGRAM_USERNAME and not update.message.from_user.username:
            await update.message.reply_text('Please set a Telegram username to use this bot.')
            return
            
        metadata_json = {'telegram_message': telegram_message_to_dict(update)}
        text_content = update.message.text
        print('text_content', text_content)
        await forward_message_to_backend(text_content, update.message.chat.id)
    except Exception as e:
        print(f'Error handling message: {e}')

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages.
    
    Args:
        update (Update): Telegram update object
        context (ContextTypes.DEFAULT_TYPE): Callback context
    """
    try:
        if REQUIRE_TELEGRAM_USERNAME and not update.message.from_user.username:
            await update.message.reply_text('Please set a Telegram username to use this bot.')
            return
            
        new_file = await context.bot.get_file(update.message.voice.file_id)
        file_ending = '.m4a' if update.message.voice.mime_type == 'audio/mpeg' else '.' + new_file.file_path.split('.')[-1]
        
        os.makedirs(VOICE_STORE_DIR, exist_ok=True)
        output_path = join(VOICE_STORE_DIR, f"{new_file.file_id}{file_ending}")
        
        await download_file(new_file.file_path, output_path)
        transcript = get_transcript(output_path, openai_client)
        if DELETE_VOICE_AFTER_TRANSCRIPTION:
            os.remove(output_path)
        await forward_message_to_backend(transcript, update.message.chat.id)

        await update.message.reply_text(f'Voice message saved to: {output_path}')
        await update.message.reply_text(f'Transcript: {transcript}')

    except Exception as e:
        print(f'Error handling voice message: {e}')
        try:
            await update.message.reply_text('Failed to process voice message')
        except Exception:
            print('Failed to send error message to user')

def main():
    """Initialize and run the Telegram bot."""
    app = ApplicationBuilder().token(TELEGRAM_BOT_KEY).build()
    
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print('Starting polling...')
    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()