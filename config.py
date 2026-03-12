import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Configuration (replacing Gemini)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ElevenLabs API Configuration (for high-quality AI voice)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Telegram Allowed User IDs (comma-separated list of user IDs)
# Kosongkan untuk mengizinkan semua orang (tidak disarankan!)
# Contoh: "123456789,987654321"
_allowed_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
TELEGRAM_ALLOWED_USER_IDS = [int(uid.strip()) for uid in _allowed_ids.split(",") if uid.strip()]

# Speech Recognition Settings
SPEECH_LANGUAGE = "id-ID"  # Bahasa Indonesia
SPEECH_TIMEOUT = 5  # seconds to wait for speech
SPEECH_PHRASE_LIMIT = 10  # max seconds for a phrase

# Text-to-Speech Settings
# Options: "pyttsx3" (offline), "edge" (online free), "elevenlabs" (premium)
TTS_ENGINE = "edge"
TTS_RATE = 150  # Words per minute (pyttsx3 only)
TTS_VOLUME = 1.0  # 0.0 to 1.0 (pyttsx3 only)

# Assistant Settings
ASSISTANT_NAME = "Kaell"
WAKE_WORD = "kaell"  # Optional wake word

# Application mappings for Windows
APP_MAPPINGS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "kalkulator": "calc.exe",
    "chrome": "chrome",
    "browser": "chrome",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "cmd.exe",
    "vscode": "code",
    "visual studio code": "code",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "discord": "discord",
    # WhatsApp - menggunakan shell command untuk Windows Store app
    "whatsapp": "explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "wa": "explorer.exe shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    "telegram": "telegram",
    "steam": r"D:\steam\steam.exe",
    "sekiro": r"D:\Games\Sekiro Shadows Die Twice GOTY Edition\sekiro.exe",
    # TikTok Desktop App
    "tiktok": "explorer.exe shell:AppsFolder\\BytedancePte.Ltd.TikTok_6yccndn6064se!App",
    "tik tok": "explorer.exe shell:AppsFolder\\BytedancePte.Ltd.TikTok_6yccndn6064se!App",
    # Tambahan
    "paint": "mspaint.exe",
    "snipping tool": "snippingtool.exe",
    "settings": "ms-settings:",
    "control panel": "control.exe",
}

# Website mappings
WEBSITE_MAPPINGS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "whatsapp web": "https://web.whatsapp.com",
}

# System prompt for AI
SYSTEM_PROMPT = f"""Kamu adalah {ASSISTANT_NAME}, asisten virtual yang ramah dan membantu.
Kamu berbicara dalam Bahasa Indonesia dengan gaya yang santai tapi tetap sopan.
Jawab dengan singkat dan jelas (maksimal 2-3 kalimat) karena jawabanmu akan dibacakan dengan suara.
Jangan menggunakan format markdown, emoji, atau karakter khusus dalam jawabanmu.
Jika ditanya tentang kemampuanmu, jelaskan bahwa kamu bisa:
- Menjawab pertanyaan dan ngobrol
- Membuka aplikasi di komputer
- Membuka website
- Mengatur volume
- Mematikan atau restart komputer
- Memberitahu waktu dan tanggal
"""
