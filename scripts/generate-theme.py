#!/usr/bin/env python3
"""
generate-theme.py — Dynamic theme generator for THOT.

Generates ALL visual assets based on user choices:
  - ASCII logo via pyfiglet (571 fonts) with themed gradient colors
  - Hero art (geometric pattern) with themed colors
  - Randomized braille pet frames (unique per install)
  - Full color palette mapping for all 30+ color keys

Usage:
    python3 generate-theme.py --name "MY AGENT" --palette cyberpunk
    python3 generate-theme.py --name "THOT" --palette fire --seed 42
    python3 generate-theme.py --list-fonts
"""
import sys, subprocess, random, hashlib, json, os
from pathlib import Path


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
    except Exception as e:
        print(f"[thot] pyfiglet unavailable ({e}), using text fallback", file=sys.stderr)
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
    except Exception as e:
        print(f"[thot] FATAL: pyyaml unavailable ({e})", file=sys.stderr)
        print("[thot] Install manually: pip install pyyaml --break-system-packages", file=sys.stderr)
        raise SystemExit(1) from e


# ── Full palette definitions (all 30+ keys) ──────

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

def _text_logo(name, palette_name):
    """Pure-Python fallback logo — works without pyfiglet."""
    p = PALETTES[palette_name]
    name_upper = name.upper().strip()
    LETTERS_5X5 = {
        'A': [' ███ ', '█   █', '█████', '█   █', '█   █'],
        'B': ['████ ', '█   █', '████ ', '█   █', '████ '],
        'C': [' ████', '█    ', '█    ', '█    ', ' ████'],
        'D': ['████ ', '█   █', '█   █', '█   █', '████ '],
        'E': ['█████', '█    ', '████ ', '█    ', '█████'],
        'F': ['█████', '█    ', '████ ', '█    ', '█    '],
        'G': [' ████', '█    ', '█  ██', '█   █', ' ████'],
        'H': ['█   █', '█   █', '█████', '█   █', '█   █'],
        'I': ['█████', '  █  ', '  █  ', '  █  ', '█████'],
        'J': ['█████', '   █ ', '   █ ', '█  █ ', ' ██  '],
        'K': ['█   █', '█  █ ', '███  ', '█  █ ', '█   █'],
        'L': ['█    ', '█    ', '█    ', '█    ', '█████'],
        'M': ['█   █', '██ ██', '█ █ █', '█   █', '█   █'],
        'N': ['█   █', '██  █', '█ █ █', '█  ██', '█   █'],
        'O': [' ███ ', '█   █', '█   █', '█   █', ' ███ '],
        'P': ['████ ', '█   █', '████ ', '█    ', '█    '],
        'Q': [' ███ ', '█   █', '█ █ █', '█  █ ', ' ██ █'],
        'R': ['████ ', '█   █', '████ ', '█  █ ', '█   █'],
        'S': [' ████', '█    ', ' ███ ', '    █', '████ '],
        'T': ['█████', '  █  ', '  █  ', '  █  ', '  █  '],
        'U': ['█   █', '█   █', '█   █', '█   █', ' ███ '],
        'V': ['█   █', '█   █', ' █ █ ', ' █ █ ', '  █  '],
        'W': ['█   █', '█   █', '█ █ █', '██ ██', '█   █'],
        'X': ['█   █', ' █ █ ', '  █  ', ' █ █ ', '█   █'],
        'Y': ['█   █', ' █ █ ', '  █  ', '  █  ', '  █  '],
        'Z': ['█████', '   █ ', '  █  ', ' █   ', '█████'],
        ' ': ['     ', '     ', '     ', '     ', '     '],
        '-': ['     ', '     ', '█████', '     ', '     '],
        '_': ['     ', '     ', '     ', '     ', '█████'],
    }
    gradient = _palette_gradient(palette_name)
    lines = ['', '', '', '', '']
    for i, ch in enumerate(name_upper[:8]):
        glyph = LETTERS_5X5.get(ch, LETTERS_5X5.get(' ', ['     ']*5))
        c = gradient[min(i, len(gradient) - 1)]
        for row in range(5):
            lines[row] += f'[{c}]{glyph[row]}[/] '
    return '\n'.join(lines)


