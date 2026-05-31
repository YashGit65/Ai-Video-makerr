import shutil
from pathlib import Path

def cleanup_files(audio_file, video_file, output_dir):
    try:
        audio_path = Path(audio_file)
        video_path = Path(video_file)
        output_path = Path(output_dir)

        if audio_path.exists():
            audio_path.unlink()
            print(f"Deleted audio: {audio_path}")

        if video_path.exists():
            video_path.unlink()
            print(f"Deleted video: {video_path}")

        if output_path.exists():
            shutil.rmtree(output_path)
            print(f"Deleted directory: {output_path}")

        print("Cleanup complete.")

    except Exception as e:
        print(f"Cleanup failed: {e}")