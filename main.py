from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Load environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not TOKEN or not BASE_URL:
    raise Exception("Missing TELEGRAM_BOT_TOKEN or RENDER_EXTERNAL_URL")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Telegram command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is working.")

telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is Live!"

if __name__ == "__main__":
    import asyncio

    # Set webhook
    async def set_webhook():
        webhook_url = f"{BASE_URL}/webhook/{TOKEN}"
        await bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

    asyncio.run(set_webhook())
    
    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
