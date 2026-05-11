#!/usr/bin/env python3
"""Verify all YAML files in skins/ parse correctly."""
import sys; from pathlib import Path
try: import yaml
except ImportError: print("SKIP: PyYAML not installed"); sys.exit(0)

skins_dir = Path(__file__).parent.parent / "skins"
failed = 0
for yf in sorted(skins_dir.rglob("*.yaml")):
    try:
        d = yaml.safe_load(open(yf))
        if not isinstance(d, dict): print(f"FAIL: {yf} — not dict"); failed += 1
        elif "name" not in d: print(f"FAIL: {yf} — no name"); failed += 1
        else: print(f"  OK : {yf} → '{d['name']}'")
    except Exception as e: print(f"FAIL: {yf} — {e}"); failed += 1
if failed: print(f"\n{failed} failed!"); sys.exit(1)
print(f"\nAll {len(list(skins_dir.rglob('*.yaml')))} valid.")
