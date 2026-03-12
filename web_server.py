"""
Web Server Module
Flask server for remote control from phone with HTTPS and AI support
Supports React Native mobile app connection
"""

import socket
import os
import base64
import tempfile
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from commands.system_commands import SystemCommands
from commands.command_parser import get_simple_response
from speech.synthesizer import SpeechSynthesizer
from config import GROQ_API_KEY
import psutil

# Import Bardi IoT Controller
try:
    from bardi_controller import get_bardi_controller, get_safe_shutdown
    BARDI_AVAILABLE = True
except ImportError:
    BARDI_AVAILABLE = False
    print("⚠️ Bardi Controller not available - run: pip install tinytuya")

# Try to import cv2 for webcam capture
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available - Kaell Eye disabled")

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # Enable CORS for React Native
commands = SystemCommands()
synthesizer = None
ai_chat = None  # Will be initialized if API key is available


def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def init_ai():
    """Initialize AI chat if API key is available"""
    global ai_chat
    if GROQ_API_KEY and ai_chat is None:
        try:
            from ai.groq_chat import GroqChat
            ai_chat = GroqChat()
            print("✅ Groq AI initialized")
        except Exception as e:
            print(f"⚠️ AI not available: {e}")
            ai_chat = None


@app.route('/')
def index():
    """Serve the main control page"""
    return render_template('index.html')


@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a command from the web interface"""
    global synthesizer, ai_chat
    
    data = request.json
    command_text = data.get('command', '').strip()
    speak = data.get('speak', True)
    
    if not command_text:
        return jsonify({'success': False, 'message': 'No command provided'})
    
    result = {'success': True, 'message': '', 'intent': 'chat'}
    
    # Use AI to analyze intent if available
    if ai_chat:
        try:
            intent = ai_chat.analyze_intent(command_text)
            intent_type = intent.get('type', 'chat')
            target = intent.get('target', '')
        except Exception as e:
            print(f"⚠️ AI intent error: {e}")
            intent_type = 'chat'
            target = ''
    else:
        # Use simple keyword parser
        from commands.command_parser import CommandParser
        parser = CommandParser()
        intent = parser.parse(command_text)
        intent_type = intent.get('type', 'simple_chat')
        target = intent.get('target', '')
    
    result['intent'] = intent_type
    
    # Process based on intent
    if intent_type == "open_app":
        if target:
            success, message = commands.open_application(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Aplikasi apa yang ingin dibuka?"
    
    elif intent_type == "close_app":
        if target:
            success, message = commands.close_application(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Aplikasi apa yang ingin ditutup?"
    
    elif intent_type == "open_website":
        if target:
            success, message = commands.open_website(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Website apa yang ingin dibuka?"
    
    elif intent_type == "close_tab":
        success, message = commands.close_browser_tab()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "close_all_tabs":
        success, message = commands.close_all_browser_tabs()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "time":
        result['message'] = commands.get_current_time()
    
    elif intent_type == "date":
        result['message'] = commands.get_current_date()
    
    elif intent_type == "volume_up":
        success, message = commands.volume_up()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "volume_down":
        success, message = commands.volume_down()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "volume_mute":
        success, message = commands.volume_mute()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "volume_max":
        success, message = commands.volume_max()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "shutdown":
        success, message = commands.shutdown(delay=10)
        result['success'] = success
        result['message'] = "Komputer akan mati dalam 10 detik. Bilang batalkan shutdown untuk membatalkan."
    
    elif intent_type == "restart":
        success, message = commands.restart(delay=10)
        result['success'] = success
        result['message'] = "Komputer akan restart dalam 10 detik."
    
    elif intent_type == "sleep":
        success, message = commands.sleep()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "lock":
        success, message = commands.lock_screen()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "cancel_shutdown":
        success, message = commands.cancel_shutdown()
        result['success'] = success
        result['message'] = message
    
    elif intent_type == "play_youtube":
        if target:
            success, message = commands.play_youtube(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Apa yang ingin diputar di YouTube?"
    
    elif intent_type == "search_youtube":
        if target:
            success, message = commands.search_youtube(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Apa yang ingin dicari di YouTube?"
    
    elif intent_type == "search_google":
        if target:
            success, message = commands.search_google(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "Apa yang ingin dicari di Google?"
    
    elif intent_type == "open_url":
        if target:
            success, message = commands.open_url(target)
            result['success'] = success
            result['message'] = message
        else:
            result['message'] = "URL apa yang ingin dibuka?"
    
    else:
        # Use AI for chat response if available
        if ai_chat:
            try:
                result['message'] = ai_chat.get_response(command_text)
                result['is_ai_chat'] = True  # Mark as AI chat response
            except Exception as e:
                print(f"⚠️ AI chat error: {e}")
                result['message'] = get_simple_response(command_text)
                result['is_ai_chat'] = True
        else:
            result['message'] = get_simple_response(command_text)
            result['is_ai_chat'] = True
    
    # Speak the response ONLY for AI chat responses (not for commands like volume, open app, etc.)
    is_ai_chat = result.get('is_ai_chat', False)
    if speak and result['message'] and is_ai_chat:
        try:
            if synthesizer is None:
                synthesizer = SpeechSynthesizer()
            synthesizer.speak(result['message'])
        except Exception as e:
            print(f"TTS Error: {e}")
    
    return jsonify(result)


@app.route('/api/quick/<action>', methods=['POST'])
def quick_action(action):
    """Quick action buttons"""
    global synthesizer
    
    actions = {
        'volume_up': commands.volume_up,
        'volume_down': commands.volume_down,
        'volume_mute': commands.volume_mute,
        'volume_max': commands.volume_max,
        'shutdown': lambda: commands.shutdown(delay=10),
        'restart': lambda: commands.restart(delay=10),
        'sleep': commands.sleep,
        'lock': commands.lock_screen,
        'cancel_shutdown': commands.cancel_shutdown,
    }
    
    if action in actions:
        success, message = actions[action]()
        # TTS disabled for quick actions (volume, power controls)
        # Only AI chat responses will use TTS
        
        return jsonify({'success': success, 'message': message})
    
    return jsonify({'success': False, 'message': 'Unknown action'})


@app.route('/api/stats', methods=['GET'])
def system_stats():
    """Get system stats for React Native app"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.5)
        
        # RAM usage
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        
        # Battery info
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = battery.percent
            is_charging = battery.power_plugged
        else:
            battery_percent = 0
            is_charging = False
        
        return jsonify({
            'success': True,
            'cpu': cpu_percent,
            'ram': ram_percent,
            'battery': battery_percent,
            'charging': is_charging,
            'server': 'KAELL SYSTEM'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'cpu': 0,
            'ram': 0,
            'battery': 0,
            'charging': False
        })


