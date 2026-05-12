#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# CRYPTEX Banner System Installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════════════
set -euo pipefail
V="1.0.0"; SKIN="cryptex"; H="${HERMES_HOME:-$HOME/.hermes}"
REPO="https://raw.githubusercontent.com/m4xx101/thot/main"
G='\033[0;32m'; R='\033[0;31m'; C='\033[0;36m'; O='\033[0;33m'; N='\033[0m'

echo ""; echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo -e "${O}║  CRYPTEX v${V} — Living Terminal Identity  ║${N}"
echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo ""

# ── Detect Hermes ────────────────────────────────
[ -d "$H" ] || { echo -e "${R}✗ Hermes not found${N}"; exit 1; }
echo -e "${G}✓${N} Hermes found"
mkdir -p "$H/skins" "$H/hermes-agent/hermes_cli" "$H/hermes-agent/gateway/builtin_hooks/boot-cryptex"

# ── Resolve file source ───────────────────────────
# When piped via curl|bash, $0="bash" so dirname fails.
# Strategy: try local path first (repo clone), then download from GitHub.
resolve() {
    local rel="$1"
    local local_src="$(dirname "$0")/../${rel}"
    if [ -f "$local_src" ]; then echo "$local_src"; return 0; fi
    local tmp="/tmp/thot-install-$$-$(basename "$rel")"
    curl -fsSL "${REPO}/${rel}" -o "$tmp" 2>/dev/null && { echo "$tmp"; return 0; }
    return 1
}

# ── Install skin YAML ─────────────────────────────
SKIN_SRC=$(resolve "skins/cryptex.yaml") || { echo -e "${R}✗ Cannot fetch skin YAML${N}"; exit 1; }
cp "$SKIN_SRC" "$H/skins/$SKIN.yaml" && echo -e "${G}✓${N} Skin installed"
[ "${SKIN_SRC#/tmp/}" != "$SKIN_SRC" ] && rm -f "$SKIN_SRC"

# ── Install extended_banner.py ────────────────────
EXT_SRC=$(resolve "src/hermes_cli/extended_banner.py") || true
if [ -n "${EXT_SRC:-}" ] && [ -f "$EXT_SRC" ]; then
    cp "$EXT_SRC" "$H/hermes-agent/hermes_cli/extended_banner.py"
    echo -e "${G}✓${N} extended_banner installed"
    [ "${EXT_SRC#/tmp/}" != "$EXT_SRC" ] && rm -f "$EXT_SRC"
else
    echo -e "${O}⚠ extended_banner skipped — download it from the repo${N}"
fi

# ── Install gateway boot hook ─────────────────────
HOOK_SRC=$(resolve "gateway/boot-cryptex/hook.py") || true
if [ -n "${HOOK_SRC:-}" ] && [ -f "$HOOK_SRC" ]; then
    cp "$HOOK_SRC" "$H/hermes-agent/gateway/builtin_hooks/boot-cryptex/hook.py"
    echo -e "${G}✓${N} Boot hook installed"
    [ "${HOOK_SRC#/tmp/}" != "$HOOK_SRC" ] && rm -f "$HOOK_SRC"
else
    echo -e "${O}⚠ Boot hook skipped${N}"
fi

# ── Activate skin in config ───────────────────────
# Try pip-installing pyyaml first (needed for config edit)
python3 -c "import yaml" 2>/dev/null || python3 -m pip install pyyaml -q --break-system-packages 2>/dev/null || true

python3 -c "
import os, sys
home = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
try:
    import yaml
except ImportError:
    print('FALLBACK')
    sys.exit(0)

config_path = os.path.join(home, 'config.yaml')
if os.path.exists(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}
config.setdefault('display', {})['skin'] = '$SKIN'
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
print('DONE')
" 2>/dev/null || echo -e "${R}✗ Config update failed — run: hermes config set display.skin $SKIN${N}"

echo -e "${G}✓${N} Skin activated"

# ── Done ──────────────────────────────────────────
echo ""
echo -e "${G}╔══════════════════════════════╗${N}"
echo -e "${G}║  ⣿ CRYPTEX installed!       ║${N}"
echo -e "${G}╚══════════════════════════════╝${N}"
echo ""
echo -e "  ${C}hermes${N} — see the living terminal"
echo -e "  ${C}/skin cryptex${N} — switch in-session"
echo -e "  ${C}/thot-hotwire${N} — force re-patch after update"
echo -e "  ${C}hermes skills tap add m4xx101/thot${N} — add self-evolving skill"
