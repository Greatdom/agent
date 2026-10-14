# ── ReAct 循环 ───────────────────────────────────────
import json
import os
from pathlib import Path

from openai import OpenAI

from config.config import OPENROUTER_API_KEY, API_BASE_URL, AGENT_MODEL, WORK_BASE_DIR
from tool.tool_registery import ToolRegistry

API_BASE = os.environ.get("OPENROUTER_BASE_URL", API_BASE_URL)
MODEL    = os.environ.get("OPENROUTER_MODEL", AGENT_MODEL)
client = OpenAI(base_url=API_BASE, api_key=OPENROUTER_API_KEY)

WORKSPACE = Path(WORK_BASE_DIR).expanduser().resolve()

async def agent_loop(messages: list[dict], tools: ToolRegistry) -> str:
    tool_defs = tools.get_definitions()

    for _ in range(10):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages,# type: ignore[arg-type]
            tools=tool_defs or None,# type: ignore[arg-type]
            temperature=0.1,
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name,
                                  "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ],
            })
            for tc in msg.tool_calls:
                print(f"  [Tool] {tc.function.name}({tc.function.arguments[:80]})")
                args = json.loads(tc.function.arguments)
                result = await tools.execute(tc.function.name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            return msg.content or ""

    return "Max iterations reached."