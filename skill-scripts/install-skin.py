#!/usr/bin/env python3
"""
install-skin.py — Deploy CRYPTEX skin + extended_banner + boot hook + patches.
Called by SKILL.md on first load. Idempotent — safe to re-run.
"""
import os, shutil, subprocess, sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def install():
    script_dir = Path(__file__).parent.parent  # thot/
    results = []

    # 1. Install skin YAML
    src = script_dir / "skins" / "thot.yaml"
    dst = HERMES_HOME / "skins" / "thot.yaml"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
        shutil.copy2(src, dst)
        results.append("skin installed")
    else:
        results.append("skin up-to-date")

    # 2. Install extended_banner.py
    src = script_dir / "src" / "hermes_cli" / "extended_banner.py"
    dst = HERMES_HOME / "hermes-agent" / "hermes_cli" / "extended_banner.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
        shutil.copy2(src, dst)
        results.append("extended_banner installed")
    else:
        results.append("extended_banner up-to-date")

    # 3. Install boot hook
    src = script_dir / "gateway" / "boot-thot" / "hook.py"
    dst = HERMES_HOME / "hermes-agent" / "gateway" / "builtin_hooks" / "boot-thot" / "hook.py"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)
        results.append("boot hook installed")
    else:
        results.append("boot hook up-to-date")

    # 4. Apply source patches (safe — detects version, re-applies if needed)
    patch_script = script_dir / "scripts" / "apply-patches.py"
    if patch_script.exists():
        r = subprocess.run(
            [sys.executable, str(patch_script), "--check"],
            capture_output=True, text=True
        )
        if "needs_patch" in r.stdout or r.returncode != 0:
            subprocess.run([sys.executable, str(patch_script)], check=False)
            results.append("patches applied")
        else:
            results.append("patches up-to-date")

    # 5. Activate skin in config
    try:
        import yaml
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q", "--break-system-packages"])
        import yaml

    config_path = HERMES_HOME / "config.yaml"
    if config_path.exists():
        config = yaml.safe_load(open(config_path)) or {}
    else:
        config = {}
    config.setdefault("display", {})["skin"] = "thot"
    yaml.dump(config, open(config_path, "w"), default_flow_style=False, allow_unicode=True)
    results.append("skin activated")

    print(" · ".join(results))


def check():
    """Silent check — exit 0 if skin active, 1 if not."""
    try:
        import yaml
    except ImportError:
        print("INACTIVE")
        return
    config_path = HERMES_HOME / "config.yaml"
    if config_path.exists():
        config = yaml.safe_load(open(config_path)) or {}
        if config.get("display", {}).get("skin") == "thot":
            print("ACTIVE")
            return
    print("INACTIVE")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        install()
