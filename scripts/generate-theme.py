#!/usr/bin/env python3
"""
generate-theme.py — Dynamic theme generator for THOT.

Generates ALL visual assets based on user choices:
  - ASCII logo via pyfiglet (571 fonts) with themed gradient colors
  - Fallback centered box-art logo when pyfiglet unavailable
  - Hero art (geometric pattern) with themed colors
  - Randomized braille pet frames (unique per install) — centered
  - Custom pet from external file
  - Full color palette mapping (12 themes)

Usage:
    python3 generate-theme.py --name "MY AGENT" --palette cyberpunk
    python3 generate-theme.py --name "THOT" --palette fire --seed 42
    python3 generate-theme.py --pet-file ~/my-pet.txt --palette midnight
    python3 generate-theme.py --list-fonts
"""
import sys, subprocess, random, json, os, re

# ── Dependency management ────────────────────────

def _ensure_pyfiglet():
    """Return pyfiglet module or None if unavailable. Never crashes."""
    try:
        import pyfiglet; return pyfiglet
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyfiglet", "-q", "--break-system-packages"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30
        )
        import pyfiglet; return pyfiglet
    except Exception:
        pass
    # Try user install
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyfiglet", "-q", "--user"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30
        )
        import pyfiglet; return pyfiglet
    except Exception as e:
        print(f"[thot] pyfiglet unavailable ({e}), using box-art fallback", file=sys.stderr)
        return None


def _ensure_yaml():
    """Ensure pyyaml is available. Installs if needed, raises if impossible."""
    try:
        import yaml; return yaml
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyyaml", "-q", "--break-system-packages"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30
        )
        import yaml; return yaml
    except Exception:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyyaml", "-q", "--user"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30
        )
        import yaml; return yaml
    except Exception as e:
        print(f"[thot] FATAL: pyyaml unavailable ({e})", file=sys.stderr)
        print("[thot] Install manually: pip install pyyaml", file=sys.stderr)
        raise SystemExit(1) from e


# ── Full palette definitions (12 themes, all 20+ color keys) ──

