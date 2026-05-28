import subprocess
import shutil
from pathlib import Path


def create_video(topic, output_dir, frames_per_image, audio_file="output.mp3"):
    """
    Create vertical video from generated images + voice audio.
    
    Args:
        topic (str): Output video name
        output_dir (str): Folder containing scene images
        frames_per_image (int): Duration of each image
        audio_file (str): Voice audio file to attach
    """

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to create the video, but it was not found on PATH.")

    output_dir = Path(output_dir).resolve()
    audio_file = Path(audio_file).resolve()
    output_video = Path(f"{topic}.mp4")
    image_pattern = output_dir / "scene_%02d.png"

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    command = [
        ffmpeg,
        "-y",
        "-i", str(image_pattern),
        "-i", str(audio_file),
        "-vf",
        f"zoompan=z='min(zoom+0.0015,1.15)':d={frames_per_image}:s=1080x1920:fps=25",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(output_video)
    ]

    subprocess.run(command, check=True)

    print(f"Video created: {output_video}")
