import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, FILE_AUTO_DELETE, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2
from helper_func import encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)


async def send_media_files(client: Client, message: Message, file_token: str):
    if not file_token or file_token == "none":
        return False
    try:
        string = await decode(file_token)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return False
            ids = range(start, end + 1) if start <= end else []
            if start > end:
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end: break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return False
        else:
            return False

        temp_msg = await client.send_message(chat_id=message.chat.id, text="Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await client.send_message(chat_id=message.chat.id, text="Something Went Wrong..!")
            return False
        await temp_msg.delete()
    
        madflix_msgs = []
        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                madflix_msg = await msg.copy(
                    chat_id=message.chat.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=True
                )
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(
                    chat_id=message.chat.id, 
                    caption=caption, 
                    parse_mode=ParseMode.HTML, 
                    reply_markup=reply_markup, 
                    protect_content=True
                )
                madflix_msgs.append(madflix_msg)
            except:
                pass

        bot_me = await client.get_me()
        clean_notice_text = (
            f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\n"
            f"<b>This Video / File Will Be Deleted In {file_auto_delete}.</b>\n\n"
            f"<b>🤖 @{bot_me.username}</b>"
        )
        
        k = await client.send_message(chat_id=message.chat.id, text=clean_notice_text, parse_mode=ParseMode.HTML)
        asyncio.create_task(delete_files(madflix_msgs, client, k, file_token))
        return True
    except:
        return False


@Bot.on_message(filters.command('start') & filters.private)
async def start_and_force_sub_handler(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try: await add_user(id)
        except: pass
    
    text = message.text
    start_data = text.split(" ", 1)[1] if " " in text else "none"
    
    show_ch1 = False
    show_ch2 = False
    
    if id not in ADMINS:
        if FORCE_SUB_CHANNEL:
            try:
                member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    show_ch1 = True
            except UserNotParticipant:
                show_ch1 = True
            except:
                pass
                
        if FORCE_SUB_CHANNEL2:
            try:
                member2 = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL2, user_id=id)
                if member2.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                    show_ch2 = True
            except UserNotParticipant:
                show_ch2 = True
            except:
                pass

    if not show_ch1 and not show_ch2:
        if len(text) > 7:
            success = await send_media_files(client, message, start_data)
            if success: return
            
        # 1st MESSAGE REQ: Welcome text inside clean italic format
        welcome_text = (
            f"<i>👋 Hello {message.from_user.mention},\n\n"
            "Welcome to our bot!! You can access this bot by using special links ❤️✨💖</i>"
        )
        await message.reply_text(text=welcome_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, quote=True)
        return

    buttons = []
    ch_row = []
    if show_ch1:
        ch_row.append(InlineKeyboardButton(text="Join Here 📢", url=client.invitelink))
    if show_ch2:
        ch_row.append(InlineKeyboardButton(text="Join Here 📢", url=client.invitelink2))
        
    if ch_row:
        buttons.append(ch_row)
        
    buttons.append([InlineKeyboardButton(text='♻️ Try Again', callback_data=f"checksub_{start_data}")])

    sexy_force_msg = (
        f"<b>👋 Hello {message.from_user.mention},</b>\n\n"
        "<b>⚠️ You need to join my Channel/Group to use me!</b>\n\n"
        "<b>👉 ❤️ Kindly Please join Channel to access the content... ✨🥰💖</b>\n\n"
        "<b>⁉️ FACING PROBLEMS, USE: /help</b>"
    )
    await message.reply(text=sexy_force_msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML, quote=True, disable_web_page_preview=True)


@Bot.on_message(filters.command('help') & filters.private)
async def help_command(client: Client, message: Message):
    help_text = (
        f"⁉️ <b>Hello {message.from_user.mention} ~</b>\n\n"
        "⚠️ ⇨ <b>I am a private file sharing bot, meant to provide files and necessary stuff through special link for specific channels ❤️✨</b>\n\n"
        "📢 ⇨ <b>In order to get the files you have to join all the mentioned channels that I provide you to join 💖 You cannot access or get the files unless you joined all channels 🥰</b>\n\n"
        "🚀 ⇨ <b>So kindly join the Mentioned Channels to get your Files instantly! ❤️🌟</b>"
    )
    await message.reply_text(text=help_text, parse_mode=ParseMode.HTML, quote=True)


async def delete_files(messages, client, k, file_token):
    await asyncio.sleep(FILE_AUTO_DELETE) 
    for msg in messages:
        try: await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e: print(f"Delete failed: {e}")
            
    recycle_text = (
        "<b>Previous Message was Deleted 🗑️</b>\n\n"
        "<b>If you want to get the files again, then click: [ ♻️ Click Here ] button below else close this message ❤️✨</b>"
    )
    
    recycle_buttons = []
    if file_token:
        recycle_buttons.append([
            InlineKeyboardButton("♻️ Click Here", callback_data=f"getagain_{file_token}"),
            InlineKeyboardButton("Close ❌", callback_data="close")
        ])
    else:
        recycle_buttons.append([InlineKeyboardButton("Close ❌", callback_data="close")])
        
    try:
        await k.edit_text(text=recycle_text, reply_markup=InlineKeyboardMarkup(recycle_buttons), parse_mode=ParseMode.HTML)
    except Exception as e: print(f"Recycle UI error: {e}")


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=f"Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} Users Are Using This Bot")


@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        
        for chat_id in query:
            try:
                # DYNAMIC BROADCAST ITALIC FORCING ENGINE
                if broadcast_msg.text:
                    # Pure text message code path logic
                    await client.send_message(
                        chat_id=chat_id,
                        text=f"<i>{broadcast_msg.text.html if broadcast_msg.text.html else broadcast_msg.text}</i>",
                        parse_mode=ParseMode.HTML,
                        reply_markup=broadcast_msg.reply_markup
                    )
                else:
                    # Media templates (Photo/Video/Files captions fallback conversion)
                    caption = f"<i>{broadcast_msg.caption.html if broadcast_msg.caption else ''}</i>"
                    await broadcast_msg.copy(chat_id=chat_id, caption=caption, parse_mode=ParseMode.HTML)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                if broadcast_msg.text:
                    await client.send_message(
                        chat_id=chat_id,
                        text=f"<i>{broadcast_msg.text.html if broadcast_msg.text.html else broadcast_msg.text}</i>",
                        parse_mode=ParseMode.HTML,
                        reply_markup=broadcast_msg.reply_markup
                    )
                else:
                    caption = f"<i>{broadcast_msg.caption.html if broadcast_msg.caption else ''}</i>"
                    await broadcast_msg.copy(chat_id=chat_id, caption=caption, parse_mode=ParseMode.HTML)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"<b><u>Broadcast Completed</u></b>\n\n<b>Total Users :</b> <code>{total}</code>\n<b>Successful :</b> <code>{successful}</code>\n<b>Blocked Users :</b> <code>{blocked}</code>\n<b>Deleted Accounts :</b> <code>{deleted}</code>\n<b>Unsuccessful :</b> <code>{unsuccessful}</code>"
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(f"Use This Command As A Reply To Any Telegram Message With Out Any Spaces.")
        await asyncio.sleep(8)
        await msg.delete()
