#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# THOT — Hermes Agent Living Terminal Identity Installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════
set -euo pipefail
V="1.0.0"; SKIN="thot"; H="${HERMES_HOME:-$HOME/.hermes}"
REPO="https://raw.githubusercontent.com/m4xx101/thot/main"
G='\033[0;32m'; R='\033[0;31m'; C='\033[0;36m'; O='\033[0;33m'; W='\033[1;37m'; D='\033[2m'; N='\033[0m'

# ── Spinner helpers ───────────────────────────────
_spin_chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
_spin_pid=""
_start_spin() {
    local msg="$1"
    printf "  %s" "$msg"
    (
        i=0
        while true; do
            printf "\r  ${O}%s${N} %s" "${_spin_chars:$i:1}" "$msg"
            i=$(( (i+1) % ${#_spin_chars} ))
            sleep 0.08
        done
    ) & _spin_pid=$!
}
_stop_spin_ok()  { [ -n "${_spin_pid:-}" ] && kill "$_spin_pid" 2>/dev/null || true; wait "$_spin_pid" 2>/dev/null || true; printf "\r  ${G}✓${N} %s\n" "${1:-}"; _spin_pid=""; }
_stop_spin_warn(){ [ -n "${_spin_pid:-}" ] && kill "$_spin_pid" 2>/dev/null || true; wait "$_spin_pid" 2>/dev/null || true; printf "\r  ${O}⚠${N} %s\n" "${1:-}"; _spin_pid=""; }
_stop_spin_err() { [ -n "${_spin_pid:-}" ] && kill "$_spin_pid" 2>/dev/null || true; wait "$_spin_pid" 2>/dev/null || true; printf "\r  ${R}✗${N} %s\n" "${1:-}"; _spin_pid=""; }

# ── Resolve file source ───────────────────────────
resolve() {
    local rel="$1"
    local local_src="$(dirname "$0")/../${rel}"
    if [ -f "$local_src" ]; then echo "$local_src"; return 0; fi
    local tmp="/tmp/thot-install-$$-$(basename "$rel")"
    curl -fsSL "${REPO}/${rel}" -o "$tmp" 2>/dev/null && { echo "$tmp"; return 0; }
    return 1
}

# ── Banner ────────────────────────────────────────
echo ""
echo -e "  ${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo -e "  ${O}║  THOT v${V} — Living Terminal Identity      ║${N}"
echo -e "  ${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo ""

# ── Phase 1: Detect environment ───────────────────
_start_spin "Detecting Hermes installation..."
[ -d "$H" ] || { _stop_spin_err "Not found at $H"; echo "  Install: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"; exit 1; }
_stop_spin_ok "Hermes found at $H"

mkdir -p "$H/skins" "$H/hermes-agent/hermes_cli" "$H/hermes-agent/gateway/builtin_hooks/boot-thot"

# ── Phase 2: Install skin ─────────────────────────
_start_spin "Downloading THOT skin..."
SKIN_SRC=$(resolve "skins/thot.yaml") || { _stop_spin_err "Cannot fetch skin"; exit 1; }
cp "$SKIN_SRC" "$H/skins/$SKIN.yaml"
[ "${SKIN_SRC#/tmp/}" != "$SKIN_SRC" ] && rm -f "$SKIN_SRC"
_stop_spin_ok "Skin installed"

# ── Phase 3: Extended banner ──────────────────────
_start_spin "Installing extended banner..."
EXT_SRC=$(resolve "src/hermes_cli/extended_banner.py") || true
if [ -n "${EXT_SRC:-}" ] && [ -f "$EXT_SRC" ]; then
    cp "$EXT_SRC" "$H/hermes-agent/hermes_cli/extended_banner.py"
    [ "${EXT_SRC#/tmp/}" != "$EXT_SRC" ] && rm -f "$EXT_SRC"
    _stop_spin_ok "extended_banner installed"
else
    _stop_spin_warn "extended_banner skipped (heatmap unavailable)"
fi

# ── Phase 4: Boot hook ────────────────────────────
_start_spin "Installing gateway boot hook..."
HOOK_SRC=$(resolve "gateway/boot-thot/hook.py") || true
if [ -n "${HOOK_SRC:-}" ] && [ -f "$HOOK_SRC" ]; then
    cp "$HOOK_SRC" "$H/hermes-agent/gateway/builtin_hooks/boot-thot/hook.py"
    [ "${HOOK_SRC#/tmp/}" != "$HOOK_SRC" ] && rm -f "$HOOK_SRC"
    _stop_spin_ok "Boot hook installed"
else
    _stop_spin_warn "Boot hook skipped (gateway welcome unavailable)"
fi

# ── Phase 5: Ensure dependencies ──────────────────
_start_spin "Checking Python/YAML..."
python3 -c "import yaml" 2>/dev/null || python3 -m pip install pyyaml -q --break-system-packages 2>/dev/null || true
_stop_spin_ok "Dependencies ready"

# ── Phase 6: Interactive setup ────────────────────
# Save original stdin, read from /dev/tty, then restore.
# This prevents 'exec < /dev/tty' from hanging the script on exit.
AGENT_NAME="THOT"
PALETTE="fire"
PET_ENABLED="yes"
HEATMAP_ENABLED="yes"

_exec_tty="${EXEC_TTY:-}"
if [ -t 0 ] || [ -e /dev/tty ]; then
    echo ""
    echo -e "  ${O}─── First-Run Setup ───${N}"
    echo ""

    # Q1: Agent name
    echo -ne "  ${W}Agent name${N} [THOT]: "
    read -r answer < /dev/tty 2>/dev/null || answer=""
    if [ -n "${answer:-}" ]; then AGENT_NAME="$answer"; fi

    # Q2: Palette
    echo ""
    echo -e "  ${W}Choose a vibe:${N}"
    echo -e "    ${D}[f]${N} fire      ${O}████${N}  warm orange on black"
    echo -e "    ${D}[o]${N} ocean     ${C}████${N}  deep blue and seafoam"
    echo -e "    ${D}[g]${N} forest    ${G}████${N}  emerald green"
    echo -e "    ${D}[c]${N} cyberpunk ${C}████${N}  neon on dark"
    echo -e "    ${D}[m]${N} mono      ${W}████${N}  clean grayscale"
    echo -ne "  ${W}Vibe${N} [f]: "
    read -r answer < /dev/tty 2>/dev/null || answer=""
    case "${answer:-f}" in
        o|O) PALETTE="ocean" ;;
        g|G) PALETTE="forest" ;;
        c|C) PALETTE="cyberpunk" ;;
        m|M) PALETTE="mono" ;;
        *)   PALETTE="fire" ;;
    esac

    # Q3: Pet
    echo -ne "  ${W}Animated pet?${N} [Y/n]: "
    read -r answer < /dev/tty 2>/dev/null || answer=""
    case "${answer:-y}" in n|N|no|No) PET_ENABLED="no" ;; esac

    # Q4: Heatmap
    echo -ne "  ${W}Activity heatmap?${N} [Y/n]: "
    read -r answer < /dev/tty 2>/dev/null || answer=""
    case "${answer:-y}" in n|N|no|No) HEATMAP_ENABLED="no" ;; esac

    echo ""
    echo -e "  ${G}✓${N} Setup: ${AGENT_NAME} · ${PALETTE} · pet:${PET_ENABLED} · heatmap:${HEATMAP_ENABLED}"
