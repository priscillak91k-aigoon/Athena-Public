#!/usr/bin/env python3
"""
Athena Instinct Primer — Closes the Brain Loop
================================================
Reads lobotto_instincts.json, filters to active instincts above strength
threshold, and generates a concise markdown primer that the /start workflow
loads at session boot.

This is the equivalent of Creatures connecting biochemistry to the neural net:
instincts that have been reinforced through Hebbian LTP appear stronger,
instincts that have decayed below threshold are excluded.

Output: .context/active_instincts_primer.md
Run: python scripts/athena_instinct_primer.py
Called by: heartbeat.py (after dreaming cycle) or /start workflow
"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
INSTINCTS_FILE = CONTEXT_DIR / "lobotto_instincts.json"
STATE_FILE = CONTEXT_DIR / "lobotto_state.json"
WORKING_MEMORY_FILE = CONTEXT_DIR / "lobotto_working_memory.json"
BOOT_MODE_FILE = CONTEXT_DIR / "lobotto_boot_mode.json"
PRIMER_OUTPUT = CONTEXT_DIR / "active_instincts_primer.md"

STRENGTH_THRESHOLD = 0.45  # Only show instincts above this strength


def load_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def generate_instinct_primer():
    """Generate concise instinct primer for session boot."""
    data = load_json(INSTINCTS_FILE)
    if not data:
        return "No instinct data available."

    scenarios = data.get("scenarios", [])
    # Filter and sort by strength (strongest first)
    active = [
        s for s in scenarios
        if s.get("strength", 0) >= STRENGTH_THRESHOLD
    ]
    active.sort(key=lambda s: s.get("strength", 0), reverse=True)

    if not active:
        return "No active instincts above threshold."

    lines = ["## Active Instincts (auto-generated)", ""]
    lines.append("> These are cached behavioral patterns ranked by Hebbian reinforcement strength.")
    lines.append("> Stronger instincts have been repeatedly validated through positive outcomes.")
    lines.append("")

    for s in active[:15]:  # Cap at 15 most relevant
        strength = s.get("strength", 0)
        trigger = s.get("trigger", "unknown")
        response = s.get("response_pattern", "no response defined")
        bar = "█" * int(strength * 10) + "░" * (10 - int(strength * 10))
        lines.append(f"- **[{strength:.2f}]** `{bar}` {trigger} → {response}")

    # Add last updated
    meta = data.get("meta", {})
    lines.append("")
    lines.append(f"*Last updated: {meta.get('last_updated', 'unknown')} | "
                 f"Total scenarios: {meta.get('total_scenarios', len(scenarios))} | "
                 f"Active (>{STRENGTH_THRESHOLD}): {len(active)}*")

    return "\n".join(lines)


def generate_brain_briefing():
    """Generate a concise brain state summary for session boot."""
    sections = []

    # Boot mode
    boot = load_json(BOOT_MODE_FILE)
    if boot:
        mode = boot.get("primary_mode", "unknown")
        directive = boot.get("boot_directive", "")
        sections.append(f"**Boot Mode**: {mode}")
        if directive:
            sections.append(f"> {directive}")

    # Chemical state summary (only notable drives)
    state = load_json(STATE_FILE)
    if state:
        chemicals = state.get("chemicals", {})
        elevated = []
        depleted = []
        for name, chem in chemicals.items():
            val = chem.get("value", 0.5)
            if val > 0.70:
                elevated.append(f"{name}={val:.2f}")
            elif val < 0.30:
                depleted.append(f"{name}={val:.2f}")
        if elevated:
            sections.append(f"**Elevated drives**: {', '.join(elevated)}")
        if depleted:
            sections.append(f"**Depleted drives**: {', '.join(depleted)}")
        if not elevated and not depleted:
            sections.append("**Chemical state**: All drives within normal range (0.30-0.70)")

    # Working memory summary
    wm = load_json(WORKING_MEMORY_FILE)
    if wm:
        tasks = len(wm.get("active_tasks", []))
        hypotheses = len(wm.get("open_hypotheses", []))
        flagged = len(wm.get("flagged_for_next_session", []))
        parts = []
        if tasks:
            parts.append(f"{tasks} active task{'s' if tasks > 1 else ''}")
        if hypotheses:
            parts.append(f"{hypotheses} open hypothesis/es")
        if flagged:
            parts.append(f"{flagged} flagged for this session")
        if parts:
            sections.append(f"**Working memory**: {', '.join(parts)}")

            # Show flagged items explicitly
            for item in wm.get("flagged_for_next_session", []):
                sections.append(f"  - ⚡ {item}")
        else:
            sections.append("**Working memory**: Empty — clean slate")

    return "\n".join(sections)


def main():
    # Generate instinct primer
    primer = generate_instinct_primer()

    # Generate brain briefing
    briefing = generate_brain_briefing()

    # Combine into single output file
    output = f"""---
auto_generated: true
generated_at: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
---
# Brain State Primer

{briefing}

---

{primer}
"""

    PRIMER_OUTPUT.write_text(output.strip(), encoding="utf-8")

    # Print summary
    print(f"╔══ Instinct Primer Generated ══╗")
    print(f"║ Output: {PRIMER_OUTPUT.name}")
    active_count = primer.count("- **[")
    print(f"║ Active instincts: {active_count}")
    print(f"║ Brain briefing: {len(briefing.splitlines())} lines")
    print(f"╚{'═' * 32}╝")


if __name__ == "__main__":
    main()
