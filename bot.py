import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

ADMIN_ID = 798816989
INVITE_LINK = os.getenv("INVITE_LINK")

awaiting_transaction = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 እንኳን ወደ DS NURSING EXAM በደህና መጡ!\n\n"
        "📚 Nursing Exit Exam • COC • Licensure Exam Preparation\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "/membership — Membership\n"
        "/payment — Payment\n"
        "/myaccount — My Account\n"
        "/renew — Renew Membership\n"
        "/help — Help"
    )


async def membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 DS NURSING EXAM MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "✅ Daily MCQs\n"
        "✅ Mock Exams\n"
        "✅ High-Yield Notes\n"
        "✅ Nursing Procedures\n"
        "✅ Detailed Explanations"
    )


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ I HAVE PAID", callback_data="paid")]
    ]

    await update.message.reply_text(
        "💳 PAYMENT INFORMATION\n\n"
        "💰 Membership: 50 ETB / 30 Days\n\n"
        "📱 Telebirr: +251931745423\n"
        "🏦 CBE Birr: 1000173352925\n\n"
        "1️⃣ Make your payment.\n"
        "2️⃣ Click I HAVE PAID.\n"
        "3️⃣ Send your Transaction ID.\n"
        "4️⃣ Admin will verify your payment.\n"
        "5️⃣ After approval, you will receive the private channel link.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def paid_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    awaiting_transaction[user_id] = True

    await query.message.reply_text(
        "🧾 SEND YOUR TRANSACTION ID\n\n"
        "Please send the Transaction ID you received after payment."
    )


async def receive_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not awaiting_transaction.get(user_id):
        return

    transaction_id = update.message.text.strip()
    awaiting_transaction.pop(user_id, None)

    user = update.effective_user
    name = user.full_name
    username = user.username or "No username"

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ APPROVE",
                callback_data=f"approve:{user_id}",
            ),
            InlineKeyboardButton(
                "❌ REJECT",
                callback_data=f"reject:{user_id}",
            ),
        ]
    ]

    # Send notification to admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "💳 NEW PAYMENT REQUEST\n\n"
            f"👤 Name: {name}\n"
            f"🔗 Username: @{username}\n"
            f"🆔 User ID: {user_id}\n"
            f"🧾 Transaction ID: {transaction_id}\n\n"
            "Please verify the payment."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    # Confirm to student
    await update.message.reply_text(
        "✅ Your payment information has been sent to Admin.\n\n"
        "⏳ Please wait for payment verification."
    )


async def admin_decision(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "❌ You are not authorized.",
            show_alert=True,
        )
        return

    await query.answer()

    action, user_id_text = query.data.split(":")
    user_id = int(user_id_text)

    if action == "approve":

        if not INVITE_LINK:
            await query.message.reply_text(
                "⚠️ INVITE_LINK is not configured."
            )
            return

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 PAYMENT APPROVED!\n\n"
                "Welcome to DS NURSING EXAM. 🎓\n\n"
                "🔐 PRIVATE CHANNEL LINK:\n"
                f"{INVITE_LINK}\n\n"
                "💰 Membership: 50 ETB / 30 Days"
            ),
        )

        await query.message.edit_reply_markup(reply_markup=None)

        await query.message.reply_text(
            f"✅ Payment approved for User ID: {user_id}"
        )

    elif action == "reject":

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ PAYMENT NOT VERIFIED\n\n"
                "Your payment could not be verified.\n"
                "Please contact @DSNursing for assistance."
            ),
        )

        await query.message.edit_reply_markup(reply_markup=None)

        await query.message.reply_text(
            f"❌ Payment rejected for User ID: {user_id}"
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
        "Payment: /payment"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 HELP\n\n"
        "ለእርዳታ Admin ን ያነጋግሩ።"
    )


def main():

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("membership", membership))
    application.add_handler(CommandHandler("payment", payment))
    application.add_handler(CommandHandler("myaccount", myaccount))
    application.add_handler(CommandHandler("renew", renew))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(
        CallbackQueryHandler(
            paid_callback,
            pattern="^paid$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            admin_decision,
            pattern="^(approve|reject):"
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_transaction
        )
    )

    application.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path="webhook",
    webhook_url=RENDER_URL + "/webhook",
    drop_pending_updates=True,
)

if __name__ == "__main__":
    main()
