#!/usr/bin/env bash
# End-to-end test: install skin, verify, uninstall.
set -euo pipefail; G='\033[0;32m'; R='\033[0;31m'; N='\033[0m'
echo "═══ THOT E2E Test ═══"
TEST_HOME="/tmp/thot-test-$$"; mkdir -p "$TEST_HOME/skins"; export HERMES_HOME="$TEST_HOME"
cat > "$TEST_HOME/config.yaml" << 'YAML'
model: {provider: openrouter}
display: {skin: default}
YAML
echo "1. Installing..."; cp skins/cryptex.yaml "$TEST_HOME/skins/"
python3 -c "import os,yaml;h='$TEST_HOME';c=yaml.safe_load(open(f'{h}/config.yaml'));c.setdefault('display',{})['skin']='cryptex';yaml.dump(c,open(f'{h}/config.yaml','w'),default_flow_style=False,allow_unicode=True)"
SKIN=$(python3 -c "import yaml;print(yaml.safe_load(open('$TEST_HOME/config.yaml')).get('display',{}).get('skin',''))")
[ "$SKIN" = "cryptex" ] && echo -e "   ${G}✓${N} Skin set" || { echo -e "${R}✗${N}"; exit 1; }
echo "2. Validating YAML..."; python3 -c "import yaml;d=yaml.safe_load(open('$TEST_HOME/skins/cryptex.yaml'));assert'name'in d;print('   ✓ Valid')"
echo "3. Uninstalling..."; python3 -c "import os,yaml;h='$TEST_HOME';c=yaml.safe_load(open(f'{h}/config.yaml'));c['display']['skin']='default';yaml.dump(c,open(f'{h}/config.yaml','w'),default_flow_style=False,allow_unicode=True)"
rm -f "$TEST_HOME/skins/cryptex.yaml"; rm -rf "$TEST_HOME"
echo -e "${G}═══ All tests passed ═══${N}"
