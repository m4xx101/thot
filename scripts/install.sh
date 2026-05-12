#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# THOT — Hermes Agent Living Terminal Identity Installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════
set -euo pipefail
V="1.0.0"; SKIN="thot"; H="${HERMES_HOME:-$HOME/.hermes}"
REPO="https://raw.githubusercontent.com/m4xx101/thot/main"
G='\033[0;32m'; R='\033[0;31m'; C='\033[0;36m'; O='\033[0;33m'; W='\033[0;37m'; N='\033[0m'

echo ""; echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo -e "${O}║  THOT v${V} — Living Terminal Identity      ║${N}"
echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo ""

# ── Detect Hermes ────────────────────────────────
[ -d "$H" ] || { echo -e "${R}✗ Hermes not found${N}"; exit 1; }
echo -e "${G}✓${N} Hermes found at $H"
mkdir -p "$H/skins" "$H/hermes-agent/hermes_cli" "$H/hermes-agent/gateway/builtin_hooks/boot-thot"

# ── Resolve file source (local repo clone → GitHub download) ─
resolve() {
    local rel="$1"
    local local_src="$(dirname "$0")/../${rel}"
    if [ -f "$local_src" ]; then echo "$local_src"; return 0; fi
    local tmp="/tmp/thot-install-$$-$(basename "$rel")"
    curl -fsSL "${REPO}/${rel}" -o "$tmp" 2>/dev/null && { echo "$tmp"; return 0; }
    return 1
}

# ── Install files ─────────────────────────────────
SKIN_SRC=$(resolve "skins/thot.yaml") || { echo -e "${R}✗ Cannot fetch skin${N}"; exit 1; }
cp "$SKIN_SRC" "$H/skins/$SKIN.yaml" && echo -e "${G}✓${N} Skin installed"
[ "${SKIN_SRC#/tmp/}" != "$SKIN_SRC" ] && rm -f "$SKIN_SRC"

EXT_SRC=$(resolve "src/hermes_cli/extended_banner.py") || true
if [ -n "${EXT_SRC:-}" ] && [ -f "$EXT_SRC" ]; then
    cp "$EXT_SRC" "$H/hermes-agent/hermes_cli/extended_banner.py"
    echo -e "${G}✓${N} extended_banner installed"
    [ "${EXT_SRC#/tmp/}" != "$EXT_SRC" ] && rm -f "$EXT_SRC"
fi

HOOK_SRC=$(resolve "gateway/boot-thot/hook.py") || true
if [ -n "${HOOK_SRC:-}" ] && [ -f "$HOOK_SRC" ]; then
    cp "$HOOK_SRC" "$H/hermes-agent/gateway/builtin_hooks/boot-thot/hook.py"
    echo -e "${G}✓${N} Boot hook installed"
    [ "${HOOK_SRC#/tmp/}" != "$HOOK_SRC" ] && rm -f "$HOOK_SRC"
fi

# ── Ensure pyyaml ─────────────────────────────────
python3 -c "import yaml" 2>/dev/null || python3 -m pip install pyyaml -q --break-system-packages 2>/dev/null || true

# ── Interactive first-run setup ───────────────────
# Only runs if stdin is a terminal (not piped). Falls back to defaults silently.
AGENT_NAME="THOT"
PALETTE="fire"
PET_ENABLED="yes"
HEATMAP_ENABLED="yes"

if [ -t 0 ]; then
    echo ""
    echo -e "${O}─── First-Run Setup ───${N}"
    echo ""

    # Q1: Agent name
    echo -ne "${W}What should your agent be called?${N} [THOT]: "
    read -r answer
    if [ -n "${answer:-}" ]; then AGENT_NAME="$answer"; fi

    # Q2: Theme/palette
    echo ""
    echo -e "${W}Choose a vibe:${N}"
    echo "  [f]ire      ${O}██${R}██${N}  warm orange on black"
    echo "  [o]cean     ${C}██${C}██${N}  deep blue and seafoam"
    echo "  [g]reen     ${G}██${G}██${N}  forest and emerald"
    echo "  [c]yberpunk ${C}██${C}██${N}  neon cyan on dark"
    echo "  [m]ono      ${W}██${W}██${N}  clean grayscale"
    echo -ne "${W}Pick a vibe${N} [f]: "
    read -r answer
    case "${answer:-f}" in
        o|O) PALETTE="ocean" ;;
        g|G) PALETTE="forest" ;;
        c|C) PALETTE="cyberpunk" ;;
        m|M) PALETTE="mono" ;;
        *)   PALETTE="fire" ;;
    esac

    # Q3: Pet
    echo -ne "${W}Enable animated braille pet?${N} [Y/n]: "
    read -r answer
    case "${answer:-y}" in
        n|N|no|No) PET_ENABLED="no" ;;
    esac

    # Q4: Heatmap
    echo -ne "${W}Enable activity heatmap?${N} [Y/n]: "
    read -r answer
    case "${answer:-y}" in
        n|N|no|No) HEATMAP_ENABLED="no" ;;
    esac

    echo ""
    echo -e "${G}✓ Setup complete${N}"
