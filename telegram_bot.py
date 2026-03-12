"""
Telegram Bot Module
Control Kaell Assistant via Telegram from anywhere
"""

import asyncio
import os
import cv2
import tempfile
import psutil

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️ GPUtil not installed, GPU monitoring disabled")

from PIL import ImageGrab
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from commands.system_commands import SystemCommands
from commands.command_parser import CommandParser, get_simple_response
from config import TELEGRAM_BOT_TOKEN, GROQ_API_KEY, TELEGRAM_ALLOWED_USER_IDS

# Initialize components
commands = SystemCommands()
parser = CommandParser()
ai_chat = None

# Power Guardian State
last_power_plugged = None  # Track charger status for alerts
battery_100_alerted = False  # Prevent spam when battery full

# System Health Guardian State
last_cpu_alert_time = 0  # Prevent alert spam (timestamp)
last_ram_alert_time = 0  # Prevent alert spam
last_disk_alert_time = 0  # Prevent alert spam
ALERT_COOLDOWN = 300  # 5 minutes between same alerts
last_daily_report_date = None  # Track last daily report

# Remote File Explorer Configuration
# Default folder saat pertama kali (bisa diubah dengan /cd)
DEFAULT_EXPLORER_DIR = os.path.expanduser("~/Documents")

# Menyimpan current directory per user (user_id -> path)
user_current_dir = {}

# Folder yang dilarang diakses (keamanan)
BLOCKED_DIRS = [
    "C:/Windows",
    "C:/Program Files",
    "C:/Program Files (x86)",
    "C:/ProgramData",
    os.path.expanduser("~/AppData"),
]

