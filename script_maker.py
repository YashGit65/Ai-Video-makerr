from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()

api2 = os.getenv("api2")

client = InferenceClient(
    provider="nscale",
    api_key=api2
)

# ==========================================
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

# ==========================================
# SCRIPT GENERATOR
# ==========================================

def generate_hindi_short_script(topic):

    hindi_topic = convert_topic_to_hindi(topic)

    print("Hindi Topic:", hindi_topic)

    prompt = f"""
तुम YouTube Shorts के लिए एक expert वायरल script writer हो।

Topic: {hindi_topic}

तुम्हारा काम ऐसा narration लिखना है जिसे सुनकर viewer वीडियो skip ना करे।

STRICT RULES:
- सिर्फ voiceover narration लिखो
- कोई timestamps नहीं
- कोई scene description नहीं
- कोई camera instructions नहीं
- कोई headings नहीं
- कोई bullet points नहीं
- सिर्फ बोलने वाला टेक्स्ट
- conversational Hindi
- 30 से 40 सेकंड
- शुरुआत में strong hook
- suspense + curiosity बनाए रखो
- short spoken sentences
- emotional storytelling
- बीच में viewer retention strong रहे
- ending impactful हो
- natural pauses use करो
- script human जैसी लगे
- AI जैसी नहीं लगनी चाहिए

गलत उदाहरण:
(0-5 सेकंड)
एक आदमी दिखाई देता है...

गलत उदाहरण:
[Scene opens with a black hole]

गलत उदाहरण:
कैमरा धीरे-धीरे मंदिर की ओर जाता है।

गलत उदाहरण:
Narrator:
क्या आपको पता है...

गलत उदाहरण:
Title: ब्लैक होल का सच

सही उदाहरण:
"क्या आपको पता है कि ब्लैक होल इतने ताकतवर होते हैं कि रोशनी भी उनसे बच नहीं सकती?"

सही उदाहरण:
"लोग सोचते हैं कि नींद सिर्फ आराम के लिए होती है। लेकिन सच ये है कि अगर आप लगातार जागते रहें… तो आपका दिमाग नशे में इंसान जैसा behave करने लगता है।"

सही उदाहरण:
"कल्पना करो… अगर अचानक पृथ्वी से गुरुत्वाकर्षण गायब हो जाए तो क्या होगा?"

सही उदाहरण:
"भारत में एक ऐसा मंदिर है जहाँ आज भी लोग मानते हैं कि भगवान खुद प्रकट हुए थे।"

सही उदाहरण:
"जब Titanic डूबा था… तब सिर्फ जहाज़ ही नहीं डूबा था। उसके साथ डूब गई थीं हजारों उम्मीदें।"

अब सिर्फ narration script लिखो:
"""

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.1-8B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.9
    )

    return response.choices[0].message.content


# ==========================================
#