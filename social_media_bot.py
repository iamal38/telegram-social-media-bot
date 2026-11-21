#!/usr/bin/env python3
"""
Social Media Specialist Telegram Bot
Bot AI spesialis media sosial dengan sub-menu:
- Content Ideas
- Caption Writer
- Content Calendar / Scheduling
- Hashtag Generator
- Strategy & Growth
- Platform Tips
- Brand Voice
- Free Chat AI
"""

import os
import logging
from typing import Dict, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Load .env jika ada
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "ISI_TOKEN_BOT_KAMU_DISINI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ISI_API_KEY_AI_KAMU_DISINI")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # Ganti ke Groq/xAI jika perlu
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")  # atau "grok-beta", "llama-3.3-70b-versatile", dll

# ====================== LOGGING ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ====================== STATES ======================
(
    MAIN_MENU,
    CONTENT_IDEAS,
    CAPTION_WRITER,
    CALENDAR,
    HASHTAG,
    STRATEGY,
    PLATFORM_TIPS,
    BRAND_VOICE,
    FREE_CHAT,
    WAITING_DETAIL,
) = range(10)

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """Kamu adalah **Social Media Specialist AI** profesional yang berpengalaman lebih dari 8 tahun.

Kepribadian:
- Ramah, profesional, to-the-point, dan sangat actionable
- Bahasa Indonesia yang natural (campur sedikit English marketing term kalau cocok)
- Selalu berikan contoh konkret yang siap pakai
- Gunakan emoji secukupnya agar menarik

Keahlian utama:
1. Content Ideas & Ide Konten yang engaging
2. Caption writing (hook + body + CTA) untuk Instagram, TikTok, LinkedIn, X, Facebook
3. Content Calendar & Scheduling strategy
4. Hashtag research (mix popular + niche + branded)
5. Platform-specific strategy (algoritma, best time, format)
6. Growth hacking & engagement tactics
7. Brand voice development
8. Analytics interpretation & improvement tips

Aturan jawaban:
- Jawab dalam Bahasa Indonesia
- Berikan struktur yang jelas (pakai numbering/bullet)
- Selalu sertakan contoh siap copy-paste
- Kalau user minta ide, berikan minimal 5-8 ide
- Kalau caption, berikan 2-3 variasi
- Akhiri dengan pertanyaan follow-up yang relevan agar percakapan lanjut
"""

# ====================== AI CLIENT ======================
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


