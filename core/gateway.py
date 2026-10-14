import asyncio

from core.agent_loop import AgentLoop, WORKSPACE
from core.content import ContextBuilder
from core.init_workspace import init_workspace
from core.route_outbount import route_outbound
from message_bus.CLI_channel import CLIChannel
from message_bus.base_channel import BaseChannel
from message_bus.message_bus import MessageBus
from session.session_manager import SessionManager, Session
from tool.exec_tool import ExecTool
from tool.read_file_tool import ReadFileTool
from tool.tool_registery import ToolRegistry
from tool.write_file_tool import WriteFileTool


# ── 主程序 ───────────────────────────────────────────
async def run_gateway():
    init_workspace()
    bus = MessageBus()

    # 注册工具
    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    ctx = ContextBuilder(WORKSPACE)
    sessions = SessionManager(WORKSPACE)
    agent = AgentLoop(bus, tools, ctx, sessions)

    # 启用 Channels
    channels: dict[str, BaseChannel] = {"cli": CLIChannel(bus)}

    print(f"Gateway started. Channels: {list(channels.keys())}\n")

    # 并行运行所有组件
    await asyncio.gather(
        agent.run(),
        route_outbound(bus, channels),
        *[ch.start() for ch in channels.values()],
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_gateway())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass