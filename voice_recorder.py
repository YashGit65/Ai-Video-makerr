import asyncio
import edge_tts
from mutagen.mp3 import MP3

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


def get_audio_duration(audio_file):
    audio = MP3(audio_file)
    return audio.info.length
