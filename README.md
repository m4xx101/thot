<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-FF6600?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/license-MIT-FFAA00?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/Hermes-v0.11.0%2B-CC3300?style=flat-square" alt="hermes">
  <img src="https://img.shields.io/badge/platform-CLI%20%7C%20TUI%20%7C%20Gateway-333333?style=flat-square" alt="platform">
</p>

```
  ████████╗██╗  ██╗ ██████╗ ████████╗
  ╚══██╔══╝██║  ██║██╔═══██╗╚══██╔══╝
     ██║   ███████║██║   ██║   ██║
     ██║   ██╔══██║██║   ██║   ██║
     ██║   ██║  ██║╚██████╔╝   ██║
     ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝
```

# THOT — Living Terminal Identity for Hermes Agent

**Animated braille pet breathes during API calls. 12-week activity heatmap tracks your sessions. Interactive first-run setup asks your name, picks your vibe.**

One command. Your terminal wakes up.

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
```

The installer asks 4 questions (all optional — press Enter for defaults):

```
─── First-Run Setup ───

What should your agent be called? [THOT]:

Choose a vibe:
  [f]ire      ████  warm orange on black
  [o]cean     ████  deep blue and seafoam
  [g]reen     ████  forest and emerald
  [c]yberpunk ████  neon cyan on dark
  [m]ono      ████  clean grayscale
Pick a vibe [f]:

Enable animated braille pet? [Y/n]:
Enable activity heatmap? [Y/n]:
```

That's it. `hermes` now shows your branded terminal.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Interactive Setup](#interactive-setup)
- [What Changes](#what-changes)
- [Built-in Palettes](#built-in-palettes)
- [Pet Animation](#pet-animation)
- [Activity Heatmap](#activity-heatmap)
- [Gateway (Telegram / Discord)](#gateway-telegram--discord)
- [Self-Evolving Skill](#self-evolving-skill)
- [Architecture](#architecture)
- [Configuration Reference](#configuration-reference)
- [Commands](#commands)
- [Uninstall](#uninstall)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | CLI | TUI | Gateway | Description |
|---------|:---:|:---:|:-------:|-------------|
| **Animated pet** | ✅ | ✅ | 🧠 | 8-frame braille creature breathes during LLM calls. Emoji fallback for unsupported terminals. |
| **Activity heatmap** | ✅ | ✅ | 🧠 | 12-week GitHub-style grid (░▒▓█). Shows session density at a glance. |
| **Session stats** | ✅ | ✅ | 🧠 | Total sessions, active days, current streak, checkpoint count. |
| **Custom title** | ✅ | ✅ | — | `Re: Thot (thot.m4xx.cfd) — Hermes Agent v0.11.0 · us abc12345` |
| **5 color palettes** | ✅ | ✅ | ✅ | Fire, ocean, forest, cyberpunk, monochrome. Interactive picker at install. |
| **Scanner hero art** | ✅ | ✅ | — | Geometric pattern on the left panel. |
| **Branded spinner** | ✅ | ✅ | — | ⣿ faces, "forging chain" verbs, ⟪⣿⣿⟫ wings. |
| **Tool emojis** | ✅ | ✅ | ✅ | Every tool gets a custom emoji: ⚔ terminal, 🧠 delegate_task, 🔎 search. |
| **Gateway welcome** | — | — | ✅ | One-time branded welcome on first Telegram/Discord session. |
| **Self-evolving** | ✅ | ✅ | ✅ | Skill watches usage, recommends customizations based on your actual behavior. |
| **Survives updates** | ✅ | ✅ | ✅ | Skin lives in `~/.hermes/skins/` — outside the Hermes repo. |

---

## Installation

### One Command

```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
```

### Manual

```bash
git clone https://github.com/m4xx101/thot.git
cd thot
bash scripts/install.sh
```

### From a specific release

```bash
curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/v1.0.0/scripts/install.sh | bash
```

### Requirements

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) v0.11.0+
- Python 3.6+ (for YAML config editing)
- Terminal with Unicode support (for braille pet)
- Nothing else — no npm, no pip pre-install, no dependencies

---

## Interactive Setup

The installer presents 4 questions. All have sensible defaults — press Enter to skip.

### 1. Agent Name

```
What should your agent be called? [THOT]:
```

Changes: `branding.agent_name`, `response_label`, `welcome` message, `/help` header, gateway welcome text. Accepts spaces, emoji, anything.

### 2. Vibe / Palette

```
Choose a vibe:
  [f]ire      ████  warm orange on black
  [o]cean     ████  deep blue and seafoam
  [g]reen     ████  forest and emerald
  [c]yberpunk ████  neon cyan on dark
  [m]ono      ████  clean grayscale