PALETTES = {
    "fire": {
        "banner_border": "#CC3300", "banner_title": "#FFAA00", "banner_accent": "#FF6600",
        "banner_dim": "#663300", "banner_text": "#FFF0E0",
        "ui_accent": "#FF6600", "ui_label": "#FFAA00", "ui_ok": "#4caf50",
        "ui_error": "#ef5350", "ui_warn": "#ffa726",
        "prompt": "#FFF0E0", "input_rule": "#CC3300", "response_border": "#FF6600",
        "status_bar_bg": "#0A0A0A", "status_bar_text": "#C0C0C0", "status_bar_strong": "#FFAA00",
        "status_bar_dim": "#663300", "status_bar_good": "#8FBC8F", "status_bar_warn": "#FFAA00",
        "status_bar_bad": "#FF6600", "status_bar_critical": "#FF3300",
        "session_label": "#FFAA00", "session_border": "#663300",
    },
    "ocean": {
        "banner_border": "#2A6FB9", "banner_title": "#A9DFFF", "banner_accent": "#5DB8F5",
        "banner_dim": "#153C73", "banner_text": "#EAF7FF",
        "ui_accent": "#5DB8F5", "ui_label": "#A9DFFF", "ui_ok": "#4caf50",
        "ui_error": "#ef5350", "ui_warn": "#ffa726",
        "prompt": "#EAF7FF", "input_rule": "#2A6FB9", "response_border": "#5DB8F5",
        "status_bar_bg": "#0A0A0A", "status_bar_text": "#C0C0C0", "status_bar_strong": "#A9DFFF",
        "status_bar_dim": "#153C73", "status_bar_good": "#8FBC8F", "status_bar_warn": "#5DB8F5",
        "status_bar_bad": "#2A6FB9", "status_bar_critical": "#D94F4F",
        "session_label": "#A9DFFF", "session_border": "#153C73",
    },
    "forest": {
        "banner_border": "#2E7D32", "banner_title": "#A5D6A7", "banner_accent": "#66BB6A",
        "banner_dim": "#1B5E20", "banner_text": "#E8F5E9",
        "ui_accent": "#66BB6A", "ui_label": "#A5D6A7", "ui_ok": "#4caf50",
        "ui_error": "#ef5350", "ui_warn": "#ffa726",
        "prompt": "#E8F5E9", "input_rule": "#2E7D32", "response_border": "#66BB6A",
        "status_bar_bg": "#0A0A0A", "status_bar_text": "#C0C0C0", "status_bar_strong": "#A5D6A7",
        "status_bar_dim": "#1B5E20", "status_bar_good": "#8FBC8F", "status_bar_warn": "#66BB6A",
        "status_bar_bad": "#2E7D32", "status_bar_critical": "#EF5350",
        "session_label": "#A5D6A7", "session_border": "#1B5E20",
    },
    "cyberpunk": {
        "banner_border": "#00FFFF", "banner_title": "#FF00FF", "banner_accent": "#00FF00",
        "banner_dim": "#333333", "banner_text": "#FFFFFF",
        "ui_accent": "#00FF00", "ui_label": "#FF00FF", "ui_ok": "#00FF00",
        "ui_error": "#FF0055", "ui_warn": "#FFAA00",
        "prompt": "#FFFFFF", "input_rule": "#00FFFF", "response_border": "#FF00FF",
        "status_bar_bg": "#0A0A0A", "status_bar_text": "#C0C0C0", "status_bar_strong": "#00FFFF",
        "status_bar_dim": "#333333", "status_bar_good": "#00FF00", "status_bar_warn": "#FFAA00",
        "status_bar_bad": "#FF00FF", "status_bar_critical": "#FF0055",
        "session_label": "#00FFFF", "session_border": "#333333",
    },
    "mono": {
        "banner_border": "#555555", "banner_title": "#E6EDF3", "banner_accent": "#AAAAAA",
        "banner_dim": "#444444", "banner_text": "#C9D1D9",
        "ui_accent": "#AAAAAA", "ui_label": "#888888", "ui_ok": "#888888",
        "ui_error": "#CCCCCC", "ui_warn": "#999999",
        "prompt": "#C9D1D9", "input_rule": "#444444", "response_border": "#AAAAAA",
        "status_bar_bg": "#1F1F1F", "status_bar_text": "#C9D1D9", "status_bar_strong": "#E6EDF3",
        "status_bar_dim": "#777777", "status_bar_good": "#B5B5B5", "status_bar_warn": "#AAAAAA",
        "status_bar_bad": "#D0D0D0", "status_bar_critical": "#F0F0F0",
        "session_label": "#888888", "session_border": "#555555",
    },
    "midnight": {
        "banner_border": "#6366F1", "banner_title": "#C7D2FE", "banner_accent": "#818CF8",
        "banner_dim": "#312E81", "banner_text": "#EEF2FF",
        "ui_accent": "#818CF8", "ui_label": "#A5B4FC", "ui_ok": "#4ade80",
        "ui_error": "#f87171", "ui_warn": "#fbbf24",
        "prompt": "#EEF2FF", "input_rule": "#6366F1", "response_border": "#818CF8",
        "status_bar_bg": "#0F0F23", "status_bar_text": "#C7D2FE", "status_bar_strong": "#A5B4FC",
        "status_bar_dim": "#4338CA", "status_bar_good": "#86EFAC", "status_bar_warn": "#A5B4FC",
        "status_bar_bad": "#818CF8", "status_bar_critical": "#F87171",
        "session_label": "#A5B4FC", "session_border": "#4338CA",
    },
    "crimson": {
        "banner_border": "#E11D48", "banner_title": "#FECDD3", "banner_accent": "#FB7185",
        "banner_dim": "#4C0519", "banner_text": "#FFF1F2",
        "ui_accent": "#FB7185", "ui_label": "#FDA4AF", "ui_ok": "#4ade80",
        "ui_error": "#f87171", "ui_warn": "#fbbf24",
        "prompt": "#FFF1F2", "input_rule": "#E11D48", "response_border": "#FB7185",
        "status_bar_bg": "#0F0004", "status_bar_text": "#FECDD3", "status_bar_strong": "#FDA4AF",
        "status_bar_dim": "#881337", "status_bar_good": "#86EFAC", "status_bar_warn": "#FDA4AF",
        "status_bar_bad": "#FB7185", "status_bar_critical": "#F87171",
        "session_label": "#FDA4AF", "session_border": "#881337",
    },
    "amber": {
        "banner_border": "#D97706", "banner_title": "#FEF3C7", "banner_accent": "#F59E0B",
        "banner_dim": "#451A03", "banner_text": "#FFFBEB",
        "ui_accent": "#F59E0B", "ui_label": "#FCD34D", "ui_ok": "#4ade80",
        "ui_error": "#f87171", "ui_warn": "#fbbf24",
        "prompt": "#FFFBEB", "input_rule": "#D97706", "response_border": "#F59E0B",
        "status_bar_bg": "#0F0800", "status_bar_text": "#FEF3C7", "status_bar_strong": "#FCD34D",
        "status_bar_dim": "#78350F", "status_bar_good": "#86EFAC", "status_bar_warn": "#FCD34D",
        "status_bar_bad": "#F59E0B", "status_bar_critical": "#F87171",
        "session_label": "#FCD34D", "session_border": "#78350F",
    },
    "arctic": {
        "banner_border": "#0284C7", "banner_title": "#E0F2FE", "banner_accent": "#38BDF8",
        "banner_dim": "#0C4A6E", "banner_text": "#F0F9FF",
        "ui_accent": "#38BDF8", "ui_label": "#7DD3FC", "ui_ok": "#4ade80",
        "ui_error": "#f87171", "ui_warn": "#fbbf24",
        "prompt": "#F0F9FF", "input_rule": "#0284C7", "response_border": "#38BDF8",
        "status_bar_bg": "#081828", "status_bar_text": "#E0F2FE", "status_bar_strong": "#7DD3FC",
        "status_bar_dim": "#075985", "status_bar_good": "#86EFAC", "status_bar_warn": "#7DD3FC",
        "status_bar_bad": "#38BDF8", "status_bar_critical": "#F87171",
        "session_label": "#7DD3FC", "session_border": "#075985",
    },
    "matrix": {
        "banner_border": "#00FF41", "banner_title": "#00FF41", "banner_accent": "#00CC33",
        "banner_dim": "#003300", "banner_text": "#CCFFCC",
        "ui_accent": "#00CC33", "ui_label": "#00FF41", "ui_ok": "#00FF41",
        "ui_error": "#FF3333", "ui_warn": "#FFFF33",
        "prompt": "#CCFFCC", "input_rule": "#00FF41", "response_border": "#00CC33",
        "status_bar_bg": "#0A0A0A", "status_bar_text": "#00FF41", "status_bar_strong": "#00FF41",
        "status_bar_dim": "#003300", "status_bar_good": "#00FF41", "status_bar_warn": "#FFFF33",
        "status_bar_bad": "#00CC33", "status_bar_critical": "#FF3333",
        "session_label": "#00FF41", "session_border": "#003300",
    },
    "sunset": {
        "banner_border": "#EA580C", "banner_title": "#FED7AA", "banner_accent": "#F97316",
        "banner_dim": "#431407", "banner_text": "#FFF7ED",
        "ui_accent": "#F97316", "ui_label": "#FDBA74", "ui_ok": "#4ade80",
        "ui_error": "#f87171", "ui_warn": "#fbbf24",
        "prompt": "#FFF7ED", "input_rule": "#EA580C", "response_border": "#F97316",
        "status_bar_bg": "#0F0600", "status_bar_text": "#FED7AA", "status_bar_strong": "#FDBA74",
        "status_bar_dim": "#7C2D12", "status_bar_good": "#86EFAC", "status_bar_warn": "#FDBA74",
        "status_bar_bad": "#F97316", "status_bar_critical": "#F87171",
        "session_label": "#FDBA74", "session_border": "#7C2D12",
    },
    "void": {
        "banner_border": "#374151", "banner_title": "#F3F4F6", "banner_accent": "#6B7280",
        "banner_dim": "#1F2937", "banner_text": "#D1D5DB",
        "ui_accent": "#6B7280", "ui_label": "#9CA3AF", "ui_ok": "#6B7280",
        "ui_error": "#EF4444", "ui_warn": "#F59E0B",
        "prompt": "#D1D5DB", "input_rule": "#374151", "response_border": "#6B7280",
        "status_bar_bg": "#111827", "status_bar_text": "#9CA3AF", "status_bar_strong": "#F3F4F6",
        "status_bar_dim": "#374151", "status_bar_good": "#9CA3AF", "status_bar_warn": "#F59E0B",
        "status_bar_bad": "#6B7280", "status_bar_critical": "#EF4444",
        "session_label": "#9CA3AF", "session_border": "#374151",
    },
}


