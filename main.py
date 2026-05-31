import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from merger import create_video
from photo_generator import generate_photos
from scene_maker import generate_storyboard
from script_maker import generate_hindi_short_script, convert_topic_to_hindi
from voice_recorder import generate_voice, get_audio_duration
from youtube_uploader import authenticate_youtube, upload_video
from cleanup import cleanup_files


BASE_DIR = Path(__file__).resolve().parent
FPS = 25


def sanitize_video_name(topic):
    video_name = re.sub(r"[^\w.-]+", "_", topic, flags=re.UNICODE).strip("._-")
    return video_name or "short_video"


def generate_short_video(topic, output_dir_name=None, status_callback=None):
    os.chdir(BASE_DIR)

    def report(message):
        print(message)
        if status_callback:
            status_callback(message)

    if not topic:
        raise ValueError("Topic is required.")

    video_name = sanitize_video_name(topic)
    output_dir = BASE_DIR / (output_dir_name or video_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    report("Generating script...")
    hindi_topic = convert_topic_to_hindi(topic)
    report(f"Hindi Topic: {hindi_topic}")
    script = generate_hindi_short_script(hindi_topic)
    (output_dir / "script.txt").write_text(script, encoding="utf-8")

    report("Generating voice...")
    audio_file = asyncio.run(generate_voice(script))
    duration = get_audio_duration(audio_file)
    report(f"Duration: {round(duration, 2)} seconds")

    report("Generating storyboard...")
    storyboard = generate_storyboard(script, duration)
    (output_dir / "storyboard.json").write_text(
        json.dumps(storyboard, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report("Generating photos...")
    generated_images = generate_photos(storyboard, str(output_dir))
    report(f"Generated {len(generated_images)} images.")

    image_count = len(generated_images)
    if image_count == 0:
        raise RuntimeError(f"No generated scene images found in {output_dir}")

    duration_per_image = duration / image_count
    frames_per_image = max(1, int(duration_per_image * FPS))

    report(f"Images: {image_count}")
    report(f"Duration per image: {duration_per_image}")
    report(f"Frames per image: {frames_per_image}")

    report("Creating video...")
    create_video(video_name, str(output_dir), frames_per_image, audio_file)

    video_file = BASE_DIR / f"{video_name}.mp4"
    report(f"Done: {video_file}")
    
    

    return {
        "topic": topic,
        "hindi_topic": hindi_topic,
        "video_name": video_name,
        "output_dir": output_dir,
        "script": script,
        "audio_file": BASE_DIR / audio_file,
        "duration": duration,
        "storyboard": storyboard,
        "generated_images": generated_images,
        "image_count": image_count,
        "duration_per_image": duration_per_image,
        "frames_per_image": frames_per_image,
        "video_file": video_file
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Hindi YouTube Shorts video.")
    parser.add_argument("topic", nargs="?", help="Topic for the YouTube Short.")
    parser.add_argument("--output-dir", help="Folder where images/script/storyboard are saved.")
    args = parser.parse_args()

    topic = args.topic or input("Enter topic: ").strip()
    if not topic:
        raise SystemExit("Topic is required.")

    result = generate_short_video(topic, args.output_dir)

    print("\n========== SCRIPT ==========\n")
    print(result["script"])
