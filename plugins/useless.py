from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from config import ADMINS, BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time


@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    await message.reply(BOT_STATS_TEXT.format(uptime=time))


@Bot.on_message(filters.private & filters.incoming & ~filters.command(['start', 'help', 'users', 'broadcast', 'batch', 'bulk', 'stats']))
async def useless(_, message: Message):
    if USER_REPLY_TEXT:
        # 2nd MESSAGE REQ: Enclosing direct response in clean italics
        await message.reply(f"<i>{USER_REPLY_TEXT}</i>")


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
