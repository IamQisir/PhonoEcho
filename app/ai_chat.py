import time
import json
import streamlit as st
from openai import AzureOpenAI

class AIChat:
    def __init__(self):
        """Initialize without loading Azure client - client is loaded on first use"""
        self.client = None
        self.prompt = ""
    
    def _ensure_client(self):
        """Lazy load Azure OpenAI client only when needed"""
        if self.client is None:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=st.secrets['AzureGPT']["AZURE_OPENAI_ENDPOINT"],
                    api_key=st.secrets['AzureGPT']["AZURE_OPENAI_API_KEY"],
                    api_version="2024-02-15-preview"
                )
            except Exception as e:
                st.warning(f"Error initializing Azure OpenAI: {str(e)}")
                return False
        return True

    def create_detailed_prompt(self, pronunciation_result):
        """
        Create a detailed prompt from full Azure pronunciation assessment JSON
        
        Args:
            pronunciation_result: Full JSON response from Azure Speech API
            
        Returns:
            str: Formatted prompt for ChatGPT
        """
        # Extract key information
        overall = pronunciation_result["NBest"][0]["PronunciationAssessment"]
        words = pronunciation_result["NBest"][0]["Words"]
        display_text = pronunciation_result["NBest"][0]["Display"]
        
        # Calculate overall performance
        pron_score = overall.get("PronScore", 0)
        accuracy = overall.get("AccuracyScore", 0)
        fluency = overall.get("FluencyScore", 0)
        completeness = overall.get("CompletenessScore", 0)
        prosody = overall.get("ProsodyScore", 0)
        
        # Categorize errors
        mispronounced_words = []
        omitted_words = []
        phoneme_issues = []
        
        for word in words:
            word_text = word["Word"]
            if "PronunciationAssessment" not in word:
                continue
                
            word_assessment = word["PronunciationAssessment"]
            error_type = word_assessment.get("ErrorType", "None")
            word_accuracy = word_assessment.get("AccuracyScore", 0)
            
            if error_type == "Mispronunciation" or word_accuracy < 60:
                # Find problematic phonemes
                problematic_phonemes = []
                if "Phonemes" in word:
                    for phoneme in word["Phonemes"]:
                        phoneme_score = phoneme.get("PronunciationAssessment", {}).get("AccuracyScore", 100)
                        if phoneme_score < 60:
                            problematic_phonemes.append({
                                'phoneme': phoneme["Phoneme"],
                                'score': phoneme_score
                            })
                
                mispronounced_words.append({
                    'word': word_text,
                    'score': word_accuracy,
                    'phonemes': problematic_phonemes
                })
            elif error_type == "Omission":
                omitted_words.append(word_text)
        
        # Build comprehensive prompt
        prompt = f"""
You are an experienced English pronunciation coach. A student just practiced pronunciation and needs your detailed, encouraging feedback.

**Target Sentence:** "{display_text}"

**Overall Performance:**
- Pronunciation Score: {pron_score:.1f}/100
- Accuracy: {accuracy:.1f}/100
- Fluency: {fluency:.1f}/100
- Completeness: {completeness:.1f}/100
- Prosody (Rhythm & Intonation): {prosody:.1f}/100

**Detailed Analysis:**
"""
        
        # Add mispronounced words section
        if mispronounced_words:
            prompt += "\n**Words that need improvement:**\n"
            for item in mispronounced_words[:5]:  # Limit to top 5
                prompt += f"- '{item['word']}' (score: {item['score']:.1f})\n"
                if item['phonemes']:
                    phoneme_list = ', '.join([f"{p['phoneme']}({p['score']:.0f})" for p in item['phonemes'][:3]])
                    prompt += f"  Problem sounds: {phoneme_list}\n"
        
        # Add omitted words
        if omitted_words:
            prompt += f"\n**Omitted words:** {', '.join(omitted_words)}\n"
        
        # Add performance level context
        if pron_score >= 90:
            context = "The student performed excellently!"
        elif pron_score >= 80:
            context = "The student performed very well with minor areas for improvement."
        elif pron_score >= 70:
            context = "The student performed well but has some areas to work on."
        elif pron_score >= 60:
            context = "The student needs practice in several areas."
        else:
            context = "The student needs significant practice and support."
        
        prompt += f"\n**Context:** {context}\n"
        
        prompt += """
**Your Task:**
Provide warm, encouraging, and specific feedback in Chinese (中文). Structure your response as follows:

1. **鼓励开场** (Encouraging Opening, 2-3 sentences)
   - Start with genuine praise for their effort
   - Highlight what they did well (even if pronunciation is perfect, praise their clarity, confidence, rhythm, etc.)

2. **详细分析** (Detailed Analysis, 3-4 sentences)
   - Explain specific pronunciation issues in simple terms
   - If pronunciation is already excellent, discuss subtle nuances they can work on (intonation, natural rhythm, emotion, connecting sounds, etc.)
   - Use everyday analogies to help them understand

3. **实用建议** (Practical Tips, 3-4 specific exercises)
   - Give concrete, actionable exercises they can do RIGHT NOW
   - Focus on the most important issues first
   - Even for perfect pronunciation, suggest advanced techniques (shadowing, emotion practice, speed variation)

4. **鼓励结尾** (Encouraging Closing, 2 sentences)
   - End with motivating words
   - Set a positive expectation for next practice

**Important Guidelines:**
- ALWAYS provide feedback, even if their pronunciation is perfect (focus on advanced techniques, naturalness, prosody)
- Be warm, supportive, and conversational (像朋友一样)
- Use emojis occasionally to keep it friendly (but not too many)
- Keep total response under 400 words
- Be specific about which sounds/words need work
- Provide memorable tips they can immediately apply

请用中文回复！
"""
        
        return prompt

    def stream_generator(self, response):
        """Generate streaming response"""
        full_response = ""
        for chunk in response:
            try:
                if chunk.choices and hasattr(chunk.choices[0].delta, 'content'):
                    new_content = chunk.choices[0].delta.content
                    if new_content is not None:  # Add null check
                        full_response += new_content
                        time.sleep(0.01)
                        yield new_content
            except Exception as e:
                st.error(f"Streaming error: {str(e)}")
                continue

    def get_chat_response_from_full_result(self, pronunciation_result):
        """
        Get streaming response from Azure GPT using full pronunciation assessment JSON
        
        Args:
            pronunciation_result: Full JSON response from Azure Speech API
            
        Returns:
            Generator yielding response chunks, or None if error
        """
        # Ensure client is initialized
        if not self._ensure_client():
            return None
        
        # Create detailed prompt from full JSON
        try:
            prompt = self.create_detailed_prompt(pronunciation_result)
        except Exception as e:
            st.error(f"Error creating prompt: {str(e)}")
            return None
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a warm, encouraging, and highly skilled English pronunciation coach. You always provide specific, actionable feedback in Chinese, even for students with excellent pronunciation."},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1000  # Increased for more detailed feedback
            )
            
            if not response:
                st.error("Empty response from API")
                return None
                
            return self.stream_generator(response)
            
        except Exception as e:
            st.error(f"Error getting chat response: {str(e)}")
            return None

    # Keep old methods for backward compatibility
    def set_prompt(self, error_data):
        """Generate conversational prompt for Azure GPT"""
        base_prompt = """
        You are a ChatGPT 4o English pronunciation tutor. I've just finished a pronunciation practice session and would like your help improving. Here are my mistakes:

        {error_summary}

        Please act as my personal tutor and:
        1. 🎯 First, give me encouraging feedback about my practice attempt
        2. 💡 Explain in a conversational way why these errors might have occurred
        3. 🗣️ Provide practical examples and demonstrations using simple words
        4. ✨ Give me 2-3 quick exercises I can try right now to improve
        5. 🌟 End with an encouraging message for my next practice

        Please keep your response friendly and supportive, as if we're having a face-to-face tutoring session!
        Please respond in Chinese!
        """
        self.prompt = base_prompt.format(error_summary=error_data)

    def format_errors_for_azure(self, current_errors):
        """Format error data into prompt text"""
        if not current_errors:
            return None
            
        error_summary = []
        for error_type, data in current_errors.items():
            if isinstance(data, dict) and data.get('count', 0) > 0:
                error_summary.append(
                    f"I made {data['count']} {error_type} mistakes "
                    f"with these words: {', '.join(data['words'])}"
                )
        
        return "\n".join(error_summary) if error_summary else None

    def stream_generator(self, response):
        """Generate streaming response"""
        full_response = ""
        for chunk in response:
            try:
                if chunk.choices and hasattr(chunk.choices[0].delta, 'content'):
                    new_content = chunk.choices[0].delta.content
                    if new_content is not None:  # Add null check
                        full_response += new_content
                        time.sleep(0.01)
                        yield new_content
            except Exception as e:
                st.error(f"Streaming error: {str(e)}")
                continue

    def get_chat_response(self, error_data):
        """Get streaming response from Azure GPT"""
        # Ensure client is initialized
        if not self._ensure_client():
            return None
            
        formatted_errors = self.format_errors_for_azure(error_data)
        if not formatted_errors:
            return None
            
        self.set_prompt(formatted_errors)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful English pronunciation tutor."},
                    {"role": "user", "content": self.prompt}
                ],
                stream=True,
                temperature=0.7,
                max_tokens=800
            )
            
            # Add validation for response
            if not response:
                st.error("Empty response from API")
                return None
                
            return self.stream_generator(response)
            
        except Exception as e:
            st.error(f"Error getting chat response: {str(e)}")
            return None