import io
import os
import json
import librosa
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import soundfile as sf
import azure.cognitiveservices.speech as speechsdk
from audio_recorder_streamlit import audio_recorder
from streamlit_extras.grid import grid as extras_grid
import streamlit.components.v1 as components
from dataset import Dataset
from datetime import datetime
import traceback
from streamlit_extras.let_it_rain import rain
import altair as alt
from ai_chat import AIChat
import threading

import sys
import os
# Ensure the tools directory is in the Python path
sys.path.append(os.path.abspath("app/tools"))
# add the PhonoEcho root directory to sys.path to import bhaptics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from bhaptics import better_haptic_player as player	

# Initialize global variables for storing radar chart per attempt and error types
plt.rcParams["font.family"] = "MS Gothic"
with open(f"database/learning_database/{st.session_state.user.name}/tactglove_config.json", "r") as f:
    tact_settings = json.load(f)

# Initialize the haptic player
if "is_initialized" not in st.session_state:
    player.initialize()
    player.register("LeftGlove0", tact_settings["0"])
    player.register("LeftGlove1", tact_settings["1"])
    st.session_state.is_initialized = True
if "play_count" not in st.session_state:
    st.session_state.play_count = 0
if "just_loaded" not in st.session_state:
    st.session_state.just_loaded = True
# Used to trigger re-render (state variable)
if st.session_state.play_count != 0 and st.session_state.just_loaded:
    st.session_state.play_count = 0
st.session_state.just_loaded = False

# Function to play the haptic feedback
def play_tactglove(lesson_index):
    player.submit_registered(f"LeftGlove{lesson_index}")
    player.play_finished_event.wait()

def delay_play_tactglove(delay, lesson_index):
    """
    Delay the play of tactglove to ensure the video is ready.
    This function runs in a separate thread and should not access Streamlit context.
    """
    try:
        time.sleep(delay)
        play_tactglove(lesson_index)
    except Exception as e:
        # Log error but don't use Streamlit functions in thread
        print(f"Error in delay_play_tactglove: {e}")

# Function to get color based on score
def get_color(score):
    if score >= 90:
        # green
        return "#00ff00"
    elif score >= 70:
        # yellow
        return "#ffc000"
    elif score >= 60:
        # orange
        return "#ff4b4b"
    else:
        # red
        return "#ff0000"

def create_radar_chart(pronunciation_result):
    """
    Creates an enhanced radar chart for pronunciation assessment visualization.
    
    Args:
        pronunciation_result (dict): Dictionary containing pronunciation assessment data
        
    Returns:
        matplotlib.figure.Figure: The generated radar chart
    """
    # Extract overall assessment
    overall_assessment = pronunciation_result["NBest"][0]["PronunciationAssessment"]

    # Define categories with Japanese labels
    categories = {
        "総合": "PronScore",
        "正確性": "AccuracyScore",
        "流暢性": "FluencyScore",
        "完全性": "CompletenessScore",
        "韻律": "ProsodyScore"
    }

    # Get scores
    scores = [overall_assessment.get(categories[cat], 0) for cat in categories]

    # Create figure and polar axis
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection="polar"))

    # Calculate angles for each category
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)

    # Close the plot by appending first values
    scores += scores[:1]
    angles = np.concatenate((angles, [angles[0]]))

    # Plot data
    ax.plot(angles, scores, 'o-', linewidth=3, label='Score', color='#2E86C1', markersize=10)
    ax.fill(angles, scores, alpha=0.25, color='#2E86C1')

    # Set chart properties
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories.keys(), size=20)
    
    # Add gridlines and adjust their style
    ax.set_rgrids([20, 40, 60, 80, 100], 
                  labels=['20', '40', '60', '80', '100'],
                  angle=0,
                  fontsize=14)  # Increased from 10 to 14
    
    # Add score labels at each point with larger font
    for angle, score in zip(angles[:-1], scores[:-1]):
        ax.text(angle, score + 5, f'{score:.1f}', 
                ha='center', va='center',
                fontsize=20,  # Increased font size for score labels
                fontweight='bold')

    # Customize grid
    ax.grid(True, linestyle='--', alpha=0.7, linewidth=1.5)  # Increased grid line width
    
    # Set chart limits and direction
    ax.set_ylim(0, 100)
    ax.set_theta_direction(-1)  # Clockwise
    ax.set_theta_offset(np.pi / 2)  # Start from top
    
    # Add title with larger font
    plt.title("発音評価レーダーチャート\nPronunciation Assessment Radar Chart", 
              pad=20, size=20, fontweight='bold')  # Increased from 14 to 18

    # Add subtle background color
    ax.set_facecolor('#F8F9F9')
    fig.patch.set_facecolor('white')

    # Adjust layout
    plt.tight_layout()

    return fig

