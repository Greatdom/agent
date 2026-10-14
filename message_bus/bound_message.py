from dataclasses import dataclass

@dataclass
class InboundMessage:
    """从外部收到的消息"""
    channel: str         # "cli", "telegram", "discord"
    sender_id: str       # 发送者 ID
    chat_id: str         # 会话 ID
    content: str         # 消息正文

    @property
    def session_key(self) -> str:
        return f"{self.channel}:{self.chat_id}"

@dataclass
class OutboundMessage:
    """要发出去的消息"""
    channel: str
    chat_id: str
    content: str