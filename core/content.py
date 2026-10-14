from datetime import datetime
from pathlib import Path

"""
System Prompt = 身份
              + AGENTS.md / SOUL.md / USER.md
              + 内置 Tool Contract
              + 非模板的 MEMORY.md
              + Always Skills / Skills 摘要
              + 未被 Dream 处理的 Recent History
              + 当前 Session 的归档摘要（如果有）
"""

class ContextBuilder:
    """组装 System Prompt"""

    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md"]

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def build_system_prompt(self) -> str:
        parts = [self._get_identity()]

        # 加载 Bootstrap 文件,用户可编辑的个性化文件
        for filename in self.BOOTSTRAP_FILES:
            path = self.workspace / filename
            if path.exists():
                content = path.read_text(encoding="utf-8")
                parts.append(f"## {filename}\n\n{content}")

        # 加载长期记忆
        memory_file = self.workspace / "memory" / "MEMORY.md"
        if memory_file.exists():
            memory = memory_file.read_text(encoding="utf-8")
            if memory.strip():
                parts.append(f"# Memory\n\n{memory}")

        return "\n\n---\n\n".join(parts)

    def _get_identity(self) -> str:
        return f"""# Mini Agent

你是一个有帮助的 AI 助手。

## Workspace
工作区: {self.workspace}
长期记忆: {self.workspace}/memory/MEMORY.md

## Guidelines
- 先说意图，再调工具
- 修改文件前先读取
- 任务模糊时主动询问"""

    def build_messages(
        self, history: list[dict], user_message: str
    ) -> list[dict]:
        """组装完整的 messages 列表"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        runtime = f"[Runtime Context]\nCurrent Time: {now}"

        return [
            {"role": "system", "content": self.build_system_prompt()},
            *history,
            {"role": "user", "content": f"{runtime}\n\n{user_message}"},
        ]