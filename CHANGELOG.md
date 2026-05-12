# THOT Changelog

## [1.0.0] — 2026-05-12
### Added
- **THOT skin**: renamed from CRYPTEX to THOT. All branding unified under repo name.
- **Interactive first-run setup**: installer asks agent name, palette, pet, heatmap with silent defaults for pipes
- **5 built-in palettes**: fire, ocean, forest, cyberpunk, monochrome
- Animated braille pet: 8 breathing frames during API calls via KawaiiSpinner
- Pet fallback: emoji animation for terminals without braille support
- 12-week activity heatmap: queries SessionDB, renders gradient blocks
- Custom title format: "Re: Thot (thot.m4xx.cfd) — Hermes Agent v{version}"
- Scanner hero art: geometric pattern for left panel
- Gateway boot hook: one-time THOT welcome on first session
- extended_banner.py: SessionDB-backed heatmap, stats, streak, suggestions
- apply-patches.py: version-aware source patcher with auto-reapply, graceful degradation, hotwire
- generate-art.py: agentic ASCII art generator using pyfiglet (571 fonts)
- skill-scripts: install-skin, recommend (usage analyzer), evolve (self-evolution executor)
- Hermes skill: trigger hooks on skill_manage('create') and memory('add')
- One-click install + uninstall
- GitHub Actions release workflow
- Skin templates for community forking

### Fixed
- curl|bash installer: `resolve()` fallback downloads from GitHub raw when local path unavailable
- YAML syntax errors in full template (semicolons → proper YAML list format)