else
    echo -e "  ${O}⚠${N} Non-interactive — using defaults (THOT, fire, pet on, heatmap on)"
fi

# ── Phase 7: Generate theme (logo, hero, pet, ALL colors) ──
_start_spin "Generating theme assets..."
THEME_SCRIPT=$(resolve "scripts/generate-theme.py") || true
if [ -n "${THEME_SCRIPT:-}" ] && [ -f "$THEME_SCRIPT" ]; then
    /usr/bin/python3 "$THEME_SCRIPT" \
        --skin "$H/skins/$SKIN.yaml" \
        --name "${AGENT_NAME}" \
        --palette "${PALETTE}" 2>/dev/null && _stop_spin_ok "Theme generated (${AGENT_NAME} · ${PALETTE})" || _stop_spin_warn "Theme generation skipped"
    [ "${THEME_SCRIPT#/tmp/}" != "$THEME_SCRIPT" ] && rm -f "$THEME_SCRIPT"
else
    _stop_spin_warn "Theme generator unavailable — using defaults"
fi

# ── Phase 7.5: Apply disable flags (pet/heatmap) ──
if [ "${PET_ENABLED}" = "no" ]; then
    _start_spin "Disabling pet..."
    /usr/bin/python3 -c "
import yaml; h='$H'
s=yaml.safe_load(open(f'{h}/skins/thot.yaml')); s['spinner']['pet_frames']=[]; s['spinner']['pet_fallback']=[]
yaml.dump(s,open(f'{h}/skins/thot.yaml','w'),default_flow_style=False,allow_unicode=True)
" 2>/dev/null && _stop_spin_ok "Pet disabled" || _stop_spin_warn "Pet disable skipped"
fi

