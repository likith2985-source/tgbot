from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp
import os

BOT_TOKEN = "7743265807:AAHpmLsIdNsww2M-tGo6vz6neB7mudKKI2k"  # Replace with your bot token
OWNER_NAME = "Likith Vardhan"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Hello! Welcome to the Media Downloader Bot!\n"
        f"👤 Owner: {OWNER_NAME}\n\n"
        "📥 Send a YouTube or Instagram Reel/Story link to download."
    )

def is_supported_url(url):
    return any(domain in url for domain in ["youtube.com", "youtu.be", "instagram.com"])

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not is_supported_url(url):
        await update.message.reply_text("❌ Unsupported link. Please send a valid YouTube or Instagram link.")
        return

    await update.message.reply_text("⏳ Downloading... please wait.")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        file_size = os.path.getsize(file_path)
        max_size = 50 * 1024 * 1024  # Telegram max for bots: 50MB

        if file_size > max_size:
            await update.message.reply_text("⚠️ File is too large to send on Telegram (limit 50MB).")
        else:
            with open(file_path, 'rb') as f:
                if file_path.endswith(('.mp4', '.mov')):
                    await update.message.reply_video(f)
                else:
                    await update.message.reply_document(f)

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    os.makedirs("downloads", exist_ok=True)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
