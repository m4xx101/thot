#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════
# CRYPTEX Banner System Installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash
# ═══════════════════════════════════════════════════════
set -euo pipefail
V="1.0.0"; SKIN="cryptex"; H="${HERMES_HOME:-$HOME/.hermes}"
G='\033[0;32m'; R='\033[0;31m'; C='\033[0;36m'; O='\033[0;33m'; N='\033[0m'
echo ""; echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo -e "${O}║  CRYPTEX v${V} — Living Terminal Identity  ║${N}"
echo -e "${O}⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿${N}"
echo ""
[ -d "$H" ] || { echo -e "${R}✗ Hermes not found${N}"; exit 1; }
echo -e "${G}✓${N} Hermes found"
mkdir -p "$H/skins"
D="$(dirname "$0")/.."
cp "$D/skins/cryptex.yaml" "$H/skins/$SKIN.yaml" && echo -e "${G}✓${N} Skin installed"
[ -f "$D/src/hermes_cli/extended_banner.py" ] && mkdir -p "$H/hermes-agent/hermes_cli" && cp "$D/src/hermes_cli/extended_banner.py" "$H/hermes-agent/hermes_cli/" && echo -e "${G}✓${N} extended_banner installed"
[ -f "$D/gateway/boot-cryptex/hook.py" ] && mkdir -p "$H/hermes-agent/gateway/builtin_hooks/boot-cryptex" && cp "$D/gateway/boot-cryptex/hook.py" "$H/hermes-agent/gateway/builtin_hooks/boot-cryptex/" && echo -e "${G}✓${N} Boot hook installed"
python3 -c "import os,yaml;h=os.environ.get('HERMES_HOME',os.path.expanduser('~/.hermes'));c=yaml.safe_load(open(f'{h}/config.yaml'))if os.path.exists(f'{h}/config.yaml')else{};c.setdefault('display',{})['skin']='$SKIN';yaml.dump(c,open(f'{h}/config.yaml','w'),default_flow_style=False,allow_unicode=True)" 2>/dev/null && echo -e "${G}✓${N} Skin activated" || echo -e "${R}✗ Config update failed — run: hermes config set display.skin $SKIN${N}"
[ -f "$D/scripts/apply-patches.py" ] && python3 "$D/scripts/apply-patches.py" 2>&1 && echo -e "${G}✓${N} Patches applied" || true
echo ""; echo -e "${G}╔══════════════════════════════╗${N}"
echo -e "${G}║  ⣿ CRYPTEX installed!       ║${N}"
echo -e "${G}╚══════════════════════════════╝${N}"
echo -e "  ${C}hermes${N} — see the living terminal"
echo -e "  ${C}/skin cryptex${N} — switch in-session"
echo -e "  ${C}/thot-hotwire${N} — force re-patch after update"
