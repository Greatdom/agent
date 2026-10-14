import asyncio


from core.agent_loop import agent_loop
from tool.exec_tool import ExecTool
from tool.read_file_tool import ReadFileTool
from tool.tool_registery import ToolRegistry
from tool.write_file_tool import WriteFileTool






# ── 主程序 ───────────────────────────────────────────

async def main():
    print("Mini Agent (输入 exit 退出)\n")

    tools = ToolRegistry()
    tools.register(ExecTool())
    tools.register(ReadFileTool())
    tools.register(WriteFileTool())

    messages = [{"role": "system", "content": "你是一个有帮助的AI助手。你可以使用工具来完成任务。"}]

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        reply = await agent_loop(messages, tools)
        messages.append({"role": "assistant", "content": reply})
        print(f"\nBot: {reply}\n")

if __name__ == "__main__":
    asyncio.run(main())