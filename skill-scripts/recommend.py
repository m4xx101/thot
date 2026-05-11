#!/usr/bin/env python3
"""
recommend.py — Scan sessions, tool usage, time of day. Return top suggestion as JSON.
"""
import json, time
from pathlib import Path
from collections import Counter

HERMES_HOME = Path.home() / ".hermes"


def count_sessions():
    d = HERMES_HOME / "sessions"
    return sum(1 for f in d.iterdir() if f.suffix in (".json", ".jsonl")) if d.is_dir() else 0


def detect_tool_usage():
    d = HERMES_HOME / "sessions"
    if not d.is_dir():
        return Counter()
    c = Counter()
    for f in sorted(d.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
        try:
            txt = f.read_text()
            for tool in ["terminal", "web_search", "delegate_task", "read_file",
                         "write_file", "patch", "browser_navigate", "vision_analyze",
                         "memory", "execute_code", "todo", "session_search"]:
                if f'"name": "{tool}"' in txt:
                    c[tool] += txt.count(f'"name": "{tool}"')
        except Exception:
            pass
    return c


def generate():
    recs = []
    sessions = count_sessions()
    tools = detect_tool_usage()
    emoji_map = {
        "delegate_task": "🧠", "terminal": "⚔", "web_search": "🔎",
        "read_file": "📖", "write_file": "✏️", "patch": "🔧",
        "browser_navigate": "🌐", "vision_analyze": "👁️",
        "memory": "🧿", "execute_code": "💻", "todo": "📋",
        "session_search": "🔍"
    }

    for tool, cnt in tools.most_common(3):
        if cnt >= 5 and tool in emoji_map:
            recs.append({
                "type": "tool_emoji", "tool": tool, "count": cnt,
                "emoji": emoji_map[tool],
                "action": f"evolve --set tool_emojis.{tool} '{emoji_map[tool]}'"
            })

    if sessions >= 10:
        recs.append({
            "type": "refresh",
            "reason": f"{sessions} sessions — colors may feel stale.",
            "action": "evolve --palette-shift warm"
        })

    h = time.localtime().tm_hour
    if h >= 20 or h < 6:
        recs.append({
            "type": "dark_mode",
            "reason": f"{h}:00 — nighttime.",
            "action": "evolve --set-palette dark"
        })

    return recs[:1]  # Only the strongest


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