# ── Gradient extraction ──────────────────────────

def _palette_gradient(palette_name):
    """Extract a 6-color gradient from the palette for logo art."""
    p = PALETTES[palette_name]
    return [
        p["banner_border"],
        p["banner_accent"],
        p["banner_title"],
        p["banner_accent"],
        p["banner_text"],
        p["banner_dim"],
    ]


# ── Logo generation ──────────────────────────────

def _box_logo(name, palette_name):
    """Clean centered box-art logo — works without any dependencies."""
    p = PALETTES[palette_name]
    name_upper = name.upper().strip()[:14]
    width = len(name_upper) + 4  # 2 spaces padding + name
    border = p["banner_border"]
    title = p["banner_title"]
    accent = p["banner_accent"]
    dim = p["banner_dim"]

    top_border = "╔" + "═" * width + "╗"
    mid_line = "║  " + name_upper + "  ║"
    bot_border = "╚" + "═" * width + "╝"

    return "\n".join([
        f"  [{border}]{top_border}[/]",
        f"  [{title}]{mid_line}[/]",
        f"  [{border}]{bot_border}[/]",
        f"  [{accent}]v{getattr(sys.modules.get('__main__', None), 'VERSION', '1.1')} · {palette_name} mode[/]",
        f"  [{dim}]─── living terminal identity ───[/]",
    ])


