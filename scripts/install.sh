#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# THOT — Hermes Agent Living Terminal Identity Installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════

# ── Pipe detection: curl|bash kills TTY — re-exec properly ──
if [ ! -t 0 ]; then
    # We're piped in (curl|bash, CI, etc).
    # Try to re-exec with a real TTY for interactive setup.
    # If /dev/tty is unavailable (CI, Docker), fall through to defaults.
    _THOT_REEXEC=$(mktemp /tmp/thot-install-XXXXXX.sh)
    if curl -fsSL --connect-timeout 5 --max-time 15 \
        "https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh" \
        -o "$_THOT_REEXEC" 2>/dev/null; then
        # Attempt re-exec with /dev/tty. If no TTY available, fall through.
        { exec bash "$_THOT_REEXEC" "$@" < /dev/tty; } 2>/dev/null || true
    fi
    # Re-exec failed or TTY unavailable — continue non-interactively
    echo ""
    echo -e "  ${O}─── Non-interactive mode ───${N}"
    echo -e "  ${D}Tips for interactive setup:${N}"
    echo -e "  ${D}  curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh -o /tmp/thot.sh && bash /tmp/thot.sh${N}"
    echo -e "  ${D}  …or pipe answers: printf 'NAME\\npalette\\ny\\ny\\n' | bash /tmp/thot.sh${N}"
    echo ""
fi

set -euo pipefail
V="1.1.0"; SKIN="thot"; H="${HERMES_HOME:-$HOME/.hermes}"
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
    # 1. Try relative to script location (works for git clones)
    local script_dir="$(cd "$(dirname "$0")" 2>/dev/null && pwd || dirname "$0")"
    local local_src="${script_dir}/../${rel}"
    if [ -f "$local_src" ]; then echo "$local_src"; return 0; fi
    # 2. Try relative to PWD (works when running from repo root)
    if [ -f "${rel}" ]; then echo "${PWD}/${rel}"; return 0; fi
    # 3. Download from GitHub (3 retries, 5s timeout)
    local tmp="/tmp/thot-install-$$-$(basename "$rel")"
    for i in 1 2 3; do
        curl -fsSL --connect-timeout 5 --max-time 10 "${REPO}/${rel}" -o "$tmp" 2>/dev/null && { echo "$tmp"; return 0; }
        sleep 1
    done
    return 1
}

# ── Banner ────────────────────────────────────────
echo ""
echo -e "  ${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo -e "  ${O}║  THOT v${V} — Living Terminal Identity      ║${N}"
echo -e "  ${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo ""

# ── Phase 0: Already-installed check ──────────────
_detect_installed() {
    # Returns "full|partial|none" — pure bash, no Python/yaml dependency
    local skin_f="$H/skins/thot.yaml"
    local cfg_f="$H/config.yaml"
    local active=""

    # Check if config references skin=thot (without needing pyyaml)
    if [ -f "$cfg_f" ]; then
        # YAML is simple enough: look for "skin: thot" line
        if grep -qE '^\s*skin:\s*"?thot"?' "$cfg_f" 2>/dev/null; then
            active="thot"
        fi
    fi

    if [ "$active" = "thot" ] && [ -f "$skin_f" ]; then
        echo "full"
    elif [ -f "$skin_f" ] || [ "$active" = "thot" ]; then
        echo "partial"
    else
        echo "none"
    fi
}

# ── Run detection (catch errors, never crash) ──────
INSTALLED_STATE="$(_detect_installed 2>/dev/null || echo "none")"

if [ "$INSTALLED_STATE" != "none" ]; then
    echo -e "  ${O}⚠  THOT is already installed${N}"
    echo ""
    # Show current state (pure bash, no yaml dep)
    if [ -f "$H/skins/thot.yaml" ]; then
        # Use Python only if yaml is available, otherwise show basic info
        python3 -c "
try:
    import yaml
    s=yaml.safe_load(open('$H/skins/thot.yaml')) or {}
    name=s.get('branding',{}).get('agent_name','THOT')
    colors=s.get('colors',{})
    c=colors.get('banner_border','')
    if   '#CC3300' in c: pal='fire'
    elif '#2A6FB9' in c: pal='ocean'
    elif '#2E7D32' in c: pal='forest'
    elif '#00FFFF' in c: pal='cyberpunk'
    elif '#555555' in c: pal='mono'
    else: pal='custom'
    pet=len(s.get('spinner',{}).get('pet_frames',[]))
    heat='yes' if s.get('heatmap_colors') else 'no'
    print(f'  {name} · {pal} · pet({pet} frames) · heatmap({heat})')
except:
    print('  THOT · (yaml not available — re-run to inspect)')
