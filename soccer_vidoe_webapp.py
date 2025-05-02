# soccer_video_webapp.py

import openai
from gtts import gTTS
from moviepy.editor import *
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
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response['choices'][0]['message']['content']

def generate_audio(script_text, audio_path):
    tts = gTTS(text=script_text, lang='en')
    tts.save(audio_path)

def generate_image(prompt, image_path):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url"
    )
    image_url = response['data'][0]['url']
    img_data = requests.get(image_url).content
    with open(image_path, 'wb') as f:
        f.write(img_data)

def add_background_music(audio_path, music_path, output_path):
    narration = AudioFileClip(audio_path)
    music = AudioFileClip(music_path).volumex(0.2).subclip(0, narration.duration)
    final_audio = CompositeAudioClip([narration, music])
    final_audio.write_audiofile(output_path)

def add_subtitles(image_path, script_text, audio_path, output_path):
    audio = AudioFileClip(audio_path)
    image = ImageClip(image_path).set_duration(audio.duration)
    txt_clip = TextClip(script_text, fontsize=24, color='white', bg_color='black', size=image.size)
    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(audio.duration)
    video = CompositeVideoClip([image, txt_clip]).set_audio(audio).set_fps(24)
    video.write_videofile(output_path, codec='libx264', audio_codec='aac')

def generate_video(position):
    safe_name = position.lower().replace(" ", "_")
    base_path = f"output/{safe_name}"

    script = generate_script(position)
    with open(f"{base_path}_script.txt", "w") as f:
        f.write(script)

    generate_audio(script, f"{base_path}_audio.mp3")
    generate_image(f"Cartoon-style drawing of a {position} in a kids soccer match, fun and colourful", f"{base_path}_image.jpg")

    # Add music
    music_sample = "alone-296348.mp3"  # Place a royalty-free sample music in the same folder
    add_background_music(f"{base_path}_audio.mp3", music_sample, f"{base_path}_mixed_audio.mp3")

    # Create video with subtitles
    add_subtitles(f"{base_path}_image.jpg", script, f"{base_path}_mixed_audio.mp3", f"{base_path}_video.mp4")
    return f"{base_path}_video.mp4"

# ========== STREAMLIT UI ==========
st.title("\ud83c\udfc0 Soccer Explainer Video Generator for Kids")

st.markdown("""
Generate a fun animated video to explain soccer positions to kids under 11! 
Choose a position, and we do the rest: script, voice, animation, music, subtitles, and export.
""")

selected_position = st.selectbox("Choose a position:", POSITIONS)

if st.button("Generate Video"):
    with st.spinner("Creating video... this may take up to 2 minutes"):
        output_path = generate_video(selected_position)
        st.success("Video created successfully!")
        st.video(output_path)
        with open(output_path, "rb") as file:
            st.download_button(label="Download Video", data=file, file_name=os.path.basename(output_path))