def generate_logo(name, palette_name, font="banner3-D"):
    """Generate Rich-markup ASCII logo with themed gradient colors."""
    pf = _ensure_pyfiglet()
    if pf is None:
        return _text_logo(name, palette_name)
    try:
        art = pf.figlet_format(name, font=font)
    except Exception:
        try:
            art = pf.figlet_format(name, font="standard")
        except Exception:
            return _text_logo(name, palette_name)

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
        # Expand {═*12} → ════════════, {▀*6} → ▀▀▀▀▀▀
        import re
        line = tpl
        line = re.sub(r'\{name(?::\^(\d+))?\}', lambda m: name[:int(m.group(1))].center(int(m.group(1))) if m.group(1) else name[:8], line)
        line = line.replace("{icon}", icon)
        # Handle {"="*N} patterns
        line = re.sub(r'\{"(.)"\*(\d+)\}', lambda m: m.group(1) * int(m.group(2)), line)
        lines.append(f"  [{c}]{line}[/]")

    return "\n".join(lines)


# ── Pet generation ───────────────────────────────

# Braille building blocks
_BRAILLE_BLOCKS = [
    "⠀", "⣀", "⣤", "⣶", "⣿", "⣾", "⣷", "⣧", "⣦",
    "⠉", "⠟", "⠿", "⠛", "⠋", "⠙", "⠛",
    "⣄", "⣠", "⣴", "⣼", "⣽",
]
_PET_SHAPES = [
    # Heartbeat shape (expanding/contracting)
    [0, 1, 2, 3, 4, 4, 3, 2],
    # Wave shape
    [0, 1, 2, 3, 2, 1, 0, 0],
    # Burst shape
    [0, 2, 4, 3, 1, 0, 2, 1],
    # Slow pulse
    [0, 1, 1, 2, 2, 1, 1, 0],
    # Lightning
    [0, 3, 4, 2, 3, 1, 4, 0],
]


def generate_pet_frames(seed=None, palette_name="fire"):
    """Generate 8 random braille pet frames with themed colors."""
    if seed is None:
        import time
        seed = int(time.time() * 1000) % 10000

    rng = random.Random(seed)
    shape = rng.choice(_PET_SHAPES)

    p = PALETTES[palette_name]
    top_color = p["banner_accent"]
    bot_color = p["banner_dim"]

    frames = []
    for intensity in shape:
        # Build top and bottom lines from braille blocks
        top_line = ""
        bot_line = ""
        for col in range(6):
            idx = min(intensity + rng.randint(0, 1), len(_BRAILLE_BLOCKS) - 1)
            top_line += _BRAILLE_BLOCKS[idx]
        for col in range(6):
            idx = max(0, min(intensity - 1 + rng.randint(0, 1), len(_BRAILLE_BLOCKS) - 1))
            bot_line += _BRAILLE_BLOCKS[idx]

        frames.append(f"[{top_color}]{top_line}[/]\n[{bot_color}]{bot_line}[/]")

    # Generate emoji fallback
    emojis = ["🔥", "⚡", "💀", "⣿", "⌁", "⚔", "🧿", "◉"]
    fallback = []
    for intensity in shape:
        n = max(1, min(intensity + 1, 3))
        chars = "".join(rng.sample(emojis, n))
        fallback.append(f"[{top_color}]{chars.center(6)}[/]\n[{bot_color}]{('.'*n).center(6)}[/]")

    return frames, fallback


# ── Full theme application ───────────────────────

def apply_theme(skin_path, agent_name, palette_name, pet_seed=None):
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
    try:
        if pet_seed is None:
            import time
            pet_seed = int(time.time() * 1000) % 10000
        frames, fallback = generate_pet_frames(pet_seed, palette_name)
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

    return skin_path


# ── CLI ──────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="THOT Theme Generator")
    ap.add_argument("--name", default="THOT", help="Agent name")
    ap.add_argument("--palette", default="fire", choices=list(PALETTES.keys()))
    ap.add_argument("--seed", type=int, help="Pet seed (random if not set)")
    ap.add_argument("--skin", help="Skin YAML path to modify")
    ap.add_argument("--list-fonts", action="store_true")
    ap.add_argument("--output-logo", action="store_true", help="Print logo only")
    ap.add_argument("--output-hero", action="store_true", help="Print hero only")
    ap.add_argument("--output-pet", action="store_true", help="Print pet frames only")
    args = ap.parse_args()

    if args.list_fonts:
        pf = _ensure_pyfiglet()
        fonts = sorted(pf.FigletFont.getFonts())
        print(f"{len(fonts)} fonts:")
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
        frames, _ = generate_pet_frames(args.seed, args.palette)
        for i, f in enumerate(frames):
            print(f"--- Frame {i} ---\n{f}\n")
        return

    if args.skin:
        result = apply_theme(args.skin, args.name, args.palette, args.seed)
        print(json.dumps({
            "status": "ok",
            "skin": result,
            "name": args.name,
            "palette": args.palette,
            "seed": args.seed or "random",
        }))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
