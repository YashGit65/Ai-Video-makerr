# AI YouTube Shorts Generator

This project turns a single topic into a complete Hindi YouTube Shorts style video. It generates a viral-style Hindi narration script, creates a Hindi voiceover, builds a storyboard, generates vertical AI images for each scene, and merges everything into a 1080x1920 MP4 video.

The project can run from the command line or through a Streamlit web interface.

## What I Implemented

- End-to-end short video generation from only a topic.
- English-to-Hindi topic conversion before script creation.
- Hindi viral Shorts script generation using an LLM prompt.
- Automatic voiceover generation using Microsoft Edge TTS.
- Audio duration detection to decide how many visual scenes are needed.
- AI storyboard generation with narration chunks and matching image prompts.
- JSON parsing, normalization, and repair retry for unreliable LLM storyboard output.
- Vertical AI image generation for every storyboard scene.
- FFmpeg-based final video rendering with a smooth zoom effect.
- Streamlit frontend for entering the topic, generating the video, previewing it, and downloading the MP4.
- Optional YouTube upload helper using the YouTube Data API and OAuth.
- Optional cleanup utility for deleting generated temporary files.

## Techniques Used

### LLM Prompt Engineering

The project uses `meta-llama/Llama-3.1-8B-Instruct` through Hugging Face Inference API. `llm.py` creates a Hugging Face `InferenceClient` with the `nscale` provider and reads the token from the `api2` environment variable. Prompts are written with strict rules so the model returns useful production content:

- Topic translation returns only the Hindi topic.
- Script generation returns only voiceover narration, with no timestamps, headings, bullets, camera notes, or scene descriptions.
- The script prompt focuses on hook, suspense, retention, emotional storytelling, short spoken lines, and an impactful ending.
- Storyboard generation asks for structured JSON with a consistent base visual style and scene-specific prompts.

### Structured Output Handling

`scene_maker.py` expects the storyboard as JSON, but LLMs can sometimes return markdown or invalid JSON. To make this more reliable, the project:

- Removes fenced code blocks if the response contains them.
- Attempts normal `json.loads`.
- Falls back to decoding from the first JSON object found in the text.
- Validates that `base_style` and `scene_map` exist.
- Normalizes alternate scene keys like `prompt`, `image_prompt`, and `visual`.
- Sends a repair prompt and retries once if the first storyboard response is invalid.

### Dynamic Scene Timing

The number of storyboard scenes is based on the generated audio duration:

```python
scene_count = max(1, int(duration // 3))
```

After images are generated, the project calculates:

- Duration per image
- Frames per image
- Final image timing at 25 FPS

This keeps the visuals aligned with the voiceover instead of using a fixed number of scenes.

### AI Image Generation

`photo_generator.py` uses `black-forest-labs/FLUX.1-schnell` through Hugging Face Inference API. Images are generated in a vertical format:

```text
864 x 1536
```

Each scene prompt is combined with the storyboard `base_style` so the video keeps a consistent visual direction while still changing scene-by-scene.

### AI Voice Generation

`voice_recorder.py` uses `edge-tts` with the Hindi voice:

```text
hi-IN-SwaraNeural
```

The voice is tuned with:

- Rate: `+40%`
- Pitch: `+2Hz`
- Volume: `+5%`

`mutagen` is used to read the MP3 duration after the voiceover is generated.

### Video Rendering

`merger.py` uses FFmpeg directly. It combines generated images and the MP3 voiceover into the final video.

The video technique used is a simple Ken Burns style zoom effect through FFmpeg `zoompan`:

```text
zoompan=z='min(zoom+0.0015,1.15)':d=<frames_per_image>:s=1080x1920:fps=25
```

The final video uses:

- 1080x1920 vertical Shorts resolution
- 25 FPS
- H.264 video encoding
- AAC audio encoding
- `yuv420p` pixel format for compatibility

## Project Flow

```text
User topic
   |
   v
main.py
   |
   +--> script_maker.py
   |       Converts topic to Hindi and generates a Shorts narration script
   |
   +--> voice_recorder.py
   |       Generates output.mp3 and reads its duration
   |
   +--> scene_maker.py
   |       Splits the script into timed visual scenes and returns storyboard JSON
   |
   +--> photo_generator.py
   |       Generates vertical scene images from storyboard prompts
   |
   +--> merger.py
   |       Uses FFmpeg to combine images and voice into the final MP4
   |
   +--> youtube_uploader.py
           Optional YouTube upload support
```