# Try to initialize AI
if GROQ_API_KEY:
    try:
        from ai.groq_chat import GroqChat
        ai_chat = GroqChat()
        print("✅ Groq AI initialized for Telegram")
    except Exception as e:
        print(f"⚠️ AI not available: {e}")


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized to use the bot"""
    # Jika list kosong, izinkan semua (backward compatibility)
    if not TELEGRAM_ALLOWED_USER_IDS:
        return True
    return user_id in TELEGRAM_ALLOWED_USER_IDS


async def unauthorized_response(update: Update) -> None:
    """Send response to unauthorized users"""
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🚫 *Akses Ditolak*\n\n"
        f"Maaf, Anda tidak memiliki izin untuk menggunakan bot ini.\n\n"
        f"User ID Anda: `{user_id}`\n\n"
        f"Hubungi admin untuk mendapatkan akses.",
        parse_mode="Markdown"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    keyboard = [
        # Volume Controls
        [
            InlineKeyboardButton("🔊 Vol+", callback_data="volume_up"),
            InlineKeyboardButton("🔉 Vol-", callback_data="volume_down"),
            InlineKeyboardButton("🔇 Mute", callback_data="volume_mute"),
            InlineKeyboardButton("🔊 Max", callback_data="volume_max"),
        ],
        # Power Controls
        [
            InlineKeyboardButton("🔒 Lock", callback_data="lock"),
            InlineKeyboardButton("😴 Sleep", callback_data="sleep"),
            InlineKeyboardButton("🔄 Restart", callback_data="restart"),
        ],
        [
            InlineKeyboardButton("⏻ Shutdown", callback_data="shutdown"),
            InlineKeyboardButton("❌ Batalkan", callback_data="cancel_shutdown"),
        ],
        # File & Voice & Cam
        [
            InlineKeyboardButton("📂 File", callback_data="file_ls"),
            InlineKeyboardButton("👁️ Eye", callback_data="kaell_eye"),
            InlineKeyboardButton("📸 Shot", callback_data="screenshot"),
        ],
        # Info
        [
            InlineKeyboardButton("📊 Status", callback_data="status"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *KAELL ASSISTANT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        "📱 *Aplikasi:* `buka/tutup [nama]`\n"
        "🌐 *Website:* `buka youtube/google`\n"
        "🎵 *Musik:* `putar lagu [judul]`\n"
        "🔍 *Cari:* `cari [keyword]`\n"
        "🕐 *Waktu:* `jam/tanggal berapa?`\n"
        "💬 *AI Chat:* ketik apa saja!\n\n"
        
        "📂 *FILE:* `/cd` `/ls` `/ambil`\n"
        "📸 *CAM:* `/foto` `/ss`\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *QUICK ACTIONS:*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return

    await update.message.reply_text(
        "📚 *Panduan Kaell Assistant*\n\n"
        "*Perintah Suara/Teks:*\n"
        "• `buka [aplikasi]` - buka aplikasi\n"
        "• `buka [website]` - buka website\n"
        "• `cari [query] di youtube` - cari video\n"
        "• `putar [lagu]` - putar musik\n"
        "• `jam berapa?` - waktu sekarang\n"
        "• `tanggal berapa?` - tanggal hari ini\n\n"
        "*Kontrol Volume:*\n"
        "• `naikkan volume` / `keraskan`\n"
        "• `turunkan volume` / `kecilkan`\n"
        "• `mute` / `bisukan`\n\n"
        "*Kontrol Power:*\n"
        "• `matikan komputer` - shutdown\n"
        "• `restart komputer`\n"
        "• `sleep` / `tidurkan`\n"
        "• `kunci layar`\n\n"
        "*Slash Commands:*\n"
        "/start - Menu utama\n"
        "/help - Panduan ini\n"
        "/info - Info lengkap\n"
        "/status - Status sistem\n\n"
        "*File Explorer:*\n"
        "/cd [path] - Pindah direktori\n"
        "/pwd - Lihat direktori saat ini\n"
        "/ls [path] - List files/folders\n"
        "/ambil [file] - Ambil file\n\n"
        "*Camera & Screen:*\n"
        "/foto - Ambil foto webcam\n"
        "/ss - Screenshot layar\n\n"
        "*📊 Auto Monitoring:*\n"
        "_Bot otomatis mengirim alert:_\n"
        "• 🌅 Daily report (7 pagi)\n"
        "• 🔴 CPU >80%\n"
        "• 🔴 RAM >80%\n"
        "• 🔴 Disk >90%",
        parse_mode="Markdown"
    )


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - complete list of features"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    await update.message.reply_text(
        "🤖 *KAELL VOICE ASSISTANT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        "📱 *BUKA APLIKASI*\n"
        "• Notepad, Calculator, Chrome\n"
        "• Spotify, Discord, VSCode\n"
        "• Word, Excel, PowerPoint\n"
        "• WhatsApp, Telegram, Steam\n"
        "• File Explorer, Settings\n"
        "_Contoh: \"buka notepad\"_\n\n"
        
        "🌐 *BUKA WEBSITE*\n"
        "• YouTube, Google, Facebook\n"
        "• Instagram, Twitter, GitHub\n"
        "• Gmail, WhatsApp Web\n"
        "_Contoh: \"buka youtube\"_\n\n"
        
        "❌ *TUTUP APLIKASI*\n"
        "• Tutup aplikasi apapun\n"
        "• Tutup tab browser\n"
        "• Tutup semua tab\n"
        "_Contoh: \"tutup chrome\"_\n\n"
        
        "🎵 *YOUTUBE*\n"
        "• Putar lagu langsung\n"
        "• Cari video\n"
        "_Contoh: \"putar lagu Coldplay\"_\n\n"
        
        "🔍 *PENCARIAN*\n"
        "• Cari di Google\n"
        "• Cari di YouTube\n"
        "_Contoh: \"cari resep nasi goreng\"_\n\n"
        
        "🔊 *KONTROL VOLUME*\n"
        "• Naikkan volume\n"
        "• Turunkan volume\n"
        "• Mute / Bisukan\n"
        "• Volume maksimal\n"
        "_Contoh: \"keraskan volume\"_\n\n"
        
        "⏻ *KONTROL POWER*\n"
        "• Shutdown (30 detik delay)\n"
        "• Restart komputer\n"
        "• Sleep mode\n"
        "• Kunci layar\n"
        "• Batalkan shutdown\n"
        "_Contoh: \"matikan komputer\"_\n\n"
        
        "🕐 *WAKTU & TANGGAL*\n"
        "• Jam berapa sekarang?\n"
        "• Tanggal berapa hari ini?\n\n"
        
        "💬 *AI CHAT*\n"
        "• Tanya apa saja!\n"
        "• Powered by Groq AI\n"
        "_Contoh: \"siapa presiden Indonesia?\"_\n\n"
        
        "📂 *FILE EXPLORER*\n"
        "• `/ls` - List files/folders\n"
        "• `/ls [path]` - List files/folders in path\n"
        "• `/ambil [filename]` - Get file\n\n"
        "📸 *CAMERA & SCREEN*\n"
        "• `/foto` - Ambil foto webcam\n"
        "• `/ss` - Screenshot layar pc\n\n"
        "📊 *AUTO MONITORING (Active 24/7)*\n"
        "• 🌅 Daily System Report (7 pagi)\n"
        "• 🔴 Alert saat CPU >80%\n"
        "• 🔴 Alert saat RAM >80%\n"
        "• 🔴 Alert saat Disk >90%\n"
        "• 🔋 Battery monitoring & alerts\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎤 Kirim pesan untuk mulai!",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - Enhanced System Health Report"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    time_str = commands.get_current_time()
    date_str = commands.get_current_date()
    ai_status = "✅ Active" if ai_chat else "❌ Disabled"
    
    # === Battery Info ===
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        power_status = "⚡ Charging" if battery.power_plugged else "🔋 Discharging"
        if battery.secsleft > 0 and not battery.power_plugged:
            mins_left = battery.secsleft // 60
            hrs = mins_left // 60
            mins = mins_left % 60
            time_remaining = f" ({hrs}h {mins}m left)"
        else:
            time_remaining = ""
        battery_info = f"🔋 Baterai: `{battery_percent}%` {power_status}{time_remaining}"
    else:
        battery_info = "🔋 Baterai: `N/A (Desktop)`"
    
    # === CPU Info ===
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    
    # === RAM Info ===
    ram = psutil.virtual_memory()
    ram_used_gb = ram.used / (1024**3)
    ram_total_gb = ram.total / (1024**3)
    
    # === Disk Info ===
    disk = psutil.disk_usage('C:/')
    disk_used_gb = disk.used / (1024**3)
    disk_total_gb = disk.total / (1024**3)
    
    # === GPU Info ===
    gpu_info = ""
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                for i, gpu in enumerate(gpus):
                    gpu_info += f"🎮 GPU{i}: `{gpu.name[:20]}` | Temp: `{gpu.temperature}°C` | Load: `{gpu.load*100:.0f}%`\n"
            else:
                gpu_info = "🎮 GPU: `Integrated/Not detected`\n"
        except Exception:
            gpu_info = "🎮 GPU: `Unable to read`\n"
    else:
        gpu_info = "🎮 GPU: `GPUtil not installed`\n"
    
    # === System Health Assessment ===
    health_issues = []
    if battery and battery.percent <= 20 and not battery.power_plugged:
        health_issues.append("⚠️ Baterai rendah!")
    if cpu_percent > 80:
        health_issues.append("⚠️ CPU load tinggi!")
    if ram.percent > 85:
        health_issues.append("⚠️ RAM hampir penuh!")
    if disk.percent > 90:
        health_issues.append("⚠️ Disk hampir penuh!")
    
    if health_issues:
        health_status = "\n".join(health_issues)
    else:
        health_status = "✅ Sistem berjalan optimal!"
    
    await update.message.reply_text(
        f"🛡️ *KAELL SYSTEM REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🕐 Waktu: `{time_str}`\n"
        f"📅 Tanggal: `{date_str}`\n"
        f"🤖 AI: {ai_status}\n\n"
        
        f"⚡ *POWER STATUS*\n"
        f"{battery_info}\n\n"
        
        f"🖥️ *HARDWARE HEALTH*\n"
        f"🚀 CPU: `{cpu_percent}%` ({cpu_count} cores)\n"
        f"🧠 RAM: `{ram.percent}%` ({ram_used_gb:.1f}/{ram_total_gb:.1f} GB)\n"
        f"💾 Disk C: `{disk.percent}%` ({disk_used_gb:.0f}/{disk_total_gb:.0f} GB)\n"
        f"{gpu_info}\n"
        
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{health_status}",
        parse_mode="Markdown"
    )

def get_user_dir(user_id: int) -> str:
    """Get current directory for a user"""
    return user_current_dir.get(user_id, DEFAULT_EXPLORER_DIR)


def is_path_blocked(path: str) -> bool:
    """Check if path is in blocked directories"""
    abs_path = os.path.abspath(path).replace("\\", "/")
    for blocked in BLOCKED_DIRS:
        blocked_abs = os.path.abspath(blocked).replace("\\", "/")
        if abs_path.startswith(blocked_abs):
            return True
    return False


async def cd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cd command - Change directory"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    user_id = update.effective_user.id
    
    if not context.args:
        # Show current directory
        current = get_user_dir(user_id)
        await update.message.reply_text(
            f"📍 *Direktori saat ini:*\n`{current}`\n\n"
            "💡 *Cara pakai:*\n"
            "• `/cd D:/` - pindah ke drive D\n"
            "• `/cd ..` - naik satu level\n"
            "• `/cd subfolder` - masuk subfolder\n"
            "• `/cd ~` - kembali ke Documents",
            parse_mode="Markdown"
        )
        return
    
    target = " ".join(context.args)
    current = get_user_dir(user_id)
    
    # Handle special cases
    if target == "~":
        new_path = DEFAULT_EXPLORER_DIR
    elif target == "..":
        new_path = os.path.dirname(current)
    elif os.path.isabs(target):
        # Absolute path (e.g., D:/ or C:/Users)
        new_path = target
    else:
        # Relative path
        new_path = os.path.join(current, target)
    
    new_path = os.path.abspath(new_path)
    
    # Security check
    if is_path_blocked(new_path):
        await update.message.reply_text(
            "🚫 *Akses ditolak!*\n\n"
            "Folder sistem tidak dapat diakses untuk keamanan.",
            parse_mode="Markdown"
        )
        return
    
    if not os.path.exists(new_path):
        await update.message.reply_text(f"❌ Direktori tidak ditemukan: `{target}`", parse_mode="Markdown")
        return
    
    if not os.path.isdir(new_path):
        await update.message.reply_text(f"❌ `{target}` bukan direktori.", parse_mode="Markdown")
        return
    
    # Update user's current directory
    user_current_dir[user_id] = new_path
    
    await update.message.reply_text(
        f"✅ Pindah ke:\n`{new_path}`\n\n"
        "💡 Ketik `/ls` untuk melihat isi folder.",
        parse_mode="Markdown"
    )


async def pwd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pwd command - Print working directory"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    current = get_user_dir(update.effective_user.id)
    await update.message.reply_text(f"📍 Direktori saat ini:\n`{current}`", parse_mode="Markdown")





async def foto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /foto command - Kaell Eye webcam capture"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    status_msg = await update.message.reply_text("📸 Membuka mata Kaell...")
    
    try:
        # Run webcam capture in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, capture_webcam_photo)
        
        if result:
            temp_path, success = result
            if success and temp_path:
                with open(temp_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption="👁️ Ini yang Kaell lihat sekarang, Bos!"
                    )
                # Cleanup
                try:
                    os.remove(temp_path)
                except:
                    pass
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Gagal mengambil foto. Webcam mungkin sedang digunakan.")
        else:
            await status_msg.edit_text("❌ Webcam tidak tersedia.")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: `{e}`", parse_mode="Markdown")


async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ss command - Screenshot capture"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    status_msg = await update.message.reply_text("📸 Mengambil screenshot...")
    
    try:
        # Run screenshot capture in a thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, capture_screenshot)
        
        if result:
            temp_path, success = result
            if success and temp_path:
                with open(temp_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption="🖥️ Screenshot layar laptop saat ini, Bos!"
                    )
                # Cleanup
                try:
                    os.remove(temp_path)
                except:
                    pass
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ Gagal mengambil screenshot.")
        else:
            await status_msg.edit_text("❌ Gagal mengambil screenshot.")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: `{e}`", parse_mode="Markdown")

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /refresh command - Restart bot to clear RAM"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    await update.message.reply_text(
        "🔃 *Refresh Bot*\n\n"
        "Kaell pamit sebentar untuk membersihkan RAM...\n"
        "Bot akan kembali dalam hitungan detik!",
        parse_mode="Markdown"
    )
    
    # Give time for message to be sent
    await asyncio.sleep(1)
    
    # Exit - will be restarted by batch file
    os._exit(0)


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /task command - List running processes like task manager"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    # Check sort parameter
    sort_by = "memory"
    if context.args and context.args[0].lower() in ["cpu", "ram", "memory"]:
        sort_by = "cpu" if context.args[0].lower() == "cpu" else "memory"
    
    status_msg = await update.message.reply_text("⏳ Mengambil daftar proses...")
    
    try:
        processes = commands.list_processes(sort_by=sort_by, limit=25)
        
        if not processes:
            await status_msg.edit_text("❌ Tidak ada proses yang ditemukan.")
            return
        
        # Calculate total memory
        total_mem = sum(p['memory_mb'] for p in processes)
        
        sort_label = "RAM" if sort_by == "memory" else "CPU"
        response = f"📊 *TASK MANAGER* (sort: {sort_label})\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, proc in enumerate(processes, 1):
            # Truncate long names
            name = proc['name'][:20]
            mem = proc['memory_mb']
            
            # Size indicator
            if mem > 500:
                icon = "🔴"
            elif mem > 100:
                icon = "🟡"
            else:
                icon = "🟢"
            
            response += f"{icon} `{name}` — `{mem}MB` | PID: `{proc['pid']}`\n"
        
        response += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        response += f"📦 Total RAM (top {len(processes)}): `{total_mem:.0f} MB`\n\n"
        response += f"💡 *Tips:*\n"
        response += f"• `/task cpu` — sort by CPU\n"
        response += f"• `/kill [PID]` — matikan proses\n"
        
        await status_msg.edit_text(response, parse_mode="Markdown")
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: `{e}`", parse_mode="Markdown")


async def kill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /kill command - Kill a process by PID"""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    if not context.args:
        await update.message.reply_text(
            "💀 *Kill Process*\n\n"
            "Gunakan: `/kill [PID]`\n"
            "Contoh: `/kill 1234`\n\n"
            "💡 Gunakan `/task` untuk melihat daftar PID.",
            parse_mode="Markdown"
        )
        return
    
    try:
        pid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ PID harus berupa angka. Contoh: `/kill 1234`", parse_mode="Markdown")
        return
    
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()
        
        # Wait a moment for graceful termination
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()  # Force kill if not terminated
        
        await update.message.reply_text(
            f"✅ Proses `{proc_name}` (PID: `{pid}`) berhasil dimatikan.",
            parse_mode="Markdown"
        )
    except psutil.NoSuchProcess:
        await update.message.reply_text(f"❌ Proses dengan PID `{pid}` tidak ditemukan.", parse_mode="Markdown")
    except psutil.AccessDenied:
        await update.message.reply_text(f"🚫 Akses ditolak untuk PID `{pid}`. Proses sistem tidak bisa dimatikan.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mematikan proses: `{e}`", parse_mode="Markdown")


