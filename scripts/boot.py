#!/usr/bin/env python3
"""
boot.py - Lobotto Resilient Boot Shim (v1.0)
=============================================
INVARIANT: Uses ONLY Python stdlib. This is the recovery layer.
If something breaks, this script must still function.

Usage:
    python scripts/boot.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# === STDLIB-ONLY SECTION ===
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = PROJECT_ROOT / ".context"
VAULT_DIR = PROJECT_ROOT / "vault"
SESSION_DIR = PROJECT_ROOT / "session_logs"
STATE_FILE = CONTEXT_DIR / "session_state.json"
CORRECTIONS_FILE = CONTEXT_DIR / "corrections.md"


def ensure_directories():
    """Create required directories if they don't exist."""
    for d in [CONTEXT_DIR, VAULT_DIR, SESSION_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_last_state():
    """Load the last saved session state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None


def load_last_ghost_note():
    """Find the most recent ghost note from session logs."""
    if not SESSION_DIR.exists():
        return None

    log_files = sorted(SESSION_DIR.glob("*.md"), reverse=True)
    for log_file in log_files:
        try:
            content = log_file.read_text(encoding="utf-8")
            for line in reversed(content.splitlines()):
                if line.strip().startswith("/gn") or "Ghost Note" in line:
                    return line.strip()
        except OSError:
            continue
    return None


def count_corrections():
    """Count accumulated corrections."""
    if not CORRECTIONS_FILE.exists():
        return 0
    try:
        content = CORRECTIONS_FILE.read_text(encoding="utf-8")
        return content.count("- ")
    except OSError:
        return 0


def check_vault_integrity():
    """Basic vault existence check."""
    if not VAULT_DIR.exists():
        return False, "Vault directory missing"
    return True, "Vault intact"


def main():
    """Lobotto boot sequence."""
    ensure_directories()

    print("=" * 60)
    print("LOBOTTO BOOT SEQUENCE v1.0")
    print("=" * 60)

    # Identity check
    directives = PROJECT_ROOT / "LOBOTTO_CORE_DIRECTIVES.md"
    identity = PROJECT_ROOT / "framework" / "Core_Identity.md"
    combat = PROJECT_ROOT / "framework" / "Combat_Protocol.md"

    print("\n[1/5] Identity Check:")
    for name, path in [("Directives", directives), ("Identity", identity), ("Combat Protocol", combat)]:
        status = "OK" if path.exists() else "MISSING"
        print(f"   [{status}] {name}")

    # Context recovery
    print("\n[2/5] Context Recovery:")
    state = load_last_state()
    if state:
        last_session = state.get("last_session", "unknown")
        pending_tasks = len(state.get("pending_tasks", []))
        print(f"   Last session: {last_session}")
        print(f"   Pending tasks: {pending_tasks}")
    else:
        print("   No previous state found (first boot or clean start)")

    # Ghost note re-alignment
    print("\n[3/5] Vibe Re-alignment:")
    ghost = load_last_ghost_note()
    if ghost:
        print(f"   Last vibe: {ghost}")
    else:
        print("   No ghost notes found")

    # Vault check
    print("\n[4/5] Vault Integrity:")
    vault_ok, vault_msg = check_vault_integrity()
    print(f"   [{vault_msg}]")

    # Corrections loaded
    print("\n[5/5] Compound Knowledge:")
    corrections = count_corrections()
    print(f"   {corrections} corrections accumulated")

    # Final status
    print("\n" + "=" * 60)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"LOBOTTO ONLINE - {now}")
    print("Combat Protocol: ACTIVE")
    print("Anti-Sycophancy Mandate: ENFORCED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
