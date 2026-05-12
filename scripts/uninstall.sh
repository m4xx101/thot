#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# THOT Uninstaller — One command to revert to default Hermes theme
# curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/uninstall.sh | bash
# ═══════════════════════════════════════════════════════════════
set -euo pipefail
H="${HERMES_HOME:-$HOME/.hermes}"
G='\033[0;32m'; O='\033[0;33m'; R='\033[0;31m'; N='\033[0m'

echo ""
echo -e "  ${O}⣿ THOT Uninstaller${N}"
echo ""

# ── Already-installed? ───────────────────────────
SKIN_F="$H/skins/thot.yaml"
if [ ! -f "$SKIN_F" ]; then
    python3 -c "
import yaml,os
cp=os.path.join(os.environ.get('HERMES_HOME',os.path.expanduser('~/.hermes')),'config.yaml')
try:
    c=yaml.safe_load(open(cp)) or {}
    s=c.get('display',{}).get('skin','')
except: s=''
if s!='thot': exit(1)
" 2>/dev/null || {
        echo -e "  ${R}✗${N} THOT is not installed"
        echo -e "  ${O}→${N} Nothing to uninstall."
        echo ""
        exit 0
    }
fi

# 1. Revert skin in config
python3 -c "
import os, yaml
h=os.environ.get('HERMES_HOME',os.path.expanduser('~/.hermes'))
cp=os.path.join(h,'config.yaml')
if os.path.exists(cp):
    with open(cp) as f:
        c=yaml.safe_load(f) or {}
    if c and c.get('display',{}).get('skin')=='thot':
        c['display']['skin']='default'
        with open(cp,'w') as f:
            yaml.dump(c,f,default_flow_style=False,allow_unicode=True)
        print('REVERTED')
" 2>/dev/null && echo -e "  ${G}✓${N} Skin reverted to default" || echo -e "  ${O}⚠${N} Config already default"

# 2. Remove skin file
rm -f "$H/skins/thot.yaml" && echo -e "  ${G}✓${N} Skin removed"

# 3. Remove extended_banner
rm -f "$H/hermes-agent/hermes_cli/extended_banner.py" && echo -e "  ${G}✓${N} extended_banner removed"

# 4. Remove boot hook
rm -rf "$H/hermes-agent/gateway/builtin_hooks/boot-thot" 2>/dev/null && echo -e "  ${G}✓${N} Boot hook removed" || true

# 5. Remove sentinels
rm -f "$H/.thot_welcome_sent" "$H/.thot_patch_version" && echo -e "  ${G}✓${N} Cleanup complete"

echo ""
echo -e "  ${G}✓ THOT uninstalled. Hermes Agent restored to default.${N}"
echo -e "  ${O}Reinstall:${N} curl -fsSL https://raw.githubusercontent.com/m4xx101/thot/main/scripts/install.sh | bash"
echo ""
