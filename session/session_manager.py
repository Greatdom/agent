import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Session:
    """一次对话的所有状态"""
    key: str
    messages: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_history(self, max_messages: int = 50) -> list[dict]:
        """取最近的 N 条消息，供 LLM 使用"""
        recent = self.messages[-max_messages:]
        # 确保从 user 消息开始（避免孤立的 tool_result）
        for i, m in enumerate(recent):
            if m.get("role") == "user":
                return recent[i:]
        return recent


class SessionManager:
    """管理多个会话的持久化"""

    def __init__(self, data_dir: Path):
        self.dir = data_dir / "sessions"
        self.dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Session] = {}

    def get_or_create(self, key: str) -> Session:
        if key in self._cache:
            return self._cache[key]
        session = self._load(key) or Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session):
        path = self.dir / f"{session.key.replace(':', '_')}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for msg in session.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self._cache[session.key] = session

    def _load(self, key: str) -> Session | None:
        path = self.dir / f"{key.replace(':', '_')}.jsonl"
        if not path.exists():
            return None
        messages = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                messages.append(json.loads(line))
        return Session(key=key, messages=messages)