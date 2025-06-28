# FINAL version – NO Updater used, PTB v20+ and Python 3.13 compatible
# Webhook-based, works perfectly on Render

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
    telegram_app.create_task(telegram_app.process_update(update))
    return jsonify({"status": "ok"})

@app.route("/")
def index():
    return "Bot is live and running on PTB v20+"

if __name__ == "__main__":
    import asyncio

    async def run():
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.bot.set_webhook(url=f"https://telegram-chatgpt-bot-ai.onrender.com/{TELEGRAM_BOT_TOKEN}")
        print("Webhook set")

    asyncio.get_event_loop().run_until_complete(run())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
