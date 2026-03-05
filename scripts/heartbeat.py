#!/usr/bin/env python3
"""
heartbeat.py - Lobotto Sleep-Cycle-Aware Watchdog (v1.0)
========================================================
Monitors system state and detects sleep/wake transitions.
Saves state before Fury sleeps, recovers on wake.

Usage:
    python scripts/heartbeat.py          # Run continuous loop
    python scripts/heartbeat.py once     # Single heartbeat check
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / ".context"
STATE_FILE = CONTEXT_DIR / "heartbeat_state.json"
SESSION_STATE = CONTEXT_DIR / "session_state.json"
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

HEARTBEAT_INTERVAL_SECONDS = 60
SLEEP_THRESHOLD_SECONDS = 300  # 5 min gap = laptop probably slept


def load_state():
    """Load heartbeat state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "last_beat": None,
        "boot_count": 0,
        "sleep_events": [],
        "total_uptime_seconds": 0,
    }


def save_state(state):
    """Persist heartbeat state."""
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def detect_sleep_event(state):
    """Check if we just woke up from a sleep event."""
    last_beat = state.get("last_beat")
    if not last_beat:
        return False, 0

    try:
        last_dt = datetime.fromisoformat(last_beat)
        gap = (datetime.now() - last_dt).total_seconds()

        if gap > SLEEP_THRESHOLD_SECONDS:
            return True, gap
    except (ValueError, TypeError):
        pass

    return False, 0


def save_pre_sleep_state():
    """Save critical state before detected sleep."""
    session_state = {
        "pre_sleep_save": True,
        "timestamp": datetime.now().isoformat(),
        "reason": "Heartbeat detected imminent or recent sleep event",
    }

    if SESSION_STATE.exists():
        try:
            existing = json.loads(SESSION_STATE.read_text(encoding="utf-8"))
            existing.update(session_state)
            session_state = existing
        except (json.JSONDecodeError, OSError):
            pass

    SESSION_STATE.write_text(json.dumps(session_state, indent=2), encoding="utf-8")


def heartbeat_tick():
    """Single heartbeat tick."""
    state = load_state()
    now = datetime.now()

    # Detect sleep event
    slept, gap_seconds = detect_sleep_event(state)

    if slept:
        gap_minutes = int(gap_seconds / 60)
        gap_hours = round(gap_seconds / 3600, 1)

        event = {
            "wake_time": now.isoformat(),
            "sleep_duration_minutes": gap_minutes,
        }
        state.setdefault("sleep_events", []).append(event)

        # Keep last 50 events
        state["sleep_events"] = state["sleep_events"][-50:]

        print(f"[{now.strftime('%H:%M:%S')}] WAKE DETECTED - Fury slept for {gap_hours}h ({gap_minutes}m)")
        print(f"  Total sleep events recorded: {len(state['sleep_events'])}")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] Heartbeat OK")

    # Update state
    state["last_beat"] = now.isoformat()
    state["boot_count"] = state.get("boot_count", 0) + (1 if slept else 0)

    save_state(state)
    return slept


def run_loop():
    """Continuous heartbeat loop."""
    print("Lobotto Heartbeat Watchdog - ONLINE")
    print(f"Checking every {HEARTBEAT_INTERVAL_SECONDS}s")
    print(f"Sleep threshold: {SLEEP_THRESHOLD_SECONDS}s")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            heartbeat_tick()
        except Exception as e:
            print(f"Heartbeat error: {e}")

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        heartbeat_tick()
    else:
        run_loop()