Pick a vibe [f]:
```

Changes: all `colors.*` keys in the skin YAML to the selected palette.

### 3. Animated Pet

```
Enable animated braille pet? [Y/n]:
```

- **Yes (default):** 8-frame braille creature breathes in the spinner during API calls
- **No:** Pet frames cleared. Spinner shows ⣿ faces only.

### 4. Activity Heatmap

```
Enable activity heatmap? [Y/n]:
```

- **Yes (default):** 12-week session grid + stats line rendered in the banner
- **No:** Heatmap removed. Banner shows tools + skills only.

### Non-Interactive Mode

When piped or run in CI/cron (no terminal available), all defaults are used silently:
- Name: THOT
- Palette: fire
- Pet: on
- Heatmap: on

---

## What Changes

After installation, the following files are created:

```
~/.hermes/
├── skins/thot.yaml                          ← The skin (colors, pet, branding, art)
├── config.yaml       (modified: display.skin: thot)
├── .thot_welcome_sent                       ← Sentinel for gateway welcome
├── .thot_patch_version                      ← Tracks last Hermes version patched
└── hermes-agent/
    ├── hermes_cli/extended_banner.py         ← Heatmap + stats data layer
    └── gateway/builtin_hooks/boot-thot/      ← Gateway welcome hook
```

No Hermes source files are modified unless you run `/thot-hotwire` to apply optional source patches.

---

## Built-in Palettes

| Name | Border | Title | Accent | Dim | Text | Preview |
|------|--------|-------|--------|-----|------|---------|
| **Fire** | `#CC3300` | `#FFAA00` | `#FF6600` | `#663300` | `#FFF0E0` | 🔥 🔥 🔥 |
| **Ocean** | `#2A6FB9` | `#A9DFFF` | `#5DB8F5` | `#153C73` | `#EAF7FF` | 🌊 🌊 🌊 |
| **Forest** | `#2E7D32` | `#A5D6A7` | `#66BB6A` | `#1B5E20` | `#E8F5E9` | 🌿 🌿 🌿 |
| **Cyberpunk** | `#00FFFF` | `#FF00FF` | `#00FF00` | `#333333` | `#FFFFFF` | ⚡ ⚡ ⚡ |
| **Monochrome** | `#555555` | `#E6EDF3` | `#AAAAAA` | `#444444` | `#C9D1D9` | ◼ ◼ ◼ |

Switch palettes post-install:

```bash
# Edit directly
nano ~/.hermes/skins/thot.yaml  # Change colors.* section

# Or use evolve.py
python3 skill-scripts/evolve.py --palette-shift warm
python3 skill-scripts/evolve.py --palette-shift cool
```

---

## Pet Animation

The pet is an 8-frame braille creature stored in `spinner.pet_frames` in the skin YAML. Each frame is 2 lines × 6 braille chars wide. Colors: `#FF6600` (top line), `#FF7700` (bottom line).

**Breathing cycle (~960ms):**
```
Frame 0:   ⠀⠀⠀     (rest, exhaled)
          ⠀⠀⠀

Frame 1:   ⣀⣀⣀      (slight inhale)
          ⠀⠀⠀

Frame 2:  ⣶⣿⣿⣶     (early inhale)
         ⠀⠉⠉⠀

Frame 3: ⣾⣿⣿⣿⣷   (mid inhale)
        ⠀⠉⠟⠉⠀

Frame 4:⣿⣿⣿⣿⣿⣿  (full inhale — peak)
        ⣀⣤⣿⣤⣀

Frame 5: ⣾⣿⣿⣿⣷   (early exhale)
        ⠀⠉⠟⠉⠀

Frame 6:  ⣶⣿⣿⣶     (mid exhale)
         ⠀⠉⠉⠀

Frame 7:   ⣀⣀⣀      (returning to rest)
          ⠀⠀⠀
```

The pet renders ABOVE the spinner message during LLM API calls. If the terminal doesn't support braille characters (detected via `$TERM`), an emoji fallback (🔥 🔥 🔥) is used instead.

