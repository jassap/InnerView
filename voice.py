import os
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from dotenv import load_dotenv

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def speak_from_file(file_path):
    """Reads text from a file and converts it to speech."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"Reading from {file_path}...")
    audio = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", 
        text=content,
        model_id="eleven_multilingual_v2"
    )
    play(audio)