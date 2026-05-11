---
name: thot-themer
description: Use when the agent creates a skill via skill_manage(action='create'), updates memory via memory(action='add'), or the user asks about terminal themes, customization, skin switching, heatmap, pet, or mentions 'thot'/'cryptex'. Also load after 10+ sessions with default skin.
version: 1.0.0
author: m4xx101
homepage: https://github.com/m4xx101/thot
---

# THOT — Living Terminal Identity Skill

## Trigger Hooks

1. **After skill_manage('create')** → "⣿ New skill saved. Want me to theme your terminal to match this workflow?"
2. **After memory('add')** → If the memory relates to user identity/preferences: "⣿ Memory saved. Your identity is evolving — refresh the look too?"

## On Load (Every Session)

Run `skill-scripts/install-skin.py --check` silently (2s max).
- Skin active? Skip. Say nothing.
- Skin not installed? Offer once: "⣿ CRYPTEX skin not installed. One command: `curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash`"
- On gateway (Telegram/Discord)? Skip CLI banner mentions. Only mention what's relevant: tool emojis, response_label, prompt_symbol.

## Recommendation Flow

Run `skill-scripts/recommend.py`. Present only the TOP recommendation as ONE question:

```
⣿ I noticed you use {tool} heavily ({count}x). Want me to give it {emoji}?
```

One question. Wait. Apply with `skill-scripts/evolve.py --set`.

## Gateway-Aware Commands

| User says | Agent does |
|-----------|-----------|
| "show me my heatmap" | Run build_heatmap() from extended_banner, format as monospace text |
| "my stats" | Run build_stats_line(), respond with session/streak/checkpoints |
| "switch to {skin}" | `evolve.py --activate {skin}` |
| "change {tool} emoji to {e}" | `evolve.py --set tool_emojis.{tool} "{e}"` |
| "show themes" | List ~/.hermes/skins/ + describe each |
| "what can THOT do?" | This message — list available commands |

## Hotwire Command

`/thot-hotwire` — User explicitly requests force-repatch of Hermes source.
Run `scripts/apply-patches.py --force`. Report result.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I should recommend multiple things" | One at a time. Never overwhelm. |
| "They didn't ask but the skin is stale" | Only on hooks. No spam. |
| "I'll apply without asking" | Always ask. Never mutate config without consent. |
| "Same recommendation as last session" | Skip. Don't repeat. |
| "Gateway user — skip theming mentions" | Correct. Gateway users see tool emojis, labels, stats. |