" 2>/dev/null || echo "  THOT · (detected: skin file exists)"
    fi
    echo ""
    echo -ne "  ${W}Update? This will regenerate art, pet & theme${N} [Y/n]: "
    if [ -t 0 ]; then
        read -r answer < /dev/tty 2>/dev/null || answer=""
    else
        read -r answer || answer=""  # consume one line from piped stdin
    fi
    case "${answer:-y}" in
        n|N|no|No)
            echo -e "\n  ${O}→${N} Keeping current install. To force: ${D}curl ...install.sh | bash -s -- --force${N}"
            echo ""
            exit 0
            ;;
    esac
    echo -e "\n  ${G}→${N} Updating THOT...\n"
fi

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

_start_spin "Installing pyfiglet (font rendering)..."
python3 -c "import pyfiglet" 2>/dev/null || python3 -m pip install pyfiglet -q --break-system-packages 2>/dev/null || {
    _stop_spin_warn "pyfiglet unavailable — will use block-art fallback for logo"
    PYFIGLET_OK="no"
}
[ "${PYFIGLET_OK:-yes}" != "no" ] && _stop_spin_ok "pyfiglet ready" || true

# ── Phase 6: Interactive setup ────────────────────
# Save original stdin, read from /dev/tty, then restore.
# This prevents 'exec < /dev/tty' from hanging the script on exit.
AGENT_NAME="THOT"
PALETTE="fire"
PET_ENABLED="yes"
HEATMAP_ENABLED="yes"

if [ -t 0 ]; then
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
    # Non-interactive: read answers from piped stdin (one per line)
    echo -e "  ${O}─── Reading setup from stdin... ───${N}"
    read -r answer || answer=""; [ -n "${answer:-}" ] && AGENT_NAME="$answer"
    read -r answer || answer=""
    case "${answer:-f}" in
        o|O) PALETTE="ocean" ;; g|G) PALETTE="forest" ;;
        c|C) PALETTE="cyberpunk" ;; m|M) PALETTE="mono" ;;
        *)   PALETTE="fire" ;;
    esac
    read -r answer || answer=""
    case "${answer:-y}" in n|N|no|No) PET_ENABLED="no" ;; esac
    read -r answer || answer=""
    case "${answer:-y}" in n|N|no|No) HEATMAP_ENABLED="no" ;; esac
    echo -e "  ${G}✓${N} Setup: ${AGENT_NAME} · ${PALETTE} · pet:${PET_ENABLED} · heatmap:${HEATMAP_ENABLED}"
fi

# ── Phase 7: Generate theme (logo, hero, pet, ALL colors) ──
_start_spin "Generating theme assets..."
THEME_SCRIPT=$(resolve "scripts/generate-theme.py") || true
if [ -n "${THEME_SCRIPT:-}" ] && [ -f "$THEME_SCRIPT" ]; then
    THEME_ERR=$(mktemp)
    if python3 "$THEME_SCRIPT" \
        --skin "$H/skins/$SKIN.yaml" \
        --name "${AGENT_NAME}" \
        --palette "${PALETTE}" 2>"$THEME_ERR"; then
        _stop_spin_ok "Theme generated (${AGENT_NAME} · ${PALETTE})"
    else
        _stop_spin_err "Theme generation failed:"
        cat "$THEME_ERR" | while IFS= read -r line; do echo "    ${R}${line}${N}"; done
    fi
    rm -f "$THEME_ERR"
    [ "${THEME_SCRIPT#/tmp/}" != "$THEME_SCRIPT" ] && rm -f "$THEME_SCRIPT"
else
    _stop_spin_warn "Theme generator unavailable — using defaults"
fi

# ── Phase 7.5: Apply disable flags (pet/heatmap) ──
if [ "${PET_ENABLED}" = "no" ]; then
    _start_spin "Disabling pet..."
    python3 -c "
import yaml; h='$H'
s=yaml.safe_load(open(f'{h}/skins/thot.yaml')); s['spinner']['pet_frames']=[]; s['spinner']['pet_fallback']=[]
yaml.dump(s,open(f'{h}/skins/thot.yaml','w'),default_flow_style=False,allow_unicode=True)
" 2>/dev/null && _stop_spin_ok "Pet disabled" || _stop_spin_warn "Pet disable skipped"
fi

if [ "${HEATMAP_ENABLED}" = "no" ]; then
    _start_spin "Disabling heatmap..."
    python3 -c "
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
    python3 "$PATCH_SCRIPT" --force 2>/dev/null && _stop_spin_ok "Heatmap wired" || _stop_spin_warn "Heatmap wiring skipped (skin still works)"
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
