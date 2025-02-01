import os
import requests
from os.path import exists, join

import hashlib
import aiohttp

def md5_string(input_string):
    m = hashlib.md5()
    m.update(input_string.encode('utf-8'))
    return m.hexdigest()

def text_to_audiofile(input_text, speech_file_path, openai_client, response_format='opus', voice_model=None, voice_name=None):
    with openai_client.audio.speech.with_streaming_response.create(
        model=voice_model,
        voice=voice_name,
        response_format=response_format,
        input=input_text,
    ) as response:
        response.stream_to_file(speech_file_path)
    assert exists(speech_file_path), 'soundfile has not been created'
    return response

async def send_ogg(ogg_path, chat_id, token):
    print('send_ogg...')

    upload_audio_url = f"https://api.telegram.org/bot{token}/sendAudio?chat_id={chat_id}"
    
    # For aiohttp, we need to use FormData for file uploads
    form = aiohttp.FormData()
    form.add_field('audio',
                  open(ogg_path, 'rb'),
                  filename='Message.ogg')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(upload_audio_url, data=form) as response:
            result = await response.json()
    print('send ogg done')
    return result

async def send_voice_message(input_text, chat_id, token, outgoing_dir, openai_client, voice_model=None, voice_name=None, delete_tts_after_sending=False):
    if not os.path.exists(outgoing_dir):
        os.makedirs(outgoing_dir)
    print('sending voice message', input_text)
    input_md5 = md5_string(input_text)
    ogg_path = join(outgoing_dir, input_md5 + '.ogg')
    if exists(ogg_path):
        print('ogg for input text already exists')
    else:
        text_to_audiofile(input_text, ogg_path, openai_client, voice_model=voice_model, voice_name=voice_name)
    send_ogg_response = await send_ogg(ogg_path, chat_id, token)
    if delete_tts_after_sending:
        print('deleting tts file after sending')
        os.remove(ogg_path)
    return send_ogg_response


async def send_text_message(chat_id, text, token):
    assert len(text) > 0, "Cannot send an empty msg back on Telegram"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            return await response.json()