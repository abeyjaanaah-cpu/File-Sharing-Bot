from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
    # === 1. TUMHARA PURANA SYSTEM LOGIC (PRESERVED) ===
    if data == "about":
        await query.message.edit_text(
            text = f"<b>🤖 My Name :</b> <a href='https://t.me/FileSharingXProBot'>File Sharing Bot</a> \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram {__version__}</a> \n<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a> \n<b>📢 Channel :</b> <a href='https://t.me/Madflix_Bots'>Madflix Botz</a> \n<b>🧑‍💻 Developer :</b> <a href='tg://user?id={OWNER_ID}'>Jishu Developer</a>",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    # === 2. NAYA CALLBACK ROUTING SYSTEM FOR SUBS & RECYCLE ===
    elif data.startswith("checksub_"):
        from helper_func import is_subscribed
        from plugins.start import send_media_files
        
        is_user_subscribed = await is_subscribed(None, client, query)
        if not is_user_subscribed:
            await query.answer("⚠️ Aapne dono channels join nahi kiye hain! Pehle join karein ❤️", show_alert=True)
            return

        await query.answer("✅ Verification Successful! Processing files... 💖", show_alert=False)
        file_token = data.split("_", 1)[1]
        
        try:
            await query.message.delete()
        except:
            pass

        if file_token == "none" or not file_token:
            welcome_text = (
                f"👋 Hello {query.from_user.mention},\n\n"
                "<blockquote>Welcome to our bot!! You can access this bot by using special links ❤️✨💖</blockquote>"
            )
            await client.send_message(chat_id=query.from_user.id, text=welcome_text, parse_mode=client.parse_mode)
        else:
            await send_media_files(client, query.message, file_token)

    elif data.startswith("getagain_"):
        from plugins.start import send_media_files
        await query.answer("♻️ Restoring your media... ✨", show_alert=False)
        file_token = data.split("_", 1)[1]
        try:
            await query.message.delete()
        except:
            pass
        await send_media_files(client, query.message, file_token)


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
