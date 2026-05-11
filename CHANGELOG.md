# THOT Changelog

## [1.0.0] — 2026-05-11
### Added
- CRYPTEX skin: warm orange on deep black palette, 30+ color slots
- Animated braille pet: 8 breathing frames rendered during API calls via KawaiiSpinner
- Pet fallback: emoji animation for terminals without braille support
- 12-week activity heatmap: queries SessionDB, renders ░▒▓█ gradient blocks
- Custom title format: "Re: Thot (cryptex.m4xx.cfd) — Hermes Agent v{version} · us {upstream}"
- Scanner hero art: 13-line geometric pattern for left panel
- Gateway boot hook: one-time branded welcome on first Telegram/Discord session
- extended_banner.py: SessionDB-backed heatmap, stats, streak, suggestions
- apply-patches.py: version-aware source patcher with auto-reapply and graceful degradation
- generate-art.py: agentic ASCII art generator using pyfiglet (571 fonts)
- skill-scripts: install-skin, recommend (usage analyzer), evolve (self-evolution executor)
- Hermes skill: trigger hooks on skill_manage('create') and memory('add')
- One-click installer: curl | bash
- One-click uninstall: revert to default theme
- GitHub Actions release workflow
- Skin templates for community forking (minimal + full)