def capture_webcam_photo():
    """Capture a photo from webcam (runs in thread)"""
    try:
        # Initialize camera (0 is default webcam)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None
        
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        import time
        
        # Warm up camera - read multiple frames to let auto-exposure adjust
        # This is crucial for getting proper brightness
        for _ in range(30):  # Read 30 frames (~1 second at 30fps)
            cap.read()
        
        # Additional delay for exposure adjustment
        time.sleep(1.5)
        
        # Read a few more frames to ensure stability
        for _ in range(10):
            ret, frame = cap.read()
        
        cap.release()
        
        if ret and frame is not None:
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_path = temp_file.name
            temp_file.close()
            
            cv2.imwrite(temp_path, frame)
            return (temp_path, True)
        else:
            return (None, False)
            
    except Exception as e:
        print(f"Webcam error: {e}")
        return None


def capture_screenshot():
    """Capture a screenshot (runs in thread)"""
    try:
        # Capture screen
        screenshot = ImageGrab.grab()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_path = temp_file.name
        temp_file.close()
        
        screenshot.save(temp_path)
        return (temp_path, True)
            
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


async def list_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ls command to list files in the current directory."""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return

    user_id = update.effective_user.id
    base_dir = get_user_dir(user_id)
    
    if context.args:
        # Allow specifying a subdirectory
        target = " ".join(context.args)
        if os.path.isabs(target):
            current_dir = os.path.abspath(target)
        else:
            current_dir = os.path.abspath(os.path.join(base_dir, target))
    else:
        current_dir = os.path.abspath(base_dir)
    
    # Security check
    if is_path_blocked(current_dir):
        await update.message.reply_text("🚫 Akses ditolak: Folder sistem tidak dapat diakses.")
        return

    if not os.path.isdir(current_dir):
        await update.message.reply_text(f"❌ Direktori tidak ditemukan: `{current_dir}`", parse_mode="Markdown")
        return

    try:
        files = os.listdir(current_dir)
        if not files:
            await update.message.reply_text(f"📂 Direktori kosong:\n`{current_dir}`", parse_mode="Markdown")
            return

        # Separate dirs and files
        dirs = []
        file_list = []
        for item in sorted(files, key=str.lower):
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                file_list.append(item)
        
        response_text = f"� `{current_dir}`\n"
        response_text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for d in dirs:
            response_text += f"📁 `{d}/`\n"
        for f in file_list:
            response_text += f"📄 `{f}`\n"
        
        response_text += f"\n📊 {len(dirs)} folder, {len(file_list)} file"
        
        await update.message.reply_text(response_text, parse_mode="Markdown")

    except PermissionError:
        await update.message.reply_text("🚫 Tidak ada izin untuk mengakses folder ini.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


async def send_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ambil command to send a file."""
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return

    if not context.args:
        await update.message.reply_text(
            "📥 *Cara menggunakan:*\n\n"
            "`/ambil nama_file.pdf`\n"
            "`/ambil subfolder/file.docx`\n\n"
            "💡 Gunakan `/ls` untuk melihat daftar file.",
            parse_mode="Markdown"
        )
        return

    user_id = update.effective_user.id
    base_dir = get_user_dir(user_id)
    filename = " ".join(context.args)
    
    if os.path.isabs(filename):
        file_path = os.path.abspath(filename)
    else:
        file_path = os.path.abspath(os.path.join(base_dir, filename))

    # Security check
    if is_path_blocked(file_path):
        await update.message.reply_text("🚫 Akses ditolak: File dalam folder sistem tidak dapat diakses.")
        return

    if not os.path.exists(file_path):
        await update.message.reply_text(f"❌ File tidak ditemukan: `{filename}`", parse_mode="Markdown")
        return
    
    if os.path.isdir(file_path):
        await update.message.reply_text(
            f"❌ `{filename}` adalah direktori.\n"
            f"Gunakan `/ls {filename}` untuk melihat isinya.",
            parse_mode="Markdown"
        )
        return

    try:
        # Check file size (50MB limit)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            size_mb = file_size / (1024 * 1024)
            await update.message.reply_text(
                f"⚠️ File terlalu besar: `{size_mb:.1f} MB`\n"
                "Telegram maksimal 50MB.",
                parse_mode="Markdown"
            )
            return

        # Send status
        status_msg = await update.message.reply_text(f"⏳ Mengirim `{os.path.basename(file_path)}`...", parse_mode="Markdown")
        
        with open(file_path, 'rb') as doc:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=doc,
                filename=os.path.basename(file_path)
            )
        
        await status_msg.delete()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengirim file: `{e}`", parse_mode="Markdown")


