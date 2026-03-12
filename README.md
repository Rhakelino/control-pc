# Kaell Voice Assistant v2 🎤

Asisten virtual berbasis suara yang dapat menjawab pertanyaan dan menjalankan perintah sistem.

## Fitur

- 🗣️ **Speech Recognition** - Mendengarkan perintah suara dalam Bahasa Indonesia
- 🤖 **AI Chat** - Menjawab pertanyaan menggunakan Google Gemini
- 🔊 **Text-to-Speech** - Menjawab dengan suara
- 📂 **Buka Aplikasi** - Membuka aplikasi di komputer
- 🌐 **Buka Website** - Membuka website di browser
- ⏰ **Cek Waktu** - Memberitahu waktu saat ini

## Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note untuk Windows**: Jika PyAudio gagal diinstall, download wheel dari [sini](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) dan install manual:
> ```bash
> pip install PyAudio‑0.2.14‑cp311‑cp311‑win_amd64.whl
> ```

### 2. Setup API Key

1. Dapatkan API key dari [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Buat file `.env` dari template:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` dan masukkan API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Jalankan

```bash
python main.py
```

## Contoh Perintah

| Perintah | Aksi |
|----------|------|
| "Halo, apa kabar?" | Ngobrol dengan AI |
| "Siapa presiden Indonesia?" | Bertanya ke AI |
| "Buka notepad" | Membuka Notepad |
| "Buka chrome" | Membuka Chrome |
| "Buka youtube" | Membuka YouTube di browser |
| "Jam berapa sekarang?" | Memberitahu waktu |
| "Keluar" / "Stop" | Keluar dari aplikasi |

## Struktur Folder

```
kaell-assistan-v2/
├── main.py              # Entry point
├── config.py            # Konfigurasi
├── requirements.txt     # Dependencies
├── .env                 # API keys (buat sendiri)
├── speech/
│   ├── recognizer.py    # Speech-to-text
│   └── synthesizer.py   # Text-to-speech
├── ai/
│   └── gemini_chat.py   # Integrasi Gemini
└── commands/
    └── system_commands.py  # Perintah sistem
```

## Troubleshooting

### Microphone tidak terdeteksi
- Pastikan microphone sudah terhubung
- Cek permission microphone di Windows Settings

### Error "GEMINI_API_KEY tidak ditemukan"
- Pastikan file `.env` sudah dibuat
- Pastikan API key sudah dimasukkan dengan benar

### PyAudio installation error
- Windows: Install Visual C++ Build Tools terlebih dahulu
- Atau gunakan pre-built wheel seperti di instruksi di atas
