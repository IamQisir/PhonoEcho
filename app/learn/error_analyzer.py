"""
Error Analyzer Module
Handles collection and analysis of pronunciation errors
"""

import pandas as pd
import streamlit as st


def collect_errors(pronunciation_result):
    """
    Collect error statistics and words from pronunciation result
    
    Args:
        pronunciation_result: Dictionary containing pronunciation assessment data
    
    Returns:
        dict: Error data with counts and word lists for each error type
    """
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


def create_error_table():
    """
    Create error table from session state
    
    Returns:
        pd.DataFrame: DataFrame containing error statistics
    """
    if 'current_errors' not in st.session_state:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(st.session_state.current_errors, orient='index')
    return df


def get_error_stats():
    """
    Get error statistics from current session state
    
    Returns:
        dict: Error counts for current practice attempt
    """
    if (
        'learning_state' not in st.session_state or 
        'current_errors' not in st.session_state.learning_state
    ):
        return {}
    return {k: v['count'] for k, v in st.session_state.learning_state['current_errors'].items() if v['count'] > 0}


def get_total_error_stats():
    """
    Get total error statistics from session state
    
    Returns:
        dict: Cumulative error counts for the current lesson
    """
    if (
        'learning_state' not in st.session_state or 
        'total_errors' not in st.session_state.learning_state
    ):
        return {}
    lesson_index = st.session_state.lesson_index
    if lesson_index not in st.session_state.learning_state['total_errors']:
        return {}
    return {k: v['count'] for k, v in st.session_state.learning_state['total_errors'][lesson_index].items() if v['count'] > 0}