# ============ Voice Note Handler ============




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await unauthorized_response(update)
        return
    
    command_text = update.message.text.strip()
    
    if not command_text:
        return
    
    # Use AI to analyze intent if available
    if ai_chat:
        try:
            intent = ai_chat.analyze_intent(command_text)
            intent_type = intent.get('type', 'chat')
            target = intent.get('target', '')
        except Exception:
            intent_type = 'chat'
            target = ''
    else:
        intent = parser.parse(command_text)
        intent_type = intent.get('type', 'simple_chat')
        target = intent.get('target', '')
    
    response = await process_intent(intent_type, target, command_text)
    await update.message.reply_text(response)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    # Check authorization
    if not is_authorized(update.effective_user.id):
        await update.callback_query.answer("🚫 Akses ditolak!", show_alert=True)
        return
    
    query = update.callback_query
    await query.answer()
    
    action = query.data
    user_id = update.effective_user.id
    
    # Handle file explorer actions
    if action == "file_ls":
        current = get_user_dir(user_id)
        try:
            files = os.listdir(current)
            if not files:
                await query.edit_message_text(f"📂 Direktori kosong:\n`{current}`", parse_mode="Markdown")
                return
            
            dirs = [f for f in sorted(files, key=str.lower) if os.path.isdir(os.path.join(current, f))]
            file_list = [f for f in sorted(files, key=str.lower) if not os.path.isdir(os.path.join(current, f))]
            
            response = f"📂 `{current}`\n━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for d in dirs[:10]:
                response += f"📁 `{d}/`\n"
            for f in file_list[:15]:
                response += f"📄 `{f}`\n"
            
            if len(dirs) > 10 or len(file_list) > 15:
                response += f"\n_...dan lainnya_\n"
            response += f"\n📊 {len(dirs)} folder, {len(file_list)} file"
            
            await query.edit_message_text(response, parse_mode="Markdown")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: `{e}`", parse_mode="Markdown")
        return
    
    elif action == "file_pwd":
        current = get_user_dir(user_id)
        await query.edit_message_text(
            f"📍 *Lokasi saat ini:*\n`{current}`\n\n"
            "💡 Gunakan `/cd [path]` untuk pindah folder.",
            parse_mode="Markdown"
        )
        return
    
    elif action == "status":
        time_str = commands.get_current_time()
        date_str = commands.get_current_date()
        ai_status = "✅ Active" if ai_chat else "❌ Disabled"
        
        # Get system stats for quick status
        battery = psutil.sensors_battery()
        cpu_percent = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory()
        
        if battery:
            battery_info = f"🔋 `{battery.percent}%` {'⚡' if battery.power_plugged else '🔌'}"
        else:
            battery_info = "🔋 `N/A`"
        
        await query.edit_message_text(
            f"�️ *SYSTEM STATUS*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🕐 `{time_str}` | 📅 `{date_str}`\n"
            f"🤖 AI: {ai_status}\n\n"
            f"⚡ *Quick Stats:*\n"
            f"{battery_info} | 🚀 CPU `{cpu_percent}%` | 🧠 RAM `{ram.percent}%`\n\n"
            f"💡 Ketik `/status` untuk laporan lengkap.",
            parse_mode="Markdown"
        )
        return
    

    
    elif action == "kaell_eye":
        # Trigger webcam capture via callback
        await query.edit_message_text("📸 Membuka mata Kaell...")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, capture_webcam_photo)
            
            if result:
                temp_path, success = result
                if success and temp_path:
                    with open(temp_path, 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption="👁️ Ini yang Kaell lihat sekarang, Bos!"
                        )
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="❌ Gagal mengambil foto. Webcam mungkin sedang digunakan."
                    )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Webcam tidak tersedia."
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Error: {e}"
            )
        return

    elif action == "screenshot":
        # Trigger screenshot capture via callback
        await query.edit_message_text("📸 Mengambil screenshot...")
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, capture_screenshot)
            
            if result:
                temp_path, success = result
                if success and temp_path:
                    with open(temp_path, 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption="🖥️ Screenshot layar laptop saat ini, Bos!"
                        )
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                else:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="❌ Gagal mengambil screenshot."
                    )
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Error: {e}"
            )
        return
    
    elif action == "help":
        await query.edit_message_text(
            "📚 *Panduan Singkat*\n\n"
            "*Perintah Teks:*\n"
            "• `buka/tutup [app]`\n"
            "• `putar lagu [judul]`\n"
            "• `cari [keyword]`\n\n"
            "*File Explorer:*\n"
            "• `/cd` `/ls` `/ambil`\n\n"
            "*Remote Control:*\n"

            "• `/foto` - webcam\n"
            "• `/ss` - screenshot\n"
            "• `/refresh` - restart bot\n\n"
            "Ketik /start untuk menu.",
            parse_mode="Markdown"
        )
        return
    
    elif action == "refresh_bot":
        await query.edit_message_text(
            "🔃 *Refresh Bot*\n\n"
            "Kaell pamit sebentar untuk membersihkan RAM...\n"
            "Bot akan kembali dalam hitungan detik!",
            parse_mode="Markdown"
        )
        # Give time for message to be sent
        await asyncio.sleep(1)
        # Exit - will be restarted by batch file
        os._exit(0)
        return
    
    # Handle other quick actions
    response = await process_quick_action(action)
    
    await query.edit_message_text(
        text=f"✅ {response}\n\n"
        "Kirim /start untuk menu.",
    )


