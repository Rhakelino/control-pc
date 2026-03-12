"""
Command Parser Module
Simple keyword-based command detection without AI
"""

import re
from config import APP_MAPPINGS, WEBSITE_MAPPINGS


class CommandParser:
    """Parse commands using keyword matching"""
    
    def __init__(self):
        self.app_keywords = list(APP_MAPPINGS.keys())
        self.website_keywords = list(WEBSITE_MAPPINGS.keys())
        
        # Patterns for different commands
        self.open_patterns = [
            r"buka\s+(.+)",
            r"bukan\s+(.+)",  # Typo handling
            r"open\s+(.+)",
            r"jalankan\s+(.+)",
            r"run\s+(.+)"
        ]
        
        self.time_keywords = ["jam berapa", "waktu", "pukul berapa", "what time"]
        self.date_keywords = ["tanggal berapa", "hari apa", "tanggal", "what date"]
        
        # Volume keywords
        self.volume_up_keywords = [
            "naikkan volume", "volume naik", "keraskan suara", "tambah volume",
            "volume up", "besarkan suara", "keras", "lebih keras"
        ]
        self.volume_down_keywords = [
            "turunkan volume", "volume turun", "kecilkan suara", "kurangi volume",
            "volume down", "pelankan suara", "pelan", "lebih pelan"
        ]
        self.volume_mute_keywords = [
            "mute", "bisukan", "diam", "matikan suara", "silent"
        ]
        self.volume_max_keywords = [
            "volume maksimal", "volume max", "volume penuh", "full volume"
        ]
        
        # Power keywords
        self.shutdown_keywords = [
            "matikan komputer", "shutdown", "matikan laptop", "matikan pc",
            "turn off", "power off"
        ]
        self.restart_keywords = [
            "restart", "restart komputer", "restart laptop", "reboot"
        ]
        self.sleep_keywords = [
            "sleep", "tidurkan komputer", "mode tidur", "hibernate"
        ]
        self.lock_keywords = [
            "kunci layar", "lock screen", "lock", "kunci komputer"
        ]
        self.cancel_shutdown_keywords = [
            "batalkan shutdown", "cancel shutdown", "jangan matikan", "batal matikan"
        ]
    
    def parse(self, text: str) -> dict:
        """
        Parse user input to determine intent.
        
        Args:
            text: User's spoken text
            
        Returns:
            dict: {"type": str, "target": str}
        """
        text_lower = text.lower().strip()
        
        # Check for time
        if any(keyword in text_lower for keyword in self.time_keywords):
            return {"type": "time", "target": None}
        
        # Check for date
        if any(keyword in text_lower for keyword in self.date_keywords):
            return {"type": "date", "target": None}
        
        # ============ Volume Commands ============
        if any(keyword in text_lower for keyword in self.volume_up_keywords):
            return {"type": "volume_up", "target": None}
        
        if any(keyword in text_lower for keyword in self.volume_down_keywords):
            return {"type": "volume_down", "target": None}
        
        if any(keyword in text_lower for keyword in self.volume_mute_keywords):
            return {"type": "volume_mute", "target": None}
        
        if any(keyword in text_lower for keyword in self.volume_max_keywords):
            return {"type": "volume_max", "target": None}
        
        # ============ Power Commands ============
        if any(keyword in text_lower for keyword in self.cancel_shutdown_keywords):
            return {"type": "cancel_shutdown", "target": None}
        
        if any(keyword in text_lower for keyword in self.shutdown_keywords):
            return {"type": "shutdown", "target": None}
        
        if any(keyword in text_lower for keyword in self.restart_keywords):
            return {"type": "restart", "target": None}
        
        if any(keyword in text_lower for keyword in self.sleep_keywords):
            return {"type": "sleep", "target": None}
        
        if any(keyword in text_lower for keyword in self.lock_keywords):
            return {"type": "lock", "target": None}
        
        # Check for open commands
        for pattern in self.open_patterns:
            match = re.search(pattern, text_lower)
            if match:
                target = match.group(1).strip()
                
                # Check if it's a website
                for website in self.website_keywords:
                    if website in target:
                        return {"type": "open_website", "target": website}
                
                # Check if it's an app
                for app in self.app_keywords:
                    if app in target:
                        return {"type": "open_app", "target": app}
                
                # Default: try to open as app
                return {"type": "open_app", "target": target}
        
        # Default: just respond with a simple message
        return {"type": "simple_chat", "target": text}


# Simple responses for common greetings
SIMPLE_RESPONSES = {
    "halo": "Halo! Ada yang bisa saya bantu?",
    "hai": "Hai! Ada yang bisa saya bantu?",
    "hi": "Hi! Ada yang bisa saya bantu?",
    "hello": "Hello! Ada yang bisa saya bantu?",
    "apa kabar": "Saya baik! Terima kasih sudah bertanya.",
    "siapa kamu": "Saya Kaell, asisten virtual Anda. Saya bisa membantu membuka aplikasi, mengatur volume, dan mematikan komputer.",
    "siapa namamu": "Nama saya Kaell, asisten virtual Anda.",
    "terima kasih": "Sama-sama!",
    "makasih": "Sama-sama!",
    "thanks": "Sama-sama!",
    "thank you": "Sama-sama!",
    "selamat pagi": "Selamat pagi juga!",
    "selamat siang": "Selamat siang juga!",
    "selamat sore": "Selamat sore juga!",
    "selamat malam": "Selamat malam juga!",
    "bisa apa": "Saya bisa membuka aplikasi, membuka website, mengatur volume, dan mematikan komputer.",
    "help": "Saya bisa membantu: buka aplikasi, buka website, naikkan volume, turunkan volume, matikan komputer, dan lainnya.",
    "bantuan": "Saya bisa membantu: buka aplikasi, buka website, naikkan volume, turunkan volume, matikan komputer, dan lainnya.",
}


def get_simple_response(text: str) -> str:
    """Get a simple response for common phrases"""
    text_lower = text.lower().strip()
    
    for keyword, response in SIMPLE_RESPONSES.items():
        if keyword in text_lower:
            return response
    
    return "Maaf, saya tidak mengerti. Coba bilang 'buka notepad', 'naikkan volume', atau 'jam berapa'."
