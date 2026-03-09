import time
import streamlit as st
from openai import AzureOpenAI

class AIChat:
    """Represent the Aichat."""
    def __init__(self):
        """Handle init."""
        try:
            self.client = AzureOpenAI(
                azure_endpoint=st.secrets['AzureGPT']["AZURE_OPENAI_ENDPOINT"],
                api_key=st.secrets['AzureGPT']["AZURE_OPENAI_API_KEY"],
                api_version="2024-12-01-preview"
            )
        except Exception as e:
            st.warning(f"Error initializing Azure OpenAI: {str(e)}")
        self.prompt = ""

    def set_prompt(self, practice_text, score_summary, error_data):
        """Generate conversational prompt for Azure GPT"""
        base_prompt = """
            あなたは英語発音チューターです。私は今、発音練習セッションを終えたばかりで、改善のためにあなたのサポートをお願いしたいです。
        今回の練習で使ったテキストは以下の通りです：  
        {practice_text}

        各項目のスコアは以下の通りです：  
        {score_summary}

        以下は、今回の練習での発音ミスの要約です：  
        {error_summary}

        私の専属チューターとして、以下の点にやさしく丁寧に対応してください：

        1. 🎯 まず、今回の発音練習について前向きなフィードバックをください  
        2. 💡 発音ミスがある場合は、これらの間違いが起こった理由について会話調で分かりやすく説明してください。ミスがない場合は、今回の発音の良かった点を具体的に褒めてください  
        3. 🗣️ シンプルな単語を使って、実際の例やデモンストレーションを交えて解説してください  
        4. ✨ さらなる上達のための簡単な練習を2〜3個教えてください  
        5. 🌟 最後に、次回の練習に向けた励ましのメッセージをお願いします  

        発音の説明を行う際には、カタカナや仮名を使わず、必ずIPA（国際音声記号）を使ってください。  
        まるで目の前で一緒にレッスンしているような、フレンドリーで親しみやすい口調でお願いします。
        日本語で答えてください。  
        """
        self.prompt = base_prompt.format(practice_text=practice_text, score_summary=score_summary, error_summary=error_data)

    def format_errors_for_azure(self, current_errors):
        """Format error data into prompt text"""
        if not current_errors:
            return "今回の練習では発音エラーはありませんでした。素晴らしい発音でした！"
            
        error_summary = []
        for error_type, data in current_errors.items():
            if isinstance(data, dict) and data.get('count', 0) > 0:
                error_summary.append(
                    f"I made {data['count']} {error_type} mistakes "
                    f"with these words: {', '.join(data['words'])}"
                )
        
        return "\n".join(error_summary) if error_summary else "今回の練習では発音エラーはありませんでした。素晴らしい発音でした！"

    def format_score_summary(self, overall_score):
        """Format score summary for Azure GPT"""
        if not overall_score:
            return "評価データが利用できません"
        
        score_text = []
        score_text.append(f"総合スコア: {overall_score.get('PronScore', 0):.1f}/100")
        score_text.append(f"正確性: {overall_score.get('AccuracyScore', 0):.1f}/100")
        score_text.append(f"流暢性: {overall_score.get('FluencyScore', 0):.1f}/100")
        score_text.append(f"完全性: {overall_score.get('CompletenessScore', 0):.1f}/100")
        score_text.append(f"韻律: {overall_score.get('ProsodyScore', 0):.1f}/100")
        
        return "\n".join(score_text)

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

    def get_chat_response(self, error_data, practice_text=None, score_summary=None):
        """Get streaming response from Azure GPT"""
        formatted_errors = self.format_errors_for_azure(error_data)
        
        # Use empty strings as fallback if not provided
        practice_text = practice_text or "練習テキストが提供されていません"
        score_summary = score_summary or "スコア情報が提供されていません"
            
        self.set_prompt(practice_text, score_summary, formatted_errors)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",  # Update with your actual deployment name
                messages=[
                    {"role": "system", "content": "You are a helpful English pronunciation tutor."},
                    {"role": "user", "content": self.prompt}
                ],
                stream=True
            )
            
            # Add validation for response
            if not response:
                st.error("Empty response from API")
                return None
                
            return self.stream_generator(response)
            
        except Exception as e:
            st.error(f"Error getting chat response: {str(e)}")
            return None
