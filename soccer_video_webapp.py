# soccer_video_webapp.py

import openai
from gtts import gTTS
import requests
import os
import streamlit as st

# ========== CONFIGURATION ==========
# Use Streamlit secrets to load the OpenAI API key securely
openai.api_key = st.secrets["openai_api_key"]
os.makedirs("output", exist_ok=True)

POSITIONS = ["Goalkeeper", "Defender", "Midfielder", "Forward", "Captain"]

# ========== FUNCTIONS ==========

def generate_script(position):
    prompt = f"""Write a 1-minute script for an animated video for kids aged 8-10.
    The video explains the role of a {position} in a soccer team using fun, friendly language,
    short sentences, and exciting tone. Include a few silly jokes or playful moments."""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content

def generate_audio(script_text, audio_path):
    tts = gTTS(text=script_text, lang='en')
    tts.save(audio_path)

def generate_image(prompt, image_path):
    response = openai.images.generate(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url"
    )
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    with open(image_path, 'wb') as f:
        f.write(img_data)

def generate_assets(position):
    safe_name = position.lower().replace(" ", "_")
    base_path = f"output/{safe_name}"

    script = generate_script(position)
    with open(f"{base_path}_script.txt", "w") as f:
        f.write(script)

    generate_audio(script, f"{base_path}_audio.mp3")
    generate_image(
        f"Cartoon-style drawing of a {position} in a kids soccer match, fun and colourful",
        f"{base_path}_image.jpg"
    )

    return base_path, script

# ========== STREAMLIT UI ==========
st.title("Soccer Explainer Audio + Visual Generator for Kids")

st.markdown("""
Create a fun mini-lesson to explain soccer positions to kids under 11! 
This app uses AI to generate a script, narration, and image — ready to share.
""")

selected_position = st.selectbox("Choose a position:", POSITIONS)

if st.button("Generate Content"):
    with st.spinner("Generating content... this may take up to 1 minute"):
        base_path, script = generate_assets(selected_position)
        st.success("Content generated successfully!")

        st.image(f"{base_path}_image.jpg", caption=selected_position, use_column_width=True)
        st.audio(f"{base_path}_audio.mp3")

        st.markdown("### Script")
        st.markdown(script)

        with open(f"{base_path}_audio.mp3", "rb") as f:
            st.download_button("Download Narration (MP3)", data=f, file_name=os.path.basename(f.name))

        with open(f"{base_path}_image.jpg", "rb") as f:
            st.download_button("Download Image (JPG)", data=f, file_name=os.path.basename(f.name))

        with open(f"{base_path}_script.txt", "rb") as f:
            st.download_button("Download Script (TXT)", data=f, file_name=os.path.basename(f.name))
