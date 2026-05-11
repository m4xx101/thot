#!/usr/bin/env python3
"""
extended_banner.py — CRYPTEX data layer for extended banner sections.

Queries Hermes SessionDB (SQLite) and returns Rich-markup STRINGS.
NO Rich objects — TUI-safe passthrough for all outputs.

Usage:
    from hermes_cli.extended_banner import build_extended_sections
    for line in build_extended_sections():
        right_lines.append(line)  # Append to banner's right column
"""
import sqlite3
from pathlib import Path
from datetime import date, timedelta
from hermes_constants import get_hermes_home


def _get_db():
    """Return SessionDB path or None."""
    db = get_hermes_home() / "sessions.db"
    return db if db.exists() else None


def _query_heatmap(weeks=12):
    """Session counts per day for heatmap. Returns {date_iso: count}."""
    db = _get_db()
    if not db:
        return {}
    start = date.today() - timedelta(weeks=weeks)
    try:
        conn = sqlite3.connect(str(db))
        c = conn.cursor()
        c.execute(
            "SELECT DATE(created_at), COUNT(*) FROM sessions "
            "WHERE DATE(created_at) >= ? GROUP BY DATE(created_at)",
            (start.isoformat(),)
        )
        data = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        return data
    except Exception:
        return {}


def _query_stats():
    """{total, active_days, streak} or zeros."""
    db = _get_db()
    if not db:
        return {"total": 0, "active_days": 0, "streak": 0}
    try:
        conn = sqlite3.connect(str(db))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sessions")
        total = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(DISTINCT DATE(created_at)) FROM sessions")
        active_days = c.fetchone()[0] or 0

        today = date.today()
        streak = 0
        for i in range(365):
            day = today - timedelta(days=i)
            c.execute("SELECT COUNT(*) FROM sessions WHERE DATE(created_at)=?", (day.isoformat(),))
            if c.fetchone()[0] > 0:
                streak += 1
            else:
                break
        conn.close()
        return {"total": total, "active_days": active_days, "streak": streak}
    except Exception:
        return {"total": 0, "active_days": 0, "streak": 0}


def _count_checkpoints():
    """Count filesystem checkpoints."""
    d = get_hermes_home() / "checkpoints"
    return len(list(d.iterdir())) if d.is_dir() else 0


def _get_heatmap_colors():
    """Read heatmap_colors from skin YAML, or return defaults."""
    try:
        from hermes_cli.skin_engine import get_active_skin
        import yaml
        skin = get_active_skin()
        path = get_hermes_home() / "skins" / f"{skin.name}.yaml"
        if path.exists():
            raw = yaml.safe_load(open(path)) or {}
            return raw.get("heatmap_colors", {})
    except Exception:
        pass
    return {"empty":"#333333","level_1":"#993300","level_2":"#CC4400","level_3":"#FF6600","level_4":"#FF8800"}


def _render_block(count, max_count, c):
    """Rich-markup heatmap cell."""
    if count == 0:
        return f"[dim {c['empty']}]·[/]"
    r = count / max(max_count, 1)
    if r < 0.25:   return f"[{c['level_1']}]░[/]"
    elif r < 0.50: return f"[{c['level_2']}]▒[/]"
    elif r < 0.75: return f"[{c['level_3']}]▓[/]"
    else:          return f"[bold {c['level_4']}]█[/]"


def build_heatmap():
    """12-week heatmap as Rich-markup string. None if no data."""
    data = _query_heatmap(12)
    if not data:
        return None
    c = _get_heatmap_colors()
    mx = max(data.values()) if data else 1
    today = date.today()
    start = today - timedelta(weeks=12)

    monday = start - timedelta(days=start.weekday())
    labels = ["Mo","Tu","We","Th","Fr","Sa","Su"]
    lines = []
    for dow in range(7):
        row = f"[dim {c['empty']}]{labels[dow]}[/] "
        for w in range(12):
            day = monday + timedelta(weeks=w, days=dow)
            cnt = data.get(day.isoformat(), 0)
            row += _render_block(cnt, mx, c) + " "
        lines.append(row)
    return "\n".join(lines)


def build_stats_line():
    """Rich-markup stats summary."""
    s = _query_stats()
    cp = _count_checkpoints()
    a, d = "#FF6600", "#663300"
    parts = [
        f"[bold {a}]{s['total']}[/] [dim {d}]sessions[/]",
        f"[bold {a}]{s['active_days']}[/] [dim {d}]active days[/]",
    ]
    if s['streak'] > 1:
        fire = "🔥" if s['streak'] >= 7 else "⚡"
        parts.append(f"[bold {a}]{s['streak']}d[/] [dim {d}]streak {fire}[/]")
    if cp > 0:
        parts.append(f"[dim {d}]{cp} checkpoints[/]")
    return " · ".join(parts)


def build_personality_line():
    """Rich-markup skin + model line."""
    try:
        from hermes_cli.skin_engine import get_active_skin_name
        skin = get_active_skin_name()
    except Exception:
        skin = "default"
    try:
        import yaml
        config = yaml.safe_load(open(get_hermes_home()/"config.yaml")) or {}
        model = config.get("model",{}).get("default","unknown").split("/")[-1]
    except Exception:
        model = "unknown"
    return f"[dim #663300]skin:[/] [#FFAA00]{skin}[/]  [dim #663300]model:[/] [#FFAA00]{model}[/]"


def build_suggestions():
    """Contextual suggestion string. None if nothing to suggest."""
    s = _query_stats()
    if s['total'] == 0:
        return "[#FFAA00]First session? /help for commands, /skills to browse, /model to switch LLM.[/]"
    if s['streak'] >= 14:
        return "[#FFAA00]14d streak! Say 'save this as a skill' after complex tasks to build your arsenal.[/]"
    try:
        from hermes_cli.skin_engine import get_active_skin_name
        if get_active_skin_name() == "default":
            return "[#FFAA00]Default theme. Try /skin cryptex for animated pet + heatmap.[/]"
    except Exception:
        pass
    return None


def build_extended_sections():
    """Return list of Rich-markup strings for right column of main panel."""
    out = []
    hm = build_heatmap()
    if hm:
        out.append("")
        out.append(f"[bold #FF6600]Activity[/] [dim #663300]— 12 weeks[/]")
        out.append(hm)
    st = build_stats_line()
    if st:
        out.append("")
        out.append(st)
    pr = build_personality_line()
    if pr:
        out.append(pr)
    sg = build_suggestions()
    if sg:
        out.append("")
        out.append(sg)
    return out
