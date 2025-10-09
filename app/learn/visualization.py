"""
Visualization Module
Handles all visualization components including charts, plots, and tables
"""

import streamlit as st

# Lazy imports - only import heavy libraries when functions are called
# This speeds up initial page load significantly


def get_color(score):
    """
    Get color based on pronunciation score
    
    Args:
        score: Pronunciation score (0-100)
    
    Returns:
        str: Hex color code
    """
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


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def create_radar_chart(pronunciation_result, cache_key=None):
    """
    Creates an enhanced radar chart for pronunciation assessment visualization.
    Cached to avoid recreating the same chart multiple times.
    
    Args:
        pronunciation_result (dict): Dictionary containing pronunciation assessment data
        cache_key: Unique identifier for cache invalidation (e.g., timestamp or attempt number)
        
    Returns:
        matplotlib.figure.Figure: The generated radar chart
    """
    # Lazy imports
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Initialize matplotlib font settings
    plt.rcParams["font.family"] = "MS Gothic"
    
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


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def create_waveform_plot(audio_file, pronunciation_result, cache_key=None):
    """
    Create waveform visualization with pronunciation scores.
    Cached to avoid recreating the same waveform multiple times.
    
    Args:
        audio_file: Path to audio file
        pronunciation_result: Dictionary containing pronunciation assessment data
        cache_key: Unique identifier for cache invalidation (e.g., timestamp or attempt number)
    
    Returns:
        matplotlib.figure.Figure: The generated waveform plot
    """
    # Lazy imports
    import numpy as np
    import matplotlib.pyplot as plt
    import librosa
    
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

                # Add phoneme labels
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


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def create_syllable_table(pronunciation_result, cache_key=None):
    """
    Create HTML table showing word-level and phoneme-level pronunciation scores.
    Cached to avoid recreating the same table multiple times.
    
    Args:
        pronunciation_result: Dictionary containing pronunciation assessment data
        cache_key: Unique identifier for cache invalidation (e.g., timestamp or attempt number)
    
    Returns:
        str: HTML string for the syllable table
    """
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


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes (shorter since data changes more)
def create_doughnut_chart(data, title):
    """
    Create a doughnut chart using Altair.
    Cached with shorter TTL since error data changes frequently.
    
    Args:
        data: Dictionary of error types and counts
        title: Chart title
    
    Returns:
        altair.Chart: The generated doughnut chart
    """
    # Lazy imports
    import pandas as pd
    import altair as alt
    
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


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def plot_overall_score(data):
    """
    Plot overall pronunciation score over attempts.
    Cached with shorter TTL since score data changes frequently.
    
    Args:
        data: DataFrame containing score history
    
    Returns:
        altair.Chart: The generated line chart
    """
    # Lazy imports
    import altair as alt
    
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


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def plot_detail_scores(data):
    """
    Plot detailed score components over attempts.
    Cached with shorter TTL since score data changes frequently.
    
    Args:
        data: DataFrame containing score history
    
    Returns:
        altair.Chart: The generated line chart
    """
    # Lazy imports
    import altair as alt
    
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
    """
    Plot complete score history for current lesson
    Displays both overall and detailed score charts
    """
    # Lazy imports
    import pandas as pd
    
    if 'scores_history' not in st.session_state:
        st.warning("まだ学習記録がありません")
        return
    
    lesson_index = st.session_state.lesson_index
    
    if lesson_index not in st.session_state.scores_history:
        st.warning(f"レッスン {lesson_index + 1} の記録がありません")
        return
    
    # Check if data exists
    scores = st.session_state.scores_history[lesson_index]
    if not any(scores.values()):  # Check if all score lists are empty
        st.warning("まだ学習記録がありません")
        return
        
    # Create DataFrame only if we have data
    data = pd.DataFrame(scores)
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


def plot_error_charts():
    """
    Plot both current and total error charts using doughnut charts
    """
    from error_analyzer import get_error_stats, get_total_error_stats
    
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
