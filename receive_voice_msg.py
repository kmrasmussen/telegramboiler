import requests

def get_transcript(recording_file_path : str, openai_client) -> str:
    """
    Takes a complete path to a m4a voice memo and calls OpenAI Whisper API and returns transcript as string

    Parameter:
        recording_file_path (str): complete path to a m4a voice memo
    
    Returns:
        transcript (str): text transcript from Whisper
    """
    media_file = open(recording_file_path, 'rb')
    response = openai_client.audio.transcriptions.create(
        model='whisper-1',
        file=media_file,
        response_format='json'
    )
    return response.text

def download_oga_file(input_url, output_path):
    response = requests.get(input_url)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded .oga file from {input_url} to {output_path}")
    else:
        print(f"Failed to download file. HTTP status code: {response.status_code}")
