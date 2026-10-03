import os
from datetime import datetime, timedelta, timezone

import psycopg
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
DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_ID = 798816989
INVITE_LINK = os.getenv("INVITE_LINK")
CHANNEL_ID = -1003758223501

awaiting_transaction = {}


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_database():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memberships (
                    user_id BIGINT PRIMARY KEY,
                    start_date TIMESTAMPTZ NOT NULL,
                    expiry_date TIMESTAMPTZ NOT NULL
                )
            """)
        conn.commit()


def save_membership(user_id, start_date, expiry_date):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO memberships
                (user_id, start_date, expiry_date)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    start_date = EXCLUDED.start_date,
                    expiry_date = EXCLUDED.expiry_date
            """, (user_id, start_date, expiry_date))
        conn.commit()


def get_membership(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT start_date, expiry_date
                FROM memberships
                WHERE user_id = %s
            """, (user_id,))
            return cur.fetchone()


async def remove_expired_members(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc)

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id
                FROM memberships
                WHERE expiry_date <= %s
            """, (now,))
            expired_users = [row[0] for row in cur.fetchall()]

    for user_id in expired_users:
        try:
            await context.bot.ban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user_id
            )

            await context.bot.unban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user_id,
                only_if_banned=True
            )

            print(f"Removed expired member: {user_id}")

            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "🔴 MEMBERSHIP EXPIRED\n\n"
                        "Your DS NURSING EXAM membership has expired.\n\n"
                        "💰 Renewal: 50
