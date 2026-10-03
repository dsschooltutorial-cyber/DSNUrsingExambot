import os
import threading
from datetime import datetime, timedelta, timezone

import psycopg
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# SETTINGS
# =========================

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 798816989
INVITE_LINK = os.getenv("INVITE_LINK")
CHANNEL_ID = -1003758223501

awaiting_transaction = {}

app = Flask(__name__)


@app.route("/")
def home():
    return "DS Nursing Exam Bot is running."


# =========================
# DATABASE
# =========================

def get_db():
    return psycopg.connect(DATABASE_URL)


def init_database():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memberships (
                    user_id BIGINT PRIMARY KEY,
                    start_date TIMESTAMPTZ NOT NULL,
                    expiry_date TIMESTAMPTZ NOT NULL,
                    expired_notified BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

            # Add column if old database already exists
            cur.execute(
                """
                ALTER TABLE memberships
                ADD COLUMN IF NOT EXISTS expired_notified
                BOOLEAN NOT NULL DEFAULT FALSE
                """
            )

        conn.commit()


def save_membership(user_id, start_date, expiry_date):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO memberships
                (user_id, start_date, expiry_date, expired_notified)
                VALUES (%s, %s, %s, FALSE)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    start_date = EXCLUDED.start_date,
                    expiry_date = EXCLUDED.expiry_date,
                    expired_notified = FALSE
                """,
                (user_id, start_date, expiry_date),
            )
        conn.commit()


def get_membership(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT start_date, expiry_date, expired_notified
                FROM memberships
                WHERE user_id = %s
                """,
                (user_id,),
            )
            return cur.fetchone()


# =========================
# AUTOMATIC EXPIRY
# =========================

