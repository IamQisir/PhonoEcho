"""
Quick Start Guide: Using Sammy IPA Animations in PhonoEcho
===========================================================

This is a minimal example to get you started with the IPA animations.
"""

import streamlit as st
from pathlib import Path

# Paths to animation directories (relative to your app root)
CONSONANTS_DIR = Path("app/tools/sammy_consonants_gifs")
VOWELS_DIR = Path("app/tools/sammy_vowels_gifs")


def show_phoneme_animation(phoneme: str):
    """
    Display an IPA animation for a given phoneme.
    
    Args:
        phoneme: IPA symbol (e.g., 'θ', 'i', 's', etc.)
    
    Returns:
        True if animation found and displayed, False otherwise
    """
    # Try consonants first
    consonant_path = CONSONANTS_DIR / f"{phoneme}.gif"
    if consonant_path.exists():
        st.image(str(consonant_path), caption=f"IPA: /{phoneme}/", width=300)
        return True
    
    # Try vowels
    vowel_path = VOWELS_DIR / f"{phoneme}.gif"
    if vowel_path.exists():
        st.image(str(vowel_path), caption=f"IPA: /{phoneme}/", width=300)
        return True
    
    st.warning(f"Animation not found for: /{phoneme}/")
    return False


# ============================================================================
# EXAMPLE 1: Simple Display
# ============================================================================

def example_1_simple_display():
    """Show a single phoneme animation"""
    st.header("Example 1: Display a Phoneme")
    
    # Show the /θ/ sound (as in "think")
    st.write("The /θ/ sound in 'think':")
    show_phoneme_animation('θ')


# ============================================================================
# EXAMPLE 2: Interactive Selector
# ============================================================================

def example_2_interactive():
    """Let users select and view different phonemes"""
    st.header("Example 2: Interactive Phoneme Explorer")
    
    # Common phonemes
    phonemes = {
        'Consonants': ['p', 'b', 't', 'd', 'k', 'g', 'f', 'v', 'θ', 'ð', 
                      's', 'z', 'ʃ', 'ʒ', 'h', 'm', 'n', 'ŋ', 'l', 'ɹ', 'w', 'j'],
        'Vowels': ['i', 'ɪ', 'e', 'ɛ', 'æ', 'ə', 'ʌ', 'ɜ', 'u', 'ʊ', 
                   'o', 'ɔ', 'ɑ', 'eɪ', 'aɪ', 'ɔɪ', 'aʊ', 'oʊ']
    }
    
    category = st.radio("Select category:", list(phonemes.keys()))
    phoneme = st.selectbox("Select phoneme:", phonemes[category])
    
    show_phoneme_animation(phoneme)


# ============================================================================
# EXAMPLE 3: Pronunciation Feedback
# ============================================================================

def example_3_feedback():
    """Show target vs. detected pronunciation"""
    st.header("Example 3: Pronunciation Feedback")
    
    # Simulate pronunciation detection
    target = st.selectbox("Target phoneme:", ['θ', 's', 'ʃ', 'f', 'v'])
    detected = st.selectbox("Detected phoneme:", ['θ', 's', 'ʃ', 'f', 'v'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Target")
        show_phoneme_animation(target)
    
    with col2:
        st.subheader("🗣️ Your Pronunciation")
        show_phoneme_animation(detected)
    
    if target == detected:
        st.success("✅ Perfect match!")
    else:
        st.error(f"❌ You said /{detected}/ instead of /{target}/")


# ============================================================================
# EXAMPLE 4: Word-Level Feedback
# ============================================================================

def example_4_word_feedback():
    """Show phoneme-by-phoneme feedback for a word"""
    st.header("Example 4: Word-Level Feedback")
    
    # Example: the word "think"
    word = "think"
    target_phonemes = ['θ', 'ɪ', 'ŋ', 'k']
    detected_phonemes = ['s', 'ɪ', 'ŋ', 'k']  # User said 's' instead of 'θ'
    
    st.write(f"**Word**: {word}")
    st.write(f"**Target**: [{' '.join(target_phonemes)}]")
    st.write(f"**Detected**: [{' '.join(detected_phonemes)}]")
    
    # Show each phoneme
    cols = st.columns(len(target_phonemes))
    for idx, (target, detected) in enumerate(zip(target_phonemes, detected_phonemes)):
        with cols[idx]:
            if target == detected:
                st.success(f"✅")
            else:
                st.error(f"❌")
            show_phoneme_animation(target)
            st.caption(f"Target: /{target}/")
            if target != detected:
                st.caption(f"You: /{detected}/", help="Click to see details")


# ============================================================================
# EXAMPLE 5: Integration with Existing PhonoEcho Code
# ============================================================================

def example_5_integration():
    """
    How to integrate into existing PhonoEcho pronunciation feedback
    """
    st.header("Example 5: Integration Pattern")
    
    st.code('''
# In your existing pronunciation analysis code:

def analyze_pronunciation(audio_data, target_text):
    # ... your existing analysis code ...
    
    # Get phoneme-level results
    target_phonemes = extract_target_phonemes(target_text)
    detected_phonemes = recognize_phonemes(audio_data)
    
    # NEW: Display visual feedback for mismatches
    for i, (target, detected) in enumerate(zip(target_phonemes, detected_phonemes)):
        if target != detected:
            st.subheader(f"Error at position {i+1}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("Target:")
                show_phoneme_animation(target)
            with col2:
                st.write("Your pronunciation:")
                show_phoneme_animation(detected)
            
            st.info(f"Try adjusting your articulation to match the target.")
    ''', language='python')


# ============================================================================
# Main App
# ============================================================================

def main():
    st.title("🗣️ Sammy IPA Animations - Quick Start Examples")
    
    st.markdown("""
    This guide shows 5 ways to use the IPA animations in PhonoEcho.
    Select an example from the sidebar to see it in action.
    """)
    
    example = st.sidebar.radio(
        "Choose an example:",
        [
            "1. Simple Display",
            "2. Interactive Explorer",
            "3. Pronunciation Feedback",
            "4. Word-Level Feedback",
            "5. Integration Pattern"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Available Animations:**
    - 24 consonants
    - 21 vowels
    - All in GIF format
    - ~34 KB each
    """)
    
    if "1. Simple" in example:
        example_1_simple_display()
    elif "2. Interactive" in example:
        example_2_interactive()
    elif "3. Pronunciation" in example:
        example_3_feedback()
    elif "4. Word-Level" in example:
        example_4_word_feedback()
    elif "5. Integration" in example:
        example_5_integration()


if __name__ == "__main__":
    main()


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================
"""
To run this example:

1. Make sure you've generated the animations:
   cd app/tools
   conda run --name phonoecho python sammy_all_english_ipa.py

2. Run this Streamlit app:
   cd app/tools
   conda run --name phonoecho streamlit run quickstart_guide.py

3. Or integrate directly into your existing PhonoEcho code:
   from app.tools.quickstart_guide import show_phoneme_animation
   
   # Then use it anywhere:
   show_phoneme_animation('θ')
"""
