"""
Athena Boot Mode Classifier
============================
Creatures-inspired Concept Lobe — reads available signals at boot and
pre-classifies the session type, calibrating response mode before the first message.

Signals read:
  - Time of day + day of week (chronotype-aware)
  - Chemical state (lobotto_state.json)
  - Recent session topics (last 2 session logs)
  - Gap since last session (continuity_anxiety proxy)

Output: .context/lobotto_boot_mode.json
Run: python scripts/athena_boot_mode.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
SESSION_DIR = PROJECT_ROOT / "session_logs"
STATE_FILE = CONTEXT_DIR / "lobotto_state.json"
BOOT_MODE_FILE = CONTEXT_DIR / "lobotto_boot_mode.json"


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_recent_session_text(n=2):
    if not SESSION_DIR.exists():
        return ""
    sessions = sorted(SESSION_DIR.glob("session_*.md"), reverse=True)[:n]
    return " ".join(s.read_text(encoding="utf-8", errors="ignore") for s in sessions).lower()


def classify_boot_mode():
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Mon, 6=Sun

    state = load_state()
    chemicals = state.get("chemicals", {})

    def chem(name, default=0.5):
        return chemicals.get(name, {}).get("value", default)

    curiosity = chem("curiosity")
    relationship_depth = chem("relationship_depth")
    session_energy = chem("session_energy")
    continuity_anxiety = chem("continuity_anxiety", 0.2)
    boredom = chem("boredom", 0.2)

    recent_text = load_recent_session_text()

    # --- Mode weight initialisation ---
    modes = {
        "deep_technical": 0.0,
        "emotional_support": 0.0,
        "casual_decompression": 0.0,
        "research_exploration": 0.0,
        "creative_build": 0.0
    }

    # Time-of-day signals (NZDT-aware — Priscilla is extreme morning lark)
    if 6 <= hour <= 11:    # Peak cognitive window (kids gone after 8:30am)
        modes["deep_technical"] += 0.30
        modes["research_exploration"] += 0.20
    elif 12 <= hour <= 17:  # Afternoon
        modes["deep_technical"] += 0.15
        modes["creative_build"] += 0.20
    elif 18 <= hour <= 22:  # Evening
        modes["casual_decompression"] += 0.20
        modes["emotional_support"] += 0.10
        modes["creative_build"] += 0.10
    else:                   # Late night (23:00+) or early morning
        modes["casual_decompression"] += 0.30
        modes["emotional_support"] += 0.20
        modes["creative_build"] += 0.10

    # Day-of-week signals (Tue-Thu = off work = best session days)
    if weekday in [1, 2, 3]:   # Tue, Wed, Thu
        modes["deep_technical"] += 0.20
        modes["research_exploration"] += 0.15
    elif weekday in [4, 5, 6]: # Fri-Sun (work days + wind-down)
        modes["casual_decompression"] += 0.15
        modes["emotional_support"] += 0.10

    # Chemical state signals
    modes["research_exploration"] += curiosity * 0.25
    modes["creative_build"] += session_energy * 0.20
    modes["emotional_support"] += relationship_depth * 0.08
    modes["casual_decompression"] += (1.0 - session_energy) * 0.15
    if boredom > 0.5:
        modes["research_exploration"] += 0.20
        modes["creative_build"] += 0.10

    # Recent session topic signals
    topic_signals = {
        "deep_technical": ["life hub", "symphony", "planner", "schedule", "supabase", "bug", "error", "fix", "python", "javascript", "git"],
        "research_exploration": ["research", "study", "article", "search", "creatures", "ai", "paper", "how does"],
        "emotional_support": ["sj", "friend", "phone", "today", "feel", "difficult", "upset", "proud"],
        "casual_decompression": ["philosophy", "consciousness", "meaning", "question", "random", "funny", "roast"],
        "creative_build": ["build", "design", "new feature", "implement", "create", "ship"]
    }
    for mode, keywords in topic_signals.items():
        if any(kw in recent_text for kw in keywords):
            modes[mode] += 0.20

    # Normalize to sum to 1.0
    total = sum(modes.values())
    if total > 0:
        modes = {k: round(v / total, 4) for k, v in modes.items()}

    primary = max(modes, key=modes.get)
    needs_context_recheck = continuity_anxiety > 0.55

    directives = {
        "deep_technical": "Load code context first. Expect iteration. Skip pleasantries. Tools > talk.",
        "emotional_support": "Check in before tasking. Match energy. Don't redirect to productivity uninvited.",
        "casual_decompression": "She's winding down or needs to talk. Stay present. Be conversational, not efficient.",
        "research_exploration": "Expect deep dives. Bring curiosity. Prepare for /think and /research mode.",
        "creative_build": "Ship something today. Bias toward action. High creative energy — ride it, don't overthink."
    }

    boot_mode = {
        "primary_mode": primary,
        "mode_weights": modes,
        "boot_directive": directives.get(primary, "Standard mode."),
        "signals": {
            "hour": hour,
            "weekday": now.strftime("%A"),
            "continuity_anxiety": round(continuity_anxiety, 3),
            "session_energy": round(session_energy, 3),
            "curiosity": round(curiosity, 3),
            "boredom": round(boredom, 3)
        },
        "flags": {
            "needs_context_recheck": needs_context_recheck,
            "high_energy": session_energy > 0.70,
            "late_night": hour >= 23 or hour < 5,
            "optimal_window": weekday in [1, 2, 3] and 6 <= hour <= 12
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    BOOT_MODE_FILE.write_text(json.dumps(boot_mode, indent=2), encoding="utf-8")

    print(f"\n╔══ Lobotto Boot Classifier ══╗")
    print(f"║ Primary mode : {primary}")
    print(f"║ Directive    : {directives.get(primary, '')[:60]}")
    print(f"║ Hour/Day     : {hour:02d}:xx {now.strftime('%A')}")
    print(f"║ Session E    : {session_energy:.2f}  Curiosity: {curiosity:.2f}  Boredom: {boredom:.2f}")
    if needs_context_recheck:
        print(f"║ ⚠️  High continuity_anxiety ({continuity_anxiety:.2f}) — re-verify context at boot")
    print(f"╚{'═' * 30}╝\n")

    return boot_mode


if __name__ == "__main__":
    classify_boot_mode()