**Visibility:** The pet is visible in CLI and TUI modes. Gateway users (Telegram/Discord) can see stats via "show me my pet" commands.

---

## Activity Heatmap

A 12-week grid rendered in the right column of the welcome banner. Each cell is a session day, colored by intensity:

```
Activity — 12 weeks
Mo ·░▒▓█ ░░▒█ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ░▒▓█
Tu ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓
We ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓
Th ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓
Fr ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓
Sa ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓
Su ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓ ·░▒▓

42 sessions · 18 active days · 5d streak 🔥 · 3 checkpoints
```

**Data source:** Hermes SessionDB (`~/.hermes/sessions.db`). Queried directly by `extended_banner.py`. No third-party dependencies. Falls back gracefully if the database is missing or locked.

**Gateway users:** Type "show me my heatmap" and the agent responds with a monospace text version.

---

## Gateway (Telegram / Discord)

THOT sends a one-time welcome message on first gateway session after install:

```
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿  THOT — Living Terminal Identity v1.0.0         ⣿
⣿                                                  ⣿
⣿  42 sessions · 18 active days · 5d streak 🔥      ⣿
⣿                                                  ⣿
⣿  ⣿ Pet breathes during CLI API calls.            ⣿
⣿  'show me my heatmap' for activity graph.        ⣿
⣿  /help for commands. /skin to switch themes.      ⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
```

Re-sent if the skin YAML is updated (detected via file modification time).

---

## Self-Evolving Skill

The THOT skill watches your behavior and recommends customizations based on actual usage.

```bash
hermes skills tap add m4xx101/thot
/skill thot-themer
```

### What it does

| Trigger | Action |
|---------|--------|
| You call `delegate_task` heavily | "⣿ Want me to give delegate_task the 🧠 emoji?" |
| 10+ sessions without a theme change | "⣿ Colors may feel stale. Shift to ocean tones?" |
| Nighttime (8pm-6am) | "⣿ Dark mode recommended for eye comfort." |
| You create a new skill | "⣿ New skill saved. Theme your terminal to match?" |
| You update a memory | "⣿ Memory saved. Your identity is evolving — refresh the look?" |

### Gateway Commands

| You say | Agent responds |
|---------|---------------|
| "show me my heatmap" | Monospace-formatted 12-week grid |
| "my stats" | Session count, streak, checkpoints |
| "switch to ocean" | Changes palette to ocean |
| "change terminal emoji to 💀" | Sets tool_emojis.terminal to 💀 |
| "show themes" | Lists installed skins with descriptions |
| "what can THOT do?" | Lists all available commands |

### Red Flags (Anti-Spam)

The skill follows strict rules to avoid being annoying:
- One recommendation per conversation. Never multiple at once.
- Never recommends the same thing twice in consecutive sessions.
- Never applies changes without explicit user consent.
- On gateway (Telegram/Discord), skips CLI-only mentions (banners, hero art).

---

## Architecture

```
                        ┌──────────────────────┐
                        │   curl | bash          │
                        │   scripts/install.sh   │
                        └──────────┬─────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────────┐
│ ~/.hermes/skins/│    │ ~/.hermes/       │    │ ~/.hermes/hermes-agent│
│   thot.yaml      │    │   config.yaml     │    │ /hermes_cli/          │
│                  │    │ display.skin:thot │    │   extended_banner.py  │
│ colors, spinner, │    └──────────────────┘    │                       │
│ pet_frames,      │                            │ /gateway/builtin_hooks│
│ branding, hero,  │                            │   /boot-thot/hook.py  │
│ heatmap_colors   │                            └──────────────────────┘
└────────┬─────────┘
         │
    ┌────┴────────────────────────────┐
    │  Hermes skin engine             │
    │  skin_engine.py → SkinConfig    │
    │                                 │
    │  build_welcome_banner()         │
    │  ├─ banner_logo (THOT art)     │
    │  ├─ banner_hero (scanner)      │
    │  ├─ colors (palette)           │
    │  ├─ extended_banner sections   │  ← queries SessionDB
    │  │   ├─ heatmap (12 weeks)     │
    │  │   ├─ stats (streak, etc)    │
    │  │   └─ suggestions            │
    │  └─ branding (title, labels)   │
    │                                 │
    │  KawaiiSpinner._animate()       │
    │  └─ pet_frames (8-frame cycle) │
    └─────────────────────────────────┘
```

### Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Pet lives in spinner, not banner | Banner renders once. Spinner has an animation loop already. |
| 2 | Rich markup strings, not Panel objects | TUI passthrough safe. Panel objects break Ink render pipeline. |
| 3 | Hero is static; pet handles animation | Panel layout can't cycle frames without full re-render. |
| 4 | No notcurses | Hermes uses Rich + KawaiiSpinner. Third path = conflict. |
| 5 | Skin YAML as single source of truth | One file. Survives `hermes update`. Outside the repo. |
| 6 | SessionDB for heatmap data | Direct SQLite query. No Python deps beyond stdlib. |
| 7 | Gateway boot hook + skill welcome | One-time welcome + ongoing awareness for Telegram/Discord. |
| 8 | Patch auto-reapply + graceful degrade | Version detection. Falls back silently if upstream API changes. |

---

## Configuration Reference

### Skin YAML (`~/.hermes/skins/thot.yaml`)

All fields optional. Missing values inherit from the built-in `default` skin.

```yaml
name: thot                # Required — unique skin name
description: "..."        # Shown in /skin listing

colors:                   # All hex (#RRGGBB), all optional
  banner_border: "#CC3300"
  banner_title: "#FFAA00"
  banner_accent: "#FF6600"
  banner_dim: "#663300"
  banner_text: "#FFF0E0"
  # ... 20+ more color slots

spinner:
  pet_frames: [...]       # 8 Rich-markup strings (braille)
  pet_fallback: [...]     # 8 Rich-markup strings (emoji)
  waiting_faces: [...]    # Faces cycling during API wait
  thinking_faces: [...]   # Faces cycling during reasoning
  thinking_verbs: [...]   # Random verbs for spinner messages
  wings: [...]            # Left/right wing decorations

branding:
  agent_name: "THOT"      # In banner title + compact mode
  title_format: "..."     # Banner title (supports {version}, {release}, {upstream})
  welcome: "..."          # Startup message
  goodbye: "..."          # Exit message
  response_label: "..."   # Response box header
  prompt_symbol: "⣿ ❯ "  # Input prompt prefix
  help_header: "..."      # /help header

tool_prefix: "╎"           # Character prefix for tool output
tool_emojis: {}            # Per-tool emoji overrides

banner_logo: |             # Rich markup — THOT text (max 98w)
  [#FF6600]  ASCII_HERE  [/]

banner_hero: |             # Rich markup — left panel art (max 30w)
  [#FF6600]  ASCII_HERE  [/]

heatmap_colors:            # Custom heatmap cell colors
  empty: "#333333"
  level_1: "#993300"
  level_2: "#CC4400"
  level_3: "#FF6600"
  level_4: "#FF8800"
```

### Config Activation (`~/.hermes/config.yaml`)

```yaml
display:
  skin: thot
```

Set via: `hermes config set display.skin thot`

---

## Commands

### In-Session

| Command | Action |
|---------|--------|
| `/skin thot` | Switch to THOT skin (applies on restart) |
| `/skin default` | Revert to original Hermes theme |
| `/thot-hotwire` | Force re-apply source patches after `hermes update` |
| `/skill thot-themer` | Load the self-evolving recommendation engine |

### CLI

| Command | Action |
|---------|--------|
| `hermes config set display.skin thot` | Activate THOT skin |
| `hermes config set display.skin default` | Revert to default |
| `hermes skills tap add m4xx101/thot` | Install the self-evolving skill |

### Scripts

| Script | Action |
|--------|--------|
| `bash scripts/install.sh` | Install (interactive) |
| `bash scripts/uninstall.sh` | Revert to default, remove all THOT files |
| `python3 scripts/generate-art.py "NAME" logo` | Generate ASCII text art |
| `python3 scripts/apply-patches.py --check` | Check if patches are needed |
| `python3 scripts/apply-patches.py --force` | Force-apply patches |

---

## Uninstall