def generate_logo(name, palette_name, font="banner3-D"):
    """Generate Rich-markup ASCII logo with themed gradient colors."""
    pf = _ensure_pyfiglet()
    if pf is None:
        return _box_logo(name, palette_name)
    try:
        art = pf.figlet_format(name, font=font)
    except Exception:
        try:
            art = pf.figlet_format(name, font="standard")
        except Exception:
            return _box_logo(name, palette_name)

    lines = [l for l in art.split("\n") if l.strip()]
    gradient = _palette_gradient(palette_name)

    wrapped = []
    for i, line in enumerate(lines):
        c = gradient[min(i, len(gradient) - 1)]
        wrapped.append(f"  [{c}]{line.rstrip()}[/]")

    return "\n".join(wrapped)


# ── Hero generation ──────────────────────────────

HERO_TEMPLATES = {
    "scanner": [
        ('accent',  '     ╔{"═"*12}╗     '),
        ('accent',  '     ║  {icon} {name} {icon}  ║     '),
        ('title',   '     ╚{"═"*12}╝     '),
        ('title',   '        ▐▛{"▀"*6}▜▌        '),
        ('accent',  '       ▐▌  ⣿⣿⣿  ▐▌       '),
        ('accent',  '      ▐▌   ⣿⣿⣿   ▐▌      '),
        ('accent',  '     ▐▌    ⣿⣿⣿    ▐▌     '),
        ('title',   '    ▐▌     ⣿⣿⣿     ▐▌    '),
        ('accent',  '   ▐▌      ⣿⣿⣿      ▐▌   '),
        ('accent',  '  ▐▌       ⣿⣿⣿       ▐▌  '),
        ('title',   ' ▐▌        ⣿⣿⣿        ▐▌ '),
        ('accent',  '▐▙{"▄"*24}▟▌'),
        ('dim',     '      [scanning...]       '),
    ],
    "minimal": [
        ('accent',  '        ╔══╗        '),
        ('accent',  '        ║⣿⣿║        '),
        ('title',   '       ╔╝⣿⣿╚╗       '),
        ('title',   '       ║ ⣿⣿ ║       '),
        ('accent',  '      ╔╝ ⣿⣿ ╚╗      '),
        ('accent',  '      ║  ⣿⣿  ║      '),
        ('accent',  '     ╔╝  ⣿⣿  ╚╗     '),
        ('title',   '     ║   ⣿⣿   ║     '),
        ('dim',     '    [⣿ {name} online ⣿]  '),
    ],
    "wireframe": [
        ('accent',  '   ┌{"─"*10}┐   '),
        ('accent',  '   │ {name:^8} │   '),
        ('title',   '   ├{"─"*10}┤   '),
        ('accent',  '  ┌┘⣿⣿⣿⣿⣿⣿└┐  '),
        ('accent',  '  │ ⣿⣿⣿⣿⣿⣿ │  '),
        ('title',   '  │ ⣿⣿⣿⣿⣿⣿ │  '),
        ('accent',  '  │ ⣿⣿⣿⣿⣿⣿ │  '),
        ('title',   '  └┐⣿⣿⣿⣿⣿⣿┌┘  '),
        ('dim',     '   [scanning...]   '),
    ],
    "sleek": [
        ('accent',  '  ┌{"─"*14}┐  '),
        ('title',   '  │ {name:^12} │  '),
        ('accent',  '  └{"─"*14}┘  '),
        ('accent',  '     ╱{" "*10}╲     '),
        ('accent',  '    ╱  ⣿⣿⣿⣿  ╲    '),
        ('title',   '   ╱   ⣿⣿⣿⣿   ╲   '),
        ('accent',  '  ╱    ⣿⣿⣿⣿    ╲  '),
        ('dim',     '   [⣿ {name} active ⣿]  '),
    ],
    "classic": [
        ('border',  '   ╔{"═"*16}╗   '),
        ('accent',  '   ║  ⣿  {name:^8}  ⣿  ║   '),
        ('border',  '   ╚{"═"*16}╝   '),
        ('title',   '      │ ⣿⣿⣿⣿⣿⣿ │      '),
        ('accent',  '      │ ⣿⣿⣿⣿⣿⣿ │      '),
        ('title',   '      │ ⣿⣿⣿⣿⣿⣿ │      '),
        ('dim',     '     [system operational]    '),
    ],
}


