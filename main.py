from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import os

# ENV variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("RENDER_EXTERNAL_URL")  # render provides this automatically

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

# Flask app
flask_app = Flask(__name__)

# Telegram app
telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I am your ChatGPT bot. Ask me anything ✨")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Error from OpenAI: {e}"

    await update.message.reply_text(reply)

# Add handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook route
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

# Set webhook on startup
@flask_app.before_first_request
def setup_webhook():
    webhook_url = BASE_URL + "webhook"
    telegram_app.bot.set_webhook(webhook_url)

# Run flask server
if __name__ == '__main__':
    flask_app.run(host="0.0.0.0", port=10000)