async def remove_expired_members(context: ContextTypes.DEFAULT_TYPE):

    now = datetime.now(timezone.utc)

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT user_id
                    FROM memberships
                    WHERE expiry_date <= %s
                    AND expired_notified = FALSE
                    """,
                    (now,),
                )

                expired_users = [row[0] for row in cur.fetchall()]

        print(
            f"Expiry checker ran successfully. "
            f"Expired users found: {len(expired_users)}"
        )

        for user_id in expired_users:

            removed = False

            # -------------------------
            # Remove from private channel
            # -------------------------

            try:

                await context.bot.ban_chat_member(
                    chat_id=CHANNEL_ID,
                    user_id=user_id,
                )

                await context.bot.unban_chat_member(
                    chat_id=CHANNEL_ID,
                    user_id=user_id,
                    only_if_banned=True,
                )

                removed = True

                print(
                    f"Removed expired member: {user_id}"
                )

            except Exception as e:

                print(
                    f"Could not remove expired user "
                    f"{user_id}: {e}"
                )

                # Even if user already left,
                # continue with expiry notification.
                removed = True

            # -------------------------
            # Notify user
            # -------------------------

            if removed:

                try:

                    await context.bot.send_message(
                        chat_id=user_id,
                        text=(
                            "🔴 MEMBERSHIP EXPIRED\n\n"
                            "Your DS NURSING EXAM membership "
                            "has expired.\n\n"
                            "💰 Renewal: 50 ETB / 30 Days\n\n"
                            "👉 Use /renew to renew your membership."
                        ),
                    )

                except Exception as e:

                    print(
                        f"Could not notify user "
                        f"{user_id}: {e}"
                    )

                # -------------------------
                # Mark as processed
                # -------------------------

                try:

                    with get_db() as conn:
                        with conn.cursor() as cur:

                            cur.execute(
                                """
                                UPDATE memberships
                                SET expired_notified = TRUE
                                WHERE user_id = %s
                                """,
                                (user_id,),
                            )

                        conn.commit()

                    print(
                        f"Expired membership marked as processed: "
                        f"{user_id}"
                    )

                except Exception as e:

                    print(
                        f"Could not update expired status "
                        f"for {user_id}: {e}"
                    )

    except Exception as e:

        print(
            f"Expiry checker error: {e}"
        )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

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


# =========================
# MEMBERSHIP
# =========================

async def membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "💎 DS NURSING EXAM MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "✅ Daily MCQs\n"
        "✅ Mock Exams\n"
        "✅ High-Yield Notes\n"
        "✅ Nursing Procedures\n"
        "✅ Detailed Explanations"
    )


# =========================
# PAYMENT
# =========================

async def payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ I HAVE PAID",
                callback_data="paid"
            )
        ]
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
        "5️⃣ After approval, you will receive "
        "the private channel link.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def paid_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    await query.answer()

    user_id = query.from_user.id

    awaiting_transaction[user_id] = True

    await query.message.reply_text(
        "🧾 SEND YOUR TRANSACTION ID\n\n"
        "Please send the Transaction ID "
        "you received after payment."
    )


# =========================
# TRANSACTION
# =========================

async def receive_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.effective_user:
        return

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
                callback_data=f"approve:{user_id}"
            ),
            InlineKeyboardButton(
                "❌ REJECT",
                callback_data=f"reject:{user_id}"
            ),
        ]
    ]

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

    await update.message.reply_text(
        "✅ Your payment information has been sent to Admin.\n\n"
        "⏳ Please wait for payment verification."
    )


# =========================
# ADMIN APPROVE / REJECT
# =========================

async def admin_decision(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    if query.from_user.id != ADMIN_ID:

        await query.answer(
            "❌ You are not authorized.",
            show_alert=True,
        )

        return

    await query.answer()

    action, user_id_text = query.data.split(":")

    user_id = int(user_id_text)

    # =====================
    # APPROVE
    # =====================

    if action == "approve":

        if not INVITE_LINK:

            await query.message.reply_text(
                "⚠️ INVITE_LINK is not configured."
            )

            return

        now = datetime.now(timezone.utc)

        membership_data = get_membership(user_id)

        if membership_data:

            old_start = membership_data[0]
            old_expiry = membership_data[1]

            if now < old_expiry:

                start_date = old_start

                expiry_date = (
                    old_expiry +
                    timedelta(days=30)
                )

            else:

                start_date = now

                expiry_date = (
                    now +
                    timedelta(days=30)
                )

        else:

            start_date = now

            expiry_date = (
                now +
                timedelta(days=30)
            )

        save_membership(
            user_id,
            start_date,
            expiry_date,
        )

        expiry_text = expiry_date.strftime(
            "%d %B %Y"
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 PAYMENT APPROVED!\n\n"
                "Welcome to DS NURSING EXAM. 🎓\n\n"
                "🔐 PRIVATE CHANNEL LINK:\n"
                f"{INVITE_LINK}\n\n"
                "💰 Membership: 50 ETB / 30 Days\n"
                f"📅 Expires: {expiry_text}\n\n"
                "Use /myaccount to check your membership."
            ),
        )

        await query.message.edit_reply_markup(
            reply_markup=None
        )

        await query.message.reply_text(
            f"✅ Payment approved for User ID: {user_id}\n"
            f"📅 Expires: {expiry_text}"
        )

    # =====================
    # REJECT
    # =====================

    elif action == "reject":

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ PAYMENT NOT VERIFIED\n\n"
                "Your payment could not be verified.\n"
                "Please contact @DSNursing for assistance."
            ),
        )

        await query.message.edit_reply_markup(
            reply_markup=None
        )

        await query.message.reply_text(
            f"❌ Payment rejected for User ID: {user_id}"
        )


# =========================
# MY ACCOUNT
# =========================

async def myaccount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.effective_user:
        return

    user_id = update.effective_user.id

    membership_data = get_membership(user_id)

    if not membership_data:

        await update.message.reply_text(
            "👤 MY ACCOUNT\n\n"
            "🔴 Membership: INACTIVE\n\n"
            "💰 Membership: 50 ETB / 30 Days\n"
            "👉 Use /payment to subscribe."
        )

        return

    start_date = membership_data[0]
    expiry_date = membership_data[1]

    now = datetime.now(timezone.utc)

    if now >= expiry_date:

        await update.message.reply_text(
            "👤 MY ACCOUNT\n\n"
            "🔴 Membership: EXPIRED\n\n"
            "💰 Renewal: 50 ETB / 30 Days\n"
            "👉 Use /renew to renew your membership."
        )

        return

    days_left = (
        expiry_date - now
    ).days

    expiry_text = expiry_date.strftime(
        "%d %B %Y"
    )

    await update.message.reply_text(
        "👤 MY ACCOUNT\n\n"
        "🟢 Membership: ACTIVE\n"
        f"📅 Expires: {expiry_text}\n"
        f"⏳ Days remaining: {days_left} days\n\n"
        "💰 50 ETB / 30 Days"
    )


# =========================
# RENEW
# =========================

async def renew(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "🔄 RENEW MEMBERSHIP\n\n"
        "💰 50 ETB / 30 Days\n\n"
        "👉 Payment: /payment"
    )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "🆘 HELP\n\n"
        "For assistance, contact @DSNursing."
    )


# =========================
# FLASK SERVER
# =========================

def run_flask():

    app.run(
        host="0.0.0.0",
        port=PORT,
        use_reloader=False,
    )


# =========================
# MAIN
# =========================

def main():

    # Database
    init_database()

    # Start Flask health server
    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True,
    )

    flask_thread.start()

    # Telegram application
    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # =====================
    # COMMANDS
    # =====================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "membership",
            membership
        )
    )

    application.add_handler(
        CommandHandler(
            "payment",
            payment
        )
    )

    application.add_handler(
        CommandHandler(
            "myaccount",
            myaccount
        )
    )

    application.add_handler(
        CommandHandler(
            "renew",
            renew
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    # =====================
    # PAYMENT BUTTON
    # =====================

    application.add_handler(
        CallbackQueryHandler(
            paid_callback,
            pattern="^paid$"
        )
    )

    # =====================
    # ADMIN BUTTONS
    # =====================

    application.add_handler(
        CallbackQueryHandler(
            admin_decision,
            pattern="^(approve|reject):"
        )
    )

    # =====================
    # TRANSACTION ID
    # =====================

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_transaction
        )
    )

    # =====================
    # EXPIRY CHECKER
    # =====================

    application.job_queue.run_repeating(
        remove_expired_members,
        interval=300,
        first=30,
    )

    print(
        "DS Nursing Exam Bot starting..."
    )

    print(
        "Automatic membership expiry checker enabled."
    )

    print(
        f"Health server running on port {PORT}."
    )

    # =====================
    # START BOT
    # =====================

    application.run_polling(
        drop_pending_updates=True
    )


# =========================
# START
# =========================

if __name__ == "__main__":
    main()
