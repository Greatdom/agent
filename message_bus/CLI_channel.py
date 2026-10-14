import asyncio

from message_bus.base_channel import BaseChannel
from message_bus.bound_message import OutboundMessage


class CLIChannel(BaseChannel):
    """终端 Channel"""
    name = "cli"

    async def start(self):
        """在独立的线程中读取终端输入"""
        loop = asyncio.get_event_loop()
        while True:
            user_input = await loop.run_in_executor(None, lambda: input("You: ").strip())
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                return
            await self.handle_message("user", "direct", user_input)

    async def stop(self):
        pass

    async def send(self, msg: OutboundMessage):
        print(f"\nBot: {msg.content}\n")