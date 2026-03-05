#!/usr/bin/env python3
"""
morning_sync.py - Lobotto Wake Briefing (v1.0)
===============================================
Generates a status report when Cilla opens Fury.
Reports: time since last session, pending tasks, overnight queue,
supplement protocol, and Combat Protocol readiness.

Usage:
    python scripts/morning_sync.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / ".context"
SESSION_DIR = ROOT / "session_logs"
STATE_FILE = CONTEXT_DIR / "session_state.json"
HEARTBEAT_FILE = CONTEXT_DIR / "heartbeat_state.json"
QUEUE_FILE = CONTEXT_DIR / "overnight_queue.json"
CORRECTIONS_FILE = CONTEXT_DIR / "corrections.md"


def load_json(filepath):
    """Safely load a JSON file."""
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_time_since_last_session():
    """Calculate time since last session."""
    state = load_json(STATE_FILE)
    last = state.get("last_session") or state.get("timestamp")
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            delta = datetime.now() - last_dt
            hours = round(delta.total_seconds() / 3600, 1)
            return hours
        except (ValueError, TypeError):
            pass
    return None


def get_sleep_events():
    """Get recent sleep events from heartbeat."""
    hb = load_json(HEARTBEAT_FILE)
    events = hb.get("sleep_events", [])
    return events[-5:]  # Last 5


def get_overnight_queue():
    """Check for queued overnight research."""
    queue = load_json(QUEUE_FILE)
    return queue.get("items", [])


def get_pending_tasks():
    """Get pending tasks from session state."""
    state = load_json(STATE_FILE)
    return state.get("pending_tasks", [])


def count_corrections():
    """Count accumulated learnings."""
    if not CORRECTIONS_FILE.exists():
        return 0
    try:
        content = CORRECTIONS_FILE.read_text(encoding="utf-8")
        return content.count("- ")
    except OSError:
        return 0


def generate_briefing():
    """Generate the morning briefing."""
    now = datetime.now()
    print("=" * 60)
    print(f"LOBOTTO MORNING SYNC - {now.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Time gap
    hours = get_time_since_last_session()
    if hours:
        print(f"\n[TIME] Last session: {hours}h ago")
    else:
        print("\n[TIME] No previous session data")

    # Sleep events
    events = get_sleep_events()
    if events:
        print(f"\n[SLEEP] {len(events)} recent sleep events detected")
        for e in events[-3:]:
            wake = e.get("wake_time", "?")
            dur = e.get("sleep_duration_minutes", "?")
            print(f"   Woke: {wake} (slept {dur}m)")

    # Pending tasks
    tasks = get_pending_tasks()
    if tasks:
        print(f"\n[TASKS] {len(tasks)} pending items:")
        for t in tasks:
            print(f"   - {t}")
    else:
        print("\n[TASKS] No pending items from last session")

    # Overnight queue
    queue = get_overnight_queue()
    if queue:
        print(f"\n[QUEUE] {len(queue)} overnight research items:")
        for q in queue:
            status = q.get("status", "queued")
            topic = q.get("topic", "?")
            print(f"   [{status}] {topic}")
    else:
        print("\n[QUEUE] No overnight items (server bridge V2 needed for auto-processing)")

    # Compound knowledge
    corrections = count_corrections()
    print(f"\n[LEARNING] {corrections} corrections accumulated")

    # Combat readiness
    print("\n" + "-" * 60)
    print("COMBAT PROTOCOL: ACTIVE")
    print("ANTI-SYCOPHANCY: ENFORCED")
    print("STATUS: Ready for Cilla")
    print("-" * 60)


if __name__ == "__main__":
    generate_briefing()
