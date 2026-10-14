import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from config.config import WORK_BASE_DIR, OPENROUTER_API_KEY, AGENT_MODEL, API_BASE_URL
from core.content import ContextBuilder
from message_bus.bound_message import OutboundMessage
from message_bus.message_bus import MessageBus
from session.session_manager import SessionManager
from tool.tool_registery import ToolRegistry
API_BASE = os.environ.get("OPENROUTER_BASE_URL", API_BASE_URL)
MODEL    = os.environ.get("OPENROUTER_MODEL", AGENT_MODEL)
client = OpenAI(base_url=API_BASE, api_key=OPENROUTER_API_KEY)

WORKSPACE = Path(WORK_BASE_DIR).expanduser().resolve()


class AgentLoop:

    def __init__(self, bus: MessageBus, tools: ToolRegistry,
                 ctx: ContextBuilder, sessions: SessionManager):
        self.bus = bus
        self.tools = tools
        self.ctx = ctx
        self.sessions = sessions

    async def run(self):
        """持续监听并处理消息"""
        while True:
            try:
                msg = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            # 处理消息
            session = self.sessions.get_or_create(msg.session_key)
            history = session.get_history(max_messages=50)
            messages = self.ctx.build_messages(history, msg.content)

            reply = await self._react_loop(messages)

            # 保存到 session
            session.messages.append({"role": "user", "content": msg.content,
                                      "timestamp": datetime.now().isoformat()})
            session.messages.append({"role": "assistant", "content": reply,
                                      "timestamp": datetime.now().isoformat()})
            self.sessions.save(session)

            # 发回消息（通过 Bus）
            await self.bus.publish_outbound(OutboundMessage(
                channel=msg.channel, chat_id=msg.chat_id, content=reply,
            ))


    async def _react_loop(self, messages: list[dict]) -> str:
        for _ in range(10):
            resp = client.chat.completions.create(
                model=MODEL, messages=messages,
                tools=self.tools.get_definitions() or None, temperature=0.1,
            )
            m = resp.choices[0].message
            if m.tool_calls:
                messages.append({"role": "assistant", "content": m.content, "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in m.tool_calls
                ]})
                for tc in m.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = await self.tools.execute(tc.function.name, args)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return m.content or ""
        return "Max iterations reached."