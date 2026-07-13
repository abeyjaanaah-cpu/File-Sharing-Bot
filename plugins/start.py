import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()
    
        madflix_msgs = []

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption = caption, parse_mode = ParseMode.HTML, reply_markup = reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
                
            except:
                pass

        k = await client.send_message(chat_id = message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issues).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        asyncio.create_task(delete_files(madflix_msgs, client, k, text.split(" ", 1)[1] if " " in text else ""))
        
        return
    else:
        # IMAGE 2 FIX: Real Markdown Quote Box
        welcome_text = (
            f"👋 Hello {message.from_user.mention},\n\n"
            f"> Welcome to our bot!! You can access this bot by using special links ❤️✨💖"
        )
        await message.reply_text(
            text = welcome_text,
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview = True,
            quote = True
        )
        return

    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # FIXED: Extracting token safely from raw text to prevent dead links
    text = message.text
    start_data = ""
    if " " in text:
        start_data = text.split(" ", 1)[1]
    
    buttons = [
        [
            InlineKeyboardButton(text="Join Channel 1 📢", url=client.invitelink),
            InlineKeyboardButton(text="Join Channel 2 📢", url=client.invitelink2),
        ],
        [
            InlineKeyboardButton(
                text='♻️ Try Again',
                url=f"https://t.me/{client.username}?start={start_data}"
            )
        ]
    ]

    sexy_force_msg = (
        f"👋 Hello {message.from_user.mention},\n\n"
        f"⚠️ **You need to join my Channel/Group to use me!**\n\n"
        f"> 👉 ❤️ Kindly Please join Channel to access the premium videos... ✨🥰💖\n\n"
        f"⁉️ **FACING PROBLEMS, USE:** /help"
    )

    await message.reply(
        text = sexy_force_msg,
        reply_markup = InlineKeyboardMarkup(buttons),
        parse_mode = ParseMode.MARKDOWN,
        quote = True,
        disable_web_page_preview = True
    )


@Bot.on_message(filters.command('help') & filters.private)
async def help_command(client: Client, message: Message):
    # IMAGE 3 & 4 FIX: True Markdown Quote Blocks with unified flow
    help_text = (
        f"⁉️ **Hello {message.from_user.mention} ~**\n\n"
        "> ⚠️ ⇨ **I am a private file sharing bot, meant to provide files and necessary stuff through special link for specific channels.**\n"
        ">\n"
        "> 📢 ⇨ **In order to get the files you have to join the all mentioned channel that I provide you to join. You can not access or get the files unless you joined all channels.**\n"
        ">\n"
        "> 🚀 ⇨ **So join Mentioned Channels to get Files or initiate messages...**"
    )
    await message.reply_text(
        text=help_text,
        parse_mode=ParseMode.MARKDOWN,
        quote=True
    )


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
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
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
        
        status = f"""<b><u>Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(f"Use This Command As A Reply To Any Telegram Message With Out Any Spaces.")
        await asyncio.sleep(8)
        await msg.delete()


async def delete_files(messages, client, k, file_token):
    await asyncio.sleep(FILE_AUTO_DELETE) 
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")
            
    # FIXED: Clear Markdown Quote Box for Recycle Notice
    recycle_text = (
        "**Previous Message was Deleted**\n"
        "> **If you want to get the files again, then click: [ ♻️ Click Here ] button below else close this message. ❞**"
    )
    
    recycle_buttons = []
    if file_token:
        recycle_buttons.append([
            InlineKeyboardButton("♻️ Click Here", url=f"https://t.me/{client.username}?start={file_token}"),
            InlineKeyboardButton("Close ❌", callback_data="close")
        ])
    else:
        recycle_buttons.append([InlineKeyboardButton("Close ❌", callback_data="close")])
        
    try:
        await k.edit_text(
            text=recycle_text,
            reply_markup=InlineKeyboardMarkup(recycle_buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Failed to show recycle UI: {e}")