def create_waveform_plot(audio_file, pronunciation_result):
    y, sr = librosa.load(audio_file)
    duration = len(y) / sr

    fig, ax = plt.subplots(figsize=(12, 6))
    times = np.linspace(0, duration, num=len(y))

    ax.plot(times, y, color="gray", alpha=0.5)

    words = pronunciation_result["NBest"][0]["Words"]
    for word in words:
        if (
            "PronunciationAssessment" not in word
            or "ErrorType" not in word["PronunciationAssessment"]
        ):
            continue
        if word["PronunciationAssessment"]["ErrorType"] == "Omission":
            continue

        start_time = word["Offset"] / 10000000
        word_duration = word["Duration"] / 10000000
        end_time = start_time + word_duration

        start_idx = int(start_time * sr)
        end_idx = int(end_time * sr)
        word_y = y[start_idx:end_idx]
        word_times = times[start_idx:end_idx]

        score = word["PronunciationAssessment"].get("AccuracyScore", 0)
        color = get_color(score)

        ax.plot(word_times, word_y, color=color)
        ax.text(
            (start_time + end_time) / 2,
            ax.get_ylim()[0],
            word["Word"],
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=45,
        )
        ax.axvline(x=start_time, color="gray", linestyle="--", alpha=0.5)

        if "Phonemes" in word:
            for phoneme in word["Phonemes"]:
                phoneme_start = phoneme["Offset"] / 10000000
                phoneme_duration = phoneme["Duration"] / 10000000
                phoneme_end = phoneme_start + phoneme_duration

                phoneme_score = phoneme["PronunciationAssessment"].get(
                    "AccuracyScore", 0
                )
                phoneme_color = get_color(phoneme_score)

                # 绘制音节的垂直线
                # ax.axvline(x=phoneme_start, color='black', linestyle='--', alpha=0.5)
                # ax.axvline(x=phoneme_end, color='black', linestyle='--', alpha=0.5)

                # 添加音节 Phoneme 标签
                ax.text(
                    phoneme_start,
                    ax.get_ylim()[1],
                    phoneme["Phoneme"],
                    ha="left",
                    va="top",
                    fontsize=6,
                    color=phoneme_color,
                )
        ax.axvline(x=end_time, color="gray", linestyle="--", alpha=0.5)

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")
    ax.set_title("音声の波形と発音評価")
    plt.tight_layout()

    return fig

