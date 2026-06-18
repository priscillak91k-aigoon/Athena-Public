#!/usr/bin/env python3
"""
Athena State Recovery — Rollback & Snapshot Engine
===================================================
Operates as the fallback mechanism for athena_brain_health.py.
State files (.context/*.json) are untrusted surfaces. This script
provides a known-good reset point.

Usage:
  python scripts/athena_state_recovery.py --backup
  python scripts/athena_state_recovery.py --restore

Called by: 
  --backup: /sleep workflow
  --restore: Manual or automated trigger upon CRITICAL health failure.
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
SNAPSHOT_DIR = CONTEXT_DIR / "snapshots" / "last_known_good"

TARGET_FILES = [
    "lobotto_working_memory.json",
    "lobotto_boot_mode.json",
    "session_state.json",
    "corrections.md"
]

def backup_state():
    """Create a snapshot of all tracked state files."""
    print("Initiating state backup...")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    backed_up = 0
    for filename in TARGET_FILES:
        src = CONTEXT_DIR / filename
        dst = SNAPSHOT_DIR / filename
        
        if src.exists():
            shutil.copy2(src, dst)
            backed_up += 1
            print(f"  [OK] Snapshot saved: {filename}")
        else:
            print(f"  [SKIP] File missing: {filename}")
            
    # Write metadata
    meta = SNAPSHOT_DIR / "snapshot_meta.txt"
    meta.write_text(f"Snapshot created: {datetime.now(timezone.utc).isoformat()}Z\nTrigger: /sleep workflow\n", encoding="utf-8")
    
    print(f"Backup complete. {backed_up} files secured in last_known_good.")

def restore_state():
    """Restore state files from the last known-good snapshot."""
    print("Initiating emergency state rollback...")
    if not SNAPSHOT_DIR.exists():
        print("[FATAL] No snapshot directory found. Cannot restore.")
        sys.exit(1)
        
    restored = 0
    for filename in TARGET_FILES:
        src = SNAPSHOT_DIR / filename
        dst = CONTEXT_DIR / filename
        
        if src.exists():
            shutil.copy2(src, dst)
            restored += 1
            print(f"  [OK] Restored: {filename}")
        else:
            print(f"  [WARN] Missing from snapshot: {filename}")
            
    print(f"Rollback complete. {restored} files restored to last known-good state.")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["--backup", "--restore"]:
        print("Usage: python athena_state_recovery.py [--backup | --restore]")
        sys.exit(1)
        
    if sys.argv[1] == "--backup":
        backup_state()
    elif sys.argv[1] == "--restore":
        restore_state()
