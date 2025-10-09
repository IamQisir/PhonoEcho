"""
Sammy Visual Feedback Module for PhonoEcho
==========================================

This module integrates Sammy IPA animations into PhonoEcho's pronunciation feedback.
It displays visual articulatory guidance when learners make pronunciation errors.

HOW IT WORKS:
1. Azure pronunciation assessment detects errors (already in PhonoEcho)
2. This module extracts phoneme-level errors
3. Sammy animations show correct tongue/lip positions
4. Learners see exactly how to fix their pronunciation
"""

import streamlit as st
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# Paths to Sammy animation directories
CONSONANTS_DIR = Path("app/tools/sammy_consonants_gifs")
VOWELS_DIR = Path("app/tools/sammy_vowels_gifs")


# Mapping Azure phonemes to IPA symbols for Sammy animations
AZURE_TO_IPA = {
    # Consonants
    'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'g',
    'f': 'f', 'v': 'v', 'θ': 'θ', 'ð': 'ð', 's': 's', 'z': 'z',
    'ʃ': 'ʃ', 'ʒ': 'ʒ', 'h': 'h', 'tʃ': 'tʃ', 'dʒ': 'dʒ',
    'm': 'm', 'n': 'n', 'ŋ': 'ŋ', 'l': 'l', 'ɹ': 'ɹ', 'j': 'j', 'w': 'w',
    # Alternative notations
    'th': 'θ', 'dh': 'ð', 'sh': 'ʃ', 'zh': 'ʒ', 'ch': 'tʃ', 'jh': 'dʒ',
    'ng': 'ŋ', 'r': 'ɹ', 'y': 'j',
    # Vowels
    'i': 'i', 'ɪ': 'ɪ', 'e': 'e', 'ɛ': 'ɛ', 'æ': 'æ',
    'ə': 'ə', 'ʌ': 'ʌ', 'ɜ': 'ɜ',
    'u': 'u', 'ʊ': 'ʊ', 'o': 'o', 'ɔ': 'ɔ', 'ɑ': 'ɑ', 'ɒ': 'ɒ',
    'eɪ': 'eɪ', 'aɪ': 'aɪ', 'ɔɪ': 'ɔɪ', 'aʊ': 'aʊ', 'oʊ': 'oʊ',
    'ɝ': 'ɝ', 'ɚ': 'ɚ',
    # Alternative vowel notations
    'iy': 'i', 'ih': 'ɪ', 'eh': 'ɛ', 'ae': 'æ',
    'ah': 'ʌ', 'uh': 'ʊ', 'uw': 'u', 'ow': 'oʊ',
    'ey': 'eɪ', 'ay': 'aɪ', 'oy': 'ɔɪ', 'aw': 'aʊ',
    'er': 'ɝ', 'ax': 'ə',
}


# Articulation descriptions for each phoneme
ARTICULATION_GUIDE = {
    'θ': "Place your tongue tip lightly between your teeth. Push air through gently.",
    'ð': "Same as /θ/ but vibrate your vocal cords (make it 'voiced').",
    's': "Place your tongue near the ridge behind your teeth. Create a narrow air channel.",
    'z': "Same as /s/ but vibrate your vocal cords.",
    'ʃ': "Pull your tongue slightly back from /s/ position. Round lips slightly.",
    'ʒ': "Same as /ʃ/ but vibrate your vocal cords.",
    'l': "Touch tongue tip to the ridge behind teeth. Let air flow around the sides.",
    'ɹ': "Curl your tongue tip slightly back without touching the roof of your mouth.",
    'v': "Touch your upper teeth to your lower lip. Vibrate vocal cords.",
    'f': "Same position as /v/ but without vocal cord vibration.",
}