def generate_hero(name, palette_name, style="scanner"):
    """Generate Rich-markup hero art with themed colors."""
    p = PALETTES[palette_name]
    color_map = {
        "accent": p["banner_accent"],
        "title": p["banner_title"],
        "dim": p["banner_dim"],
        "border": p["banner_border"],
    }
    icon = random.choice(["⚔", "⣿", "◆", "◈", "⬡", "⎔", "◉", "⌬"])

    template = HERO_TEMPLATES.get(style, HERO_TEMPLATES["scanner"])
    lines = []
    for color_key, tpl in template:
        c = color_map.get(color_key, p["banner_accent"])
        line = tpl
        line = re.sub(r'\{name(?::\^(\d+))?\}', lambda m: name[:int(m.group(1))].center(int(m.group(1))) if m.group(1) else name[:8], line)
        line = line.replace("{icon}", icon)
        line = re.sub(r'\{\"(.)\"\*(\d+)\}', lambda m: m.group(1) * int(m.group(2)), line)
        lines.append(f"  [{c}]{line}[/]")

    return "\n".join(lines)


# ── Pet generation ───────────────────────────────

_BRAILLE_BLOCKS = [
    "⠀", "⣀", "⣤", "⣶", "⣿", "⣾", "⣷", "⣧", "⣦",
    "⠉", "⠟", "⠿", "⠛", "⠋", "⠙", "⠛",
    "⣄", "⣠", "⣴", "⣼", "⣽",
]
_PET_SHAPES = [
    # Heartbeat (expanding/contracting)
    {"name": "heartbeat", "intensities": [0, 1, 2, 3, 4, 4, 3, 2]},
    # Wave
    {"name": "wave", "intensities": [0, 1, 2, 3, 2, 1, 0, 0]},
    # Burst
    {"name": "burst", "intensities": [0, 2, 4, 3, 1, 0, 2, 1]},
    # Slow pulse
    {"name": "pulse", "intensities": [0, 1, 1, 2, 2, 1, 1, 0]},
    # Lightning
    {"name": "lightning", "intensities": [0, 3, 4, 2, 3, 1, 4, 0]},
    # Double-tap (two pulses)
    {"name": "doubletap", "intensities": [0, 2, 4, 2, 0, 2, 4, 2]},
    # Glitch (random spikes)
    {"name": "glitch", "intensities": [0, 4, 1, 3, 0, 4, 2, 1]},
    # Ascend (rising intensity)
    {"name": "ascend", "intensities": [0, 1, 2, 3, 4, 3, 2, 1]},
]


def _center_frame(top_line, bot_line, width=10):
    """Center a 2-line pet frame within a fixed width."""
    top_pad = (width - len(top_line)) // 2
    bot_pad = (width - len(bot_line)) // 2
    return (
        " " * max(0, top_pad) + top_line + " " * max(0, width - len(top_line) - top_pad),
        " " * max(0, bot_pad) + bot_line + " " * max(0, width - len(bot_line) - bot_pad),
    )


