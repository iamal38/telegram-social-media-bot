# Social Media Specialist Telegram Bot

Bot AI spesialis media sosial dengan menu lengkap (Content Ideas, Caption, Calendar, Hashtag, Strategy, dll).

## Cara Deploy di Railway (Jalan 24 Jam)

### 1. Siapkan Akun
- Buat akun di [https://railway.app](https://railway.app) (bisa login pakai GitHub/Google)

### 2. Upload Bot ke GitHub (Recommended)
1. Buat repository baru di GitHub (contoh: `social-media-bot`)
2. Upload semua file di folder ini ke repository tersebut

### 3. Deploy di Railway
1. Masuk ke Railway → **New Project**
2. Pilih **Deploy from GitHub repo**
3. Pilih repository bot kamu
4. Railway akan otomatis detect Python

### 4. Setting Environment Variables
Di halaman project Railway:
1. Klik service bot kamu
2. Masuk ke tab **Variables**
3. Tambahkan variabel berikut satu per satu:

| Nama Variabel         | Isi |
|-----------------------|-----|
| `TELEGRAM_BOT_TOKEN`  | Token dari BotFather |
| `OPENAI_API_KEY`      | API Key dari Groq / OpenAI / xAI |
| `OPENAI_BASE_URL`     | `https://api.groq.com/openai/v1` |
| `MODEL_NAME`          | `llama-3.3-70b-versatile` |

### 5. Setting Start Command
Di tab **Settings** → **Deploy**:
- Start Command: `python social_media_bot.py`

Atau biarkan saja karena sudah ada `Procfile`.

### 6. Deploy!
Klik **Deploy**. Tunggu sampai status jadi **Success**.

Setelah itu bot sudah jalan 24 jam. Coba ketik `/start` di Telegram.

---

## File yang Ada
- `social_media_bot.py` → File utama bot
- `requirements.txt` → Daftar library
- `Procfile` → Untuk Railway
- `runtime.txt` → Versi Python
- `.env.example` → Contoh environment variable

---

## Catatan Penting
- Railway free tier sekarang memberikan credit gratis setiap bulan.
- Kalau credit habis, bot akan berhenti. Bisa upgrade atau ganti platform.
- Jangan pernah share Token Bot & API Key ke orang lain.
