"""
Gemini AI Chat Module
Handles conversation with Google Gemini AI using the new google-genai package
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, SYSTEM_PROMPT


class GeminiChat:
    """Handles AI conversation using Google Gemini"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY tidak ditemukan. "
                "Silakan set di file .env atau environment variable."
            )
        
        # Initialize client with API key
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"
        
        # Conversation history for context
        self.history = []
    
    def get_response(self, user_input: str) -> str:
        """
        Get AI response for user input.
        
        Args:
            user_input: The user's message
            
        Returns:
            str: The AI's response
        """
        try:
            # Add user message to history
            self.history.append({
                "role": "user",
                "parts": [{"text": user_input}]
            })
            
            # Generate response with chat history
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            assistant_response = response.text.strip()
            
            # Add assistant response to history
            self.history.append({
                "role": "model",
                "parts": [{"text": assistant_response}]
            })
            
            return assistant_response
        except Exception as e:
            print(f"❌ Error dari Gemini: {e}")
            return "Maaf, terjadi kesalahan saat memproses permintaan."
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.history = []
        print("🔄 Percakapan direset")
    
    def analyze_intent(self, user_input: str) -> dict:
        """
        Analyze user input to determine intent.
        
        Args:
            user_input: The user's message
            
        Returns:
            dict: Intent information with 'type' and 'target'
        """
        prompt = f"""Analisis perintah berikut dan tentukan jenisnya.
Jawab HANYA dengan format JSON tanpa markdown:
{{"type": "tipe", "target": "target"}}

Tipe yang tersedia:
- "open_app": jika pengguna ingin membuka aplikasi (notepad, chrome, calculator, dll)
- "open_website": jika pengguna ingin membuka website (youtube, google, dll) 
- "time": jika pengguna menanyakan waktu
- "chat": untuk pertanyaan umum atau obrolan biasa

Perintah: "{user_input}"
"""
        try:
            # Use generate_content for one-off analysis (not in chat history)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=100
                )
            )
            
            result_text = response.text.strip()
            
            # Clean up response if it has markdown
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            import json
            return json.loads(result_text)
        except Exception as e:
            print(f"⚠️ Error analisis intent: {e}")
            return {"type": "chat", "target": None}
