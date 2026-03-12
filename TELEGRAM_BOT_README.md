# KAELL ASSISTANT - Telegram Bot Integration

Complete documentation untuk integrasi **Kaell Telegram Bot** dengan aplikasi React/React Native.

---

## 📋 Overview

Kaell Telegram Bot adalah fitur remote control yang memungkinkan Anda mengontrol komputer dari mana saja melalui Telegram. Bot ini menggunakan **polling** (bukan webhook) sehingga tidak memerlukan server publik.

### Arsitektur

```
┌──────────────────┐     Telegram API     ┌──────────────────┐
│  React App       │◄───────────────────►│  Telegram Bot    │
│  (Mobile/Web)    │                      │  (Python Server) │
└──────────────────┘                      └────────┬─────────┘
                                                   │
                                                   ▼
                                          ┌──────────────────┐
                                          │  Kaell Assistant │
                                          │  (PC Control)    │
                                          └──────────────────┘
```

---

## 🚀 Quick Start

### 1. Setup Bot Token

Dapatkan token dari [@BotFather](https://t.me/BotFather) di Telegram:

1. Buka Telegram, cari `@BotFather`
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Copy token yang diberikan

### 2. Konfigurasi Environment

Buat file `.env` di root project:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
GROQ_API_KEY=your_groq_api_key_here

# Optional (Premium TTS)
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Security: Batasi akses ke User ID tertentu (comma-separated)
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

### 3. Mendapatkan User ID Telegram

Untuk keamanan, Anda perlu mendapatkan User ID Telegram Anda:

1. Cari bot `@userinfobot` di Telegram
2. Kirim pesan apapun
3. Bot akan reply dengan User ID Anda
4. Masukkan ID ke `TELEGRAM_ALLOWED_USER_IDS`

### 4. Install Dependencies

```bash
pip install python-telegram-bot groq psutil GPUtil pydub SpeechRecognition opencv-python
```

### 5. Jalankan Bot

```bash
python telegram_bot.py

# Atau menggunakan batch file
start_telegram_bot.bat
```

---

## 📱 Integrasi dengan React/React Native

### Cara Komunikasi

Ada **2 cara** untuk mengintegrasikan dengan React:

| Method | Pros | Cons |
|--------|------|------|
| **Telegram Bot API langsung** | Tidak perlu server tambahan | Perlu API token di client |
| **Melalui Flask Web Server** | Lebih aman | Perlu jalankan 2 server |

---

## 🔌 Method 1: Telegram Bot API (Recommended)

Kirim perintah langsung ke Telegram Bot API dari React.

### API Base URL

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/
```

### Kirim Pesan ke Bot

```javascript
const TELEGRAM_BOT_TOKEN = 'your_bot_token';
const CHAT_ID = 'your_chat_id';  // User ID atau Group ID

class TelegramBotAPI {
    constructor(token, chatId) {
        this.baseUrl = `https://api.telegram.org/bot${token}`;
        this.chatId = chatId;
    }

    // Kirim pesan/perintah
    async sendMessage(text) {
        const response = await fetch(`${this.baseUrl}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: this.chatId,
                text: text,
                parse_mode: 'Markdown'
            })
        });
        return response.json();
    }

    // Dapatkan update terbaru (untuk membaca response bot)
    async getUpdates(offset = 0) {
        const response = await fetch(`${this.baseUrl}/getUpdates?offset=${offset}`);
        return response.json();
    }
}

// Contoh penggunaan
const bot = new TelegramBotAPI(TELEGRAM_BOT_TOKEN, CHAT_ID);

// Kirim perintah
await bot.sendMessage('buka notepad');
await bot.sendMessage('/status');
await bot.sendMessage('/ls');
```

### React Native Hook

```javascript
// hooks/useTelegramBot.js
import { useState, useCallback } from 'react';

const BOT_TOKEN = 'YOUR_BOT_TOKEN';
const CHAT_ID = 'YOUR_CHAT_ID';

export function useTelegramBot() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const sendCommand = useCallback(async (command) => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: CHAT_ID,
                        text: command
                    })
                }
            );

            const data = await response.json();
            setLoading(false);
            return { success: data.ok, data };
        } catch (err) {
            setError(err.message);
            setLoading(false);
            return { success: false, error: err.message };
        }
    }, []);

    return { sendCommand, loading, error };
}
```

---

## 🔌 Method 2: Combined Flask + Telegram

Gunakan Flask Web Server sebagai proxy untuk kedua mode.

### Diagram

```
React App ──HTTP──► Flask Server ◄──Polling──► Telegram API
                         │
                         ▼
                   PC Control (Volume, Apps, etc.)
```

### Jalankan Kedua Server

```bash
# Terminal 1: Web Server
python web_server.py

# Terminal 2: Telegram Bot
python telegram_bot.py
```

---

## 📝 Available Commands

### Slash Commands

| Command | Deskripsi |
|---------|-----------|
| `/start` | Menu utama dengan quick action buttons |
| `/help` | Panduan singkat |
| `/info` | Daftar lengkap fitur |
| `/status` | Status sistem (CPU, RAM, Battery, GPU) |
| `/cd [path]` | Pindah direktori |
| `/pwd` | Lihat direktori saat ini |
| `/ls [path]` | List files/folders |
| `/ambil [file]` | Download file dari PC |
| `/speak [text]` | Text-to-Speech broadcast via speaker PC |
| `/foto` | Capture webcam (Kaell Eye) |
| `/refresh` | Restart bot untuk clear memory |

### Text Commands (Natural Language)

| Command | Deskripsi | Contoh |
|---------|-----------|--------|
| `buka [app]` | Buka aplikasi | `buka notepad`, `buka spotify` |
| `tutup [app]` | Tutup aplikasi | `tutup chrome` |
| `buka [website]` | Buka website | `buka youtube`, `buka facebook` |
| `putar [lagu]` | Play YouTube | `putar lagu Coldplay` |
| `cari [query]` | Search YouTube | `cari tutorial react native` |
| `naikkan volume` | Volume up | - |
| `turunkan volume` | Volume down | - |
| `mute` | Toggle mute | - |
| `matikan komputer` | Shutdown (30 detik delay) | - |
| `restart komputer` | Restart PC | - |
| `tidurkan komputer` | Sleep mode | - |
| `kunci layar` | Lock screen | - |
| `batalkan shutdown` | Cancel shutdown | - |
| `jam berapa?` | Waktu sekarang | - |
| `tanggal berapa?` | Tanggal hari ini | - |
| `[pertanyaan]` | AI Chat (Groq) | `siapa presiden Indonesia?` |

### Voice Notes

Kirim voice note ke bot untuk voice command! Bot menggunakan Google Speech Recognition untuk mengenali perintah.

---

## 🎮 Quick Action Buttons

Saat menjalankan `/start`, bot menampilkan keyboard interaktif:

```
┌─────────────────────────────────────────┐
│ 🔊 Vol+ │ 🔉 Vol- │ 🔇 Mute │ 🔊 Max   │
├─────────────────────────────────────────┤
│ 🔒 Lock │ 😴 Sleep │ 🔄 Restart         │
├─────────────────────────────────────────┤
│ ⏻ Shutdown │ ❌ Batalkan                │
├─────────────────────────────────────────┤
│ 📂 File │ 📢 Speak │ 👁 Eye             │
├─────────────────────────────────────────┤
│ 📊 Status │ ❓ Help                     │
└─────────────────────────────────────────┘
```

---

## 🛡️ Power Guardian

Bot secara otomatis memonitor status baterai dan mengirim notifikasi:

| Event | Notifikasi |
|-------|------------|
| Charger terlepas | 🔴 *CHARGER DISCONNECTED!* |
| Charger terpasang | 🟢 *CHARGER CONNECTED!* |
| Baterai 100% | 🟢 *BATTERY FULL!* - reminder cabut charger |
| Baterai ≤ 20% | ⚠️ *LOW BATTERY WARNING!* |

> Power Guardian otomatis aktif jika `TELEGRAM_ALLOWED_USER_IDS` dikonfigurasi.

---

## 🔐 Security

### Restrict Access

```env
# Hanya izinkan User ID tertentu
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321
```

### Blocked Directories

Untuk keamanan, folder berikut tidak dapat diakses:

- `C:/Windows`
- `C:/Program Files`
- `C:/Program Files (x86)`
- `C:/ProgramData`
- `%USERPROFILE%/AppData`

---

## 📦 Complete React Integration Class

```javascript
// api/KaellTelegramAPI.js

const API_CONFIG = {
    botToken: 'YOUR_BOT_TOKEN',
    chatId: 'YOUR_CHAT_ID',
    timeout: 10000,
};

class KaellTelegramAPI {
    constructor(config = API_CONFIG) {
        this.botToken = config.botToken;
        this.chatId = config.chatId;
        this.baseUrl = `https://api.telegram.org/bot${this.botToken}`;
    }

    // === CORE ===
    async sendMessage(text, parseMode = 'Markdown') {
        try {
            const response = await fetch(`${this.baseUrl}/sendMessage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: this.chatId,
                    text: text,
                    parse_mode: parseMode
                })
            });
            const data = await response.json();
            return { success: data.ok, data };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // === QUICK ACTIONS ===
    async volumeUp() { return this.sendMessage('naikkan volume'); }
    async volumeDown() { return this.sendMessage('turunkan volume'); }
    async volumeMute() { return this.sendMessage('mute'); }
    async volumeMax() { return this.sendMessage('volume maksimal'); }
    async lockPC() { return this.sendMessage('kunci layar'); }
    async sleep() { return this.sendMessage('tidurkan komputer'); }
    async shutdown() { return this.sendMessage('matikan komputer'); }
    async restart() { return this.sendMessage('restart komputer'); }
    async cancelShutdown() { return this.sendMessage('batalkan shutdown'); }

    // === COMMANDS ===
    async getStatus() { return this.sendMessage('/status'); }
    async getHelp() { return this.sendMessage('/help'); }
    async getInfo() { return this.sendMessage('/info'); }
    async captureWebcam() { return this.sendMessage('/foto'); }
    async speakText(text) { return this.sendMessage(`/speak ${text}`); }
    async refreshBot() { return this.sendMessage('/refresh'); }

    // === FILE EXPLORER ===
    async listFiles(path = '') { 
        return this.sendMessage(path ? `/ls ${path}` : '/ls'); 
    }
    async changeDir(path) { return this.sendMessage(`/cd ${path}`); }
    async printWorkingDir() { return this.sendMessage('/pwd'); }
    async downloadFile(filename) { return this.sendMessage(`/ambil ${filename}`); }

    // === AI & APPS ===
    async openApp(appName) { return this.sendMessage(`buka ${appName}`); }
    async closeApp(appName) { return this.sendMessage(`tutup ${appName}`); }
    async openWebsite(site) { return this.sendMessage(`buka ${site}`); }
    async playYoutube(query) { return this.sendMessage(`putar ${query}`); }
    async searchYoutube(query) { return this.sendMessage(`cari ${query}`); }
    async askAI(question) { return this.sendMessage(question); }
}

export const telegramApi = new KaellTelegramAPI();
export default telegramApi;
```

---

## 🎨 React Native Component Example

```jsx
// components/KaellController.jsx
import React, { useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import telegramApi from '../api/KaellTelegramAPI';

export default function KaellController() {
    const [status, setStatus] = useState('Ready');

    const handleAction = async (action, label) => {
        setStatus(`Executing: ${label}...`);
        const result = await action();
        setStatus(result.success ? `✅ ${label}` : `❌ Failed`);
    };

    return (
        <View style={styles.container}>
            <Text style={styles.status}>{status}</Text>
            
            <View style={styles.row}>
                <ActionButton 
                    label="🔊" 
                    onPress={() => handleAction(telegramApi.volumeUp, 'Vol+')} 
                />
                <ActionButton 
                    label="🔉" 
                    onPress={() => handleAction(telegramApi.volumeDown, 'Vol-')} 
                />
                <ActionButton 
                    label="🔇" 
                    onPress={() => handleAction(telegramApi.volumeMute, 'Mute')} 
                />
            </View>

            <View style={styles.row}>
                <ActionButton 
                    label="🔒" 
                    onPress={() => handleAction(telegramApi.lockPC, 'Lock')} 
                />
                <ActionButton 
                    label="😴" 
                    onPress={() => handleAction(telegramApi.sleep, 'Sleep')} 
                />
                <ActionButton 
                    label="📊" 
                    onPress={() => handleAction(telegramApi.getStatus, 'Status')} 
                />
            </View>

            <View style={styles.row}>
                <ActionButton 
                    label="👁️ Eye" 
                    onPress={() => handleAction(telegramApi.captureWebcam, 'Webcam')} 
                />
                <ActionButton 
                    label="📂 Files" 
                    onPress={() => handleAction(telegramApi.listFiles, 'Files')} 
                />
            </View>
        </View>
    );
}

const ActionButton = ({ label, onPress }) => (
    <TouchableOpacity style={styles.button} onPress={onPress}>
        <Text style={styles.buttonText}>{label}</Text>
    </TouchableOpacity>
);

const styles = StyleSheet.create({
    container: { padding: 20, backgroundColor: '#1a1a2e' },
    status: { color: '#0ff', fontSize: 16, marginBottom: 20, textAlign: 'center' },
    row: { flexDirection: 'row', justifyContent: 'center', marginBottom: 10 },
    button: {
        backgroundColor: '#16213e',
        padding: 15,
        margin: 5,
        borderRadius: 10,
        borderWidth: 1,
        borderColor: '#0f3460',
        minWidth: 70,
        alignItems: 'center',
    },
    buttonText: { color: '#fff', fontSize: 18 },
});
```

---

## 📊 Supported Applications

```javascript
const SUPPORTED_APPS = [
    'notepad', 'calculator', 'chrome', 'explorer', 'vscode',
    'spotify', 'discord', 'whatsapp', 'telegram', 'steam',
    'word', 'excel', 'powerpoint', 'paint', 'settings'
];

const SUPPORTED_WEBSITES = [
    'youtube', 'google', 'facebook', 'instagram', 
    'twitter', 'github', 'gmail', 'whatsapp web'
];
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot tidak respond | Cek `TELEGRAM_BOT_TOKEN` di `.env` |
| Access denied | Tambahkan User ID ke `TELEGRAM_ALLOWED_USER_IDS` |
| Voice note error | Install `ffmpeg` dan `pydub` |
| Webcam gelap | Tunggu 2 detik setelah capture |
| AI tidak respond | Cek `GROQ_API_KEY` di `.env` |

---

## 📄 .env Template

```env
# === Required ===
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# AI (untuk chat & intent analysis)
GROQ_API_KEY=your_groq_api_key

# === Security ===
# Kosongkan untuk allow semua (tidak disarankan!)
TELEGRAM_ALLOWED_USER_IDS=123456789

# === Optional ===
# Premium TTS (jika ingin suara lebih bagus)
ELEVENLABS_API_KEY=your_elevenlabs_key
```

---

## 🚀 Quick Test

```bash
# 1. Jalankan bot
python telegram_bot.py

# 2. Buka Telegram, cari bot Anda
# 3. Kirim /start
# 4. Coba kirim: "buka notepad"
# 5. Notepad akan terbuka di PC!
```

---

**Made with ❤️ by Kaell Assistant**
