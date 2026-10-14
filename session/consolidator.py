import json

from openai import OpenAI

from core.memory import MemoryStore
from session.session_manager import Session


async def archive_old_messages(
    client: OpenAI, model: str,
    session: Session, memory: MemoryStore,
    keep_recent: int = 25,
):
    """只归档摘要，不改长期记忆文件。"""
    if len(session.messages) <= keep_recent:
        return

    old = session.messages[:-keep_recent]
    prompt = f"""Summarize the durable facts and decisions in this conversation.

{json.dumps(old, ensure_ascii=False, indent=2)[:8000]}

Return only a concise archival summary."""

    resp = client.chat.completions.create(
        model=model,
        messages=[ # type: ignore[arg-type]
            {"role": "system", "content": "You archive conversation history."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    summary = (resp.choices[0].message.content or "").strip()
    if summary:
        memory.append_history(summary)
        session.messages = session.messages[-keep_recent:]