from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, API_ID, LOGGER, BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, CHANNEL_ID, PORT, ADMINS
import pyrogram.utils

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.username = usr_bot_me.username # FIXED: Username cached globally right at startup!

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite Link From Force Sub Channel !")
                sys.exit()
        if FORCE_SUB_CHANNEL2:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL2)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL2)).invite_link
                self.invitelink2 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite Link From Force Sub Channel !")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Hey 🖐")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            sys.exit()

        # DYNAMIC ADMIN MENU SCOPE HOOK: Set exclusive commands on Telegram interface for Admins automatically
        from pyrogram.types import BotCommand, BotCommandScopeChat
        for admin_id in ADMINS:
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Bot ko shuru karne ke liye"),
                        BotCommand("batch", "Batch link banane ke liye"),
                        BotCommand("bulk", "Range files ka single link"),
                        BotCommand("stats", "Live server stats dekhne ke liye"),
                        BotCommand("broadcast", "Saare users ko message bhejna")
                    ],
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
            except Exception:
                pass

        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated By \nhttps://t.me/Madflix_Bots")
        self.LOGGER(__name__).info(f"""ミ💖 MADFLIX BOTZ 💖彡""")
        
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot Stopped...")