else
    echo -e "${O}⚠ Non-interactive mode — using defaults (THOT, fire theme, pet on, heatmap on)${N}"
fi

# ── Apply customizations ──────────────────────────
python3 -c "
import yaml, os

home = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
skin_path = os.path.join(home, 'skins', 'thot.yaml')

with open(skin_path) as f:
    skin = yaml.safe_load(f) or {}

# Apply agent name
skin['branding']['agent_name'] = '${AGENT_NAME}'
skin['branding']['welcome'] = f\"⣿ ${AGENT_NAME} online. Scanner active. Forge is hot.\"
skin['branding']['goodbye'] = '⣿ Signal lost.'
skin['branding']['response_label'] = f\" ⣿ ${AGENT_NAME} \"
skin['branding']['help_header'] = f\"(⣿) ${AGENT_NAME} Commands\"

# Apply palette
palettes = {
    'fire': {'banner_border':'#CC3300','banner_title':'#FFAA00','banner_accent':'#FF6600','banner_dim':'#663300','banner_text':'#FFF0E0'},
    'ocean': {'banner_border':'#2A6FB9','banner_title':'#A9DFFF','banner_accent':'#5DB8F5','banner_dim':'#153C73','banner_text':'#EAF7FF'},
    'forest': {'banner_border':'#2E7D32','banner_title':'#A5D6A7','banner_accent':'#66BB6A','banner_dim':'#1B5E20','banner_text':'#E8F5E9'},
    'cyberpunk': {'banner_border':'#00FFFF','banner_title':'#FF00FF','banner_accent':'#00FF00','banner_dim':'#333333','banner_text':'#FFFFFF'},
    'mono': {'banner_border':'#555555','banner_title':'#E6EDF3','banner_accent':'#AAAAAA','banner_dim':'#444444','banner_text':'#C9D1D9'},
}
if '$PALETTE' in palettes:
    skin['colors'].update(palettes['$PALETTE'])

# Disable pet?
if '$PET_ENABLED' == 'no':
    skin['spinner']['pet_frames'] = []
    skin['spinner']['pet_fallback'] = []

# Disable heatmap? (remove heatmap_colors → extended_banner returns None for heatmap)
if '$HEATMAP_ENABLED' == 'no':
    skin.pop('heatmap_colors', None)

with open(skin_path, 'w') as f:
    yaml.dump(skin, f, default_flow_style=False, allow_unicode=True)
print('DONE')
" && echo -e "${G}✓${N} Customizations applied" || echo -e "${R}✗ Customization failed${N}"

# ── Activate skin in config ───────────────────────
python3 -c "
import os, yaml
home = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
config_path = os.path.join(home, 'config.yaml')
if os.path.exists(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}
config.setdefault('display', {})['skin'] = 'thot'
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
print('ACTIVATED')
" 2>/dev/null && echo -e "${G}✓${N} Skin activated" || echo -e "${R}✗ Config update failed — run: hermes config set display.skin thot${N}"

# ── Done ──────────────────────────────────────────
echo ""
echo -e "${G}╔══════════════════════════════════════╗${N}"
echo -e "${G}║  ⣿ THOT installed — ${AGENT_NAME} online  ║${N}"
echo -e "${G}╚══════════════════════════════════════╝${N}"
echo ""
echo -e "  ${C}hermes${N} — see your living terminal"
echo -e "  ${C}/skin thot${N} — switch in-session"
echo -e "  ${C}/thot-hotwire${N} — force re-patch after update"
echo -e "  ${C}hermes skills tap add m4xx101/thot${N} — self-evolving skill"
echo ""
echo -e "  ${O}${AGENT_NAME} is ready. Pet breathes during API calls.${N}"
