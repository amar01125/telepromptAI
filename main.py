# Fully async Telegram + ChatGPT bot for PTB v20+ and Python 3.13-compatible
# For Render deployment (web service), using Flask + python-telegram-bot v20+

import os
import openai
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    chat_id = update.effective_chat.id

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}]
        )
        bot_response = response["choices"][0]["message"]["content"]
    except Exception as e:
        bot_response = f"Error: {e}"

    await context.bot.send_message(chat_id=chat_id, text=bot_response)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    return "Bot is running with PTB v20+!"

if __name__ == "__main__":
    import asyncio
    port = int(os.environ.get("PORT", 10000))
    telegram_app.run_webhook(listen="0.0.0.0", port=port, webhook_url=f"https://your-app-name.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host="0.0.0.0", port=port)
