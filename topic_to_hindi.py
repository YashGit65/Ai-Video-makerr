# ENGLISH → HINDI TOPIC
# ==========================================

def convert_topic_to_hindi(topic):

    prompt = f"""
Convert this topic into natural Hindi.

Rules:
- ONLY return Hindi topic
- No explanation
- No quotes

Topic:
{topic}
"""

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0
    )

    return response.choices[0].message.content.strip()