async def process_intent(intent_type: str, target: str, original_text: str) -> str:
    """Process intent and execute command"""
    response = ""
    
    if intent_type == "open_app":
        if target:
            success, message = commands.open_application(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Aplikasi apa yang ingin dibuka?"
    
    elif intent_type == "close_app":
        if target:
            success, message = commands.close_application(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Aplikasi apa yang ingin ditutup?"
    
    elif intent_type == "open_website":
        if target:
            success, message = commands.open_website(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Website apa yang ingin dibuka?"
    
    elif intent_type == "close_tab":
        success, message = commands.close_browser_tab()
        return f"{'✅' if success else '❌'} {message}"
    
    elif intent_type == "close_all_tabs":
        success, message = commands.close_all_browser_tabs()
        return f"{'✅' if success else '❌'} {message}"
    
    elif intent_type == "play_youtube":
        if target:
            success, message = commands.play_youtube(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Apa yang ingin diputar di YouTube?"
    
    elif intent_type == "search_youtube":
        if target:
            success, message = commands.search_youtube(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Apa yang ingin dicari di YouTube?"
    
    elif intent_type == "search_google":
        if target:
            success, message = commands.search_google(target)
            return f"{'✅' if success else '❌'} {message}"
        return "❓ Apa yang ingin dicari di Google?"
    
    elif intent_type == "open_url":
        if target:
            success, message = commands.open_url(target)
            return f"{'🌐' if success else '❌'} {message}"
        return "❓ URL apa yang ingin dibuka?"
    
    elif intent_type == "time":
        time_msg = commands.get_current_time()
        return f"🕐 {time_msg}"
    
    elif intent_type == "date":
        date_msg = commands.get_current_date()
        return f"📅 {date_msg}"
    
    elif intent_type == "volume_up":
        success, message = commands.volume_up()
        return f"{'🔊' if success else '❌'} {message}"
    
    elif intent_type == "volume_down":
        success, message = commands.volume_down()
        return f"{'🔉' if success else '❌'} {message}"
    
    elif intent_type == "volume_mute":
        success, message = commands.volume_mute()
        return f"{'🔇' if success else '❌'} {message}"
    
    elif intent_type == "volume_max":
        success, message = commands.volume_max()
        return f"{'🔊' if success else '❌'} {message}"
    
    elif intent_type == "shutdown":
        success, message = commands.shutdown(delay=30)
        return f"⚠️ Komputer akan mati dalam 30 detik!\nKetik 'batalkan shutdown' untuk membatalkan."
    
    elif intent_type == "restart":
        success, message = commands.restart(delay=30)
        return f"⚠️ Komputer akan restart dalam 30 detik!"
    
    elif intent_type == "sleep":
        success, message = commands.sleep()
        return f"{'😴' if success else '❌'} {message}"
    
    elif intent_type == "lock":
        success, message = commands.lock_screen()
        return f"{'🔒' if success else '❌'} {message}"
    
    elif intent_type == "cancel_shutdown":
        success, message = commands.cancel_shutdown()
        return f"{'✅' if success else '❌'} {message}"
    
    else:
        # Use AI for chat
        if ai_chat:
            try:
                chat_response = ai_chat.get_response(original_text)
                return f"💬 {chat_response}"
            except Exception:
                pass
        simple_response = get_simple_response(original_text)
        return f"💬 {simple_response}"


async def process_quick_action(action: str) -> str:
    """Process quick action button"""
    actions = {
        'volume_up': ('🔊', commands.volume_up),
        'volume_down': ('🔉', commands.volume_down),
        'volume_mute': ('🔇', commands.volume_mute),
        'volume_max': ('🔊', commands.volume_max),
        'shutdown': ('⚠️', lambda: commands.shutdown(delay=30)),
        'restart': ('🔄', lambda: commands.restart(delay=30)),
        'sleep': ('😴', commands.sleep),
        'lock': ('🔒', commands.lock_screen),
        'cancel_shutdown': ('✅', commands.cancel_shutdown),
    }
    
    if action in actions:
        emoji, func = actions[action]
        success, message = func()
        return f"{emoji} {message}"
    
    return "❓ Unknown action"


# ============ Power Guardian & System Health Background Job ============

async def power_guardian_check(context: ContextTypes.DEFAULT_TYPE):
    """Background job to monitor battery and system health (CPU, RAM, Disk)"""
    global last_power_plugged, battery_100_alerted
    global last_cpu_alert_time, last_ram_alert_time, last_disk_alert_time
    global last_daily_report_date

    # Only send to authorized users
    if not TELEGRAM_ALLOWED_USER_IDS:
        return  # No users configured

    import time
    from datetime import datetime

    current_time = time.time()
    today = datetime.now().date()

    try:
        # ========== BATTERY MONITORING ==========
        battery = psutil.sensors_battery()
        if battery:
            current_plugged = battery.power_plugged

            # Alert 1: Charger disconnected (mati lampu/tercabut)
            if last_power_plugged is not None and last_power_plugged and not current_plugged:
                for user_id in TELEGRAM_ALLOWED_USER_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🔴 *CHARGER DISCONNECTED!*\n\n"
                                 f"⚡ Charger terlepas/mati!\n"
                                 f"🔋 Baterai: `{battery.percent}%`\n\n"
                                 f"_Mungkin mati lampu atau charger tercabut._",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Failed to send power alert to {user_id}: {e}")

            # Alert 1b: Charger connected (listrik nyala/charger dipasang)
            if last_power_plugged is not None and not last_power_plugged and current_plugged:
                for user_id in TELEGRAM_ALLOWED_USER_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🟢 *CHARGER CONNECTED!*\n\n"
                                 f"⚡ Charger terpasang!\n"
                                 f"🔋 Baterai: `{battery.percent}%`\n\n"
                                 f"_Laptop sedang mengisi daya._",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Failed to send charger connected alert to {user_id}: {e}")

            # Alert 2: Battery 100% while charging
            if battery.percent == 100 and current_plugged and not battery_100_alerted:
                battery_100_alerted = True
                for user_id in TELEGRAM_ALLOWED_USER_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🟢 *BATTERY FULL!*\n\n"
                                 f"🔋 Baterai sudah `100%`!\n"
                                 f"⚡ Cabut charger untuk menjaga kesehatan baterai.\n\n"
                                 f"_Atau aktifkan Smart Plug untuk auto-disconnect._",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Failed to send battery full alert to {user_id}: {e}")

            # Reset alert flag when battery drops below 100
            if battery.percent < 100:
                battery_100_alerted = False

            # Alert 3: Low battery warning (20%)
            if battery.percent <= 20 and not current_plugged:
                for user_id in TELEGRAM_ALLOWED_USER_IDS:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"⚠️ *LOW BATTERY WARNING!*\n\n"
                                 f"🔋 Baterai tinggal `{battery.percent}%`!\n"
                                 f"🔌 Segera pasang charger!",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Failed to send low battery alert to {user_id}: {e}")

            # Update state
            last_power_plugged = current_plugged

        # ========== SYSTEM HEALTH MONITORING ==========
        
        # CPU Usage Check (>80%)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        if cpu_percent > 80 and (current_time - last_cpu_alert_time) > ALERT_COOLDOWN:
            last_cpu_alert_time = current_time
            for user_id in TELEGRAM_ALLOWED_USER_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🔴 *HIGH CPU USAGE!*\n\n"
                             f"🚀 CPU Load: `{cpu_percent}%`\n\n"
                             f"_CPU usage sangat tinggi! Pertimbangkan untuk menutup aplikasi yang berat._",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Failed to send CPU alert to {user_id}: {e}")

        # RAM Usage Check (>80%)
        ram = psutil.virtual_memory()
        if ram.percent > 80 and (current_time - last_ram_alert_time) > ALERT_COOLDOWN:
            last_ram_alert_time = current_time
            ram_used_gb = ram.used / (1024**3)
            ram_total_gb = ram.total / (1024**3)
            for user_id in TELEGRAM_ALLOWED_USER_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🔴 *HIGH RAM USAGE!*\n\n"
                             f"🧠 RAM: `{ram.percent}%` ({ram_used_gb:.1f}/{ram_total_gb:.1f} GB)\n\n"
                             f"_RAM hampir penuh! Pertimbangkan untuk menutup aplikasi yang tidak digunakan._",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Failed to send RAM alert to {user_id}: {e}")

        # Disk Usage Check (>90%)
        disk = psutil.disk_usage('C:/')
        if disk.percent > 90 and (current_time - last_disk_alert_time) > ALERT_COOLDOWN:
            last_disk_alert_time = current_time
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            for user_id in TELEGRAM_ALLOWED_USER_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🔴 *DISK ALMOST FULL!*\n\n"
                             f"💾 Disk C: `{disk.percent}%` ({disk_used_gb:.0f}/{disk_total_gb:.0f} GB)\n"
                             f"_Free space: `{disk_free_gb:.0f} GB`_\n\n"
                             f"_Segera bersihkan file tidak diperlukan!_",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Failed to send disk alert to {user_id}: {e}")

        # ========== DAILY REPORT (7 AM) ==========
        current_hour = datetime.now().hour
        if current_hour == 7 and last_daily_report_date != today:
            last_daily_report_date = today
            
            # Get GPU info if available
            gpu_info = ""
            if GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        for i, gpu in enumerate(gpus):
                            gpu_info += f"🎮 GPU{i}: `{gpu.temperature}°C` | Load: `{gpu.load*100:.0f}%`\n"
                except Exception:
                    gpu_info = "🎮 GPU: `Unable to read`\n"
            
            for user_id in TELEGRAM_ALLOWED_USER_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🌅 *GOOD MORNING! Daily System Report*\n"
                             f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                             f"📅 {datetime.now().strftime('%A, %d %B %Y')}\n\n"
                             f"⚡ *POWER STATUS*\n"
                             f"{'🔋 Battery: `' + str(battery.percent) + '%` ' + ('⚡ Charging' if battery.power_plugged else '🔋 Discharging') if battery else '🔋 Battery: `N/A (Desktop)`'}\n\n"
                             f"🖥️ *SYSTEM HEALTH*\n"
                             f"🚀 CPU: `{cpu_percent}%`\n"
                             f"🧠 RAM: `{ram.percent}%` ({ram.used/(1024**3):.1f}/{ram.total/(1024**3):.1f} GB)\n"
                             f"💾 Disk C: `{disk.percent}%` ({disk.free/(1024**3):.0f} GB free)\n"
                             f"{gpu_info if gpu_info else ''}\n"
                             f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                             f"✅ Sistem berjalan optimal!\n"
                             f"_Have a great day!_",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"Failed to send daily report to {user_id}: {e}")

    except Exception as e:
        print(f"Power guardian error: {e}")


def run_bot():
    """Run the Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di .env")
        return
    
    print(f"""
╔══════════════════════════════════════════════════════╗
║        🤖 Kaell Telegram Bot Started! 🤖             ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Bot: @kaell_assistant_bot                           ║
║  Status: Online ✅                                   ║
║                                                      ║
║  Buka Telegram dan cari @kaell_assistant_bot         ║
║  Tekan Ctrl+C untuk stop bot                         ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cd", cd_command))
    app.add_handler(CommandHandler("pwd", pwd_command))
    app.add_handler(CommandHandler("ls", list_files_command))
    app.add_handler(CommandHandler("ambil", send_file_command))
    app.add_handler(CommandHandler("task", task_command))
    app.add_handler(CommandHandler("kill", kill_command))
    app.add_handler(CommandHandler("foto", foto_command))
    app.add_handler(CommandHandler("ss", screenshot_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    
    # Setup Power Guardian & System Health background job (runs every 10 seconds)
    if TELEGRAM_ALLOWED_USER_IDS:
        app.job_queue.run_repeating(
            power_guardian_check,
            interval=10,  # Check every 10 seconds for responsive alerts
            first=5,      # First check after 5 seconds
            name="power_guardian"
        )
        print("🛡️ Power Guardian enabled - monitoring battery status (10s interval)")
        print("📊 System Health Auto-Report enabled:")
        print("   • Daily report at 7 AM")
        print("   • CPU alert when >80%")
        print("   • RAM alert when >80%")
        print("   • Disk alert when >90%")
    else:
        print("⚠️ Power Guardian disabled - no authorized users configured")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    run_bot()