def pronunciation_assessment(audio_file, reference_text):
    print("進入 pronunciation_assessment 関数")

    # Be Aware!!! We are using free keys here but nonfree keys in Avatar
    speech_key, service_region = (
        st.secrets["Azure_Speech"]["SPEECH_KEY"],
        st.secrets["Azure_Speech"]["SPEECH_REGION"],
    )
    print(f"SPEECH_KEY: {speech_key}, SPEECH_REGION: {service_region}")

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region
    )
    print("SpeechConfig 作成成功")

    audio_config = speechsdk.audio.AudioConfig(filename=audio_file)
    print("AudioConfig 作成成功")

    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True,
    )
    pronunciation_config.enable_prosody_assessment()
    pronunciation_config.phoneme_alphabet = "IPA"
    print("PronunciationAssessmentConfig 作成成功")

    try:
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        print("SpeechRecognizer 作成成功")

        pronunciation_config.apply_to(speech_recognizer)
        print("PronunciationConfig 適用成功")

        result = speech_recognizer.recognize_once_async().get()
        print(f"識別結果: {result}")

        pronunciation_result = json.loads(
            result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        )
        print("JSON 結果解析成功")

        return pronunciation_result
    except Exception as e:
        st.error(f"pronunciation_assessment 関数で例外をキャッチしました: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        raise

def collect_errors(pronunciation_result):
    """Base function to collect error statistics and words"""
    error_data = {
        "省略 (Omission)": {'count': 0, 'words': []},
        "挿入 (Insertion)": {'count': 0, 'words': []},
        "発音ミス (Mispronunciation)": {'count': 0, 'words': []},
        "不適切な間 (UnexpectedBreak)": {'count': 0, 'words': []},
        "間の欠如 (MissingBreak)": {'count': 0, 'words': []},
        "単調 (Monotone)": {'count': 0, 'words': []}
    }
    
    error_mapping = {
        "Omission": "省略 (Omission)",
        "Insertion": "挿入 (Insertion)",
        "Mispronunciation": "発音ミス (Mispronunciation)",
        "UnexpectedBreak": "不適切な間 (UnexpectedBreak)",
        "MissingBreak": "間の欠如 (MissingBreak)",
        "Monotone": "単調 (Monotone)"
    }
    
    words = pronunciation_result["NBest"][0]["Words"]
    for word in words:
        if "PronunciationAssessment" in word and "ErrorType" in word["PronunciationAssessment"]:
            error_type = word["PronunciationAssessment"]["ErrorType"]
            if error_type and error_type in error_mapping:
                jp_error = error_mapping[error_type]
                error_data[jp_error]['count'] += 1
                error_data[jp_error]['words'].append(word["Word"])
    
    return error_data

# Function to create error statistics table
def create_error_table():
    """Create error table from session state"""
    if 'current_errors' not in st.session_state:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(st.session_state.current_errors, orient='index')
    return df

def get_error_stats():
    """Get error statistics from current session state"""
    if (
        'learning_state' not in st.session_state or 
        'current_errors' not in st.session_state.learning_state
    ):
        return {}
    return {k: v['count'] for k, v in st.session_state.learning_state['current_errors'].items() if v['count'] > 0}

def get_total_error_stats():
    """Get total error statistics from session state"""
    if (
        'learning_state' not in st.session_state or 
        'total_errors' not in st.session_state.learning_state
    ):
        return {}
    lesson_index = st.session_state.lesson_index
    if lesson_index not in st.session_state.learning_state['total_errors']:
        return {}
    return {k: v['count'] for k, v in st.session_state.learning_state['total_errors'][lesson_index].items() if v['count'] > 0}

def create_doughnut_chart(data, title):
    """Create a doughnut chart using Altair"""
    # Convert data to DataFrame
    df = pd.DataFrame(list(data.items()), columns=['Error', 'Count'])
    
    return alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(
            field="Error",
            type="nominal",
            scale=alt.Scale(range=['#FF4B4B', '#FFC000', '#00B050', '#2F75B5', '#7030A0', '#000000'])
        ),
        tooltip=['Error', 'Count']
    ).properties(
        title=title,
        width=300,
        height=300
    )

def create_syllable_table(pronunciation_result):
    output = """
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #00008B; }
    </style>
    <table>
        <tr><th>Word</th><th>Pronunciation</th><th>Score</th></tr>
    """
    for word in pronunciation_result["NBest"][0]["Words"]:
        word_text = word["Word"]
        accuracy_score = word.get("PronunciationAssessment", {}).get("AccuracyScore", 0)
        color = get_color(accuracy_score)

        output += f"<tr><td>{word_text}</td><td>"

        if "Phonemes" in word:
            for phoneme in word["Phonemes"]:
                phoneme_text = phoneme["Phoneme"]
                phoneme_score = phoneme.get("PronunciationAssessment", {}).get(
                    "AccuracyScore", 0
                )
                phoneme_color = get_color(phoneme_score)
                output += f"<span style='color: {phoneme_color};'>{phoneme_text}</span>"
        else:
            output += word_text

        output += f"</td><td style='background-color: {color};'>{accuracy_score:.2f}</td></tr>"

    output += "</table>"
    return output

