"""
Echo Learning Module - Main UI Orchestration
Handles the main learning interface and coordinates between different modules
"""

import streamlit as st
from streamlit_extras.grid import grid as extras_grid
from streamlit_extras.let_it_rain import rain
from dataset import Dataset
from ai_chat import AIChat
import traceback
import sys
import os
from datetime import datetime

# Add the current directory to path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import from new modular files
from audio_handler import get_audio_from_mic_v2, save_audio_bytes_to_wav
from pronunciation_service import pronunciation_assessment
from error_analyzer import collect_errors, create_error_table
from visualization import (
    create_radar_chart, 
    create_waveform_plot, 
    create_syllable_table,
    plot_score_history,
    plot_error_charts
)
from score_manager import store_scores, initialize_lesson_state


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_lesson_text(file_path: str) -> str:
    """
    Cache lesson text content to avoid reading file on every rerun
    
    Args:
        file_path: Path to the text file
    
    Returns:
        str: Content of the text file
    """
    with open(file_path, "r", encoding='utf-8') as f:
        return f.read()


def initialize_session_state():
    """
    Initialize all session state variables at once
    Centralizes initialization logic and improves maintainability
    """
    defaults = {
        'lesson_index': 0,
        'dataset': None,
        'scores_history': {},  # Will be lazily populated per lesson
        'learning_data': {
            'overall_score': None,
            'radar_chart': None,
            'waveform_plot': None,
            'error_table': None,
            'syllable_table': None
        },
        'ai_initial_input': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def course_navigation(my_grid, courses):
    """
    Handle course navigation with previous/next buttons
    
    Args:
        my_grid: Grid element from streamlit_extras
        courses: List of available courses
    
    Returns:
        str: Currently selected course name
    """
    # Initialize session state for course index
    if 'lesson_index' not in st.session_state:
        st.session_state.lesson_index = 0
    user = st.session_state.user
    
    # Previous button
    if my_grid.button("◀ 前", key="prev_lesson_btn", disabled=st.session_state.lesson_index == 0, use_container_width=True):
        st.session_state.lesson_index -= 1
        user.load_scores_history(st.session_state.lesson_index)
        # Removed explicit st.rerun() - let Streamlit handle it naturally
            
    # Next button
    if my_grid.button("次 ▶", key="next_lesson_btn", disabled=st.session_state.lesson_index == len(courses) - 1, use_container_width=True):
        st.session_state.lesson_index += 1
        user.load_scores_history(st.session_state.lesson_index)
        # Removed explicit st.rerun() - let Streamlit handle it naturally
            
    # Show current course name
    current_course = courses[st.session_state.lesson_index]
    questionnaire_lst = [
        "https://docs.google.com/forms/d/e/1FAIpQLSd4pu9pK-tZ6ETRH_dBQTqgE1KOj52I9c7j6AqKFH8IwG8v8w/viewform?usp=dialog",
        "https://docs.google.com/forms/d/e/1FAIpQLSchcktzjBXCLhKVWvMScXGUHWCw96iJHnW6N2TC90LVMRNMhg/viewform?usp=dialog"
    ]
    if st.session_state.lesson_index == 0:
        questionnaire_address = questionnaire_lst[0]
    elif st.session_state.lesson_index == 1:
        questionnaire_address = questionnaire_lst[1]
    my_grid.info(f"{current_course}を練習しましょう😆👉 10回の練習が終わったら、アンケートを回答してください！[アンケート🫡]({questionnaire_address})")

    return current_course


def main():
    """
    Main function for the learning page layout and functionality
    """
    if st.session_state.user is None:
        st.warning("No user is logined! Something wrong happened!")
        return
    
    # Initialize all session state variables
    initialize_session_state()
    
    # Reset the ai_initial_input to None for state control    
    st.session_state.ai_initial_input = None 
    
    user = st.session_state.user
    initialize_lesson_state(user, st.session_state.lesson_index)

    # Initialize dataset (cached) with loading spinner
    if st.session_state.dataset is None:
        with st.spinner('データを読み込み中...'):
            dataset = Dataset(user.name)
            dataset.load_data()
            st.session_state.dataset = dataset
    dataset = st.session_state.dataset
    lessons = [f'レッスン{i}' for i in range(1, len(dataset.text_data) + 1)]
    
    # Lazy load score history - only load current lesson instead of all lessons
    current_lesson_idx = st.session_state.lesson_index
    if current_lesson_idx not in st.session_state.scores_history:
        with st.spinner('学習履歴を読み込み中...'):
            user.load_scores_history(current_lesson_idx)

    st.title("フォノエコー英語発音トレーニングシステム😆")
    
    # Set the names of tabs - Added フィードバック tab
    tab1, tab2, tab3 = st.tabs(['ラーニング', 'フィードバック', 'まとめ'])
    
    with tab1:
        # The layout of the grid structure
        my_grid = extras_grid([0.1, 0.1, 0.8], [0.2, 0.8], 1, 1, vertical_align="center")

        # Row1: selectbox and navigation
        selection = course_navigation(my_grid, lessons)

        lesson_idx = int(selection.replace("レッスン", "")) - 1
        selected_lessons = {
            "text": dataset.text_data[lesson_idx],
            "video": dataset.video_data[lesson_idx]
        }

        # Row2: video, text
        my_grid.video(dataset.path + selected_lessons["video"])
        
        # Use cached text loading
        text_content = load_lesson_text(dataset.path + selected_lessons["text"])
        
        my_grid.markdown(
            f"""
            <div style="text-align: left; font-size: 24px; font-weight: bold; color: #F0F0F0;">
                {text_content}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Row3: mic and learning button - KEEP IN SAME tab1 context
        overall_score = st.session_state['learning_data']['overall_score']
        
        # Add spacing to separate from grid
        st.markdown("---")
        
        # Wrap audio input and button in a form to prevent auto-submission
        with st.form(key='learning_form', clear_on_submit=False):
            st.markdown("### 🎤 音声録音")
            audio_file_io = get_audio_from_mic_v2(user, selection)
            
            if_started = st.form_submit_button('学習開始！', use_container_width=True, type='primary')
        
        if if_started:
            if audio_file_io is None:
                st.warning("⚠️ 音声が録音されていません。マイクアイコンをクリックして録音してください。")
            else:
                # Show processing indicator
                with st.spinner('🔄 音声を分析中... しばらくお待ちください'):
                    # Save the audio when the submit button is clicked
                    audio_file_name = save_audio_bytes_to_wav(user, audio_file_io, selection)
                    
                    if audio_file_name:
                        try:
                            pronunciation_result = pronunciation_assessment(
                                audio_file=audio_file_name, reference_text=text_content
                            )
                            
                            # Save the pronunciation_result to disk
                            user.save_pron_history(selection, pronunciation_result)

                            overall_score = pronunciation_result["NBest"][0]["PronunciationAssessment"]

                            # Store the pronunciation results into session_state
                            store_scores(user, st.session_state.lesson_index, pronunciation_result)

                            # Add timestamp as cache_key to force cache invalidation for each new recording
                            cache_key = datetime.now().isoformat()

                            # Create visualizations and analysis with unique cache key
                            radar_chart = create_radar_chart(pronunciation_result, cache_key)
                            waveform_plot = create_waveform_plot(audio_file_name, pronunciation_result, cache_key)

                            # Process errors
                            error_data = collect_errors(pronunciation_result)
                            st.session_state.current_errors = error_data
                            error_table = create_error_table()

                            syllable_table = create_syllable_table(pronunciation_result, cache_key)

                            # Store results in session state
                            st.session_state['learning_data']['overall_score'] = overall_score
                            st.session_state['learning_data']['radar_chart'] = radar_chart
                            st.session_state['learning_data']['waveform_plot'] = waveform_plot
                            st.session_state['learning_data']['error_table'] = error_table
                            st.session_state['learning_data']['syllable_table'] = syllable_table

                            # Data for AI
                            st.session_state['ai_initial_input'] = error_table
                            
                            # Show success message AFTER processing completes
                            st.success("✅ 処理完了！フィードバックタブで結果を確認してください。")
                            
                        except Exception as e:
                            st.error(f"❌ エラーが発生しました: {str(e)}")
                            st.error(
                                "音声ファイルの処理中に問題が発生した可能性があります。もう一度試すか、別の音声ファイルを使用してください。"
                            )
                            print(traceback.format_exc())
        
        # Celebration for excellent score (moved here, stays in learning tab)
        if overall_score and overall_score['PronScore'] >= 90:
            rain(
                emoji="🥳🎉",
                font_size=54,
                falling_speed=5,
                animation_length=1
            )

    with tab2:
        # フィードバック Tab - Pronunciation Feedback
        st.header("📊 発音フィードバック")
        
        # Check if there's any data to display
        if not st.session_state['learning_data']['waveform_plot']:
            st.info("👈 まず「ラーニング」タブで練習を始めてください！")
        else:
            # Row1: Waveform (full width)
            st.subheader("🌊 音声波形と発音スコア")
            st.pyplot(st.session_state['learning_data']['waveform_plot'])
            
            # Row2: Radar chart and Error table (side by side)
            col1, col2 = st.columns([0.5, 0.5])
            
            with col1:
                st.subheader("🎯 総合評価レーダーチャート")
                if st.session_state['learning_data']['radar_chart']:
                    st.pyplot(st.session_state['learning_data']['radar_chart'])
            
            with col2:
                st.subheader("⚠️ エラータイプ統計")
                if st.session_state['learning_data']['error_table'] is not None:
                    st.dataframe(st.session_state['learning_data']['error_table'], use_container_width=True)
            
            # Row3: Syllable/Phoneme table (full width)
            st.subheader("🔤 単語・音素別スコア")
            if st.session_state['learning_data']['syllable_table']:
                st.markdown(st.session_state['learning_data']['syllable_table'], unsafe_allow_html=True)

    with tab3:
        # まとめ Tab - Overall Progress & Summary
        st.header("📈 学習進捗まとめ")
        
        # Display score history
        plot_score_history()
        
        # Display error charts
        plot_error_charts()
        
        # Lazy initialize AI Chat only when Tab 3 is active
        if 'ai_chat' not in st.session_state:
            st.session_state.ai_chat = AIChat()
        ai_chat = st.session_state.ai_chat
        
        # Feedback from AI
        st.subheader("🤖 AIコーチからのアドバイス")
        with st.chat_message('AI'):
            if 'learning_state' not in st.session_state or not st.session_state.learning_state['current_errors']:
                st.write("練習を始めましょう！")
            elif if_started:
                st.write("GPTによる発音のアドバイス:")
                feedback = ai_chat.get_chat_response(st.session_state.learning_state['current_errors'])
                if feedback:
                    st.write(feedback)
            else:
                st.write("まだ頑張りましょう！")


# Entry point
main()
