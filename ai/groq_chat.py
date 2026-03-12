"""
Groq AI Chat Module
Handles conversation with Groq AI (fast LLM inference)
"""

from groq import Groq
import json
from config import GROQ_API_KEY, SYSTEM_PROMPT


class GroqChat:
    """Handles AI conversation using Groq"""
    
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY tidak ditemukan. "
                "Silakan set di file .env atau environment variable."
            )
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"  # Fast and capable
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
                "content": user_input
            })
            
            # Keep history manageable (last 10 messages)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(self.history[-10:])
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add assistant response to history
            self.history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            return assistant_response
        except Exception as e:
            print(f"❌ Error dari Groq: {e}")
            return "Maaf, terjadi kesalahan saat memproses permintaan."
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.history = []
        print("🔄 Percakapan direset")
    
    def analyze_intent(self, user_input: str) -> dict:
        """
        Analyze user input to determine intent using AI.
        
        Args:
            user_input: The user's message
            
        Returns:
            dict: Intent information with 'type' and 'target'
        """
        prompt = f"""Analisis perintah pengguna dan tentukan jenisnya.
Jawab HANYA dengan format JSON, tanpa penjelasan tambahan:
{{"type": "tipe", "target": "target"}}

Tipe yang tersedia:
- "open_app": membuka aplikasi (notepad, chrome, calculator, spotify, discord, dll)
- "close_app": menutup/tutup aplikasi (target = nama aplikasi)
- "open_website": membuka website populer (youtube, google, facebook, instagram, dll) 
- "open_url": membuka URL/link custom langsung (target = URL lengkap seperti rhakelino.site, example.com/page)
- "play_youtube": memutar lagu/musik/video di YouTube langsung (target = judul)
- "search_youtube": mencari video di YouTube (target = kata kunci)
- "search_google": mencari di Google (target = kata kunci)
- "close_tab": menutup tab browser saat ini
- "close_all_tabs": menutup semua tab browser
- "time": menanyakan waktu
- "date": menanyakan tanggal
- "volume_up": menaikkan volume
- "volume_down": menurunkan volume
- "volume_mute": mute volume
- "shutdown": mematikan komputer
- "restart": restart komputer
- "sleep": sleep mode
- "lock": mengunci layar
- "chat": untuk pertanyaan umum, obrolan, atau hal lain

Contoh:
- "buka notepad" -> {{"type": "open_app", "target": "notepad"}}
- "buka youtube" -> {{"type": "open_website", "target": "youtube"}}
- "buka facebook" -> {{"type": "open_website", "target": "facebook"}}
- "buka instagram" -> {{"type": "open_website", "target": "instagram"}}
- "tutup chrome" -> {{"type": "close_app", "target": "chrome"}}
- "putar lagu Sheila on 7" -> {{"type": "play_youtube", "target": "Sheila on 7"}}
- "cari tutorial python" -> {{"type": "search_youtube", "target": "tutorial python"}}
- "jam berapa" -> {{"type": "time", "target": null}}
- "siapa presiden indonesia" -> {{"type": "chat", "target": null}}
- "buka url rhakelino.site" -> {{"type": "open_url", "target": "rhakelino.site"}}
- "buka link example.com/page" -> {{"type": "open_url", "target": "example.com/page"}}
- "tolong buka https://github.com/user" -> {{"type": "open_url", "target": "https://github.com/user"}}
- "akses mysite.id" -> {{"type": "open_url", "target": "mysite.id"}}

Perintah pengguna: "{user_input}"
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response if it has markdown
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1])
            
            return json.loads(result_text)
        except Exception as e:
            print(f"⚠️ Error analisis intent: {e}")
            return {"type": "chat", "target": None}