if [ "${HEATMAP_ENABLED}" = "no" ]; then
    _start_spin "Disabling heatmap..."
    /usr/bin/python3 -c "
import yaml; h='$H'
s=yaml.safe_load(open(f'{h}/skins/thot.yaml')); s.pop('heatmap_colors',None)
yaml.dump(s,open(f'{h}/skins/thot.yaml','w'),default_flow_style=False,allow_unicode=True)
" 2>/dev/null && _stop_spin_ok "Heatmap disabled" || _stop_spin_warn "Heatmap disable skipped"
fi

# ── Phase 8: Activate skin ────────────────────────
_start_spin "Activating skin..."
python3 -c "
import os, yaml
home = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
cp = os.path.join(home, 'config.yaml')
if os.path.exists(cp):
    with open(cp) as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}
config.setdefault('display', {})['skin'] = 'thot'
with open(cp, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
" 2>/dev/null && _stop_spin_ok "Skin activated" || _stop_spin_err "Config update failed — run: hermes config set display.skin thot"

# ── Phase 9: Wire in heatmap (optional source patch) ──
PATCH_SCRIPT=$(resolve "scripts/apply-patches.py") || true
if [ -n "${PATCH_SCRIPT:-}" ] && [ -f "$PATCH_SCRIPT" ] && [ "${HEATMAP_ENABLED}" != "no" ]; then
    _start_spin "Wiring heatmap into banner..."
    /usr/bin/python3 "$PATCH_SCRIPT" --force 2>/dev/null && _stop_spin_ok "Heatmap wired" || _stop_spin_warn "Heatmap wiring skipped (skin still works)"
    [ "${PATCH_SCRIPT#/tmp/}" != "$PATCH_SCRIPT" ] && rm -f "$PATCH_SCRIPT"
fi

# ── Done ──────────────────────────────────────────
echo ""
echo -e "  ${G}╔══════════════════════════════════════╗${N}"
echo -e "  ${G}║  ⣿ ${AGENT_NAME} is online                    ║${N}"
echo -e "  ${G}╚══════════════════════════════════════╝${N}"
echo ""
echo -e "  ${C}hermes${N}          — see your living terminal"
echo -e "  ${C}/skin thot${N}      — switch in-session"
echo -e "  ${C}/thot-hotwire${N}   — re-patch after hermes update"
echo ""
echo -e "  ${O}Uninstall:${N} ${D}curl -fsSL ${REPO}/scripts/uninstall.sh | bash${N}"
echo -e "  ${O}Skill:${N}    ${D}hermes skills tap add m4xx101/thot${N}"
echo ""
