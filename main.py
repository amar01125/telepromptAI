import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not TOKEN or not BASE_URL:
    raise Exception("Missing TELEGRAM_BOT_TOKEN or RENDER_EXTERNAL_URL")

app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is working.")

application.add_handler(CommandHandler("start", start))

@app.post(f"/webhook/{TOKEN}")
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.get_event_loop().create_task(application.process_update(update))
    return "OK"

@app.route("/")
def home():
    return "Bot is Live!"

if __name__ == "__main__":
    async def main():
        await application.initialize()
        await application.bot.set_webhook(f"{BASE_URL}/webhook/{TOKEN}")
        await application.start()
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

    asyncio.run(main())
