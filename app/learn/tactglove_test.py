import sys
import os
import streamlit as st
import streamlit.components.v1 as components
import threading


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from bhaptics import better_haptic_player as player

if "is_initialized" not in st.session_state:
    st.session_state.is_initialized = False
if "play_count" not in st.session_state:
    st.session_state.play_count = 0
if "just_loaded" not in st.session_state:
    st.session_state.just_loaded = True

# Used to trigger re-render (state variable)
if st.session_state.play_count != 0 and st.session_state.just_loaded:
    st.session_state.play_count = 0

st.session_state.just_loaded = False

def play_tactglove(is_initialized_flag):
    if not is_initialized_flag:
        player.initialize()
        player.register("RightGlove", "RightGlove.tact")
        # 不能在子线程里设置 st.session_state
    player.submit_registered("RightGlove")
    player.play_finished_event.wait()

if st.button("Play Video"):
    st.session_state.play_count += 1
    is_initialized_flag = st.session_state.is_initialized
    threading.Thread(target=play_tactglove, args=(is_initialized_flag,), daemon=True).start()
    if not st.session_state.is_initialized:
        st.session_state.is_initialized = True

# Use play counter in JS to force different code each time → trigger component refresh
play_version = st.session_state.play_count

video_html = f"""
    <video id="myVideo" width="640" height="360" controls>
        <source src="http://localhost:8000/database/learning_database/qi/0.mp4" type="video/mp4">
    </video>
"""

if play_version > 0:
    video_html += f"""
    <script>
        const video = document.getElementById("myVideo");
        video.pause();
        video.currentTime = 0;
        video.load();
        video.play();
        video.onended = function() {{
            console.log("Playback finished! Version: {play_version}");
        }};
    </script>
    """
components.html(video_html, height=400)