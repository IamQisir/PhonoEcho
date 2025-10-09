"""
Integration example: How to use Sammy IPA animations in PhonoEcho
This demonstrates how to display articulatory animations as feedback
"""

import streamlit as st
from pathlib import Path
from typing import Optional

# Paths to animation directories
CONSONANTS_DIR = Path("app/tools/sammy_consonants_gifs")
VOWELS_DIR = Path("app/tools/sammy_vowels_gifs")

# Mapping common phonemes to their IPA symbols
PHONEME_MAPPING = {
    # Consonants
    'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'g',
    'f': 'f', 'v': 'v', 'θ': 'θ', 'ð': 'ð', 's': 's', 'z': 'z',
    'ʃ': 'ʃ', 'ʒ': 'ʒ', 'h': 'h', 'tʃ': 'tʃ', 'dʒ': 'dʒ',
    'm': 'm', 'n': 'n', 'ŋ': 'ŋ', 'l': 'l', 'ɹ': 'ɹ', 'j': 'j', 'w': 'w',
    # Common alternative notations
    'sh': 'ʃ', 'zh': 'ʒ', 'ch': 'tʃ', 'j': 'dʒ', 'ng': 'ŋ', 'r': 'ɹ',
    'th': 'θ',  # voiceless
    'dh': 'ð',  # voiced
    
    # Vowels
    'i': 'i', 'ɪ': 'ɪ', 'e': 'e', 'ɛ': 'ɛ', 'æ': 'æ',
    'ə': 'ə', 'ʌ': 'ʌ', 'ɜ': 'ɜ',
    'u': 'u', 'ʊ': 'ʊ', 'o': 'o', 'ɔ': 'ɔ', 'ɑ': 'ɑ', 'ɒ': 'ɒ',
    'eɪ': 'eɪ', 'aɪ': 'aɪ', 'ɔɪ': 'ɔɪ', 'aʊ': 'aʊ', 'oʊ': 'oʊ',
    'ɝ': 'ɝ', 'ɚ': 'ɚ',
    # Common alternative notations
    'iy': 'i', 'ih': 'ɪ', 'eh': 'ɛ', 'ae': 'æ',
    'ah': 'ʌ', 'uh': 'ʊ', 'uw': 'u', 'ow': 'oʊ',
    'ey': 'eɪ', 'ay': 'aɪ', 'oy': 'ɔɪ', 'aw': 'aʊ',
}


def get_ipa_animation_path(phoneme: str) -> Optional[Path]:
    """
    Get the path to the IPA animation GIF for a given phoneme
    
    Args:
        phoneme: The phoneme symbol (IPA or common notation)
    
    Returns:
        Path to the GIF file, or None if not found
    """
    # Normalize phoneme notation
    ipa_symbol = PHONEME_MAPPING.get(phoneme, phoneme)
    
    # Check consonants directory
    consonant_path = CONSONANTS_DIR / f"{ipa_symbol}.gif"
    if consonant_path.exists():
        return consonant_path
    
    # Check vowels directory
    vowel_path = VOWELS_DIR / f"{ipa_symbol}.gif"
    if vowel_path.exists():
        return vowel_path
    
    return None


def display_articulation_feedback(phoneme: str, title: str = "Articulatory Position"):
    """
    Display Sammy animation as articulatory feedback in Streamlit
    
    Args:
        phoneme: The phoneme to display
        title: Title for the display section
    """
    animation_path = get_ipa_animation_path(phoneme)
    
    if animation_path and animation_path.exists():
        st.subheader(title)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(animation_path), caption=f"IPA: /{phoneme}/", use_column_width=True)
            st.caption("Sagittal section showing tongue, lip, and velum positions")
    else:
        st.warning(f"Animation not found for phoneme: {phoneme}")


def display_phoneme_comparison(target_phoneme: str, user_phoneme: str):
    """
    Display side-by-side comparison of target and user's phoneme
    
    Args:
        target_phoneme: The correct target phoneme
        user_phoneme: The phoneme detected from user's pronunciation
    """
    st.subheader("📊 Pronunciation Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Target Pronunciation**")
        target_path = get_ipa_animation_path(target_phoneme)
        if target_path and target_path.exists():
            st.image(str(target_path), caption=f"/{target_phoneme}/")
        else:
            st.info(f"Target: /{target_phoneme}/")
    
    with col2:
        st.markdown("**🗣️ Your Pronunciation**")
        user_path = get_ipa_animation_path(user_phoneme)
        if user_path and user_path.exists():
            st.image(str(user_path), caption=f"/{user_phoneme}/")
        else:
            st.info(f"Detected: /{user_phoneme}/")
    
    # Provide feedback
    if target_phoneme == user_phoneme:
        st.success("✅ Perfect! Your articulation matches the target.")
    else:
        st.warning(f"⚠️ Try adjusting your articulation to match the target position.")