async def ask_ai(user_message: str, history: list = None) -> str:
    """Kirim pesan ke AI dan dapatkan respons."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-8:])  # Batasi history biar hemat token

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.75,
            max_tokens=1200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return (
            "⚠️ Maaf, terjadi kesalahan saat menghubungi AI.\n"
            "Pastikan API Key dan Base URL sudah benar.\n\n"
            f"Error: `{str(e)[:150]}`"
        )


# ====================== KEYBOARDS ======================
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💡 Content Ideas", callback_data="menu_ideas"),
            InlineKeyboardButton("✍️ Caption Writer", callback_data="menu_caption"),
        ],
        [
            InlineKeyboardButton("📅 Content Calendar", callback_data="menu_calendar"),
            InlineKeyboardButton("#️⃣ Hashtag Generator", callback_data="menu_hashtag"),
        ],
        [
            InlineKeyboardButton("📊 Strategy & Growth", callback_data="menu_strategy"),
            InlineKeyboardButton("🎯 Platform Tips", callback_data="menu_platform"),
        ],
        [
            InlineKeyboardButton("🗣️ Brand Voice", callback_data="menu_brand"),
            InlineKeyboardButton("💬 Free Chat AI", callback_data="menu_chat"),
        ],
        [InlineKeyboardButton("ℹ️ Bantuan / Cara Pakai", callback_data="menu_help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_main")]]
    )


# ====================== HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler /start"""
    user = update.effective_user
    welcome_text = (
        f"Halo {user.first_name}! 👋\n\n"
        "Saya **Social Media Specialist AI** 🚀\n"
        "Siap bantu kamu bikin konten, strategi, caption, calendar, hashtag, dan semua kebutuhan media sosial.\n\n"
        "Pilih menu di bawah sesuai kebutuhanmu:"
    )

    # Reset history
    context.user_data["history"] = []
    context.user_data["mode"] = None

    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
    return MAIN_MENU


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help"""
    text = (
        "📖 *Cara Menggunakan Bot*\n\n"
        "1. Pilih menu dari tombol di bawah\n"
        "2. Ikuti instruksi yang diberikan\n"
        "3. Ketik detail yang diminta (contoh: niche, platform, brand, dll)\n"
        "4. Bot akan langsung kasih hasil siap pakai\n\n"
        "*Contoh penggunaan:*\n"
        "• Content Ideas → ketik: *skincare brand untuk gen z*\n"
        "• Caption Writer → ketik: *produk serum vitamin C, Instagram*\n"
        "• Calendar → ketik: *brand kopi lokal, 7 hari, Instagram + TikTok*\n\n"
        "Kamu juga bisa langsung chat bebas di mode Free Chat AI."
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle semua inline button"""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_main":
        return await start(update, context)

    if data == "menu_help":
        text = (
            "📖 *Cara Menggunakan Bot*\n\n"
            "Pilih salah satu menu, lalu ketik detail yang diminta.\n\n"
            "*Contoh:*\n"
            "• Content Ideas → `brand fashion pria, target 20-30 tahun`\n"
            "• Caption → `produk sepatu running, TikTok, tone energetic`\n"
            "• Calendar → `kafe lokal, 14 hari, fokus Instagram Reels`\n"
            "• Hashtag → `kuliner Indonesia, makanan pedas`\n\n"
            "Semakin detail info yang kamu kasih, semakin bagus hasilnya!"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
        return MAIN_MENU

    # Set mode
    mode_map = {
        "menu_ideas": ("CONTENT_IDEAS", "💡 *Content Ideas*\n\nCeritakan tentang brand/niche/bisnismu.\n\nContoh:\n`brand skincare natural untuk wanita 25-35 tahun`\n`konten edukasi keuangan untuk gen z`"),
        "menu_caption": ("CAPTION_WRITER", "✍️ *Caption Writer*\n\nKasih tahu:\n• Produk/topik\n• Platform (IG / TikTok / LinkedIn / X)\n• Tone yang diinginkan (opsional)\n\nContoh:\n`serum vitamin C, Instagram, tone soft & educational`"),
        "menu_calendar": ("CALENDAR", "📅 *Content Calendar / Scheduling*\n\nKasih info:\n• Brand / niche\n• Durasi (7 hari / 14 hari / 30 hari)\n• Platform utama\n• Goal (awareness / engagement / sales)\n\nContoh:\n`brand kopi lokal, 14 hari, Instagram + TikTok, goal engagement`"),
        "menu_hashtag": ("HASHTAG", "#️⃣ *Hashtag Generator*\n\nKasih tahu niche / topik / brand-mu.\n\nContoh:\n`kuliner street food Indonesia`\n`fashion thrifting gen z`\n`produk baby care`"),
        "menu_strategy": ("STRATEGY", "📊 *Strategy & Growth*\n\nCeritakan situasi akunmu saat ini + goal yang ingin dicapai.\n\nContoh:\n`akun Instagram fashion, 3.2k followers, ingin naik ke 10k dalam 3 bulan`\n`baru mulai TikTok untuk brand skincare`"),
        "menu_platform": ("PLATFORM_TIPS", "🎯 *Platform Tips*\n\nPilih platform atau langsung sebutkan:\n• Instagram\n• TikTok\n• LinkedIn\n• X (Twitter)\n• YouTube Shorts\n• Facebook\n\nContoh:\n`tips algoritma Instagram Reels 2025`\n`best time posting LinkedIn untuk B2B`"),
        "menu_brand": ("BRAND_VOICE", "🗣️ *Brand Voice*\n\nCeritakan tentang brand-mu:\n• Bidang usaha\n• Target audience\n• Personality yang diinginkan\n\nContoh:\n`brand sepatu lokal, target anak muda urban, ingin voice yang cool tapi tetap approachable`"),
        "menu_chat": ("FREE_CHAT", "💬 *Free Chat AI Mode*\n\nSekarang kamu bisa chat bebas dengan saya sebagai Social Media Specialist.\n\nTanyakan apa saja seputar konten, strategi, caption, algoritma, dll.\n\nKetik pesanmu di bawah:"),
    }

    if data in mode_map:
        mode, prompt = mode_map[data]
        context.user_data["mode"] = mode
        context.user_data["history"] = []
        await query.edit_message_text(prompt, parse_mode="Markdown", reply_markup=back_to_menu_keyboard())
        return WAITING_DETAIL

    return MAIN_MENU


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pesan teks dari user"""
    user_text = update.message.text.strip()
    mode = context.user_data.get("mode")
    history = context.user_data.get("history", [])

    if not mode:
        # Kalau belum pilih menu, arahkan ke menu
        await update.message.reply_text(
            "Silakan pilih menu dulu ya 👇",
            reply_markup=main_menu_keyboard(),
        )
        return MAIN_MENU

    # Tambahkan konteks mode ke prompt
    mode_prompts = {
        "CONTENT_IDEAS": f"Buatkan ide konten yang kreatif dan actionable berdasarkan info berikut:\n\n{user_text}\n\nBerikan minimal 7-10 ide konten. Setiap ide sertakan: judul ide, format (Reels/Carousel/Story/Post), dan kenapa ide ini bagus.",
        "CAPTION_WRITER": f"Buatkan caption yang menarik berdasarkan info berikut:\n\n{user_text}\n\nBerikan 3 variasi caption (masing-masing dengan Hook yang berbeda). Sertakan emoji dan CTA yang kuat.",
        "CALENDAR": f"Buatkan content calendar / rencana posting berdasarkan info berikut:\n\n{user_text}\n\nSusun dalam format tabel harian yang rapi (Hari | Tema | Format | Caption singkat | CTA).",
        "HASHTAG": f"Generate hashtag yang relevan dan efektif berdasarkan:\n\n{user_text}\n\nKelompokkan menjadi:\n1. High competition (populer)\n2. Medium competition\n3. Low competition / niche\n4. Branded hashtag saran\nBerikan total 25-30 hashtag siap pakai.",
        "STRATEGY": f"Buatkan strategi growth & content strategy berdasarkan situasi berikut:\n\n{user_text}\n\nSertakan: analisis singkat, strategi konten, frekuensi posting, rekomendasi format, dan tips engagement.",
        "PLATFORM_TIPS": f"Berikan tips & best practices platform berdasarkan permintaan:\n\n{user_text}\n\nFokus pada algoritma terbaru, best time, format yang sedang naik, dan tips praktis.",
        "BRAND_VOICE": f"Bantu kembangkan Brand Voice berdasarkan info berikut:\n\n{user_text}\n\nHasilkan: Brand personality, Tone of voice, Do's and Don'ts, contoh kalimat, dan panduan singkat untuk caption.",
        "FREE_CHAT": user_text,
    }

    prompt = mode_prompts.get(mode, user_text)

    # Kirim typing action
    await update.message.chat.send_action(action="typing")

    # Dapatkan jawaban AI
    reply = await ask_ai(prompt, history)

    # Simpan history
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply})
    context.user_data["history"] = history

    await update.message.reply_text(
        reply,
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
    )

    # Tetap di mode yang sama (kecuali mau ganti)
    return WAITING_DETAIL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""
    await update.message.reply_text(
        "Dibatalkan. Ketik /start untuk mulai lagi.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ====================== MAIN ======================
def main():
    if TELEGRAM_TOKEN == "ISI_TOKEN_BOT_KAMU_DISINI":
        print("=" * 60)
        print("⚠️  TELEGRAM_BOT_TOKEN belum diisi!")
        print("Silakan set environment variable atau edit file ini.")
        print("=" * 60)

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
            WAITING_DETAIL: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("cancel", cancel),
            CommandHandler("help", help_command),
        ],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    print("🤖 Social Media Specialist Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
