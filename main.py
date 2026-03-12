"""
Kaell Voice Assistant v2 - Simple Version
Main entry point for the voice assistant application (No AI required)
"""

import sys
from config import ASSISTANT_NAME


def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    
    try:
        import pyttsx3
    except ImportError:
        missing.append("pyttsx3")
    
    try:
        import pyaudio
    except ImportError:
        missing.append("PyAudio")
    
    if missing:
        print("❌ Dependensi berikut belum terinstall:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n💡 Jalankan: pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main function to run the voice assistant"""
    print(f"""
╔══════════════════════════════════════════╗
║   🎤 {ASSISTANT_NAME} Voice Assistant v2 🎤    ║
║        (Simple Version - No AI)          ║
╠══════════════════════════════════════════╣
║  Perintah yang tersedia:                 ║
║  • "Buka [aplikasi]" - buka aplikasi     ║
║  • "Buka [website]" - buka website       ║
║  • "Jam berapa?" - cek waktu             ║
║  • "Naikkan volume" - volume up          ║
║  • "Turunkan volume" - volume down       ║
║  • "Matikan komputer" - shutdown         ║
║  • "Keluar" / "Stop" - keluar            ║
╚══════════════════════════════════════════╝
    """)
    
    # Check dependencies first
    check_dependencies()
    
    # Import modules after dependency check
    from speech.recognizer import SpeechRecognizer
    from speech.synthesizer import SpeechSynthesizer
    from commands.system_commands import SystemCommands
    from commands.command_parser import CommandParser, get_simple_response
    
    # Initialize components
    print("🔄 Menginisialisasi komponen...")
    
    try:
        recognizer = SpeechRecognizer()
        synthesizer = SpeechSynthesizer()
        commands = SystemCommands()
        parser = CommandParser()
    except Exception as e:
        print(f"❌ Error saat inisialisasi: {e}")
        sys.exit(1)
    
    print(f"✅ {ASSISTANT_NAME} siap! Silakan bicara...\n")
    synthesizer.speak(f"Halo! Saya {ASSISTANT_NAME}. Silakan beri perintah.")
    
    # Main loop
    running = True
    while running:
        try:
            # Listen for user input
            user_input = recognizer.listen()
            
            if not user_input:
                continue
            
            user_input_lower = user_input.lower()
            
            # Check for exit commands
            if any(word in user_input_lower for word in ["keluar", "stop", "berhenti", "exit", "quit"]):
                synthesizer.speak("Sampai jumpa!")
                running = False
                continue
            
            # Parse the command
            intent = parser.parse(user_input)
            intent_type = intent.get("type", "simple_chat")
            target = intent.get("target", "")
            
            print(f"🎯 Perintah: {intent_type}, Target: {target}")
            
            # Process based on intent
            if intent_type == "open_app":
                if target:
                    success, message = commands.open_application(target)
                    synthesizer.speak(message)
                else:
                    synthesizer.speak("Aplikasi apa yang ingin dibuka?")
            
            elif intent_type == "open_website":
                if target:
                    success, message = commands.open_website(target)
                    synthesizer.speak(message)
                else:
                    synthesizer.speak("Website apa yang ingin dibuka?")
            
            elif intent_type == "time":
                time_str = commands.get_current_time()
                synthesizer.speak(time_str)
            
            elif intent_type == "date":
                date_str = commands.get_current_date()
                synthesizer.speak(date_str)
            
            # ============ Volume Commands ============
            elif intent_type == "volume_up":
                success, message = commands.volume_up()
                synthesizer.speak(message)
            
            elif intent_type == "volume_down":
                success, message = commands.volume_down()
                synthesizer.speak(message)
            
            elif intent_type == "volume_mute":
                success, message = commands.volume_mute()
                synthesizer.speak(message)
            
            elif intent_type == "volume_max":
                success, message = commands.volume_max()
                synthesizer.speak(message)
            
            # ============ Power Commands ============
            elif intent_type == "shutdown":
                synthesizer.speak("Komputer akan mati dalam 5 detik. Bilang 'batalkan shutdown' untuk membatalkan.")
                success, message = commands.shutdown(delay=5)
            
            elif intent_type == "restart":
                synthesizer.speak("Komputer akan restart dalam 5 detik. Bilang 'batalkan shutdown' untuk membatalkan.")
                success, message = commands.restart(delay=5)
            
            elif intent_type == "sleep":
                success, message = commands.sleep()
                synthesizer.speak(message)
            
            elif intent_type == "lock":
                success, message = commands.lock_screen()
                synthesizer.speak(message)
            
            elif intent_type == "cancel_shutdown":
                success, message = commands.cancel_shutdown()
                synthesizer.speak(message)
            
            else:
                # Simple response
                response = get_simple_response(user_input)
                synthesizer.speak(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            synthesizer.speak("Sampai jumpa!")
            running = False
        except Exception as e:
            print(f"❌ Error: {e}")
            synthesizer.speak("Maaf, terjadi kesalahan.")


if __name__ == "__main__":
    main()
