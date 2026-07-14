from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    
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

    elif data.startswith("checksub_"):
        from helper_func import is_subscribed
        from plugins.start import send_media_files, start_and_force_sub_handler
        
        # IMAGE 1 FIX: Instead of native hindi popup alert, dynamic loop routing fallback
        is_user_subscribed = await is_subscribed(None, client, query)
        if not is_user_subscribed:
            await query.answer() # Dynamic silent acknowledgement to stop buffering
            # Force trigger the validation message block inside chat screen again
            query.message.from_user = query.from_user
            file_token = data.split("_", 1)[1]
            query.message.text = f"/start {file_token}" if file_token != "none" else "/start"
            await start_and_force_sub_handler(client, query.message)
            try:
                await query.message.delete()
            except:
                pass
            return

        await query.answer()
        file_token = data.split("_", 1)[1]
        
        try:
            await query.message.delete()
        except:
            pass

        if file_token == "none" or not file_token:
            welcome_text = (
                f"<b><i>👋 Hello {query.from_user.mention},\n\n"
                "Welcome to our bot!! You can access this bot by using special links ❤️✨💖</i></b>"
            )
            await client.send_message(chat_id=query.from_user.id, text=welcome_text, parse_mode=client.parse_mode)
        else:
            await send_media_files(client, query.message, file_token)

    elif data.startswith("getagain_"):
        from plugins.start import send_media_files
        await query.answer()
        file_token = data.split("_", 1)[1]
        try:
            await query.message.delete()
        except:
            pass
        await send_media_files(client, query.message, file_token)
