import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()

api2 = os.getenv("api2")

HF_TOKEN = api2

client = InferenceClient(
    provider="nscale",
    api_key=api2,
)

# --------------------------------
# STORYBOARD GENERATOR
# --------------------------------
def generate_storyboard(script, duration):

    scene_count = max(1, int(duration // 2.5))

    prompt = f"""
You are an AI storyboard generator for YouTube Shorts.

SCRIPT:
{script}

AUDIO DURATION:
{duration} seconds

SCENE COUNT:
{scene_count}

TASK:
1. Analyze the script
2. Split narration naturally into EXACTLY {scene_count} scenes
3. Generate ONE consistent cinematic base style
4. Generate scene prompts matching narration

RETURN ONLY VALID JSON.

FORMAT:

{{
  "base_style": "single consistent visual style",

  "scene_map": [
    {{
      "text": "part of narration",
      "scene": "matching cinematic image prompt"
    }}
  ]
}}

STRICT RULES:
- EXACTLY {scene_count} scene objects
- Every scene must visually match narration
- Every scene prompt must look DIFFERENT
- Use cinematic camera variety:
  close-up,
  wide shot,
  aerial shot,
  POV,
  dramatic angle,
  silhouette shot
- Highly visual prompts
- Rich environments
- Emotional storytelling
- Vertical cinematic composition
- NO markdown
- NO explanations
- JSON only

STYLE RULES:

Science:
futuristic scientific realism

Space:
cosmic cinematic realism

Psychology:
cinematic documentary realism

Mythology:
divine spiritual realism,
sacred Hindu aesthetics,
golden temple lighting

History:
epic historical realism

Horror:
dark cinematic realism

Health:
medical documentary realism

IMPORTANT:
The narration chunks should follow story flow naturally.
"""

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.8
    )

    content = response.choices[0].message.content

    return json.loads(content)

