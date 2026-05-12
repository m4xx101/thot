#!/usr/bin/env python3
"""
boot-thot/hook.py — Gateway boot hook for THOT identity system.

Place at: ~/.hermes/hermes-agent/gateway/builtin_hooks/boot-thot/hook.py
Sends a one-time welcome message when a user first connects after install.
"""
import json
from pathlib import Path
from datetime import datetime
from hermes_constants import get_hermes_home


SENTINEL = get_hermes_home() / ".thot_welcome_sent"


def _should_send():
    """Check if welcome should be sent. Only once per install/skin-update."""
    if SENTINEL.exists():
        try:
            data = json.loads(SENTINEL.read_text())
            skin_path = get_hermes_home() / "skins" / "thot.yaml"
            if skin_path.exists():
                skin_mtime = skin_path.stat().st_mtime
                if skin_mtime > data.get("sent_at", 0):
                    return True
            return False
        except Exception:
            return True
    return True


def _mark_sent():
    """Write sentinel to prevent re-sending."""
    SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL.write_text(json.dumps({"sent_at": datetime.now().timestamp()}))


def build_welcome_message():
    """Build the THOT welcome message with live stats."""
    try:
        from hermes_cli.extended_banner import build_stats_line
        stats = build_stats_line()
    except Exception:
        stats = "THOT online."

    return (
        "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
        "⣿  THOT — Living Terminal Identity v1.0.0         ⣿\n"
        "⣿                                                  ⣿\n"
        f"⣿  {stats}\n"
        "⣿                                                  ⣿\n"
        "⣿  ⣿ Pet breathes during CLI API calls.            ⣿\n"
        "⣿  'show me my heatmap' for activity graph.        ⣿\n"
        "⣿  /help for commands. /skin to switch themes.      ⣿\n"
        "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n"
    )


def on_session_start(session):
    """Called by gateway when a new session starts."""
    if not _should_send():
        return

    try:
        msg = build_welcome_message()
        session.send_message(msg)
        _mark_sent()
    except Exception:
        pass  # Never break the gateway over a welcome message
