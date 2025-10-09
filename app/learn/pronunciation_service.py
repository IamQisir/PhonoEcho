"""
Pronunciation Service Module
Handles Azure Cognitive Services pronunciation assessment
"""

import json
import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import traceback


def pronunciation_assessment(audio_file, reference_text):
    """
    Perform pronunciation assessment using Azure Cognitive Services
    
    Args:
        audio_file: Path to the audio file to assess
        reference_text: Reference text that should have been spoken
    
    Returns:
        dict: Pronunciation assessment results in JSON format
    
    Raises:
        Exception: If assessment fails
    """
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
        st.error(traceback.format_exc())
        raise
