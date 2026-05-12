#!/usr/bin/env python3
"""
apply-patches.py — Version-aware source patcher for CRYPTEX.

Features:
- Checks Hermes version before patching
- Re-applies after 'hermes update' (version changed)
- Graceful degradation if upstream API changed
- --force flag (hotwire) to patch regardless
- --check flag to report status without applying
- py_compile validation before committing patch
- Auto-restore backup on syntax failure
"""
import os, sys, shutil
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
SRC = HERMES_HOME / "hermes-agent"
VERSION_FILE = SRC / "hermes_cli" / "__init__.py"
SENTINEL = HERMES_HOME / ".thot_patch_version"


def get_version():
    """Extract version string from hermes_cli/__init__.py."""
    if not VERSION_FILE.exists():
        return None
    for line in open(VERSION_FILE):
        if line.startswith("__version__"):
            return line.split("=")[1].strip().strip('"').strip("'")
    return None


def get_patched_version():
    """Read the version that was last patched."""
    if SENTINEL.exists():
        return SENTINEL.read_text().strip()
    return None


def backup_original(target):
    """Backup original file if not already backed up."""
    backup = target.with_suffix(target.suffix + ".cryptex-backup")
    if not backup.exists():
        shutil.copy2(target, backup)
    return backup


def patch_banner():
    """Add extended_banner import to banner.py."""
    target = SRC / "hermes_cli" / "banner.py"
    if not target.exists():
        return False, "banner.py not found"

    backup_original(target)
    content = target.read_text()

    if "from hermes_cli.extended_banner import build_extended_sections" in content:
        return True, "already patched"

    marker = '    right_content = "\\n".join(right_lines)'
    if marker not in content:
        return False, "banner.py structure changed — cannot patch (graceful degrade)"

    insert = (
        '\n    # ── CRYPTEX extended sections ──\n'
        '    try:\n'
        '        from hermes_cli.extended_banner import build_extended_sections\n'
        '        for line in build_extended_sections():\n'
        '            right_lines.append(line)\n'
        '    except ImportError:\n'
        '        pass\n'
    )
    content = content.replace(marker, insert + "\n" + marker)
    target.write_text(content)
    return True, "banner.py patched"


def patch_display():
    """Add pet frame rendering to agent/display.py."""
    target = SRC / "agent" / "display.py"
    if not target.exists():
        return False, "display.py not found"

    backup_original(target)
    content = target.read_text()

    if "pet_frames" in content:
        return True, "already patched"

    marker = "self.console.print("
    if marker not in content:
        return False, "display.py structure changed — cannot patch (graceful degrade)"

    insert = (
        '\n'
        '                # ── CRYPTEX pet animation ──\n'
        '                try:\n'
        '                    from hermes_cli.skin_engine import get_active_skin\n'
        '                    skin = get_active_skin()\n'
        '                    pet = skin.spinner.get("pet_frames") or skin.spinner.get("pet_fallback", [])\n'
        '                    if pet:\n'
        '                        import os as _os\n'
        '                        term = _os.environ.get("TERM", "")\n'
        '                        use_braille = "screen" not in term and "tmux" not in term\n'
        '                        frames = skin.spinner.get("pet_frames") if use_braille else skin.spinner.get("pet_fallback", pet)\n'
        '                        if frames:\n'
        '                            idx = getattr(self, "_pet_idx", 0) % len(frames)\n'
        '                            self.console.print(frames[idx])\n'
        '                            self._pet_idx = idx + 1\n'
        '                except Exception:\n'
        '                    pass\n'
    )
    content = content.replace(marker, insert + "\n" + marker, 1)
    target.write_text(content)
    return True, "display.py patched"


def check_syntax(target):
    """Verify Python file still parses after patching."""
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(target)],
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stderr


def apply():
    """Apply all patches. Returns list of (filename, success, message)."""
    ver = get_version()
    if not ver:
        return [("version_check", False, "cannot determine Hermes version")]

    results = []

    # Patch banner.py
    target = SRC / "hermes_cli" / "banner.py"
    ok, msg = patch_banner()
    if ok:
        syntax_ok, err = check_syntax(target)
        if not syntax_ok:
            results.append(("banner.py", False, f"patch breaks syntax — reverted: {err[:100]}"))
            backup = target.with_suffix(".py.cryptex-backup")
            if backup.exists():
                shutil.copy2(backup, target)
        else:
            results.append(("banner.py", True, msg))
    else:
        results.append(("banner.py", False, msg))

    # Patch display.py
    target = SRC / "agent" / "display.py"
    ok, msg = patch_display()
    if ok:
        syntax_ok, err = check_syntax(target)
        if not syntax_ok:
            results.append(("display.py", False, f"patch breaks syntax — reverted: {err[:100]}"))
            backup = target.with_suffix(".py.cryptex-backup")
            if backup.exists():
                shutil.copy2(backup, target)
        else:
            results.append(("display.py", True, msg))
    else:
        results.append(("display.py", False, msg))

    SENTINEL.write_text(ver)
    return results


def main():
    force = "--force" in sys.argv
    check = "--check" in sys.argv

    ver = get_version()
    patched_ver = get_patched_version()

    if check:
        if ver and ver == patched_ver:
            print("up_to_date")
        elif ver:
            print(f"needs_patch: {patched_ver} → {ver}")
        else:
            print("version_unknown")
        return

    if force or (ver and ver != patched_ver):
        results = apply()
        for fname, ok, msg in results:
            print(f"  {'✓' if ok else '⚠'} {fname}: {msg}")

        all_ok = all(r[1] for r in results)
        if not all_ok:
            print("\n⚠ Some patches could not be applied.")
            print("  CRYPTEX skin still works (colors, branding, spinner).")
            print("  Extended sections (heatmap, pet) degraded gracefully.")
            print("  Use /thot-hotwire after updating Hermes to retry.")
    else:
        print("patches already up-to-date")


if __name__ == "__main__":
    main()