def get_phoneme_description(phoneme: str) -> str:
    """
    Get a descriptive explanation of how to articulate a phoneme
    
    Args:
        phoneme: The IPA phoneme symbol
    
    Returns:
        Human-readable description of the articulation
    """
    descriptions = {
        # Stops
        'p': "Voiceless bilabial stop - Close both lips, build air pressure, release explosively",
        'b': "Voiced bilabial stop - Same as /p/ but with vocal fold vibration",
        't': "Voiceless alveolar stop - Touch tongue tip to alveolar ridge, release",
        'd': "Voiced alveolar stop - Same as /t/ but with vocal fold vibration",
        'k': "Voiceless velar stop - Back of tongue touches soft palate (velum)",
        'g': "Voiced velar stop - Same as /k/ but with vocal fold vibration",
        
        # Fricatives
        'f': "Voiceless labiodental fricative - Upper teeth touch lower lip, force air through",
        'v': "Voiced labiodental fricative - Same as /f/ but with vocal fold vibration",
        'θ': "Voiceless dental fricative - Tongue tip between teeth, force air through",
        'ð': "Voiced dental fricative - Same as /θ/ but with vocal fold vibration",
        's': "Voiceless alveolar fricative - Tongue near alveolar ridge, narrow air channel",
        'z': "Voiced alveolar fricative - Same as /s/ but with vocal fold vibration",
        'ʃ': "Voiceless postalveolar fricative - Tongue slightly back from /s/ position",
        'ʒ': "Voiced postalveolar fricative - Same as /ʃ/ but with vocal fold vibration",
        'h': "Voiceless glottal fricative - Open vocal tract, force air from glottis",
        
        # Affricates
        'tʃ': "Voiceless postalveolar affricate - Combine /t/ and /ʃ/ in quick sequence",
        'dʒ': "Voiced postalveolar affricate - Combine /d/ and /ʒ/ in quick sequence",
        
        # Nasals
        'm': "Bilabial nasal - Close lips, lower velum, air flows through nose",
        'n': "Alveolar nasal - Tongue tip at alveolar ridge, air through nose",
        'ŋ': "Velar nasal - Back of tongue at velum, air through nose",
        
        # Approximants
        'l': "Alveolar lateral approximant - Tongue tip at alveolar ridge, air flows around sides",
        'ɹ': "Alveolar approximant - Tongue tip curled slightly back, no contact",
        'j': "Palatal approximant - Tongue body raised toward hard palate",
        'w': "Labial-velar approximant - Lips rounded, back of tongue raised",
        
        # Vowels
        'i': "Close front unrounded - High front tongue, spread lips (as in 'bee')",
        'ɪ': "Near-close front unrounded - Slightly lower than /i/ (as in 'bit')",
        'e': "Close-mid front unrounded - Mid-high front tongue (as in 'bay')",
        'ɛ': "Open-mid front unrounded - Mid-low front tongue (as in 'bed')",
        'æ': "Near-open front unrounded - Low front tongue (as in 'cat')",
        'ə': "Mid central - Neutral tongue position (as in 'about')",
        'ʌ': "Open-mid back unrounded - Mid-low back tongue (as in 'cup')",
        'ɜ': "Open-mid central unrounded - Mid central with r-coloring (as in 'bird')",
        'u': "Close back rounded - High back tongue, rounded lips (as in 'boot')",
        'ʊ': "Near-close back rounded - Slightly lower than /u/ (as in 'book')",
        'o': "Close-mid back rounded - Mid-high back, rounded lips (as in 'boat')",
        'ɔ': "Open-mid back rounded - Mid-low back, rounded lips (as in 'thought')",
        'ɑ': "Open back unrounded - Low back tongue, unrounded (as in 'father')",
        'ɒ': "Open back rounded - Low back tongue, rounded lips (British 'got')",
    }
    
    return descriptions.get(phoneme, f"Phoneme: /{phoneme}/")


# ===== EXAMPLE USAGE IN STREAMLIT APP =====
def example_pronunciation_feedback():
    """Example integration in PhonoEcho's pronunciation feedback system"""
    st.title("🗣️ PhonoEcho Pronunciation Feedback with Articulatory Animations")
    
    # Example: User tried to pronounce a word
    target_word = "think"
    target_phonemes = ['θ', 'ɪ', 'ŋ', 'k']
    detected_phonemes = ['s', 'ɪ', 'ŋ', 'k']  # User said 's' instead of 'θ'
    
    st.header(f"📝 Word: {target_word}")
    
    # Show where the error occurred
    st.subheader("🔍 Phoneme-by-Phoneme Analysis")
    
    cols = st.columns(len(target_phonemes))
    for idx, (target, detected) in enumerate(zip(target_phonemes, detected_phonemes)):
        with cols[idx]:
            if target == detected:
                st.success(f"✅ /{target}/")
            else:
                st.error(f"❌ /{target}/ → /{detected}/")
            
            # Show animation for incorrect phonemes
            if target != detected:
                animation_path = get_ipa_animation_path(target)
                if animation_path:
                    st.image(str(animation_path), width=150)
                    st.caption(get_phoneme_description(target))
    
    # Detailed feedback on the first error
    st.markdown("---")
    error_idx = next((i for i, (t, d) in enumerate(zip(target_phonemes, detected_phonemes)) if t != d), None)
    
    if error_idx is not None:
        st.subheader("🎯 Focus on This Sound")
        target = target_phonemes[error_idx]
        detected = detected_phonemes[error_idx]
        display_phoneme_comparison(target, detected)
        
        st.info(f"**How to pronounce /{target}/:**\n\n{get_phoneme_description(target)}")


if __name__ == "__main__":
    # Run the example
    example_pronunciation_feedback()
