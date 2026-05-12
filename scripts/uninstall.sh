#!/usr/bin/env bash
set -euo pipefail
H="${HERMES_HOME:-$HOME/.hermes}"; G='\033[0;32m'; N='\033[0m'
echo "→ Reverting to default Hermes Agent theme..."
python3 -c "import os,yaml;h=os.environ.get('HERMES_HOME',os.path.expanduser('~/.hermes'));c=yaml.safe_load(open(f'{h}/config.yaml'))if os.path.exists(f'{h}/config.yaml')else{};c.setdefault('display',{})['skin']='default';yaml.dump(c,open(f'{h}/config.yaml','w'),default_flow_style=False,allow_unicode=True)" 2>/dev/null
rm -f "$H/skins/thot.yaml" "$H/hermes-agent/hermes_cli/extended_banner.py" "$H/hermes-agent/gateway/builtin_hooks/boot-thot/hook.py" "$H/.thot_welcome_sent" "$H/.thot_patch_version"
echo -e "${G}✓ Reverted to default.${N}"
