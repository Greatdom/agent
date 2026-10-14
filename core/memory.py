import json
from datetime import datetime
from pathlib import Path


class MemoryStore:
    """分层记忆"""

    def __init__(self, workspace: Path):
        mem_dir = workspace / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = mem_dir / "MEMORY.md"
        self.history_file = mem_dir / "history.jsonl"
        self.cursor_file = mem_dir / ".cursor"

    def read_memory(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_memory(self, content: str):
        self.memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str):
        cursor = self._next_cursor()
        record = {
            "cursor": cursor,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": entry.rstrip(),
        }
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.cursor_file.write_text(str(cursor), encoding="utf-8")

    def _next_cursor(self) -> int:
        if self.cursor_file.exists():
            return int(self.cursor_file.read_text(encoding="utf-8").strip()) + 1
        return 1