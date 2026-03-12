# KAELL SYSTEM - Web Server API Documentation

API documentation untuk integrasi dengan aplikasi React Native.

## Base URL
```
http://[IP_KOMPUTER]:5000
```

---

## 1. Health Check / Connection Test

### `GET /`
Mengecek apakah server berjalan.

**Response:** HTML page

**React Native Usage:**
```javascript
async checkConnection() {
    const response = await fetch(`${baseUrl}/`);
    return { connected: response.ok };
}
```

---

## 2. System Stats

### `GET /api/stats`
Mendapatkan status sistem (CPU, RAM, Battery).

**Response:**
```json
{
    "success": true,
    "cpu": 15.2,
    "ram": 45.8,
    "battery": 85,
    "charging": true,
    "server": "KAELL SYSTEM"
}
```

**React Native:**
```javascript
async getSystemStats() {
    const response = await fetch(`${baseUrl}/api/stats`);
    return await response.json();
}
```

---

## 3. Kaell Eye (Webcam Capture)

### `GET/POST /api/kaell-eye`
Capture foto dari webcam laptop.

**Response:**
```json
{
    "success": true,
    "message": "Foto berhasil diambil",
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**React Native:**
```javascript
async captureKaellEye() {
    const response = await fetch(`${baseUrl}/api/kaell-eye`, {
        method: 'POST'
    });
    const data = await response.json();
    // data.image contains base64 image
    return data;
}
```

---

## 4. Quick Actions

### `POST /api/quick/<action>`
Eksekusi aksi cepat.

**Available Actions:**

| Action | Deskripsi |
|--------|-----------|
| `volume_up` | Naikkan volume 10% |
| `volume_down` | Turunkan volume 10% |
| `volume_mute` | Toggle mute |
| `volume_max` | Volume maksimal |
| `lock` | Kunci layar (Win+L) |
| `sleep` | Mode tidur |
| `shutdown` | Matikan PC (10 detik delay) |
| `restart` | Restart PC (10 detik delay) |
| `cancel_shutdown` | Batalkan shutdown/restart |

**Response:**
```json
{
    "success": true,
    "message": "Volume dinaikkan"
}
```

**React Native:**
```javascript
async quickAction(action) {
    const response = await fetch(`${baseUrl}/api/quick/${action}`, {
        method: 'POST'
    });
    return await response.json();
}

