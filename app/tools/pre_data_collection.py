import streamlit as st
from PIL import Image
import os
from datetime import datetime

def save_audio_file(base_dir, audio_data, sentence_num):
    """Save the audio file."""
    try:
        if not audio_data:
            st.warning("録音がありません。録音してください。", icon="⚠️")
            return None
            
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentence{sentence_num}_{timestamp}.wav"
        file_path = os.path.join(base_dir, filename)
        
        # Save audio data - use getvalue() to get the bytes
        with open(file_path, "wb") as f:
            f.write(audio_data.getvalue())
            
        return file_path
    except Exception as e:
        st.error(f"音声ファイルの保存エラー：{str(e)}")
        return None

def create_user_directory(romaji):
    """Create the user directory."""
    try:
        # Create base directory if it doesn't exist
        base_dir = os.path.join("database", "pre_experiment", romaji)
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    except Exception as e:
        st.error(f"ディレクトリ作成エラー：{str(e)}")
        return None

# Page title
st.title("実験前のデータ収集😎")

# Initialize session state
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "name": None,
        "romaji": None,
        "base_dir": None,
        "photo_saved": False,
        "sentence_counts": [5],
        "audio_paths": [None]
    }

user_data = st.session_state.user_data

# User info section
st.subheader("1. あなたの個人情報を入れてください")
user_data["name"] = st.text_input("あなたの名前", value=user_data["name"] if user_data["name"] else "")
user_data["romaji"] = st.text_input("あなたの名前のローマ字", value=user_data["romaji"] if user_data["romaji"] else "")

# Create user directory when both name and romaji are provided
if user_data["name"] and user_data["romaji"]:
    if not user_data["base_dir"]:
        user_data["base_dir"] = create_user_directory(user_data["romaji"])

# Photo upload section
st.subheader("2. あなたの写真をアップロードしてください")
photo = st.file_uploader("無地背景のほうが良いです。", type=['png', 'jpg', 'jpeg'])

if photo:
    image = Image.open(photo)
    st.image(image, width=300)

    if not user_data["photo_saved"] and user_data["base_dir"]:
        photo_path = os.path.join(user_data["base_dir"], f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{photo.name.split('.')[-1]}")
        image.save(photo_path)
        user_data["photo_saved"] = True
        st.success("写真が保存されました！")
    elif user_data["photo_saved"]:
        st.info("写真は既に保存されています。", icon="ℹ️")

# Record audio
st.subheader("3. 下記のセンテンスを聞いて、リピートしてください")

sentences = [
    {"text": "Through a powerful telescope, Sara saw a galaxy spinning slowly. Its spiral arms looked like a giant whirlpool.", 
     "audio": r"database/learning_database/backup/9_stranger.wav"}
]

for i, sentence in enumerate(sentences):
    with st.form(f"sentence{i+1}"):
        st.write(sentence["text"])
        st.audio(sentence["audio"])
        audio_recording = st.audio_input("録音しましょう")
        submitted = st.form_submit_button("アップロードしましょう")

        if submitted and user_data["base_dir"]:
            if audio_recording:
                filepath = save_audio_file(user_data["base_dir"], audio_recording, i)
                if filepath:
                    user_data["sentence_counts"][i] -= 1
                    user_data["audio_paths"][i] = filepath
                    st.info(f'センテンス{i+1}は、また{user_data["sentence_counts"][i]}回を練習しましょう', icon="ℹ️")
            else:
                st.warning("録音データがありません。録音してください。", icon="⚠️")

# Check if all recordings are complete
if all(count <= 0 for count in user_data["sentence_counts"]):
    st.success("データの収集は、終了でございます。どうぞよろしくお願いいたします🫡")
    # st.markdown("[Questionnaire 🫡](https://docs.google.com/forms/d/e/1FAIpQLSczmtjqEsaVT6BizQI8N8xzHsicAikQHRaknm3qL2fGo7Vq1Q/viewform?usp=dialog)")
