"""
Audio Handler Module
Handles audio recording and file operations for pronunciation practice
"""

import io
import streamlit as st
import soundfile as sf
from datetime import datetime
from audio_recorder_streamlit import audio_recorder


def save_audio_bytes_to_wav(user, audio_bytes, selection, sample_rate=48000, channels=1):
    """
    Convert audio bytes to WAV file and save it
    
    Args:
        user: User object containing path information
        audio_bytes: Audio data in bytes format
        selection: Name of the selected lesson
        sample_rate: Audio sample rate (default: 48000)
        channels: Number of audio channels (default: 1 for mono)
    
    Returns:
        str: Path to the saved audio file
    """
    audio_data, sr = sf.read(audio_bytes, dtype="int16")
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f"{user.today_path}/{selection}-{current_time}.wav"
    sf.write(output_filename, audio_data, sample_rate, format="WAV", subtype="PCM_16")
    print("Audio saved!")
    return output_filename


def get_audio_from_mic_v2(user, selection):
    """
    Record audio from microphone using st.audio_input
    
    Args:
        user: User object containing path information
        selection: Name of the selected lesson
    
    Returns:
        BytesIO: Audio data if recorded, None otherwise
    """
    # Collect voice bytes data from audio_recorder
    audio_bytes_io = st.audio_input("マイクのアイコンをクリックして、録音しましょう！", key='audio_input')
    if audio_bytes_io:
        return audio_bytes_io
    return None


@DeprecationWarning
def get_audio_from_mic(user, selection) -> str:
    """
    DEPRECATED: This function uses audio_recorder as recorder
    Use get_audio_from_mic_v2 instead
    
    Args:
        user: User object containing path information
        selection: Name of the selected lesson
    
    Returns:
        str: Path to saved audio file
    """
    # record audio from mic and save it to a wav file, and return the name of the file
    sample_rate = 16000

    def save_audio_bytes_to_wav_deprecated(
        audio_bytes, output_filename, sample_rate=sample_rate, channels=1
    ):
        # Convert audio_bytes to a numpy array
        audio_data, sr = sf.read(io.BytesIO(audio_bytes), dtype="int16")
        # Save the numpy array to a .wav file
        sf.write(
            output_filename, audio_data, sample_rate, format="WAV", subtype="PCM_16"
        )
        print("audio has been saved!")

    # collect voice bytes data from audio_recorder
    audio_bytes = audio_recorder(
        text="クリックして録音", neutral_color="#e6ff33", sample_rate=16000
    )
    if audio_bytes:
        # save io.BytesIO obj into a file whose name is date_time.now()
        # save the wav in a mono channel for Azure pronunciation assessment
        file_name = f"{user.today_path}/{selection}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.wav"
        save_audio_bytes_to_wav_deprecated(audio_bytes, file_name, sample_rate, channels=1)
        
        return file_name
