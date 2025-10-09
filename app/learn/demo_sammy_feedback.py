"""
LIVE DEMO: See How Learners Get Sammy Feedback
==============================================

Run this to see exactly what learners will see when they make pronunciation errors!

To run:
    cd app/learn
    conda run --name phonoecho streamlit run demo_sammy_feedback.py
"""

import streamlit as st
import json
from sammy_feedback import (
    show_phoneme_error_feedback,
    display_sammy_feedback,
    show_phoneme_comparison
)


# Sample pronunciation results from Azure (simulated)
SAMPLE_RESULTS = {
    "good_pronunciation": {
        "NBest": [{
            "Words": [{
                "Word": "hello",
                "PronunciationAssessment": {
                    "AccuracyScore": 92,
                    "ErrorType": "None"
                },
                "Phonemes": [
                    {"Phoneme": "h", "PronunciationAssessment": {"AccuracyScore": 95}},
                    {"Phoneme": "ɛ", "PronunciationAssessment": {"AccuracyScore": 90}},
                    {"Phoneme": "l", "PronunciationAssessment": {"AccuracyScore": 88}},
                    {"Phoneme": "oʊ", "PronunciationAssessment": {"AccuracyScore": 94}}
                ]
            }]
        }]
    },
    
    "mispronunciation_th_sound": {
        "NBest": [{
            "Words": [
                {
                    "Word": "think",
                    "PronunciationAssessment": {
                        "AccuracyScore": 65,
                        "ErrorType": "Mispronunciation"
                    },
                    "Phonemes": [
                        {"Phoneme": "θ", "PronunciationAssessment": {"AccuracyScore": 35}},  # ERROR!
                        {"Phoneme": "ɪ", "PronunciationAssessment": {"AccuracyScore": 85}},
                        {"Phoneme": "ŋ", "PronunciationAssessment": {"AccuracyScore": 88}},
                        {"Phoneme": "k", "PronunciationAssessment": {"AccuracyScore": 92}}
                    ]
                },
                {
                    "Word": "that",
                    "PronunciationAssessment": {
                        "AccuracyScore": 70,
                        "ErrorType": "Mispronunciation"
                    },
                    "Phonemes": [
                        {"Phoneme": "ð", "PronunciationAssessment": {"AccuracyScore": 42}},  # ERROR!
                        {"Phoneme": "æ", "PronunciationAssessment": {"AccuracyScore": 88}},
                        {"Phoneme": "t", "PronunciationAssessment": {"AccuracyScore": 90}}
                    ]
                }
            ]
        }]
    },
    
    "multiple_errors": {
        "NBest": [{
            "Words": [
                {
                    "Word": "very",
                    "PronunciationAssessment": {
                        "AccuracyScore": 60,
                        "ErrorType": "Mispronunciation"
                    },
                    "Phonemes": [
                        {"Phoneme": "v", "PronunciationAssessment": {"AccuracyScore": 45}},  # ERROR!
                        {"Phoneme": "ɛ", "PronunciationAssessment": {"AccuracyScore": 75}},
                        {"Phoneme": "ɹ", "PronunciationAssessment": {"AccuracyScore": 52}},  # ERROR!
                        {"Phoneme": "i", "PronunciationAssessment": {"AccuracyScore": 88}}
                    ]
                },
                {
                    "Word": "smooth",
                    "PronunciationAssessment": {
                        "AccuracyScore": 55,
                        "ErrorType": "Mispronunciation"
                    },
                    "Phonemes": [
                        {"Phoneme": "s", "PronunciationAssessment": {"AccuracyScore": 82}},
                        {"Phoneme": "m", "PronunciationAssessment": {"AccuracyScore": 85}},
                        {"Phoneme": "u", "PronunciationAssessment": {"AccuracyScore": 78}},
                        {"Phoneme": "ð", "PronunciationAssessment": {"AccuracyScore": 38}}   # ERROR!
                    ]
                }
            ]
        }]
    }
}


