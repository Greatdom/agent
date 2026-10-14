from message_bus.base_channel import BaseChannel
from message_bus.bound_message import OutboundMessage
from message_bus.message_bus import MessageBus


class TelegramChannel(BaseChannel):
    """Telegram Channel"""
    name = "telegram"

    def __init__(self, bus: MessageBus, token: str, allow_from: list[str]):
        super().__init__(bus)
        self.token = token
        self.allow_from = allow_from
        self._app = None

    async def start(self):
        from telegram import Update
        from telegram.ext import ApplicationBuilder, MessageHandler, filters

        self._app = ApplicationBuilder().token(self.token).build()

        async def on_message(update: Update, context):
            msg = update.effective_message
            if not msg or not msg.text:
                return
            sender = str(update.effective_user.id)
            if self.allow_from and "*" not in self.allow_from:
                if sender not in self.allow_from:
                    return  # 不在白名单中
            await self.handle_message(sender, str(msg.chat_id), msg.text)

        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()

    async def stop(self):
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()

    async def send(self, msg: OutboundMessage):
        if self._app:
            await self._app.bot.send_message(chat_id=msg.chat_id, text=msg.content)