@app.route('/api/kaell-eye', methods=['POST', 'GET'])
def kaell_eye():
    """Capture photo from webcam for React Native app"""
    if not CV2_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'OpenCV not installed. Run: pip install opencv-python'
        })
    
    try:
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return jsonify({
                'success': False,
                'message': 'Webcam tidak tersedia atau sedang digunakan'
            })
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Warm up camera - let auto-exposure adjust
        import time
        for _ in range(30):
            cap.read()
        time.sleep(1.0)
        
        # Capture frame
        for _ in range(10):
            ret, frame = cap.read()
        
        cap.release()
        
        if ret and frame is not None:
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_path = temp_file.name
            temp_file.close()
            
            cv2.imwrite(temp_path, frame)
            
            # Read and encode as base64
            with open(temp_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Cleanup
            try:
                os.remove(temp_path)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': 'Foto berhasil diambil',
                'image': f'data:image/jpeg;base64,{image_data}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Gagal mengambil foto dari webcam'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


# ============= BARDI IoT ENDPOINTS =============

@app.route('/device/bardi/on', methods=['POST'])
def bardi_on():
    """Menyalakan aliran listrik"""
    if not BARDI_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Bardi Controller tidak tersedia'
        })
    
    bardi = get_bardi_controller()
    if not bardi:
        return jsonify({
            'success': False,
            'message': 'Gagal menginisialisasi Bardi Controller'
        })
    
    success, message = bardi.turn_on()
    return jsonify({'success': success, 'message': message})


@app.route('/device/bardi/off', methods=['POST'])
def bardi_off():
    """Mematikan aliran listrik"""
    if not BARDI_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'Bardi Controller tidak tersedia'
        })
    
    bardi = get_bardi_controller()
    if not bardi:
        return jsonify({
            'success': False,
            'message': 'Gagal menginisialisasi Bardi Controller'
        })
    
    success, message = bardi.turn_off()
    return jsonify({'success': success, 'message': message})


def run_server(host='0.0.0.0', port=5000, use_https=False):
    """Run the Flask server with HTTPS support"""
    local_ip = get_local_ip()
    
    # Initialize AI
    init_ai()
    
    # Generate SSL certificate if needed
    cert_file = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_file = os.path.join(os.path.dirname(__file__), 'key.pem')
    
    if use_https:
        if not os.path.exists(cert_file) or not os.path.exists(key_file):
            print("🔐 Generating SSL certificate...")
            from generate_ssl import generate_ssl_certificate
            generate_ssl_certificate(os.path.dirname(__file__) or ".")
        
        protocol = "https"
        ssl_context = (cert_file, key_file)
    else:
        protocol = "http"
        ssl_context = None
    
    ai_status = "✅ Groq AI Active" if ai_chat else "⚠️ AI Disabled (no API key)"
    
    print(f"""
╔══════════════════════════════════════════════════════╗
║        🌐 Kaell Web Server Started! 🌐               ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Buka di HP Anda:                                    ║
║  👉 {protocol}://{local_ip}:{port}                      ║
║                                                      ║
║  {ai_status}                          ║
║                                                      ║
║  ⚠️  Jika muncul peringatan "Not Secure":            ║
║      Klik "Advanced" → "Proceed anyway"              ║
║                                                      ║
║  Tekan Ctrl+C untuk stop server                      ║
╚══════════════════════════════════════════════════════╝
    """)
    
    if use_https:
        app.run(host=host, port=port, debug=False, threaded=True, ssl_context=ssl_context)
    else:
        app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    # Use HTTP for React Native compatibility
    # Change to use_https=True if you need HTTPS for browser access
    run_server(use_https=False)
