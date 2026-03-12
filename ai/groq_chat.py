"""
Groq AI Chat Module
Handles conversation with Groq AI (fast LLM inference)
With Web Search capability for real-time information
"""

from groq import Groq
import json
from config import GROQ_API_KEY, SYSTEM_PROMPT

# Try to import web search
try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    print("⚠️ duckduckgo-search not installed, web search disabled")


class GroqChat:
    """Handles AI conversation using Groq with Web Search"""
    
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY tidak ditemukan. "
                "Silakan set di file .env atau environment variable."
            )
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"  # Fast and capable
        self.history = []
    
    def _needs_web_search(self, user_input: str) -> bool:
        """
        Use AI to determine if the question needs real-time web information.
        
        Returns:
            bool: True if web search is needed
        """
        if not WEB_SEARCH_AVAILABLE:
            return False
        
        prompt = """Analisis apakah pertanyaan berikut MEMBUTUHKAN informasi terbaru/real-time dari internet.

Jawab HANYA dengan "YA" atau "TIDAK".

Butuh web search (jawab YA):
- Pertanyaan tentang skor pertandingan, hasil kompetisi terkini
- Berita terbaru atau peristiwa terkini
- Harga saham/crypto/kurs saat ini
- Cuaca saat ini
- Informasi yang berubah-ubah (jadwal, event, trending)
- Pertanyaan dengan kata "tadi", "kemarin", "hari ini", "terbaru", "sekarang", "tadi malam"

TIDAK butuh web search (jawab TIDAK):
- Pertanyaan pengetahuan umum (siapa penemu listrik, apa itu DNA)
- Pertanyaan opini atau saran
- Obrolan biasa (halo, apa kabar)
- Pertanyaan tentang kemampuan asisten
- Pertanyaan matematika atau logika
- Pertanyaan definisi atau konsep

Pertanyaan: "{}"
""".format(user_input)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return "YA" in result
        except Exception as e:
            print(f"⚠️ Error checking web search need: {e}")
            return False
    
    def _generate_search_query(self, user_input: str) -> str:
        """
        Use AI to generate an optimal search query from user input.
        
        Returns:
            str: Optimized search query
        """
        prompt = f"""Buat search query yang optimal untuk mencari di internet berdasarkan pertanyaan user.
Jawab HANYA dengan search query-nya saja, tanpa penjelasan.
Gunakan bahasa yang sesuai konteks (Indonesia atau Inggris).

Contoh:
- "berapa skor madrid tadi malam" -> "Real Madrid match score results today"
- "berita terbaru indonesia" -> "berita terbaru Indonesia hari ini"
- "harga bitcoin sekarang" -> "Bitcoin price today USD"

Pertanyaan user: "{user_input}"
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip().strip('"')
        except Exception:
            # Fallback: use user input as search query
            return user_input
    
    def _web_search(self, query: str, max_results: int = 5) -> str:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            str: Formatted search results as context
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return ""
            
            # Format results as context
            context_parts = []
            for i, result in enumerate(results, 1):
                title = result.get('title', '')
                body = result.get('body', '')
                context_parts.append(f"{i}. {title}: {body}")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"⚠️ Web search error: {e}")
            return ""
    
    def get_response(self, user_input: str) -> str:
        """
        Get AI response for user input, with automatic web search when needed.
        
        Args:
            user_input: The user's message
            
        Returns:
            str: The AI's response
        """
        try:
            # Check if web search is needed
            web_context = ""
            search_used = False
            
            if self._needs_web_search(user_input):
                # Generate optimized search query
                search_query = self._generate_search_query(user_input)
                print(f"🔍 Web search: {search_query}")
                
                # Perform web search
                web_context = self._web_search(search_query)
                if web_context:
                    search_used = True
                    print(f"✅ Found web results")
            
            # Add user message to history
            self.history.append({
                "role": "user",
                "content": user_input
            })
            
            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # If web search was used, inject context
            if search_used:
                web_prompt = (
                    f"[INFO DARI INTERNET - Gunakan informasi ini untuk menjawab pertanyaan user]\n"
                    f"{web_context}\n"
                    f"[AKHIR INFO INTERNET]\n\n"
                    f"Berdasarkan informasi di atas, jawab pertanyaan user dengan singkat dan jelas. "
                    f"Sebutkan fakta-fakta penting dari hasil pencarian."
                )
                messages.append({
                    "role": "system",
                    "content": web_prompt
                })
            
            # Keep history manageable (last 10 messages)
            messages.extend(self.history[-10:])
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500  # Slightly more tokens for web-enriched answers
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add search indicator if web was used
            if search_used:
                assistant_response = f"🌐 {assistant_response}"
            
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
