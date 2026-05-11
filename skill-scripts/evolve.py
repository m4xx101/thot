#!/usr/bin/env python3
"""
evolve.py — Apply one customization to active skin YAML.

Usage:
    python3 evolve.py --set tool_emojis.delegate_task "🧠"
    python3 evolve.py --palette-shift warm
    python3 evolve.py --activate cryptex
"""
import os, sys, json
from pathlib import Path

HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def load():
    try:
        import yaml
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q", "--break-system-packages"])
        import yaml

    cp = HOME / "config.yaml"
    name = yaml.safe_load(open(cp)).get("display", {}).get("skin", "default") if cp.exists() else "default"
    sp = HOME / "skins" / f"{name}.yaml"
    if not sp.exists():
        print(f"Skin not found: {sp}")
        sys.exit(1)
    return yaml.safe_load(open(sp)), sp


def save(data, path):
    import yaml
    yaml.dump(data, open(path, "w"), default_flow_style=False, allow_unicode=True)


def set_nested(data, path, value):
    keys = path.split(".")
    c = data
    for k in keys[:-1]:
        if k not in c:
            c[k] = {}
        c = c[k]
    try:
        value = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        pass
    c[keys[-1]] = value
    return data


def main():
    if len(sys.argv) < 3:
        print("Usage: evolve.py --set path value | --palette-shift cool|warm | --activate name")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "--set" and len(sys.argv) >= 4:
        d, p = load()
        d = set_nested(d, sys.argv[2], sys.argv[3])
        save(d, p)
        print(f"SET {sys.argv[2]} — restart Hermes to see change")

    elif cmd == "--activate" and len(sys.argv) >= 3:
        import yaml
        cp = HOME / "config.yaml"
        c = yaml.safe_load(open(cp)) if cp.exists() else {}
        c.setdefault("display", {})["skin"] = sys.argv[2]
        yaml.dump(c, open(cp, "w"), default_flow_style=False, allow_unicode=True)
        print(f"ACTIVATED {sys.argv[2]}")

    elif cmd == "--palette-shift" and len(sys.argv) >= 3:
        shift = 20 if sys.argv[2] == "warm" else -20
        d, p = load()
        for k, v in list(d.get("colors", {}).items()):
            if v.startswith("#") and len(v) == 7:
                r = max(0, min(255, int(v[1:3], 16) + shift))
                b = max(0, min(255, int(v[5:7], 16) - shift))
                d["colors"][k] = f"#{r:02X}{int(v[3:5], 16):02X}{b:02X}"
        save(d, p)
        print(f"PALETTE-SHIFT {sys.argv[2]} — restart Hermes to see change")

    else:
        print(f"Unknown: {sys.argv}")


if __name__ == "__main__":
    main()
