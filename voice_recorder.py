import asyncio
import edge_tts
from mutagen.mp3 import MP3
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()

api2 = os.getenv("api2")

client = InferenceClient(
    provider="nscale",
    api_key=api2
)


import asyncio
import edge_tts

async def generate_voice(script):
    """
    Takes script as input
    Generates output.mp3
    Returns filename
    """

    output_file = "output.mp3"

    communicate = edge_tts.Communicate(
        script,
        "hi-IN-SwaraNeural",
        rate="+40%",
        pitch="+2Hz",
        volume="+5%"
    )

    await communicate.save(output_file)

    print(f"Voice saved as {output_file}")

    return output_file


# Example usage
script = """
Did you know staying awake too long
can make your brain act drunk?
"""

audio_file = asyncio.run(generate_voice(script))

print(audio_file)

def get_audio_duration(audio_file):
    audio = MP3(audio_file)
    return audio.info.length