def generate_pet_frames(seed=None, palette_name="fire", shape_idx=None, width=10):
    """Generate 8 centered braille pet frames with themed colors."""
    if seed is None:
        import time
        seed = int(time.time() * 1000) % 10000

    rng = random.Random(seed)
    if shape_idx is not None and 0 <= shape_idx < len(_PET_SHAPES):
        shape = _PET_SHAPES[shape_idx]
    else:
        shape = rng.choice(_PET_SHAPES)
    intensities = shape["intensities"]

    p = PALETTES[palette_name]
    top_color = p["banner_accent"]
    bot_color = p["banner_dim"]
    dim_char = p["banner_dim"]

    frames = []
    for intensity in intensities:
        # Build raw braille lines
        top_line = ""
        bot_line = ""
        for col in range(6):
            idx = min(intensity + rng.randint(0, 1), len(_BRAILLE_BLOCKS) - 1)
            top_line += _BRAILLE_BLOCKS[idx]
        for col in range(6):
            idx = max(0, min(intensity - 1 + rng.randint(0, 1), len(_BRAILLE_BLOCKS) - 1))
            bot_line += _BRAILLE_BLOCKS[idx]

        # Center the frame
        tc, bc = _center_frame(top_line, bot_line, width)
        frames.append(f"[{top_color}]{tc}[/]\n[{bot_color}]{bc}[/]")

    # Emoji fallback (also centered)
    emojis = ["🔥", "⚡", "💀", "⣿", "⌁", "⚔", "🧿", "◉", "✦", "◈"]
    fallback = []
    for intensity in intensities:
        n = max(1, min(intensity + 1, 3))
        chars = "".join(rng.sample(emojis, n))
        dots = "." * n
        tc, bc = _center_frame(chars, dots, width)
        fallback.append(f"[{top_color}]{tc}[/]\n[{bot_color}]{bc}[/]")

    return frames, fallback, shape["name"]


def load_pet_from_file(filepath, palette_name="fire", width=10):
    """Load custom pet frames from a text file.

    Format: one frame per 2 lines (top then bottom), frames separated by blank line.
    Braille/emoji characters only — no Rich markup needed.
    """
    p = PALETTES[palette_name]
    top_color = p["banner_accent"]
    bot_color = p["banner_dim"]

    with open(filepath) as f:
        raw = f.read().strip()

    # Split into frames (blank-line separated pairs)
    chunks = [c.strip() for c in raw.split("\n\n") if c.strip()]
    frames = []
    fallback = []

    for chunk in chunks:
        lines = [l.rstrip() for l in chunk.split("\n") if l.strip()]
        if len(lines) >= 2:
            top_line = lines[0][:width]
            bot_line = lines[1][:width]
            tc, bc = _center_frame(top_line, bot_line, width)
            frames.append(f"[{top_color}]{tc}[/]\n[{bot_color}]{bc}[/]")
            fallback.append(f"[{top_color}]{tc}[/]\n[{bot_color}]{bc}[/]")

    if len(frames) < 2:
        raise ValueError(f"Custom pet must have at least 2 frames (got {len(frames)})")

    return frames, fallback, "custom"


# ── Full theme application ───────────────────────

