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

BASE_DIR = Path(__file__).resolve().parent
FPS = 25

if __name__ == "__main__":
    os.chdir(BASE_DIR)

    parser = argparse.ArgumentParser(description="Generate a Hindi YouTube Shorts video.")
    parser.add_argument("topic", nargs="?", help="Topic for the YouTube Short.")
    parser.add_argument("--output-dir", help="Folder where images/script/storyboard are saved.")
    args = parser.parse_args()

    topic = args.topic or input("Enter topic: ").strip()
    if not topic:
        raise SystemExit("Topic is required.")

    video_name = re.sub(r"[^\w.-]+", "_", topic, flags=re.UNICODE).strip("._-")
    video_name = video_name or "short_video"

    output_dir = BASE_DIR / (args.output_dir or video_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating script...")
    topic = convert_topic_to_hindi(topic)
    print("Hindi Topic:", topic)
    script = generate_hindi_short_script(topic)
    (output_dir / "script.txt").write_text(script, encoding="utf-8")

    print("\n========== SCRIPT ==========\n")
    print(script)

    print("\nGenerating voice...")
    audio_file = asyncio.run(generate_voice(script))
    duration = get_audio_duration(audio_file)
    print("Duration:", round(duration, 2), "seconds")

    print("\nGenerating storyboard...")
    storyboard = generate_storyboard(script, duration)
    (output_dir / "storyboard.json").write_text(
        json.dumps(storyboard, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nGenerating photos...")
    generated_images = generate_photos(storyboard, str(output_dir))
    print(f"Generated {len(generated_images)} images.")

    image_count = len(generated_images)
    if image_count == 0:
        raise RuntimeError(f"No generated scene images found in {output_dir}")

    duration_per_image = duration / image_count
    frames_per_image = max(1, int(duration_per_image * FPS))

    print("Images:", image_count)
    print("Duration per image:", duration_per_image)
    print("Frames per image:", frames_per_image)

    print("\nCreating video...")
    create_video(video_name, str(output_dir), frames_per_image, audio_file)

    print(f"\nDone: {BASE_DIR / f'{video_name}.mp4'}")