```bash
# One command:
bash scripts/uninstall.sh

# Or manual:
hermes config set display.skin default
rm ~/.hermes/skins/thot.yaml
rm ~/.hermes/hermes-agent/hermes_cli/extended_banner.py
rm -rf ~/.hermes/hermes-agent/gateway/builtin_hooks/boot-thot/
rm ~/.hermes/.thot_welcome_sent ~/.hermes/.thot_patch_version
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| **"Hermes not found"** | `HERMES_HOME` not set or Hermes not installed | `export HERMES_HOME=/path/to/.hermes` or install Hermes first |
| **"Cannot fetch skin"** | No internet or GitHub unavailable | Clone the repo locally: `git clone https://github.com/m4xx101/thot && cd thot && bash scripts/install.sh` |
| **"Config update failed"** | `pyyaml` not installed | `python3 -m pip install pyyaml --break-system-packages` |
| **Pet shows garbage** | Terminal doesn't support braille | Set `TERM=xterm-256color`. If still broken, pet_fallback (🔥 emoji) is used automatically |
| **Heatmap is empty** | No sessions yet or SessionDB locked | Normal for fresh installs. Heatmap populates as you use Hermes. Falls back gracefully. |
| **Banner shows default art** | Skin not activated | Run: `hermes config set display.skin thot` then restart |
| **Skin reset after `hermes update`** | Source patches overwritten | Run `/thot-hotwire` to reapply. Skin YAML survives updates (it's outside the repo). |
| **No gateway welcome** | Hook not installed or sentinel exists | Check: `ls ~/.hermes/hermes-agent/gateway/builtin_hooks/boot-thot/`. Delete `~/.hermes/.thot_welcome_sent` to force re-send. |
| **Interactive setup doesn't appear** | Piped install or no TTY | Normal — uses defaults silently. Run `bash scripts/install.sh` directly for interactive mode. |

---

## FAQ

**Q: Does this modify Hermes source code?**
A: By default, no. Only the skin YAML and `extended_banner.py` are installed. Optional source patches (for pet-in-spinner animation) are available via `/thot-hotwire` and reapply automatically after `hermes update`.

**Q: Will this break when I run `hermes update`?**
A: The skin YAML lives in `~/.hermes/skins/` — outside the Hermes repo. It survives updates. The `extended_banner.py` and boot hook are inside the repo and may be removed. Reinstall with `curl ... | bash` after an update, or use the skill (`hermes skills tap add m4xx101/thot`) which auto-reinstalls.

**Q: Can I use this without the pet/heatmap?**
A: Yes. During interactive setup, answer "n" to pet and heatmap. Post-install, remove the corresponding sections from `~/.hermes/skins/thot.yaml`.

**Q: Can I create my own palette?**
A: Yes. Edit `~/.hermes/skins/thot.yaml` and change the `colors:` section. Hex values only (`#RRGGBB`). Restart Hermes to apply.

**Q: How do I make my own skin based on THOT?**
A: Copy `skins/templates/full.yaml` from the repo, rename, customize, save to `~/.hermes/skins/your-name.yaml`, then `hermes config set display.skin your-name`.

**Q: Does this work on Windows?**
A: The skin YAML works on any platform Hermes supports. The installer (`install.sh`) is Linux/macOS/WSL only. A PowerShell installer is planned.

**Q: Gateway users can't see the pet — what's the point?**
A: Gateway users get: branded welcome message, live stats ("show me my heatmap"), tool emojis, ⣿ response labels, proactive customization suggestions. The terminal eye candy is CLI/TUI only.

---

## Contributing

### Adding your skin

1. Fork this repo
2. Copy `skins/templates/full.yaml` → `skins/your-brand.yaml`
3. Fill in your colors, branding, and ASCII art
4. Run `python3 test/test-yaml-validity.py` to validate
5. Submit a PR with a screenshot

### Skin Guidelines

- `name` must be unique
- `banner_logo` max width: 98 chars per line
- `banner_hero` max width: 30 chars per line
- Test at 80-col and 120-col terminal widths
- Include a screenshot in your PR

### Tool Emoji Reference

```
terminal, web_search, read_file, write_file, patch, search_files,
browser_navigate, browser_click, browser_type, browser_snapshot,
browser_back, vision_analyze, delegate_task, execute_code,
memory, session_search, todo, clarify, skill_view, skills_list,
skill_manage, send_message, cronjob, image_generate, text_to_speech
```

---

## License

MIT — [m4xx101](https://github.com/m4xx101) / Sayvdev C.

---

<p align="center">
  <sub>⣿ Built with fire. Forged in the terminal. ⣿</sub>
</p>
