# Noir Backend - Kael Smart Assistant 🤖

Repositori ini berfungsi sebagai "otak" asisten Kaell di laptop untuk mengontrol perangkat fisik dan perintah sistem Windows.

## 🔌 Bardi IoT Integration

Berhasil terhubung ke **EU02A-Bardi** menggunakan kontrol lokal via `tinytuya`.

### 🛠️ Device Specs

| Property | Value |
| :--- | :--- |
| **Device ID** | `a3c7d26023600ff7b37fye` |
| **Local Key** | `F&F=g9<J-AOmN]iI` |
| **IP Address** | `103.41.79.72` |
| **Version** | `3.4` |

### 🚀 Endpoint API Utama

| Method | Endpoint | Fungsi |
| :--- | :--- | :--- |
| `GET` | `/bardi/on` | Menyalakan aliran listrik Bardi |
| `GET` | `/bardi/off` | Mematikan aliran listrik Bardi |
| `GET` | `/bardi/status` | Mendapatkan status Bardi (ON/OFF) |
| `GET` | `/system/safe-shutdown` | Mematikan Bardi lalu mematikan Laptop (Safe Mode) |

### 📡 Contoh Penggunaan

#### Menyalakan Bardi
```bash
curl http://localhost:5000/bardi/on
```

**Response:**
```json
{
  "success": true,
  "message": "✅ Bardi Smart Plug berhasil dinyalakan!"
}
```

#### Mematikan Bardi
```bash
curl http://localhost:5000/bardi/off
```

**Response:**
```json
{
  "success": true,
  "message": "✅ Bardi Smart Plug berhasil dimatikan!"
}
```

#### Cek Status Bardi
```bash
curl http://localhost:5000/bardi/status
```

**Response:**
```json
{
  "success": true,
  "is_on": true,
  "status": "ON",
  "message": "🔌 Bardi Status: ON"
}
```

#### Safe Shutdown
```bash
curl http://localhost:5000/system/safe-shutdown
```

**Response:**
```json
{
  "success": true,
  "message": "🔄 Safe Shutdown dimulai!\n⏳ Windows akan mati dalam 20 detik\n🔌 Bardi akan dimatikan dalam 25 detik"
}
```

---

## ⚠️ Prosedur Anti-Stack (Lenovo Fix)

Untuk mencegah laptop tersangkut di logo Lenovo saat booting, script ini menggunakan parameter jeda:

```python
# Safe Shutdown Sequence
os.system("shutdown /s /t 20")  # Windows shutdown dalam 20 detik
time.sleep(25)                   # Tunggu 25 detik
bardi.turn_off()                 # Matikan Smart Plug
```

### Kenapa harus ada jeda?

1. **20 detik delay shutdown** - Memberikan waktu Windows untuk menutup semua file sistem dan aplikasi secara sempurna
2. **25 detik sebelum Bardi off** - Memastikan Windows sudah benar-benar mati sebelum Smart Plug memutus daya total

> ⚡ **PENTING:** Memutus daya terlalu cepat saat Windows belum sepenuhnya shutdown dapat menyebabkan korupsi file sistem dan laptop stuck di logo BIOS saat booting.

---

## 📂 File Structure

```
kaell-assistant-v2/
├── bardi_controller.py    # Module kontrol Bardi Smart Plug
├── web_server.py          # Flask server dengan endpoint Bardi
├── requirements.txt       # Dependencies (termasuk tinytuya)
└── BARDI_README.md        # Dokumentasi ini
```

---

## 📦 Requirements

```bash
pip install tinytuya flask flask-cors
```

### Dependencies Lengkap

| Package | Fungsi |
| :--- | :--- |
| `tinytuya` | Kontrol lokal Tuya/Bardi Smart Plug |
| `flask` | Web server untuk API endpoints |
| `flask-cors` | Enable CORS untuk React Native app |

---

## 🔧 Setup & Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verifikasi Bardi Connection

```python
import tinytuya

d = tinytuya.OutletDevice(
    dev_id='a3c7d26023600ff7b37fye',
    address='103.41.79.72',
    local_key='F&F=g9<J-AOmN]iI',
    version=3.4
)

print(d.status())  # Check connection
```

### 3. Start Server

```bash
python web_server.py
```

Server akan berjalan di `http://0.0.0.0:5000`

---

## 🔐 Security Notes

> [!WARNING]
> **Local Key** adalah kredensial sensitif. Jangan pernah commit file ini ke repository publik!

Rekomendasi:
- Simpan kredensial di file `.env`
- Tambahkan `.env` ke `.gitignore`

---

## 📱 React Native Integration

Untuk mengontrol Bardi dari aplikasi React Native:

```javascript
// Bardi ON
const bardiOn = async () => {
  const response = await fetch('http://YOUR_IP:5000/bardi/on');
  const data = await response.json();
  console.log(data.message);
};

// Bardi OFF
const bardiOff = async () => {
  const response = await fetch('http://YOUR_IP:5000/bardi/off');
  const data = await response.json();
  console.log(data.message);
};

// Safe Shutdown
const safeShutdown = async () => {
  const response = await fetch('http://YOUR_IP:5000/system/safe-shutdown');
  const data = await response.json();
  console.log(data.message);
};
```

---

## 📋 Troubleshooting

| Error | Solusi |
| :--- | :--- |
| `Connection refused` | Pastikan IP address Bardi benar dan device dalam jaringan yang sama |
| `Timeout` | Periksa firewall dan pastikan port tidak diblok |
| `No device found` | Re-scan dengan `python -m tinytuya scan` |
| `Invalid key` | Local Key mungkin sudah expired, re-link di app Bardi/Tuya |

---

## 🤝 Related Modules

- [API_README.md](./API_README.md) - Dokumentasi lengkap API
- [TELEGRAM_BOT_README.md](./TELEGRAM_BOT_README.md) - Integrasi Telegram Bot
