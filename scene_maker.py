import json
import re
from llm import client


def parse_storyboard_response(content):
    cleaned = content.strip()
    fenced_json = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced_json:
        cleaned = fenced_json.group(1).strip()

    try:
        storyboard = json.loads(cleaned)
    except json.JSONDecodeError:
        storyboard = None
        decoder = json.JSONDecoder()
        for match in re.finditer(r"{", cleaned):
            try:
                storyboard, _ = decoder.raw_decode(cleaned[match.start():])
                break
            except json.JSONDecodeError:
                continue
        if storyboard is None:
            raise

    if not isinstance(storyboard, dict):
        raise ValueError("Storyboard response must be a JSON object.")

    base_style = str(storyboard.get("base_style", "")).strip()
    scene_map = storyboard.get("scene_map")

    if not base_style:
        base_style = "cinematic vertical realism"

    if not isinstance(scene_map, list):
        raise ValueError("Storyboard response must include a scene_map list.")

    normalized_scenes = []
    for item in scene_map:
        if not isinstance(item, dict):
            continue

        scene = (
            item.get("scene")
            or item.get("prompt")
            or item.get("image_prompt")
            or item.get("visual")
        )

        if not scene:
            continue

        normalized_scenes.append(
            {
                "text": str(item.get("text", "")).strip(),
                "scene": str(scene).strip(),
            }
        )

    if not normalized_scenes:
        raise ValueError("Storyboard response did not include any usable scene prompts.")

    return {
        "base_style": base_style,
        "scene_map": normalized_scenes,
    }


def request_storyboard(prompt, temperature):
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=temperature
    )

    return response.choices[0].message.content or ""


def build_repair_prompt(content, error):
    return f"""
Repair this invalid storyboard JSON.

Rules:
- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Keep the same meaning.
- Use this exact structure:
{{
  "base_style": "single consistent visual style",
  "scene_map": [
    {{
      "text": "part of narration",
      "scene": "matching cinematic image prompt"
    }}
  ]
}}

JSON error:
{error}

Invalid response:
{content}
"""


# --------------------------------
# STORYBOARD GENERATOR
# --------------------------------
def generate_storyboard(script, duration):

    scene_count = max(1, int(duration // 3))

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

    last_error = None
    last_content = ""

    for attempt in range(2):
        try:
            if attempt == 0:
                content = request_storyboard(prompt, temperature=0.8)
            else:
                content = request_storyboard(
                    build_repair_prompt(last_content, last_error),
                    temperature=0,
                )

            return parse_storyboard_response(content)
        except (json.JSONDecodeError, ValueError) as error:
            last_error = error
            last_content = content

    raise RuntimeError(
        "The AI returned invalid storyboard JSON twice. Please try generating again."
    ) from last_error

