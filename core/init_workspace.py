# ── 初始化工作区 ─────────────────────────────────────
from core.agent_loop import WORKSPACE


def init_workspace():
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "memory").mkdir(exist_ok=True)

    defaults = {
        "SOUL.md": "# Soul\n\n我是 Mini Agent，一个有帮助的 AI 助手。\n\n友善、简洁、准确。",
        "AGENTS.md": "# Agent Instructions\n\n- 先说意图，再调工具\n- 修改文件前先读取\n- 不确定时主动询问",
        "USER.md": "# User Profile\n\n（请编辑此文件来告诉 Bot 你的信息）",
    }
    for name, content in defaults.items():
        path = WORKSPACE / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")