## Main Files

| File | Purpose |
| --- | --- |
| `main.py` | Main orchestrator for the full video generation pipeline. |
| `llm.py` | Loads `.env` and creates the Hugging Face `InferenceClient`. |
| `script_maker.py` | Converts topics to Hindi and generates Hindi narration scripts. |
| `scene_maker.py` | Generates, parses, validates, and repairs storyboard JSON. |
| `photo_generator.py` | Generates vertical FLUX images for each storyboard scene. |
| `voice_recorder.py` | Generates Hindi TTS voiceover and reads MP3 duration. |
| `merger.py` | Uses FFmpeg to create the final vertical MP4. |
| `streamlit_app.py` | Web UI for token input, topic input, video preview, download, and upload flow. |
| `youtube_uploader.py` | YouTube Data API upload helper. |
| `cleanup.py` | Optional cleanup helper for generated files. |
| `tester_script.py` | Experimental/older script generation test file. |
| `requirements.txt` | Python dependencies. |
| `packages.txt` | System dependency for deployment, currently `ffmpeg`. |

## Requirements

- Python 3.10 or newer
- FFmpeg installed and available on PATH
- Hugging Face API token with inference access
- Internet access for Hugging Face image/text generation and Edge TTS
- Optional: Google Cloud OAuth credentials for YouTube upload

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Install FFmpeg and confirm it works:

```powershell
ffmpeg -version
```

Create a `.env` file in the project root:

```text
api2=your_huggingface_token_here
```

The Streamlit app can also accept the Hugging Face token from the sidebar, so `.env` is mainly needed for command-line usage.

## Run From Command Line

Generate a video from a topic:

```powershell
python main.py "interesting space facts"
```

Use a custom output folder:

```powershell
python main.py "interesting space facts" --output-dir space_facts
```

If no topic is passed, the script asks for one interactively.

## Run Streamlit App

```powershell
streamlit run streamlit_app.py
```

The Streamlit app lets you:

- Enter a Hugging Face API token.
- Enter a video topic.
- Choose an optional output folder.
- Watch generation status updates.
- Preview the generated video.
- Download the final MP4.
- Connect a YouTube account and upload, if OAuth credentials are configured.

## Output

For a topic like:

```text
interesting space facts
```

The project creates a sanitized video name and saves:

```text
<output-folder>/
  script.txt
  storyboard.json
  scene_01.png
  scene_02.png
  ...

output.mp3
interesting_space_facts.mp4
```

Notes:

- `output.mp3` is written in the project root and may be overwritten on the next run.
- The final MP4 is written in the project root.
- Scene images, script, and storyboard are saved inside the output folder.

## YouTube Upload

YouTube upload support is implemented in `youtube_uploader.py` using:

- YouTube Data API v3
- OAuth
- `google-api-python-client`
- `google-auth-oauthlib`

In `main.py`, the direct upload lines are currently commented so local video generation remains the default behavior. The Streamlit app contains an OAuth-based upload flow after the video is generated, and that flow expects Google OAuth credentials in Streamlit secrets. `youtube_uploader.py` also provides a local client-secret based helper if you want to wire upload into the CLI flow later.

Keep OAuth files private. Do not commit:

- `.env`
- `token.json`
- `client_secret*.json`
- `.streamlit/secrets.toml`

## Troubleshooting

### `ffmpeg is required`

Install FFmpeg and make sure `ffmpeg` is available from the terminal:

```powershell
ffmpeg -version
```

### Hugging Face authentication errors

Check that your `.env` contains:

```text
api2=your_huggingface_token_here
```

For Streamlit, paste the token into the sidebar before generating.

### Invalid storyboard JSON

The project already tries to repair invalid JSON once. If it still fails, run generation again. LLM output can vary, especially for long or difficult topics.

### YouTube upload issues

Make sure:

- YouTube Data API v3 is enabled in Google Cloud.
- OAuth credentials are configured correctly.
- The YouTube upload scope is allowed.
- The account you connect has permission to upload videos.

## Current Limitations

- The generated images are still images with FFmpeg zoom animation, not true video generation.
- `output.mp3` is reused as a fixed filename, so parallel runs can overwrite each other.
- The CLI upload path exists but is commented out in `main.py`.
- Generated quality depends on the selected Hugging Face models and API availability.