def get_phoneme_animation(phoneme: str) -> Optional[Path]:
    """
    Get the path to Sammy animation for a given phoneme
    
    Args:
        phoneme: IPA symbol or Azure phoneme notation
    
    Returns:
        Path to GIF file, or None if not found
    """
    # Convert Azure notation to IPA if needed
    ipa_symbol = AZURE_TO_IPA.get(phoneme, phoneme)
    
    # Check consonants
    consonant_path = CONSONANTS_DIR / f"{ipa_symbol}.gif"
    if consonant_path.exists():
        return consonant_path
    
    # Check vowels
    vowel_path = VOWELS_DIR / f"{ipa_symbol}.gif"
    if vowel_path.exists():
        return vowel_path
    
    return None


def extract_phoneme_errors(pronunciation_result: dict) -> List[Dict]:
    """
    Extract phoneme-level errors from Azure pronunciation assessment
    
    Args:
        pronunciation_result: Azure pronunciation assessment result
    
    Returns:
        List of dictionaries containing error details:
        [
            {
                'word': str,           # The word containing the error
                'error_type': str,     # Type of error
                'phonemes': List[Dict] # Phoneme details with scores
            },
            ...
        ]
    """
    phoneme_errors = []
    
    try:
        words = pronunciation_result["NBest"][0]["Words"]
        
        for word_data in words:
            word_text = word_data.get("Word", "")
            word_assessment = word_data.get("PronunciationAssessment", {})
            error_type = word_assessment.get("ErrorType", "None")
            
            # Check if word has pronunciation errors
            if error_type in ["Mispronunciation", "Omission"]:
                phonemes = word_data.get("Phonemes", [])
                
                # Find low-scoring phonemes
                problematic_phonemes = []
                for phoneme in phonemes:
                    phoneme_score = phoneme.get("PronunciationAssessment", {}).get("AccuracyScore", 100)
                    if phoneme_score < 60:  # Threshold for showing feedback
                        problematic_phonemes.append({
                            'phoneme': phoneme.get("Phoneme", ""),
                            'score': phoneme_score
                        })
                
                if problematic_phonemes:
                    phoneme_errors.append({
                        'word': word_text,
                        'error_type': error_type,
                        'phonemes': problematic_phonemes
                    })
    
    except Exception as e:
        st.warning(f"Could not extract phoneme errors: {e}")
    
    return phoneme_errors


def display_sammy_feedback(phoneme: str, title: str = None):
    """
    Display Sammy animation for a single phoneme
    
    Args:
        phoneme: IPA symbol or phoneme notation
        title: Optional title for the display
    """
    animation_path = get_phoneme_animation(phoneme)
    
    if animation_path:
        if title:
            st.markdown(f"**{title}**")
        
        # Display the animation
        st.image(
            str(animation_path),
            caption=f"Correct articulation for /{phoneme}/",
            use_column_width=True
        )
        
        # Add text guidance if available
        ipa_symbol = AZURE_TO_IPA.get(phoneme, phoneme)
        if ipa_symbol in ARTICULATION_GUIDE:
            st.info(f"💡 **How to pronounce /{ipa_symbol}/:**\n\n{ARTICULATION_GUIDE[ipa_symbol]}")
    else:
        st.caption(f"Animation not available for: /{phoneme}/")


