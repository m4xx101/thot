# ⣿ THOT — Living Terminal Identity for Hermes Agent

**Animated braille pet. Activity heatmap. Gateway welcome. Self-evolving recommendations.**

One command. Your terminal comes alive.

```
curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
```

The installer asks you a few questions — name your agent, pick a vibe, enable/disable pet and heatmap. Skip and it defaults to THOT with fire theme.

## What You Get

| Feature | CLI | TUI | Gateway |
|---------|-----|-----|---------|
| Animated braille pet (breathes during API calls) | ✅ | ✅ | 🧠 stats |
| 12-week activity heatmap | ✅ | ✅ | 🧠 "show me my heatmap" |
| Custom title format | ✅ | ✅ | — |
| Scanner hero art (left panel) | ✅ | ✅ | — |
| 5 built-in palettes (fire/ocean/forest/cyberpunk/mono) | ✅ | ✅ | ✅ |
| ⣿ prompt + branded spinner | ✅ | ✅ | ✅ |
| Tool emojis (⚔ 🧠 🔎 📖) | ✅ | ✅ | ✅ |
| Gateway boot welcome | — | — | ✅ |
| Self-evolving recommendations | ✅ | ✅ | ✅ |

## After Install

```bash
hermes                    # See the living terminal
/skin thot               # Switch in-session
/thot-hotwire             # Force re-patch after hermes update
```

## Interactive Setup

The installer asks:
1. **Agent name** — what your agent calls itself (default: THOT)
2. **Vibe** — fire / ocean / forest / cyberpunk / monochrome
3. **Pet** — animated braille creature? (default: yes)
4. **Heatmap** — activity tracking? (default: yes)

Non-interactive (piped): uses all defaults silently.

## Self-Evolving

```bash
hermes skills tap add m4xx101/thot
/skill thot-themer
```

The agent will recommend customizations based on your actual usage.

## License

MIT — m4xx101 / Sayvdev C.
