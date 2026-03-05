#!/usr/bin/env python3
"""
ghost_note.py - Lobotto Vibe Registration (v1.0)
=================================================
Registers a one-line vibe capture to the current session log.
Ghost Notes are the first thing loaded on boot to recalibrate
Lobotto's emotional and cognitive context.

Usage:
    python scripts/ghost_note.py "Cilla is energised today"
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SESSION_DIR = ROOT / "session_logs"
CONTEXT_DIR = ROOT / ".context"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)


def get_current_session_log():
    """Get or create today's session log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = SESSION_DIR / f"session_{today}.md"

    if not log_file.exists():
        header = f"# Session Log - {today}\n\n"
        log_file.write_text(header, encoding="utf-8")

    return log_file


def register_ghost_note(note):
    """Register a ghost note to the session log and context."""
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")

    # Append to session log
    log_file = get_current_session_log()
    entry = f"\n### Ghost Note [{timestamp}]\n\n> {note}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)

    # Save as latest ghost note for boot re-alignment
    latest_file = CONTEXT_DIR / "latest_ghost_note.json"
    data = {
        "note": note,
        "timestamp": now.isoformat(),
        "session_date": now.strftime("%Y-%m-%d"),
    }
    latest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"Ghost Note registered: {note}")
    print(f"Logged to: {log_file.name}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python ghost_note.py \"Your note here\"")
        print("\nExamples:")
        print('  python ghost_note.py "Cilla is focused - COMT window optimal"')
        print('  python ghost_note.py "She is avoiding the bloodwork followup"')
        print('  python ghost_note.py "Low energy - be compassionate today"')
        sys.exit(1)

    note = " ".join(sys.argv[1:])
    register_ghost_note(note)


if __name__ == "__main__":
    main()