def show_phoneme_error_feedback(pronunciation_result: dict):
    """
    Main function to display visual feedback for pronunciation errors
    This should be called after Azure pronunciation assessment
    
    Args:
        pronunciation_result: Azure pronunciation assessment result
    """
    # Extract phoneme errors
    phoneme_errors = extract_phoneme_errors(pronunciation_result)
    
    if not phoneme_errors:
        st.success("✅ Great pronunciation! No major phoneme errors detected.")
        return
    
    # Display feedback header
    st.markdown("---")
    st.subheader("🎯 Visual Pronunciation Guidance")
    st.markdown("Here are the sounds that need improvement:")
    
    # Show each error with Sammy animation
    for idx, error in enumerate(phoneme_errors, 1):
        with st.expander(
            f"📝 Word: **{error['word']}** - {error['error_type']}", 
            expanded=(idx == 1)  # Expand first error by default
        ):
            st.markdown(f"**Error Type:** {error['error_type']}")
            
            # Show each problematic phoneme
            for phoneme_info in error['phonemes']:
                phoneme = phoneme_info['phoneme']
                score = phoneme_info['score']
                
                st.markdown(f"### Sound: /{phoneme}/ (Score: {score:.0f}%)")
                
                # Create columns for better layout
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    # Show Sammy animation
                    display_sammy_feedback(phoneme)
                
                with col2:
                    # Additional tips
                    st.markdown("**Tips for Improvement:**")
                    st.markdown(f"""
                    1. Watch the animation carefully - notice the tongue position
                    2. Try to mimic the shape with your own mouth
                    3. Practice the sound in isolation first
                    4. Then practice it within the word: **{error['word']}**
                    """)
                    
                    # Show score improvement goal
                    target_score = 80
                    improvement_needed = target_score - score
                    if improvement_needed > 0:
                        st.progress(score / 100)
                        st.caption(f"Need {improvement_needed:.0f} more points to reach target score")


def show_quick_phoneme_guide(phonemes: List[str]):
    """
    Show a quick visual guide for specific phonemes
    Useful for pre-lesson introduction
    
    Args:
        phonemes: List of phoneme symbols to display
    """
    st.subheader("📚 Sounds in This Lesson")
    
    cols = st.columns(min(len(phonemes), 4))
    
    for idx, phoneme in enumerate(phonemes):
        with cols[idx % 4]:
            animation_path = get_phoneme_animation(phoneme)
            if animation_path:
                st.image(str(animation_path), use_column_width=True)
                st.caption(f"/{phoneme}/")
            else:
                st.caption(f"/{phoneme}/")


def show_phoneme_comparison(target_phoneme: str, detected_phoneme: str):
    """
    Show side-by-side comparison of target vs detected phoneme
    
    Args:
        target_phoneme: The correct phoneme
        detected_phoneme: The phoneme user produced
    """
    st.markdown("### 🔄 What You Said vs. What to Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Target Sound**")
        display_sammy_feedback(target_phoneme)
    
    with col2:
        st.markdown("**🗣️ Your Sound**")
        display_sammy_feedback(detected_phoneme)
    
    st.warning("⚠️ Notice the difference in tongue and lip positions between these two sounds.")


# ==============================================================================
# INTEGRATION EXAMPLE - Add this to your echo_learning.py
# ==============================================================================

def integration_example():
    """
    Example of how to integrate into echo_learning.py
    
    Add this code after line 208 in echo_learning.py where you have:
        error_data = collect_errors(pronunciation_result)
    """
    
    st.code('''
# In echo_learning.py, after collecting errors (around line 208):

from app.learn.sammy_feedback import show_phoneme_error_feedback

# ... your existing code ...
error_data = collect_errors(pronunciation_result)
error_table = create_error_table(error_data)

# NEW: Add visual phoneme feedback with Sammy animations
show_phoneme_error_feedback(pronunciation_result)

# ... rest of your code ...
    ''', language='python')


if __name__ == "__main__":
    st.title("🎙️ Sammy Visual Feedback Demo")
    
    st.markdown("""
    This module provides visual articulatory feedback using Sammy animations.
    
    **How it works in PhonoEcho:**
    1. Student speaks and records audio
    2. Azure analyzes pronunciation and detects errors
    3. System identifies which phonemes were mispronounced
    4. Sammy animations show correct tongue/lip positions
    5. Student sees exactly how to improve
    """)
    
    # Demo with sample phoneme
    st.markdown("---")
    st.subheader("Demo: Try Different Sounds")
    
    phoneme = st.selectbox(
        "Select a phoneme to see its animation:",
        ['θ', 'ð', 's', 'z', 'ʃ', 'ʒ', 'l', 'ɹ', 'v', 'f']
    )
    
    display_sammy_feedback(phoneme, f"How to pronounce /{phoneme}/")
    
    st.markdown("---")
    st.info("💡 See the integration example below to add this to PhonoEcho!")
    integration_example()
