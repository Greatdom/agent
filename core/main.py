import asyncio
from datetime import datetime

from core.agent_loop import agent_loop, WORKSPACE
from core.content import ContextBuilder
from core.init_workspace import init_workspace
from session.session_manager import SessionManager, Session
from tool.exec_tool import ExecTool
from tool.read_file_tool import ReadFileTool
from tool.tool_registery import ToolRegistry
from tool.write_file_tool import WriteFileTool






# ── 主程序 ───────────────────────────────────────────

async def main():
    init_workspace()
    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())
    ctx = ContextBuilder(WORKSPACE)
    sessions = SessionManager(WORKSPACE)
    session = sessions.get_or_create("cli:direct")
    print("Mini Agent (输入 exit 退出)\n")


    messages = [{"role": "system", "content": "你是一个有帮助的AI助手。你可以使用工具来完成任务。"}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break
        except UnicodeDecodeError:
            # IDE 强制停止时可能触发，直接退出
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break
        if user_input == "/new":
            session = Session(key="cli:direct")
            sessions.save(session)
            print("New session started.\n")
            continue


        history = session.get_history(max_messages=50)
        messages = ctx.build_messages(history, user_input)

        reply = await agent_loop(messages, tools)

        # 保存本轮对话到 session
        session.messages.append({"role": "user", "content": user_input,
                                 "timestamp": datetime.now().isoformat()})
        session.messages.append({"role": "assistant", "content": reply,
                                 "timestamp": datetime.now().isoformat()})
        sessions.save(session)

        print(f"\nBot: {reply}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass