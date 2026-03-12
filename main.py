"""
Kaell Assistant v2 - Simple Version
Main entry point for the assistant application (No AI required)
"""

import sys
from config import ASSISTANT_NAME


def main():
    """Main function to run the assistant"""
    print(f"""
╔══════════════════════════════════════════╗
║   🤖 {ASSISTANT_NAME} Assistant v2 🤖        ║
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
    
    # Import modules
    from commands.system_commands import SystemCommands
    from commands.command_parser import CommandParser, get_simple_response
    
    # Initialize components
    print("🔄 Menginisialisasi komponen...")
    
    try:
        commands = SystemCommands()
        parser = CommandParser()
    except Exception as e:
        print(f"❌ Error saat inisialisasi: {e}")
        sys.exit(1)
    
    print(f"✅ {ASSISTANT_NAME} siap! Silakan ketik perintah...\n")
    
    # Main loop
    running = True
    while running:
        try:
            # Get user input from keyboard
            user_input = input(">> ").strip()
            
            if not user_input:
                continue
            
            user_input_lower = user_input.lower()
            
            # Check for exit commands
            if any(word in user_input_lower for word in ["keluar", "stop", "berhenti", "exit", "quit"]):
                print("👋 Sampai jumpa!")
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
                    print(message)
                else:
                    print("Aplikasi apa yang ingin dibuka?")
            
            elif intent_type == "open_website":
                if target:
                    success, message = commands.open_website(target)
                    print(message)
                else:
                    print("Website apa yang ingin dibuka?")
            
            elif intent_type == "time":
                time_str = commands.get_current_time()
                print(time_str)
            
            elif intent_type == "date":
                date_str = commands.get_current_date()
                print(date_str)
            
            # ============ Volume Commands ============
            elif intent_type == "volume_up":
                success, message = commands.volume_up()
                print(message)
            
            elif intent_type == "volume_down":
                success, message = commands.volume_down()
                print(message)
            
            elif intent_type == "volume_mute":
                success, message = commands.volume_mute()
                print(message)
            
            elif intent_type == "volume_max":
                success, message = commands.volume_max()
                print(message)
            
            # ============ Power Commands ============
            elif intent_type == "shutdown":
                print("Komputer akan mati dalam 5 detik. Ketik 'batalkan shutdown' untuk membatalkan.")
                success, message = commands.shutdown(delay=5)
            
            elif intent_type == "restart":
                print("Komputer akan restart dalam 5 detik. Ketik 'batalkan shutdown' untuk membatalkan.")
                success, message = commands.restart(delay=5)
            
            elif intent_type == "sleep":
                success, message = commands.sleep()
                print(message)
            
            elif intent_type == "lock":
                success, message = commands.lock_screen()
                print(message)
            
            elif intent_type == "cancel_shutdown":
                success, message = commands.cancel_shutdown()
                print(message)
            
            else:
                # Simple response
                response = get_simple_response(user_input)
                print(response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            running = False
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
