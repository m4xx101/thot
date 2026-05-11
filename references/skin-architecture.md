# Hermes Agent Skin Architecture

## How skins load

1. CLI startup → `cli.py` loads `config.yaml` → reads `display.skin`
2. `init_skin_from_config()` in `skin_engine.py` calls `load_skin(name)`
3. `load_skin()` checks `~/.hermes/skins/<name>.yaml` FIRST, then built-in
4. If user skin found → `_build_skin_config()` merges with defaults
5. `SkinConfig` dataclass: colors, spinner, branding, tool_prefix, tool_emojis, banner_logo, banner_hero
6. `build_welcome_banner()` in `banner.py` reads skin overrides

## CRYPTEX extended banner

`extended_banner.py` queries Hermes SessionDB (SQLite) for:
- 12-week session heatmap (rendered as colored block chars)
- Session statistics (total, active days, streak)
- Filesystem checkpoint count
- Active personality/model

Returns Rich-markup STRINGS only (TUI-safe). Appended to right column of main panel.

## Pet animation

Pet frames stored in `spinner.pet_frames` (braille) and `spinner.pet_fallback` (emoji).
KawaiiSpinner reads these during API calls. TERM detection (`screen`/`tmux`) switches to fallback.
8 frames × 2 lines × 6 braille chars wide. ~120ms per frame.

## Key files

| File | Role |
|------|------|
| `hermes_cli/skin_engine.py` | Skin loading, SkinConfig, built-in skins |
| `hermes_cli/banner.py` | `build_welcome_banner()` — main panel |
| `cli.py` (L1618-1658) | `_build_compact_banner()` — narrow terminals |
| `~/.hermes/skins/*.yaml` | User-installed skins |
| `~/.hermes/config.yaml` | `display.skin` → active skin |

## Color palettes

| Name | Border | Title | Accent | Dim | Text |
|------|--------|-------|--------|-----|------|
| Fire | #CC3300 | #FFAA00 | #FF6600 | #663300 | #FFF0E0 |
| Ocean | #2A6FB9 | #A9DFFF | #5DB8F5 | #153C73 | #EAF7FF |
| Forest | #2E7D32 | #A5D6A7 | #66BB6A | #1B5E20 | #E8F5E9 |
| Cyberpunk | #00FFFF | #FF00FF | #00FF00 | #333333 | #FFFFFF |
| Monochrome | #555555 | #E6EDF3 | #AAAAAA | #444444 | #C9D1D9 |
