"""
Speech Recognition Module
Handles converting speech to text using Google Speech Recognition
"""

import speech_recognition as sr
from config import SPEECH_LANGUAGE, SPEECH_TIMEOUT, SPEECH_PHRASE_LIMIT

# Check if PyAudio is available
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available - microphone input disabled")


class SpeechRecognizer:
    """Handles speech-to-text conversion"""

    def __init__(self):
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError("PyAudio is not available. Microphone input is disabled.")
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise on initialization
        with self.microphone as source:
            print("🎤 Menyesuaikan dengan suara sekitar...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen(self) -> str | None:
        """
        Listen for speech and convert to text.

        Returns:
            str: The recognized text, or None if nothing was recognized
        """
        with self.microphone as source:
            print("🎧 Mendengarkan...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=SPEECH_TIMEOUT,
                    phrase_time_limit=SPEECH_PHRASE_LIMIT
                )
            except sr.WaitTimeoutError:
                return None

        try:
            print("🔄 Memproses suara...")
            text = self.recognizer.recognize_google(
                audio,
                language=SPEECH_LANGUAGE
            )
            print(f"📝 Terdeteksi: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Tidak dapat mengenali suara")
            return None
        except sr.RequestError as e:
            print(f"❌ Error dari layanan: {e}")
            return None

    def calibrate(self, duration: float = 2.0):
        """Calibrate the recognizer for ambient noise"""
        with self.microphone as source:
            print(f"🔧 Kalibrasi untuk {duration} detik...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print("✅ Kalibrasi selesai")
