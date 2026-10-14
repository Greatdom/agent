import asyncio

from message_bus.base_channel import BaseChannel
from message_bus.message_bus import MessageBus


async def route_outbound(bus: MessageBus, channels: dict[str, BaseChannel]):
    """把 Agent 的回复路由到对应的 Channel"""
    while True:
        try:
            msg = await asyncio.wait_for(bus.consume_outbound(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        ch = channels.get(msg.channel)
        if ch:
            await ch.send(msg)