"""
Text-to-Speech Module
Supports: pyttsx3 (offline), edge (online free), elevenlabs (premium)
"""

import pyttsx3
import threading
import tempfile
import os
import asyncio
from config import TTS_RATE, TTS_VOLUME, TTS_ENGINE, ELEVENLABS_API_KEY

# Global lock for TTS operations
_tts_lock = threading.Lock()


class SpeechSynthesizer:
    """Handles text-to-speech conversion with multiple engine support"""
    
    def __init__(self):
        self.rate = TTS_RATE
        self.volume = TTS_VOLUME
        self.engine_type = TTS_ENGINE  # "pyttsx3", "edge", or "elevenlabs"
        
        # Edge TTS voice
        self.edge_voice = "id-ID-ArdiNeural"
        
        # ElevenLabs settings
        self.elevenlabs_client = None
        self.elevenlabs_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        # Initialize ElevenLabs if selected
        if self.engine_type == "elevenlabs":
            if ELEVENLABS_API_KEY:
                try:
                    from elevenlabs.client import ElevenLabs
                    self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                    print("✅ ElevenLabs TTS initialized")
                except Exception as e:
                    print(f"⚠️ ElevenLabs init failed: {e}")
                    self.engine_type = "pyttsx3"
            else:
                print("⚠️ No ElevenLabs API key, using pyttsx3")
                self.engine_type = "pyttsx3"
        elif self.engine_type == "edge":
            print("✅ Edge TTS initialized")
    
    def _create_pyttsx3_engine(self):
        """Create and configure a new pyttsx3 engine"""
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'indonesia' in voice.name.lower() or 'id' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        else:
            if voices:
                engine.setProperty('voice', voices[0].id)
        
        return engine
    
    def speak(self, text: str):
        """Convert text to speech and play it in a separate thread."""
        if not text:
            return
        
        print(f"🔊 Berbicara: {text}")
        
        thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
        thread.start()
    
    def _speak_sync(self, text: str):
        """Synchronous speak function"""
        with _tts_lock:
            try:
                if self.engine_type == "elevenlabs" and self.elevenlabs_client:
                    self._speak_elevenlabs(text)
                elif self.engine_type == "edge":
                    self._speak_edge(text)
                else:
                    self._speak_pyttsx3(text)
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
    
    def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3 (offline)"""
        try:
            engine = self._create_pyttsx3_engine()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            del engine
        except Exception as e:
            print(f"⚠️ pyttsx3 error: {e}")
    
    def _speak_elevenlabs(self, text: str):
        """Speak using ElevenLabs API"""
        try:
            # Try pygame first, fall back to winsound on Windows
            audio_played = False
            
            # Generate audio
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                voice_id=self.elevenlabs_voice_id,
                text=text,
                model_id="eleven_multilingual_v2"
            )

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                for chunk in audio_generator:
                    f.write(chunk)
                temp_path = f.name

            # Try to play with pygame
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                pygame.mixer.music.unload()
                audio_played = True
            except ImportError:
                pass  # pygame not available
            
            if not audio_played:
                # Fall back to winsound on Windows
                try:
                    import winsound
                    winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    audio_played = True
                except ImportError:
                    pass  # Not on Windows

            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass

        except Exception as e:
            print(f"⚠️ ElevenLabs error: {e}, falling back to pyttsx3")
            self._speak_pyttsx3(text)
    
    def _speak_edge(self, text: str):
        """Speak using Edge TTS (free)"""
        try:
            import edge_tts
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_path = f.name

            async def generate():
                communicate = edge_tts.Communicate(text, self.edge_voice)
                await communicate.save(temp_path)

            loop.run_until_complete(generate())
            loop.close()

            # Try to play with pygame
            audio_played = False
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                pygame.mixer.music.unload()
                audio_played = True
            except ImportError:
                pass  # pygame not available
            
            if not audio_played:
                # Fall back to winsound on Windows
                try:
                    import winsound
                    winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    audio_played = True
                except ImportError:
                    pass  # Not on Windows

            try:
                os.unlink(temp_path)
            except:
                pass

        except Exception as e:
            print(f"⚠️ Edge TTS error: {e}, falling back to pyttsx3")
            self._speak_pyttsx3(text)
    
    def set_voice(self, voice_name: str):
        """Set voice for the current engine"""
        if self.engine_type == "edge":
            self.edge_voice = voice_name
        elif self.engine_type == "elevenlabs":
            self.elevenlabs_voice_id = voice_name
    
    def speak_and_wait(self, text: str):
        """Convert text to speech and wait for it to finish."""
        if not text:
            return
        print(f"🔊 Berbicara: {text}")
        self._speak_sync(text)
    
    def set_rate(self, rate: int):
        self.rate = rate
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
    
    def get_available_voices(self) -> list:
        if self.engine_type == "elevenlabs":
            return ["Rachel", "Domi", "Bella", "Antoni", "Josh", "Adam", "Sam"]
        elif self.engine_type == "edge":
            return ["id-ID-ArdiNeural", "id-ID-GadisNeural", "en-US-JennyNeural"]
        return []