def main():
    st.set_page_config(page_title="Sammy Feedback Demo", page_icon="🎙️", layout="wide")
    
    st.title("🎙️ Sammy Visual Feedback - Live Demo")
    
    st.markdown("""
    This demo shows **exactly what learners will see** when they make pronunciation errors in PhonoEcho.
    
    Select a scenario below to see how the Sammy animations provide visual guidance!
    """)
    
    # Sidebar for scenario selection
    st.sidebar.header("📋 Demo Scenarios")
    scenario = st.sidebar.radio(
        "Choose a pronunciation scenario:",
        [
            "1. ✅ Perfect Pronunciation (No errors)",
            "2. ❌ Difficult 'th' sounds",
            "3. ❌ Multiple errors in sentence",
            "4. 🔧 Custom: Browse phonemes"
        ]
    )
    
    st.markdown("---")
    
    # === SCENARIO 1: Good pronunciation ===
    if "Perfect" in scenario:
        st.header("✅ Scenario 1: Perfect Pronunciation")
        st.info("**Student said:** 'hello' with excellent pronunciation")
        
        # Show the result
        pronunciation_result = SAMPLE_RESULTS["good_pronunciation"]
        show_phoneme_error_feedback(pronunciation_result)
        
        st.markdown("### 📊 What Happened:")
        st.success("""
        - All phonemes scored > 80%
        - No visual feedback needed
        - Student gets positive reinforcement
        - System encourages continued practice
        """)
    
    # === SCENARIO 2: TH sounds error ===
    elif "th" in scenario:
        st.header("❌ Scenario 2: Difficult 'th' Sounds")
        st.warning("**Student said:** 'think that' but struggled with /θ/ and /ð/ sounds")
        
        st.markdown("### 🎯 What the Student Sees:")
        
        # Show the actual feedback
        pronunciation_result = SAMPLE_RESULTS["mispronunciation_th_sound"]
        show_phoneme_error_feedback(pronunciation_result)
        
        st.markdown("---")
        st.markdown("### 📊 What Happened:")
        st.info("""
        **Detected Errors:**
        - /θ/ in "think" - Score: 35% ❌
        - /ð/ in "that" - Score: 42% ❌
        
        **Visual Feedback Provided:**
        - Sammy animations show tongue between teeth
        - Text explains the articulation
        - Tips guide practice strategy
        
        **Student's Next Steps:**
        1. Watch animations carefully
        2. Position tongue as shown
        3. Practice sounds in isolation
        4. Try the words again
        """)
        
        st.markdown("---")
        st.markdown("### 🔍 Side-by-Side Comparison Example")
        st.caption("If student said /s/ instead of /θ/, we can show comparison:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎯 Target: /θ/ (think)**")
            display_sammy_feedback('θ')
        with col2:
            st.markdown("**🗣️ Common mistake: /s/ (sink)**")
            display_sammy_feedback('s')
        
        st.warning("⚠️ Notice the difference: /θ/ = tongue between teeth, /s/ = tongue behind teeth")
    
    # === SCENARIO 3: Multiple errors ===
    elif "Multiple" in scenario:
        st.header("❌ Scenario 3: Multiple Pronunciation Errors")
        st.warning("**Student said:** 'very smooth' with several pronunciation challenges")
        
        st.markdown("### 🎯 What the Student Sees:")
        
        # Show the actual feedback
        pronunciation_result = SAMPLE_RESULTS["multiple_errors"]
        show_phoneme_error_feedback(pronunciation_result)
        
        st.markdown("---")
        st.markdown("### 📊 Analysis:")
        st.info("""
        **Errors Detected:**
        - /v/ in "very" - Score: 45% ❌
        - /ɹ/ in "very" - Score: 52% ❌
        - /ð/ in "smooth" - Score: 38% ❌
        
        **Smart Feedback:**
        - Shows most critical errors first
        - Provides visual guide for each
        - Prevents information overload
        - Focuses on one sound at a time
        
        **Learning Impact:**
        - Student sees exactly what to fix
        - Can practice specific sounds
        - Gets immediate visual guidance
        - Builds confidence through understanding
        """)
    
    # === SCENARIO 4: Custom phoneme browser ===
    else:
        st.header("🔧 Custom: Phoneme Explorer")
        st.info("Browse any phoneme to see how the feedback looks")
        
        # Categorize phonemes
        consonants = ['p', 'b', 't', 'd', 'k', 'g', 'f', 'v', 'θ', 'ð', 
                     's', 'z', 'ʃ', 'ʒ', 'h', 'm', 'n', 'ŋ', 'l', 'ɹ', 'w', 'j']
        vowels = ['i', 'ɪ', 'e', 'ɛ', 'æ', 'ə', 'ʌ', 'ɜ', 
                 'u', 'ʊ', 'o', 'ɔ', 'ɑ', 'eɪ', 'aɪ', 'ɔɪ', 'aʊ', 'oʊ']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Consonants")
            selected_consonant = st.selectbox(
                "Choose a consonant:",
                consonants,
                format_func=lambda x: f"/{x}/"
            )
            if st.button("Show Consonant", type="primary"):
                st.markdown("---")
                display_sammy_feedback(selected_consonant, f"Sound: /{selected_consonant}/")
        
        with col2:
            st.subheader("Vowels")
            selected_vowel = st.selectbox(
                "Choose a vowel:",
                vowels,
                format_func=lambda x: f"/{x}/"
            )
            if st.button("Show Vowel", type="primary"):
                st.markdown("---")
                display_sammy_feedback(selected_vowel, f"Sound: /{selected_vowel}/")
        
        st.markdown("---")
        st.markdown("### 💡 Try These Common Problem Sounds:")
        
        problem_sounds = {
            '/θ/ vs /s/': ('θ', 's'),
            '/v/ vs /w/': ('v', 'w'),
            '/l/ vs /ɹ/': ('l', 'ɹ'),
            '/ð/ vs /z/': ('ð', 'z')
        }
        
        selected_pair = st.selectbox("Select a comparison:", list(problem_sounds.keys()))
        
        if st.button("Compare These Sounds"):
            sound1, sound2 = problem_sounds[selected_pair]
            st.markdown("---")
            show_phoneme_comparison(sound1, sound2)
    
    # === FOOTER WITH INTEGRATION INFO ===
    st.markdown("---")
    st.markdown("## 🚀 Ready to Add This to PhonoEcho?")
    
    with st.expander("📝 See Integration Instructions", expanded=False):
        st.code('''
# Step 1: Add import at top of echo_learning.py
from sammy_feedback import show_phoneme_error_feedback

# Step 2: Add after error collection (around line 210)
error_data = collect_errors(pronunciation_result)
error_table = create_error_table(error_data)

# NEW: Add this line
show_phoneme_error_feedback(pronunciation_result)

# That's it! Students will now see Sammy animations automatically!
        ''', language='python')
        
        st.success("✅ Just 2 simple changes and your learners get visual feedback!")
    
    # === SIDEBAR INFO ===
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 About This Demo")
    st.sidebar.info("""
    This demo uses **real pronunciation assessment data structure** 
    from Azure Cognitive Services.
    
    When integrated into PhonoEcho:
    - Triggers automatically after pronunciation
    - Shows only problematic phonemes
    - Adapts to each student's errors
    - Provides personalized guidance
    """)
    
    st.sidebar.markdown("### 🎯 Key Features")
    st.sidebar.success("""
    ✅ Automatic error detection
    ✅ Visual articulatory guidance
    ✅ Text explanations
    ✅ Practice tips
    ✅ Progress tracking
    ✅ Side-by-side comparisons
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("🎙️ Sammy animations from incl.pl/sammy/")


if __name__ == "__main__":
    main()
