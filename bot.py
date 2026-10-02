import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 እንኳን ወደ DS NURSING EXAM በደህና መጡ!\n\n"
        "📚 Nursing Licensure & COC Exam Preparation\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "💎 /membership - Membership\n"
        "💳 /payment - Payment\n"
        "👤 /myaccount - My Account\n"
        "🔄 /renew - Renew Membership\n"
        "🆘 /help - Help"
    )


async def membership(update: Update, context):
    await update.message.reply_text(
        "💎 DS NURSING EXAM MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "✅ Daily MCQs\n"
        "✅ Mock Exams\n"
        "✅ High-Yield Notes\n"
        "✅ Nursing Procedures\n"
        "✅ Detailed Explanations"
    )


async def payment(update: Update, context):
    await update.message.reply_text(
        "💳 PAYMENT INFORMATION\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "📱 Telebirr: YOUR NUMBER\n"
        "🏦 CBE Birr: YOUR NUMBER\n\n"
        "ክፍያ ከፈጸሙ በኋላ Transaction ID ያስቀምጡ።"
    )


async def myaccount(update: Update, context):
    await update.message.reply_text(
        "👤 MY ACCOUNT\n\n"
        "የMembership ሁኔታዎን ለማረጋገጥ Admin ን ያነጋግሩ።"
    )


async def renew(update: Update, context):
    await update.message.reply_text(
        "🔄 RENEW MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "Payment: /payment"
    )


async def help_command(update: Update, context):
    await update.message.reply_text(
        "🆘 HELP\n\n"
        "ለእርዳታ Admin ን ያነጋግሩ።"
    )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("membership", membership))
telegram_app.add_handler(CommandHandler("payment", payment))
telegram_app.add_handler(CommandHandler("myaccount", myaccount))
telegram_app.add_handler(CommandHandler("renew", renew))
telegram_app.add_handler(CommandHandler("help", help_command))


@app.route("/", methods=["GET"])
def home():
    return "DS Nursing Exam Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    asyncio.run(telegram_app.process_update(update))

    return "OK"


async def setup():
    await telegram_app.initialize()

    await telegram_app.bot.set_webhook(
        url=RENDER_URL + "/webhook"
    )


if __name__ == "__main__":
    asyncio.run(setup())

    app.run(
        host="0.0.0.0",
        port=PORT
    )