@DeprecationWarning
def get_audio_from_mic(user, selection) -> str:
    """
    This function uses audio_recorder as recorder
    """
    # record audio from mic and save it to a wav file, and return the name of the file
    sample_rate = 16000

    # user is an obj of User and selection is the name of selected lession
    def save_audio_bytes_to_wav(
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
        save_audio_bytes_to_wav(audio_bytes, file_name, sample_rate, channels=1)
        
        return file_name

def save_audio_bytes_to_wav(user, audio_bytes, selection, sample_rate=48000, channels=1):
    audio_data, sr = sf.read(audio_bytes, dtype="int16")
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f"{user.today_path}/{selection}-{current_time}.wav"
    sf.write(output_filename, audio_data, sample_rate, format="WAV", subtype="PCM_16")
    print("Audio saved!")
    return output_filename

def get_audio_from_mic_v2(user, selection):
    # Collect voice bytes data from audio_recorder
    audio_bytes_io = st.audio_input("マイクのアイコンをクリックして、録音しましょう！", key='audio_input')
    if audio_bytes_io:
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Generate filename for new recording
        file_name = f"{user.today_path}/{selection}-{current_time}.wav"
        # Save new audio
        return audio_bytes_io
    return None

def course_navigation(my_grid, courses):
    # the first row of my_grid
    # my_grid is the grid element of streamlit_exras
    # Initialize session state for course index
    if 'lesson_index' not in st.session_state:
        st.session_state.lesson_index = 0
    user = st.session_state.user
    # Previous 
    if my_grid.button("◀ 前", disabled=st.session_state.lesson_index == 0, use_container_width=True):
        st.session_state.lesson_index -= 1
        user.load_scores_history(st.session_state.lesson_index)
        st.session_state.play_count = 0  # Reset play count when navigating back
        st.session_state.just_loaded = True  # Trigger re-render
        st.rerun()
            
    # Next button
    if my_grid.button("次 ▶", disabled=st.session_state.lesson_index == len(courses) - 1, use_container_width=True):
        st.session_state.lesson_index += 1
        user.load_scores_history(st.session_state.lesson_index)
        st.session_state.play_count = 0  # Reset play count when navigating back
        st.session_state.just_loaded = True  # Trigger re-render
        st.rerun()
    
    # Show current course name
    current_course = courses[st.session_state.lesson_index]
    # questionnaire_lst = [
    #     "https://docs.google.com/forms/d/e/1FAIpQLSd4pu9pK-tZ6ETRH_dBQTqgE1KOj52I9c7j6AqKFH8IwG8v8w/viewform?usp=dialog",
    #     "https://docs.google.com/forms/d/e/1FAIpQLSchcktzjBXCLhKVWvMScXGUHWCw96iJHnW6N2TC90LVMRNMhg/viewform?usp=dialog"

    # ]
    # if st.session_state.lesson_index == 0:
    #     questionnaire_address = questionnaire_lst[0]
    # elif st.session_state.lesson_index == 1:
    #     questionnaire_address = questionnaire_lst[1]
    # my_grid.info(f"{current_course}を練習しましょう😆👉 10回の練習が終わったら、アンケートを回答してください！[アンケート🫡]({questionnaire_address})")
    my_grid.info("10回の練習は終わりましたら、実験実施者を呼びかけてください！")
    return current_course

def video_and_tactglove(my_grid, text_content, selected_lessons):
    # Video player
    video_html = f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            <video id="myVideo" width="640" height="360" controls>
                <source src="http://localhost:8000/database/learning_database/{st.session_state.user.name}/{selected_lessons["video"]}" type="video/mp4">
            </video>
        </div>
    """
    play_version = st.session_state.play_count

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
    with my_grid.container(border=False):
        components.html(video_html, height=360)
    my_grid.markdown(
        f"""
        <div style="text-align: left; font-size: 24px; font-weight: bold; color: #F0F0F0;">
            {text_content}
        </div>
        """,
        unsafe_allow_html=True
    )

def save_scores_to_json(user, lesson_index, scores_history):
    scores_dir = os.path.join(user.today_path, "scores")
    if not os.path.exists(scores_dir):
        os.makedirs(scores_dir)
    
    json_file = os.path.join(scores_dir, "lesson_scores.json")
    
    # Load existing data
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            all_scores = json.load(f)
    else:
        all_scores = {}
    
    lesson_key = f"lesson_{lesson_index}"
    
    # Create new entry for lesson (overwrite instead of append)
    all_scores[lesson_key] = {
        'AccuracyScore': scores_history['AccuracyScore'],
        'FluencyScore': scores_history['FluencyScore'],
        'CompletenessScore': scores_history['CompletenessScore'],
        'ProsodyScore': scores_history['ProsodyScore'],
        'PronScore': scores_history['PronScore']
    }
    
    # Save updated data
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_scores, f, indent=4)

def save_error_history(user, lesson_index, error_data):
    """Save error history to JSON file"""
    # Create scores directory if not exists
    scores_dir = os.path.join(user.today_path, "scores")
    if not os.path.exists(scores_dir):
        os.makedirs(scores_dir)
    
    error_file = os.path.join(scores_dir, "error_history.json")
    
    try:
        # Load existing data if file exists
        if os.path.exists(error_file):
            with open(error_file, 'r', encoding='utf-8') as f:
                all_errors = json.load(f)
        else:
            all_errors = {}
        
        # Update with new error data
        lesson_key = f"lesson_{lesson_index}"
        all_errors[lesson_key] = {
            'current': error_data['current'],
            'total': error_data['total']
        }
        
        # Save updated data
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(all_errors, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        st.error(f"Error saving error history: {str(e)}")

def store_scores(user, lesson_index, pronunciation_result):
    """Store scores and update session state"""
    # Get scores
    scores = pronunciation_result["NBest"][0]["PronunciationAssessment"]
    error_data = collect_errors(pronunciation_result)
    
    # Initialize session state
    if 'learning_state' not in st.session_state:
        st.session_state.learning_state = {
            'scores_history': {},
            'current_errors': {},
            'total_errors': {}
        }
    
    # Initialize lesson data if needed
    if lesson_index not in st.session_state.learning_state['scores_history']:
        st.session_state.learning_state['scores_history'][lesson_index] = {
            'AccuracyScore': [],
            'FluencyScore': [],
            'CompletenessScore': [],
            'ProsodyScore': [],
            'PronScore': []
        }
        st.session_state.learning_state['total_errors'][lesson_index] = {}
    
    # Update scores
    for score_type in ['AccuracyScore', 'FluencyScore', 'CompletenessScore', 'ProsodyScore', 'PronScore']:
        st.session_state.learning_state['scores_history'][lesson_index][score_type].append(
            scores[score_type]
        )
    
    # Update current errors
    st.session_state.learning_state['current_errors'] = error_data
    
    # Update total errors
    for error_type, data in error_data.items():
        if error_type not in st.session_state.learning_state['total_errors'][lesson_index]:
            st.session_state.learning_state['total_errors'][lesson_index][error_type] = {
                'count': 0, 'words': []
            }
        st.session_state.learning_state['total_errors'][lesson_index][error_type]['count'] += data['count']
        st.session_state.learning_state['total_errors'][lesson_index][error_type]['words'].extend(data['words'])
    
    # Save to files
    save_scores_to_json(user, lesson_index, st.session_state.learning_state['scores_history'][lesson_index])
    save_error_history(user, lesson_index, {
        'current': error_data,
        'total': st.session_state.learning_state['total_errors'][lesson_index]
    })
    
    # Add this line to force reload the scores
    user.load_scores_history(lesson_index)

def plot_error_charts():
    """Plot both current and total error charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        current_errors = get_error_stats()
        if current_errors:
            current_chart = create_doughnut_chart(current_errors, '今回の発音エラー')
            st.altair_chart(current_chart, use_container_width=True)
    
    with col2:
        total_errors = get_total_error_stats()
        if total_errors:
            total_chart = create_doughnut_chart(total_errors, 'レッスン総合エラー')
            st.altair_chart(total_chart, use_container_width=True)

def plot_overall_score(data):
    """Plot overall pronunciation score"""
    # Calculate y-axis range
    y_min_pron = max(0, data['PronScore'].min() - 5)
    y_max_pron = min(100, data['PronScore'].max() + 5)
    
    chart = alt.Chart(data).mark_line(
        color='#FF4B4B',
        point=True
    ).encode(
        x=alt.X('Attempt:Q',
                axis=alt.Axis(
                    tickMinStep=1,
                    title='練習回数',
                    values=list(range(1, 11)),
                    tickCount=10,
                    format='d',
                    grid=True
                ),
                scale=alt.Scale(domain=[1, 10])
        ),
        y=alt.Y('PronScore:Q',
                title='スコア',
                scale=alt.Scale(domain=[y_min_pron, y_max_pron])),
        tooltip=['Attempt', 'PronScore']
    ).properties(
        title='総合点スコア',
        width="container",
        height=300
    ).interactive()
    
    return chart

def plot_detail_scores(data):
    """Plot detailed scores components"""
    # Prepare data
    metrics = ['AccuracyScore', 'FluencyScore', 'CompletenessScore', 'ProsodyScore']
    detail_data = data.melt(
        id_vars=['Attempt'],
        value_vars=metrics,
        var_name='Metric',
        value_name='Score'
    )
    
    # Calculate y-axis range
    y_min_detail = max(0, min(data[metrics].min()) - 5)
    y_max_detail = min(100, max(data[metrics].max()) + 5)
    
    chart = alt.Chart(detail_data).mark_line(
        point=True
    ).encode(
        x=alt.X('Attempt:Q',
                axis=alt.Axis(
                    tickMinStep=1,
                    title='練習回数',
                    values=list(range(1, 11)),
                    tickCount=10,
                    format='d',
                    grid=True
                ),
                scale=alt.Scale(domain=[1, 10])
        ),
        y=alt.Y('Score:Q',
                title='スコア',
                scale=alt.Scale(domain=[y_min_detail, y_max_detail])),
        color=alt.Color('Metric:N',
                       scale=alt.Scale(
                           range=['#00C957', '#4169E1', '#FFD700', '#FF69B4']
                       ),
                       legend=alt.Legend(
                           title='評価指標',
                           orient='right'
                       )),
        tooltip=['Attempt', 'Score', 'Metric']
    ).properties(
        title='詳細スコア',
        width="container",
        height=300
    ).interactive()
    
    return chart

def plot_score_history():
    # Check if learning_state exists and has scores_history
    if ('learning_state' not in st.session_state or 
        'scores_history' not in st.session_state.learning_state):
        st.warning("まだ学習記録がありません")
        return
    
    lesson_index = st.session_state.lesson_index
    
    if lesson_index not in st.session_state.learning_state['scores_history']:
        st.warning(f"レッスン {lesson_index + 1} の記録がありません")
        return
    
    # Check if data exists
    scores = st.session_state.learning_state['scores_history'][lesson_index]
    if not any(scores.values()):  # Check if all score lists are empty
        st.warning("まだ学習記録がありません")
        return
    
    # Ensure all arrays have the same length before creating DataFrame
    max_length = max(len(v) for v in scores.values() if v)
    if max_length == 0:
        st.warning("まだ学習記録がありません")
        return
    
    # Pad shorter arrays with None or use only the minimum length
    min_length = min(len(v) for v in scores.values() if v)
    
    # Create a clean scores dict with consistent lengths
    clean_scores = {}
    for key, value_list in scores.items():
        if value_list:  # Only include non-empty lists
            clean_scores[key] = value_list[:min_length]  # Truncate to minimum length
    
    if not clean_scores or min_length == 0:
        st.warning("まだ学習記録がありません")
        return
        
    # Create DataFrame only if we have data
    data = pd.DataFrame(clean_scores)
    if len(data) == 0:
        st.warning("まだ学習記録がありません")
        return
        
    data['Attempt'] = range(1, len(data) + 1)
    
    # Create two columns for charts
    col1, col2 = st.columns([2, 3])
    
    # Plot charts in columns
    with col1:
        overall_chart = plot_overall_score(data)
        st.altair_chart(overall_chart, use_container_width=True)
        
    with col2:
        detail_chart = plot_detail_scores(data)
        st.altair_chart(detail_chart, use_container_width=True)

def initialize_lesson_state(user, lesson_index):
    """Initialize or load lesson state from saved files"""
    # Check if this is first time initialization
    if 'learning_state' not in st.session_state:
        # First time - load everything from files
        st.session_state.learning_state = {
            'scores_history': {},
            'current_errors': {},
            'total_errors': {}
        }
        
        # Load saved data from files
        scores_dir = os.path.join(user.today_path, "scores")
        if os.path.exists(scores_dir):
            # Load scores
            scores_file = os.path.join(scores_dir, "lesson_scores.json")
            if os.path.exists(scores_file):
                with open(scores_file, 'r', encoding='utf-8') as f:
                    all_scores = json.load(f)
                    for lesson_key, scores in all_scores.items():
                        lesson_idx = int(lesson_key.split('_')[1])
                        st.session_state.learning_state['scores_history'][lesson_idx] = scores
            
            # Load errors
            error_file = os.path.join(scores_dir, "error_history.json")
            if os.path.exists(error_file):
                with open(error_file, 'r', encoding='utf-8') as f:
                    all_errors = json.load(f)
                    for lesson_key, errors in all_errors.items():
                        lesson_idx = int(lesson_key.split('_')[1])
                        st.session_state.learning_state['total_errors'][lesson_idx] = errors['total']
    
    # Initialize current lesson structures if not exist
    if lesson_index not in st.session_state.learning_state['total_errors']:
        st.session_state.learning_state['total_errors'][lesson_index] = {}
        
    if lesson_index not in st.session_state.learning_state['scores_history']:
        st.session_state.learning_state['scores_history'][lesson_index] = {
            'AccuracyScore': [],
            'FluencyScore': [],
            'CompletenessScore': [],
            'ProsodyScore': [],
            'PronScore': []
        }

# layout of learning page
def main():
    if st.session_state.user is None:
        st.warning("No user is logined! Something wrong happened!")
    # reset the ai_intial_input to None for state control    
    st.session_state.ai_initial_input = None 
    if 'lesson_index' not in st.session_state:
        st.session_state.lesson_index = 0   
    user = st.session_state.user
    initialize_lesson_state(user, st.session_state.lesson_index)
    # Initialize state at the beginning
    ai_chat = AIChat()

    if 'dataset' not in st.session_state:
        dataset = Dataset(user.name)
        dataset.load_data()
        st.session_state.dataset = dataset
    dataset = st.session_state.dataset
    lessons = [f'レッスン{i}' for i in range(1, len(dataset.text_data) + 1)]
    
    # preload the scores history
    if 'scores_history' not in st.session_state:
        for i in range(len(lessons)):
            user.load_scores_history(i)

    st.title("フォノエコー英語発音トレーニングシステム😆")
    
    # set the names of tabs
    tab1, tab2 = st.tabs(['ラーニング', 'まとめ'])
    with tab1:
        # the layout of the grid structure
        my_grid = extras_grid([0.1, 0.1, 0.8], [0.3, 0.7], 1, 1, 1, [0.3, 0.7], 1, 1, vertical_align="center")
        # when using my_grid, we need the help of st to avoid wrong layout
        # we could load only some rows of my_grid, which is a useful trick

        # row1: selectbox and blank
        selection = course_navigation(my_grid, lessons)

        lesson_idx = int(selection.replace("レッスン", "")) - 1
        selected_lessons = {
        "text": dataset.text_data[lesson_idx],
        "video": dataset.video_data[lesson_idx]
        }

        # row2: video, tacrglove
        # the text_content will be used in pronunciation assessment
        with open(os.path.join(dataset.path, selected_lessons["text"]), 'r', encoding='utf-8') as f:
            text_content = f.read()
        video_and_tactglove(my_grid, text_content, selected_lessons)
        # my_grid.video(dataset.path + selected_lessons["video"])
        
        # row2.5: play button
        if my_grid.button("多感覚学習しよう!", use_container_width=True):
            # click the button to play the tactglove and the video at the same time
            st.session_state.play_count += 1
            # Get delay_time from session state with default fallback
            delay = getattr(st.session_state, 'delay_time', 0.5)
            threading.Thread(target=delay_play_tactglove, args=(delay, lesson_idx), daemon=True).start()
            # force reload the video
            st.rerun()

        # row3: mic and learning button
        # main work will be done here
        # initialize all the elements with None for convenience
        overall_score = radar_chart = waveform_plot = error_table = syllable_table = None
        
        # using form here!
        with my_grid.form(key='learning_phase'):
            audio_file_io = get_audio_from_mic_v2(user, selection)
            if_started = st.form_submit_button('学習開始！')
        if if_started:
            # if overall_score and all the other are all None, don't run this
            # save the audio when the submit button is clicked
            audio_file_name = save_audio_bytes_to_wav(user, audio_file_io, selection)
            if audio_file_name and not overall_score:
                try:
                    pronunciation_result = pronunciation_assessment(
                        audio_file=audio_file_name, reference_text=text_content
                    )
                    # save the pronunciation_result to disk
                    user.save_pron_history(selection, pronunciation_result)

                    overall_score = pronunciation_result["NBest"][0]["PronunciationAssessment"]

                    # store the pronunciation results into session_state
                    store_scores(user, st.session_state.lesson_index, pronunciation_result)

                    # Create visualizations and analysis
                    radar_chart = create_radar_chart(pronunciation_result)
                    waveform_plot = create_waveform_plot(audio_file_name, pronunciation_result)

                    # Process errors - moved collect_errors before create_error_table
                    error_data = collect_errors(pronunciation_result)
                    st.session_state.current_errors = error_data
                    error_table = create_error_table()

                    syllable_table = create_syllable_table(pronunciation_result)

                    # Store results in session state
                    st.session_state['learning_data']['overall_score'] = overall_score
                    st.session_state['learning_data']['radar_chart'] = radar_chart
                    st.session_state['learning_data']['waveform_plot'] = waveform_plot
                    st.session_state['learning_data']['error_table'] = error_table
                    st.session_state['learning_data']['syllable_table'] = syllable_table
                    st.session_state['learning_data']['practice_text'] = text_content

                    # Data for AI
                    st.session_state['ai_initial_input'] = error_table
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    st.error(
                        "音声ファイルの処理中に問題が発生した可能性があります。もう一度試すか、別の音声ファイルを使用してください。"
                    )
                    print(traceback.format_exc())
        # row4: waveform
        if st.session_state['learning_data']['waveform_plot']:
            my_grid.pyplot(st.session_state['learning_data']['waveform_plot'])
        # row5: radar chart and errors' type
        if st.session_state['learning_data']['radar_chart']:
            my_grid.pyplot(st.session_state['learning_data']['radar_chart'])
        if st.session_state['learning_data']['error_table'] is not None:
            my_grid.dataframe(st.session_state['learning_data']['error_table'], use_container_width=True)
        
        # row6: summarization of syllable mistakes and feedback of AI
        if st.session_state['learning_data']['syllable_table']:
            my_grid.markdown(st.session_state['learning_data']['syllable_table'], unsafe_allow_html=True)
        
        # if overall score is higher than 80, rain the balloons
        if overall_score and overall_score['PronScore'] >= 90:
            rain(
            emoji="🥳🎉",
            font_size=54,
            falling_speed=5,
            animation_length=1
        )

    with tab2:
        progress_plot = plot_score_history()
        if progress_plot:
            st.pyplot(progress_plot)
        error_plot = plot_error_charts()
        if error_plot:
            st.pyplot(error_plot)
        # feedback from AI

        with st.chat_message('AI'):
            if 'learning_state' not in st.session_state:
                st.write("練習を始めましょう！")
            elif if_started:
                st.write("GPTによる発音のアドバイス:")
                # Get practice text and score summary for AI
                practice_text = st.session_state.get('learning_data', {}).get('practice_text', text_content)
                overall_score = st.session_state.get('learning_data', {}).get('overall_score')
                score_summary = ai_chat.format_score_summary(overall_score) if overall_score else None
                
                # Get current errors, or use empty dict if none
                current_errors = st.session_state.learning_state.get('current_errors', {})
                
                feedback = ai_chat.get_chat_response(
                    current_errors,
                    practice_text=practice_text,
                    score_summary=score_summary
                )
                if feedback:
                    st.write(feedback)
            else:
                st.write("まだ頑張りましょう！")
main()