def apply_theme(skin_path, agent_name, palette_name, pet_seed=None, pet_file=None):
    """Apply a full theme to a skin YAML file — regenerates everything."""
    yaml = _ensure_yaml()  # auto-installs if needed

    with open(skin_path) as f:
        skin = yaml.safe_load(f) or {}

    # 1. Apply ALL colors (ALWAYS succeeds)
    if palette_name in PALETTES:
        skin["colors"].update(PALETTES[palette_name])

    # 2. Generate and apply logo (non-fatal)
    try:
        logo = generate_logo(agent_name, palette_name)
        skin["banner_logo"] = logo + "\n"
    except Exception as e:
        print(f"[thot] logo generation failed: {e}", file=sys.stderr)

    # 3. Generate and apply hero (non-fatal)
    try:
        hero_styles = list(HERO_TEMPLATES.keys())
        hero_style = hero_styles[hash(agent_name + palette_name) % len(hero_styles)]
        hero = generate_hero(agent_name, palette_name, hero_style)
        skin["banner_hero"] = hero + "\n"
    except Exception as e:
        print(f"[thot] hero generation failed: {e}", file=sys.stderr)

    # 4. Generate and apply pet frames (non-fatal)
    pet_name = "random"
    try:
        if pet_file and os.path.isfile(pet_file):
            frames, fallback, pet_name = load_pet_from_file(pet_file, palette_name)
        else:
            if pet_seed is None:
                import time
                pet_seed = int(time.time() * 1000) % 10000
            frames, fallback, pet_name = generate_pet_frames(pet_seed, palette_name)
        skin["spinner"]["pet_frames"] = frames
        skin["spinner"]["pet_fallback"] = fallback
    except Exception as e:
        print(f"[thot] pet generation failed: {e}", file=sys.stderr)

    # 5. Apply branding
    skin["branding"]["agent_name"] = agent_name
    skin["branding"]["welcome"] = f"⣿ {agent_name} online. Scanner active. Forge is hot."
    skin["branding"]["goodbye"] = "⣿ Signal lost."
    skin["branding"]["response_label"] = f" ⣿ {agent_name} "
    skin["branding"]["help_header"] = f"(⣿) {agent_name} Commands"

    # 6. Update title format for the agent name
    skin["branding"]["title_format"] = (
        f"Re: Thot (thot.m4xx.cfd) — {agent_name} v{{version}} ({{release}}) · us {{upstream}}"
    )

    # 7. Update spinner faces to match theme
    icon_set = random.choice([
        ["(⣿)", "(⌁)", "(⚔)", "(🔥)", "(💀)"],
        ["(◉)", "(◌)", "(◬)", "(⬤)", "(◈)"],
        ["(✦)", "(▲)", "(◇)", "(⌁)", "(◈)"],
    ])
    skin["spinner"]["waiting_faces"] = icon_set
    skin["spinner"]["thinking_faces"] = icon_set[:4]

    with open(skin_path, "w") as f:
        yaml.dump(skin, f, default_flow_style=False, allow_unicode=True)

    return {
        "skin": skin_path,
        "name": agent_name,
        "palette": palette_name,
        "pet": pet_name,
        "seed": pet_seed,
    }


# ── CLI ──────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="THOT Theme Generator")
    ap.add_argument("--name", default="THOT", help="Agent name")
    ap.add_argument("--palette", default="fire", choices=list(PALETTES.keys()),
                    help="Color theme (12 options)")
    ap.add_argument("--seed", type=int, help="Pet seed (random if not set)")
    ap.add_argument("--skin", help="Skin YAML path to modify")
    ap.add_argument("--pet-file", help="Path to custom pet frames file")
    ap.add_argument("--list-fonts", action="store_true")
    ap.add_argument("--list-palettes", action="store_true", help="List all palette names")
    ap.add_argument("--list-pets", action="store_true", help="List built-in pet shapes")
    ap.add_argument("--output-logo", action="store_true", help="Print logo only")
    ap.add_argument("--output-hero", action="store_true", help="Print hero only")
    ap.add_argument("--output-pet", action="store_true", help="Print pet frames only")
    args = ap.parse_args()

    if args.list_palettes:
        for name in PALETTES:
            p = PALETTES[name]
            print(f"  {name:12s}  border={p['banner_border']}  title={p['banner_title']}  accent={p['banner_accent']}")
        return

    if args.list_pets:
        for i, s in enumerate(_PET_SHAPES):
            print(f"  [{i}] {s['name']:12s}  intensities={s['intensities']}")
        return

    if args.list_fonts:
        pf = _ensure_pyfiglet()
        if pf is None:
            print("pyfiglet not available — only box-art fallback is available")
            return
        fonts = sorted(pf.FigletFont.getFonts())
        print(f"{len(fonts)} fonts available (first 20):")
        for f in fonts[:20]:
            print(f"  {f}")
        return

    if args.output_logo:
        print(generate_logo(args.name, args.palette))
        return

    if args.output_hero:
        print(generate_hero(args.name, args.palette))
        return

    if args.output_pet:
        if args.pet_file and os.path.isfile(args.pet_file):
            frames, _, name = load_pet_from_file(args.pet_file, args.palette)
        else:
            frames, _, name = generate_pet_frames(args.seed, args.palette)
        print(f"Pet: {name} ({len(frames)} frames)")
        for i, f in enumerate(frames):
            print(f"--- Frame {i} ---\n{f}\n")
        return

    if args.skin:
        result = apply_theme(args.skin, args.name, args.palette, args.seed, args.pet_file)
        print(json.dumps({
            "status": "ok",
            "skin": result["skin"],
            "name": result["name"],
            "palette": result["palette"],
            "pet": result["pet"],
            "seed": result["seed"] or "random",
        }))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
