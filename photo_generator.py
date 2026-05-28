import os
import time
from pathlib import Path
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

api2 = os.getenv("api2")



client = InferenceClient(
    provider="nscale",
    api_key=api2,
)

def generate_photos(storyboard, output_dir):
    OUTPUT_DIR = Path(output_dir)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base_style = storyboard["base_style"]
    scene_map = storyboard["scene_map"]
    saved_images = []

    for i, item in enumerate(scene_map, start=1):
        prompt = f"{item['scene']}, {base_style}"

        print(f"Generating scene {i}...")

        try:
            image = client.text_to_image(
                prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=864,
                height=1536
            )

            image_path = OUTPUT_DIR / f"scene_{i:02}.png"
            image.save(image_path)
            saved_images.append(image_path)

            print(f"Saved {image_path}")
            time.sleep(1)

        except Exception as e:
            raise RuntimeError(f"Failed to generate scene {i}: {e}") from e

    return saved_images
