"""
Score Manager Module
Handles score tracking, persistence, and session state management
"""

import os
import json
import streamlit as st


def save_scores_to_json(user, lesson_index, scores_history):
    """
    Save score history to JSON file
    
    Args:
        user: User object containing path information
        lesson_index: Index of the current lesson
        scores_history: Dictionary containing score history
    """
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
    """
    Save error history to JSON file
    
    Args:
        user: User object containing path information
        lesson_index: Index of the current lesson
        error_data: Dictionary containing current and total error data
    """
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
    """
    Store scores and update session state
    
    Args:
        user: User object containing path information
        lesson_index: Index of the current lesson
        pronunciation_result: Dictionary containing pronunciation assessment data
    """
    from error_analyzer import collect_errors
    
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
    
    # Update scores - handle missing ProsodyScore gracefully
    score_types = ['AccuracyScore', 'FluencyScore', 'CompletenessScore', 'ProsodyScore', 'PronScore']
    for score_type in score_types:
        score_value = scores.get(score_type, 0)  # Default to 0 if not present
        st.session_state.learning_state['scores_history'][lesson_index][score_type].append(score_value)
    
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


def initialize_lesson_state(user, lesson_index):
    """
    Initialize or load lesson state from saved files
    
    Args:
        user: User object containing path information
        lesson_index: Index of the current lesson
    """
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