// Usage
await quickAction('lock');        // Kunci PC
await quickAction('volume_max');  // Volume max
await quickAction('volume_mute'); // Mute
await quickAction('shutdown');    // Shutdown
```

---

## 5. AI Command

### `POST /api/command`
Kirim perintah teks ke Kaell (dengan AI processing).

**Request Body:**
```json
{
    "command": "buka notepad",
    "speak": true
}
```

| Field | Type | Default | Deskripsi |
|-------|------|---------|-----------|
| `command` | string | required | Perintah teks |
| `speak` | boolean | true | Ucapkan response via speaker |

**Response:**
```json
{
    "success": true,
    "message": "Notepad berhasil dibuka",
    "intent": "open_app"
}
```

**Available Intents (Commands):**

| Intent | Contoh Perintah | Deskripsi |
|--------|-----------------|-----------|
| `open_app` | "buka notepad" | Buka aplikasi |
| `close_app` | "tutup chrome" | Tutup aplikasi |
| `open_website` | "buka youtube" | Buka website |
| `close_tab` | "tutup tab" | Tutup tab browser |
| `close_all_tabs` | "tutup semua tab" | Tutup semua tab |
| `time` | "jam berapa?" | Tanya waktu |
| `date` | "tanggal berapa?" | Tanya tanggal |
| `volume_up` | "keraskan volume" | Naikkan volume |
| `volume_down` | "kecilkan volume" | Turunkan volume |
| `volume_mute` | "mute" | Toggle mute |
| `volume_max` | "volume max" | Volume maksimal |
| `shutdown` | "matikan komputer" | Shutdown (10 detik delay) |
| `restart` | "restart komputer" | Restart (10 detik delay) |
| `sleep` | "tidurkan komputer" | Sleep mode |
| `lock` | "kunci layar" | Lock screen |
| `cancel_shutdown` | "batalkan shutdown" | Cancel shutdown |
| `play_youtube` | "putar lagu coldplay" | Play video YouTube |
| `search_youtube` | "cari di youtube react native" | Search YouTube |
| `search_google` | "cari di google tutorial python" | Search Google |
| `chat` | "siapa presiden indonesia?" | AI Chat response |

**React Native:**
```javascript
async sendCommand(command, speak = true) {
    const response = await fetch(`${baseUrl}/api/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, speak })
    });
    return await response.json();
}

// Usage Examples
await sendCommand('buka notepad');
await sendCommand('putar lagu bohemian rhapsody');
await sendCommand('jam berapa sekarang?');
await sendCommand('siapa presiden indonesia?');  // AI chat
```

---

## Complete React Native API Class

```javascript
// api/KaellAPI.js

const API_CONFIG = {
    baseUrl: 'http://192.168.1.5:5000',  // Ganti dengan IP komputer
    timeout: 10000,
};

class KaellAPI {
    constructor() {
        this.baseUrl = API_CONFIG.baseUrl;
    }

    setBaseUrl(url) {
        this.baseUrl = url;
    }

    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    // === CONNECTION ===
    async checkConnection() {
        try {
            const response = await fetch(`${this.baseUrl}/`, {
                signal: AbortSignal.timeout(5000)
            });
            return { connected: response.ok };
        } catch {
            return { connected: false };
        }
    }

    // === SYSTEM STATS ===
    async getSystemStats() {
        return this.request('/api/stats');
    }

    // === KAELL EYE ===
    async captureKaellEye() {
        return this.request('/api/kaell-eye', { method: 'POST' });
    }

    // === QUICK ACTIONS ===
    async quickAction(action) {
        return this.request(`/api/quick/${action}`, { method: 'POST' });
    }

    async volumeUp() { return this.quickAction('volume_up'); }
    async volumeDown() { return this.quickAction('volume_down'); }
    async volumeMute() { return this.quickAction('volume_mute'); }
    async volumeMax() { return this.quickAction('volume_max'); }
    async lockPC() { return this.quickAction('lock'); }
    async sleep() { return this.quickAction('sleep'); }
    async shutdown() { return this.quickAction('shutdown'); }
    async restart() { return this.quickAction('restart'); }
    async cancelShutdown() { return this.quickAction('cancel_shutdown'); }

    // === AI COMMAND ===
    async sendCommand(command, speak = true) {
        return this.request('/api/command', {
            method: 'POST',
            body: JSON.stringify({ command, speak }),
        });
    }

    // Shortcut methods
    async openApp(appName) { 
        return this.sendCommand(`buka ${appName}`); 
    }
    async closeApp(appName) { 
        return this.sendCommand(`tutup ${appName}`); 
    }
    async openWebsite(site) { 
        return this.sendCommand(`buka ${site}`); 
    }
    async playYoutube(query) { 
        return this.sendCommand(`putar ${query}`); 
    }
    async searchGoogle(query) { 
        return this.sendCommand(`cari di google ${query}`); 
    }
    async askAI(question) { 
        return this.sendCommand(question); 
    }
}

export const api = new KaellAPI();
export default api;
```

---

## Supported Applications

Aplikasi yang bisa dibuka/tutup:

| Nama | Command |
|------|---------|
| Notepad | `buka notepad` |
| Calculator | `buka calculator` / `buka kalkulator` |
| Chrome | `buka chrome` / `buka browser` |
| File Explorer | `buka explorer` |
| VS Code | `buka vscode` |
| Spotify | `buka spotify` |
| Discord | `buka discord` |
| WhatsApp | `buka whatsapp` / `buka wa` |
| Telegram | `buka telegram` |
| Word | `buka word` |
| Excel | `buka excel` |
| PowerPoint | `buka powerpoint` |

## Supported Websites

| Nama | Command |
|------|---------|
| YouTube | `buka youtube` |
| Google | `buka google` |
| Facebook | `buka facebook` |
| Instagram | `buka instagram` |
| Twitter | `buka twitter` |
| GitHub | `buka github` |
| Gmail | `buka gmail` |
| WhatsApp Web | `buka whatsapp web` |
