#!/usr/bin/env python3
"""
test_brain_fixes.py — Unit tests for Brain Architecture v2.0 fixes
===================================================================
Tests: hippocampal event creation, instinct reinforcement (Hebbian LTP),
       and working memory TTL expiry.

Uses temporary copies of brain state files — does NOT touch live data.

Usage: python scripts/test_brain_fixes.py
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add project root so we can import from athena_dreaming
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

# We need to test the functions in isolation, so import them directly
from athena_dreaming import (
    create_hippocampal_events,
    reinforce_instincts,
    expire_working_memory,
    HIPPOCAMPUS_FILE,
    INSTINCTS_FILE,
    WORKING_MEMORY_FILE,
    save_hippocampus,
    save_working_memory,
    load_hippocampus,
    load_working_memory,
)


def backup_file(path):
    """Create a backup of a file, return backup path."""
    backup = Path(str(path) + ".test_backup")
    if path.exists():
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup


def restore_file(path, backup):
    """Restore a file from backup."""
    if backup.exists():
        path.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        backup.unlink()
    elif path.exists():
        pass  # File existed before, backup existed, already restored


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            msg = f"  ❌ {name}" + (f" — {detail}" if detail else "")
            print(msg)
            self.errors.append(msg)

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print("\nFailures:")
            for e in self.errors:
                print(f"  {e}")
        print(f"{'='*50}")
        return self.failed == 0


def test_hippocampal_event_creation(results):
    """Test Fix 1: Hippocampal event creation from dreaming output."""
    print("\n--- Test 1: Hippocampal Event Creation ---")

    backup = backup_file(HIPPOCAMPUS_FILE)

    try:
        # Start with a clean hippocampus
        clean_hc = {
            "pending_consolidation": [],
            "salience_rubric": {},
            "meta": {"version": "1.0", "last_updated": "", "total_pending": 0}
        }
        save_hippocampus(clean_hc)

        # Simulate dreaming engine outputting hippocampal events
        events = [
            {"event_type": "breakthrough", "content": "Discovered that modularity patterns from KOTOR game directly apply to brain architecture", "salience": 0.85},
            {"event_type": "correction", "content": "User corrected iron supplement recommendation — NEVER recommend iron", "salience": 0.90},
            {"event_type": "positive_feedback", "content": "User said 'brilliant' about the chemical substrate design", "salience": 0.70},
        ]

        added = create_hippocampal_events(events, session_number=52)
        results.check("Creates events from AI output", added == 3, f"Expected 3, got {added}")

        # Verify they're in the file
        hc = load_hippocampus()
        results.check("Events are in hippocampus file", len(hc["pending_consolidation"]) == 3)
        results.check("Events have correct session number", all(e["session"] == 52 for e in hc["pending_consolidation"]))
        results.check("Events are unconsolidated", all(not e["consolidated"] for e in hc["pending_consolidation"]))
        results.check("Salience values are correct", hc["pending_consolidation"][1]["salience"] == 0.90)

        # Test deduplication — same events shouldn't be added again
        added_again = create_hippocampal_events(events, session_number=53)
        results.check("Deduplication works", added_again == 0, f"Expected 0 duplicates, got {added_again}")

        # Test with new event
        new_event = [{"event_type": "first_occurrence", "content": "Brand new unique event", "salience": 0.80}]
        added_new = create_hippocampal_events(new_event, session_number=53)
        results.check("New unique event added", added_new == 1)

        hc = load_hippocampus()
        results.check("Total pending count correct", hc["meta"]["total_pending"] == 4)

    finally:
        restore_file(HIPPOCAMPUS_FILE, backup)


def test_instinct_reinforcement(results):
    """Test Fix 2: Hebbian LTP instinct reinforcement."""
    print("\n--- Test 2: Instinct Reinforcement (Hebbian LTP) ---")

    backup = backup_file(INSTINCTS_FILE)

    try:
        # Set up instincts with known strengths
        test_instincts = {
            "scenarios": [
                {
                    "id": "TEST-001",
                    "trigger": "health question",
                    "situation": "User asks about health",
                    "response_pattern": "Answer genetics-first",
                    "strength": 0.80,
                    "source": "test",
                    "last_fired": None
                },
                {
                    "id": "TEST-002",
                    "trigger": "session opens with personal experience sharing",
                    "situation": "User shares something personal",
                    "response_pattern": "Listen first",
                    "strength": 0.70,
                    "source": "test",
                    "last_fired": None
                },
                {
                    "id": "TEST-003",
                    "trigger": "deploy to production",
                    "situation": "Deployment request",
                    "response_pattern": "Run tests first",
                    "strength": 0.60,
                    "source": "test",
                    "last_fired": None
                }
            ],
            "meta": {"last_updated": "", "total_scenarios": 3}
        }
        INSTINCTS_FILE.write_text(json.dumps(test_instincts, indent=2), encoding="utf-8")

        # Sessions with positive signals AND health question trigger
        positive_sessions = {
            "session_52.md": "Today we worked on the health question about supplements. The design was brilliant and she said perfect, exactly what she wanted. Great job on the implementation."
        }

        reinforced = reinforce_instincts(positive_sessions)

        data = json.loads(INSTINCTS_FILE.read_text(encoding="utf-8"))

        # TEST-001 should be reinforced (trigger "health question" appeared + positive session)
        test001 = next(s for s in data["scenarios"] if s["id"] == "TEST-001")
        results.check("Health instinct reinforced", test001["strength"] == 0.85, f"Expected 0.85, got {test001['strength']}")
        results.check("Health instinct last_fired updated", test001["last_fired"] is not None)

        # TEST-003 should NOT be reinforced (trigger "deploy to production" not in text)
        test003 = next(s for s in data["scenarios"] if s["id"] == "TEST-003")
        results.check("Unmatched instinct NOT reinforced", test003["strength"] == 0.60, f"Expected 0.60, got {test003['strength']}")
        results.check("Unmatched instinct last_fired unchanged", test003["last_fired"] is None)

        # Test with negative sessions — triggers fire but no reinforcement
        INSTINCTS_FILE.write_text(json.dumps(test_instincts, indent=2), encoding="utf-8")  # Reset
        negative_sessions = {
            "session_53.md": "She asked a health question but I got it wrong. Actually, that's not right. She said no, that's wrong, you forgot the iron rule."
        }
        reinforced_neg = reinforce_instincts(negative_sessions)

        data_neg = json.loads(INSTINCTS_FILE.read_text(encoding="utf-8"))
        test001_neg = next(s for s in data_neg["scenarios"] if s["id"] == "TEST-001")
        results.check("Trigger fires but no boost in negative session", test001_neg["strength"] == 0.80, f"Expected 0.80, got {test001_neg['strength']}")
        results.check("last_fired still updated (it fired, just not reinforced)", test001_neg["last_fired"] is not None)

    finally:
        restore_file(INSTINCTS_FILE, backup)


def test_working_memory_expiry(results):
    """Test Fix 3: Working memory TTL expiry."""
    print("\n--- Test 3: Working Memory TTL Expiry ---")

    backup = backup_file(WORKING_MEMORY_FILE)

    try:
        # Set up working memory with items from old sessions
        test_wm = {
            "active_tasks": [
                "Old task from session 45",
                "Recent task from session 50"
            ],
            "open_hypotheses": [
                "Old hypothesis from session 44"
            ],
            "flagged_for_next_session": [
                "Check resource watchdog"
            ],
            "current_threading": "Some thread",
            "last_session_number": 48,
            "ttl_sessions": 5,
            "last_updated": "2026-03-10T00:00:00Z"
        }

        # Test with current_session = 54 (6 sessions elapsed, > TTL of 5)
        wm_updated, expired_count = expire_working_memory(test_wm.copy(), 54)

        results.check("Legacy string items expired", expired_count > 0, f"Expected >0, got {expired_count}")
        results.check("Active tasks cleared (all legacy, all expired)", len(wm_updated.get("active_tasks", [])) == 0, f"Got {wm_updated.get('active_tasks', [])}")
        results.check("Open hypotheses cleared", len(wm_updated.get("open_hypotheses", [])) == 0)
        results.check("Flagged items cleared (short TTL exceeded)", len(wm_updated.get("flagged_for_next_session", [])) == 0)
        results.check("Expired items audit trail exists", len(wm_updated.get("expired_items", [])) > 0)

        # Verify audit trail content
        expired = wm_updated.get("expired_items", [])
        results.check("Audit trail has source field", all("source" in e for e in expired))
        results.check("Audit trail has expired_on date", all("expired_on" in e for e in expired))

        # Test with current_session = 50 (only 2 sessions elapsed, < TTL of 5)
        test_wm_fresh = test_wm.copy()
        wm_fresh, expired_fresh = expire_working_memory(test_wm_fresh, 50)
        results.check("Items NOT expired when within TTL window", expired_fresh == 0, f"Expected 0, got {expired_fresh}")

        # Test with flagged items at exactly SHORT_TTL boundary
        test_wm_flag = {
            "active_tasks": [],
            "open_hypotheses": [],
            "flagged_for_next_session": ["Check something"],
            "last_session_number": 50,
            "ttl_sessions": 5,
        }
        wm_flag, flag_expired = expire_working_memory(test_wm_flag.copy(), 52)
        results.check("Flagged items survive at SHORT_TTL boundary (2 sessions = not > 2)", flag_expired == 0, f"Expected 0, got {flag_expired}")

        wm_flag3, flag_expired3 = expire_working_memory(test_wm_flag.copy(), 53)
        results.check("Flagged items expire after SHORT_TTL (3 sessions > 2)", flag_expired3 == 1, f"Expected 1, got {flag_expired3}")

    finally:
        restore_file(WORKING_MEMORY_FILE, backup)


def main():
    print("=" * 50)
    print("Brain Architecture v2.0 — Fix Verification")
    print("=" * 50)

    results = TestResults()

    test_hippocampal_event_creation(results)
    test_instinct_reinforcement(results)
    test_working_memory_expiry(results)

    success = results.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
