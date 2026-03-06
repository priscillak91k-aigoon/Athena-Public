#!/usr/bin/env python3
"""
heartbeat.py - Lobotto Sleep-Cycle-Aware Watchdog (v2.0)
========================================================
Monitors system state and detects sleep/wake transitions.
Saves state before Fury sleeps, recovers on wake.
Now includes: 4-hour dreaming cycle (athena_dreaming.py).

Usage:
    python scripts/heartbeat.py          # Run continuous loop
    python scripts/heartbeat.py once     # Single heartbeat check
"""

import sys
import json
import time
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / ".context"
STATE_FILE = CONTEXT_DIR / "heartbeat_state.json"
SESSION_STATE = CONTEXT_DIR / "session_state.json"
DREAMING_SCRIPT = ROOT / "scripts" / "athena_dreaming.py"
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

HEARTBEAT_INTERVAL_SECONDS = 60
SLEEP_THRESHOLD_SECONDS = 300  # 5 min gap = laptop probably slept
DREAM_INTERVAL_SECONDS = 4 * 60 * 60  # 4 hours


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
        "last_dream_time": None,
        "dream_count": 0,
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


def should_dream(state):
    """Check if it's time for a dreaming cycle."""
    last_dream = state.get("last_dream_time")
    if not last_dream:
        return True  # Never dreamed — run immediately

    try:
        last_dt = datetime.fromisoformat(last_dream)
        elapsed = (datetime.now() - last_dt).total_seconds()
        return elapsed >= DREAM_INTERVAL_SECONDS
    except (ValueError, TypeError):
        return True


def run_dreaming_cycle(state):
    """Launch athena_dreaming.py as a subprocess."""
    if not DREAMING_SCRIPT.exists():
        print(f"  [DREAM] Script not found: {DREAMING_SCRIPT}")
        return

    now = datetime.now()
    print(f"  [DREAM] 🌙 Initiating dreaming cycle at {now.strftime('%H:%M:%S')}...")

    try:
        result = subprocess.run(
            [sys.executable, str(DREAMING_SCRIPT)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
        )

        if result.returncode == 0:
            print(f"  [DREAM] ✅ Dreaming cycle complete.")
            if result.stdout.strip():
                # Print last 3 lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-3:]:
                    print(f"  [DREAM]   {line}")
        else:
            print(f"  [DREAM] ⚠️ Dreaming exited with code {result.returncode}")
            if result.stderr.strip():
                for line in result.stderr.strip().split('\n')[-3:]:
                    print(f"  [DREAM]   {line}")

        state["last_dream_time"] = now.isoformat()
        state["dream_count"] = state.get("dream_count", 0) + 1

    except subprocess.TimeoutExpired:
        print(f"  [DREAM] ⏰ Dreaming timed out after 5 minutes.")
        state["last_dream_time"] = now.isoformat()
    except Exception as e:
        print(f"  [DREAM] ❌ Dreaming failed: {e}")


def heartbeat_tick(state=None):
    """Single heartbeat tick."""
    if state is None:
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

    # Check if it's time to dream
    if should_dream(state):
        run_dreaming_cycle(state)

    save_state(state)
    return slept


def run_loop():
    """Continuous heartbeat loop."""
    print("Lobotto Heartbeat Watchdog v2.0 - ONLINE")
    print(f"Checking every {HEARTBEAT_INTERVAL_SECONDS}s")
    print(f"Sleep threshold: {SLEEP_THRESHOLD_SECONDS}s")
    print(f"Dreaming cycle: every {DREAM_INTERVAL_SECONDS // 3600}h")
    print("Press Ctrl+C to stop.\n")

    state = load_state()

    while True:
        try:
            heartbeat_tick(state)
        except Exception as e:
            print(f"Heartbeat error: {e}")

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        heartbeat_tick()
    else:
        run_loop()

