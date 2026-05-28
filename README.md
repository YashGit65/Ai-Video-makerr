# AI Video Maker

AI Video Maker turns a topic into a short vertical video with a Hindi script, voiceover, generated images, and final MP4 output.

## Project Architecture

```text
User topic
   |
   v
main.py
   |
   +--> script_maker.py
   |       Converts topic to Hindi and writes a short script
   |
   +--> voice_recorder.py
   |       Generates output.mp3 and reads audio duration
   |
   +--> scene_maker.py
   |       Creates storyboard.json with scene text and image prompts
   |
   +--> photo_generator.py
   |       Generates scene_01.png, scene_02.png, ... from storyboard prompts
   |
   +--> merger.py
           Combines generated images and output.mp3 into final video.mp4
```

## How To Use

1. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

2. Install `ffmpeg` and make sure it is available on your PATH:

```powershell
ffmpeg -version
```

3. Create a `.env` file in the project root and add your Hugging Face token:

```text
api2=your_huggingface_token_here
```

4. Run the project with a topic:

```powershell
python main.py "space facts"
```

You can also choose a custom output folder:

```powershell
python main.py "space facts" --output-dir space
```

## Output

For each run, the project creates:

- `script.txt` inside the output folder
- `storyboard.json` inside the output folder
- `scene_01.png`, `scene_02.png`, etc. inside the output folder
- `output.mp3` in the project root
- `<topic>.mp4` in the project root

## Notes

- Keep `.env` private and never commit it to Git.
- The final video step requires `ffmpeg`.
- If too many images are generated, check the number of objects inside `storyboard.json` under `scene_map`.
