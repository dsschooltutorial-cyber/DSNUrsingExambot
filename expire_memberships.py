import os
import asyncio
from datetime import datetime, timezone

import psycopg
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
CHANNEL_ID = -1003758223501


def get_expired_members():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id
                FROM memberships
                WHERE expiry_date <= NOW()
            """)
            return [row[0] for row in cur.fetchall()]


async def remove_expired_users():
    bot = Bot(token=BOT_TOKEN)
    users = get_expired_members()

    for user_id in users:
        try:
            await bot.ban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user_id,
                until_date=datetime.now(timezone.utc)
            )

            await bot.unban_chat_member(
                chat_id=CHANNEL_ID,
                user_id=user_id,
                only_if_banned=True
            )

            print(f"Removed expired user: {user_id}")

        except Exception as e:
            print(f"Could not remove {user_id}: {e}")

    await bot.close()


if __name__ == "__main__":
    asyncio.run(remove_expired_users())
