import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")

if not TOKEN or not BASE_URL:
    raise Exception("Missing TELEGRAM_BOT_TOKEN or RENDER_EXTERNAL_URL")

app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is working.")

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

@app.post(f"/webhook/{TOKEN}")
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def index():
    return "Bot is Live!"

if __name__ == "__main__":
    async def main():
        webhook_url = f"{BASE_URL}/webhook/{TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

        from threading import Thread
        def run_flask():
            app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

        Thread(target=run_flask).start()

    asyncio.run(main())
