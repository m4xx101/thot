#!/usr/bin/env python3
"""
generate-art.py — Agentic ASCII art generator for CRYPTEX skins.

Uses pyfiglet (571 fonts) for text banners. Auto-installs if missing.
No built-in font — relies on pyfiglet for quality output.

Usage:
    python3 generate-art.py "CRYPTEX" logo --font banner3-D
    python3 generate-art.py "CRYPTEX" hero --style scanner
    python3 generate-art.py --list-fonts
"""
import sys, subprocess


def _ensure_pyfiglet():
    try:
        import pyfiglet
        return pyfiglet
    except ImportError:
        print("Installing pyfiglet...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfiglet", "-q", "--break-system-packages"])
        import pyfiglet
        return pyfiglet


def logo(text, font="banner3-D"):
    pf = _ensure_pyfiglet()
    art = pf.figlet_format(text, font=font)
    lines = art.split("\n")
    gradient = ["#FF0000", "#FF2200", "#FF4400", "#FF6600", "#FF8800", "#FFAA00", "#FFCC00"]
    for i, line in enumerate(lines):
        c = gradient[min(i, len(gradient) - 1)]
        print(f"  [{c}]{line.rstrip()}[/]")
    print(f"\n[dim #663300]{len(lines)} lines, {max(len(l) for l in lines)} chars wide[/]")


def hero(style="scanner"):
    patterns = {
        "scanner": [
            '[#CC3300]     ╔══════════════╗     [/]',
            '[#CC3300]     ║  ⚔ CRYPTEX ⚔  ║     [/]',
            '[#FF4400]     ╚══════════════╝     [/]',
            '[#FF4400]        ▐▛▀▀▀▀▀▀▜▌        [/]',
            '[#FF6600]       ▐▌  ⣿⣿⣿  ▐▌       [/]',
            '[#FF6600]      ▐▌   ⣿⣿⣿   ▐▌      [/]',
            '[#FF8800]     ▐▌    ⣿⣿⣿    ▐▌     [/]',
            '[#FF8800]    ▐▌     ⣿⣿⣿     ▐▌    [/]',
            '[#FFAA00]   ▐▌      ⣿⣿⣿      ▐▌   [/]',
            '[#FFAA00]  ▐▌       ⣿⣿⣿       ▐▌  [/]',
            '[#FFCC00] ▐▌        ⣿⣿⣿        ▐▌ [/]',
            '[#FFCC00]▐▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟▌[/]',
            '[dim #663300]      [scanning...]       [/]',
        ],
        "minimal": [
            '[#FF6600]        ╔══╗        [/]',
            '[#FF6600]        ║⣿⣿║        [/]',
            '[#FF8800]       ╔╝⣿⣿╚╗       [/]',
            '[#FF8800]       ║ ⣿⣿ ║       [/]',
            '[#FFAA00]      ╔╝ ⣿⣿ ╚╗      [/]',
            '[#FFAA00]      ║  ⣿⣿  ║      [/]',
            '[#FFCC00]     ╔╝  ⣿⣿  ╚╗     [/]',
            '[#FFCC00]     ║   ⣿⣿   ║     [/]',
            '[dim #663300]    [⣿ forge online ⣿]  [/]',
        ],
    }
    for line in patterns.get(style, [f"[#FF6600]{style}[/]"]):
        print(line)


def list_fonts():
    pf = _ensure_pyfiglet()
    fonts = sorted(pf.FigletFont.getFonts())
    print(f"{len(fonts)} fonts available. Top 20:")
    for f in fonts[:20]:
        print(f"  {f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--list-fonts":
        list_fonts()
    elif len(sys.argv) >= 3:
        text, mode = sys.argv[1], sys.argv[2]
        if mode == "logo":
            logo(text, sys.argv[3] if len(sys.argv) > 3 else "banner3-D")
        elif mode == "hero":
            hero(sys.argv[3] if len(sys.argv) > 3 else "scanner")
