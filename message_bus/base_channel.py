from abc import ABC, abstractmethod

from message_bus.bound_message import InboundMessage, OutboundMessage
from message_bus.message_bus import MessageBus


class BaseChannel(ABC):
    """聊天平台的抽象基类"""

    name: str = "base"

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @abstractmethod
    async def start(self):
        """连接平台，开始监听消息"""
        ...

    @abstractmethod
    async def stop(self):
        """断开连接"""
        ...

    @abstractmethod
    async def send(self, msg: OutboundMessage):
        """发送消息到平台"""
        ...

    async def handle_message(self, sender_id: str, chat_id: str, content: str):
        """收到消息时调用——转发到 Bus"""
        await self.bus.publish_inbound(InboundMessage(
            channel=self.name, sender_id=sender_id,
            chat_id=chat_id, content=content,
        ))