import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 እንኳን ወደ DS NURSING EXAM በደህና መጡ!\n\n"
        "📚 Nursing Licensure & COC Exam Preparation\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "የሚፈልጉትን አማራጭ ይምረጡ፦\n\n"
        "💎 /membership - Membership\n"
        "💳 /payment - Payment\n"
        "👤 /myaccount - My Account\n"
        "🔄 /renew - Renew Membership\n"
        "🆘 /help - Help"
    )


async def membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 DS NURSING EXAM MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "በMembership ያገኙት፦\n"
        "✅ Daily MCQs\n"
        "✅ Mock Exams\n"
        "✅ High-Yield Notes\n"
        "✅ Nursing Procedures\n"
        "✅ Detailed Explanations\n"
        "✅ Exam Preparation Materials"
    )


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 PAYMENT INFORMATION\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "📱 Telebirr: YOUR NUMBER\n"
        "🏦 CBE Birr: YOUR NUMBER\n\n"
        "ክፍያ ከፈጸሙ በኋላ Transaction ID ያስቀምጡ።\n\n"
        "ከዚያ Admin ን ያነጋግሩ።"
    )


async def myaccount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👤 MY ACCOUNT\n\n"
        "የMembership ሁኔታዎን ለማረጋገጥ Admin ን ያነጋግሩ።"
    )


async def renew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 RENEW MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "የክፍያ መመሪያ፦ /payment"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 HELP\n\n"
        "ለእርዳታ Admin ን ያነጋግሩ።"
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("membership", membership))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CommandHandler("myaccount", myaccount))
    app.add_handler(CommandHandler("renew", renew))
    app.add_handler(CommandHandler("help", help_command))

    print("DS Nursing Exam Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
