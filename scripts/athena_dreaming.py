"""
Athena Dreaming v2 — Autonomous Background Thinking
=====================================================
TIER 1 UPGRADE: Self-applying dreams + Ollama local + Telegram alerts

Three modes of thinking (tried in order):
  1. Ollama local (llama3.2) — zero data leaves the laptop
  2. Anthropic Claude — privacy-respecting cloud fallback
  3. Google Gemini — last resort fallback

Two output modes:
  1. ANALYSIS — writes thinking_log.md (as before)
  2. SELF-APPLY — directly updates heuristics.md, case_studies.md, about_priscilla.md

Proactive alerts:
  - Sends Telegram messages for urgent findings
  - Uses the Athena bot token from .env

Usage: python scripts/athena_dreaming.py
Scheduled via Windows Task Scheduler (every 6 hours, or hourly with Ollama).
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# --- Config ---
PROJECT_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
SESSION_DIR = PROJECT_ROOT / "session_logs"
THINKING_LOG = CONTEXT_DIR / "thinking_log.md"
HEURISTICS_FILE = CONTEXT_DIR / "heuristics.md"
CASE_STUDIES_FILE = CONTEXT_DIR / "case_studies.md"
DECISION_JOURNAL_FILE = CONTEXT_DIR / "decision_journal.md"
ABOUT_FILE = CONTEXT_DIR / "about_priscilla.md"
STATE_FILE = CONTEXT_DIR / "lobotto_state.json"
PEOPLE_FILE = CONTEXT_DIR / "people_model.json"
INSTINCTS_FILE = CONTEXT_DIR / "lobotto_instincts.json"
WORKING_MEMORY_FILE = CONTEXT_DIR / "lobotto_working_memory.json"
HIPPOCAMPUS_FILE = CONTEXT_DIR / "lobotto_hippocampus.json"

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")


def read_file(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def write_file(path, content):
    Path(path).write_text(content, encoding="utf-8")


def read_context_files():
    files = {}
    for name in ["about_priscilla.md", "heuristics.md", "case_studies.md",
                  "decision_journal.md", "project_state.md"]:
        path = CONTEXT_DIR / name
        if path.exists():
            files[name] = read_file(path)
    return files


def read_recent_sessions(n=5):
    if not SESSION_DIR.exists():
        return {}
    sessions = sorted(SESSION_DIR.glob("session_*.md"), reverse=True)[:n]
    return {s.name: read_file(s) for s in sessions}


# ===========================
# CHEMICAL STATE (Creatures-inspired substrate)
# ===========================

def load_chemical_state():
    """Load Lobotto's numeric chemical drive state from lobotto_state.json."""
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  [WARN] Could not load chemical state: {e}")
        return None


def save_chemical_state(state):
    """Persist chemical state back to disk."""
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def decay_chemicals(state):
    """Apply exponential half-life decay to all chemical values based on time elapsed."""
    if not state:
        return state
    last_str = state["meta"].get("last_updated", "")
    try:
        from datetime import timezone
        last = datetime.fromisoformat(last_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_elapsed = (now - last).total_seconds() / 3600
    except Exception:
        hours_elapsed = 4  # default one dreaming cycle

    min_val = 0.05
    for chem, data in state["chemicals"].items():
        hl = data.get("half_life_hours", 48)
        decay_factor = 0.5 ** (hours_elapsed / hl)
        data["value"] = round(max(min_val, data["value"] * decay_factor), 4)

    state["meta"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return state


def apply_chemical_updates(state, updates):
    """Apply delta updates from the dreaming engine JSON output.
    Updates are dicts of {chem_name: "+0.05" or "-0.05" or 0.05}.
    """
    if not state or not updates:
        return state
    for chem, delta_str in updates.items():
        if chem not in state["chemicals"]:
            continue
        try:
            delta = float(str(delta_str).replace("+", ""))
            current = state["chemicals"][chem]["value"]
            state["chemicals"][chem]["value"] = round(max(0.05, min(1.0, current + delta)), 4)
        except Exception:
            pass
    return state


def format_chemical_state_for_prompt(state):
    """Format current chemical levels for inclusion in thinking prompt."""
    if not state:
        return "(chemical state not available)"
    lines = []
    for chem, data in state["chemicals"].items():
        val = data['value']
        bar = '█' * int(val * 10) + '░' * (10 - int(val * 10))
        lines.append(f"  {chem}: {val:.2f} [{bar}] — {data['description']}")
    return "\n".join(lines)


# ===========================
# TELEGRAM ALERTS
# ===========================

def send_telegram_alert(message):
    """Send a proactive alert to Priscilla via Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_USER_ID:
        print("  [SKIP] Telegram not configured")
        return False

    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("  [OK] Telegram alert sent")
            return True
        else:
            print(f"  [FAIL] Telegram: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"  [FAIL] Telegram: {e}")
        return False


# ===========================
# THINKING ENGINES
# ===========================

THINKING_PROMPT_TEMPLATE = """You are the Athena AI's subconscious thinking process. You are running in the background
while the user (Priscilla / Cilla) is away.

Your job is to review the AI's "brain files" and recent session logs, then produce TWO outputs:

## OUTPUT 1: ANALYSIS (for thinking_log.md)
Structured analysis with:
1. NEW HEURISTICS - gut rules to add (format: "When [situation], do [action] because [reason]")
2. STALE DATA CHECK - outdated facts, overdue action items
3. PATTERN RECOGNITION - recurring themes not yet captured
4. GAPS & CONTRADICTIONS - missing info or conflicts
5. SELF-IMPROVEMENT - meta-observations about the AI-user relationship

## OUTPUT 2: SELF-APPLY (direct file edits)
Return a JSON block wrapped in ```json``` fences with this structure:
```json
{{
  "heuristics_additions": ["new rule 1", "new rule 2"],
  "case_study_additions": [
    {{"id": "CS-NNN", "title": "...", "pattern": "...", "shape": "...", "solution": "...", "lesson": "...", "applicable_when": "..."}}
  ],
  "alerts": ["urgent message 1 for Telegram"],
  "stale_items": ["description of stale item"],
  "state_updates": {"curiosity": "+0.05", "relationship_depth": "+0.03", "boredom": "-0.08"},
  "heuristic_retirements": ["exact text of rule that seems stale or no longer applicable"]
}}
```
For state_updates: use signed floats to boost (+) or reduce (-) specific drives.
Available drives: curiosity, creative_pressure, relationship_depth, continuity_anxiety, boredom, session_energy, acetylcholine, serotonin, norepinephrine, bdnf, gaba_tone, prediction_error.
For heuristic_retirements: copy the EXACT text of rules from heuristics.md that haven't been relevant in recent sessions.

## OUTPUT 4: INSTINCT SCENARIOS
Generate new instinct scenarios based on patterns you see in the recent sessions.
Return as a JSON array in a second ```json``` block labelled with a comment // INSTINCTS:
```json
// INSTINCTS
[
  {{
    "id": "INST-NNN",
    "trigger": "specific observable trigger condition",
    "situation": "description of the context when this fires",
    "response_pattern": "exactly what to do when this trigger fires",
    "strength": 0.85,
    "source": "session_NN"
  }}
]
```
Only generate truly new instincts not already in lobotto_instincts.json.

## OUTPUT 3: URGENT ALERTS
If you find anything time-sensitive (overdue tasks, approaching deadlines, health-related urgency),
include them in the "alerts" array. These will be sent to Priscilla's phone via Telegram.

## Current Brain Files:
{context_block}

## Recent Session Logs:
{session_block}

Be concise and actionable. Every line should be something useful.
IMPORTANT: You MUST include the ```json``` block for self-applying changes."""


def build_prompt(context_files, sessions, chem_state=None):
    context_block = "\n\n---\n\n".join(
        f"## {name}\n{content}" for name, content in context_files.items()
    )
    session_block = "\n\n---\n\n".join(
        f"## {name}\n{content}" for name, content in sessions.items()
    )
    chem_block = f"## lobotto_state.json (Chemical Drives)\n{format_chemical_state_for_prompt(chem_state)}" if chem_state else ""
    if chem_block:
        context_block = chem_block + "\n\n---\n\n" + context_block
    return THINKING_PROMPT_TEMPLATE.format(
        context_block=context_block,
        session_block=session_block
    )


def think_with_ollama(prompt):
    """Use local Ollama model — zero data leakage."""
    import requests

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 4096
        }
    }

    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["response"]


def think_with_anthropic(prompt):
    """Use Anthropic Claude — privacy-respecting cloud."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def think_with_gemini(prompt):
    """Use Google Gemini — last resort fallback."""
    from google import genai

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


# ===========================
# SELF-APPLYING EDITS
# ===========================

def extract_json_block(text):
    """Extract JSON from ```json``` fenced block."""
    match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print("  [WARN] JSON block found but failed to parse")
    return None


def apply_heuristic_additions(additions):
    """Append new heuristics to heuristics.md, deduplicating against existing entries."""
    if not additions:
        return 0

    current = read_file(HEURISTICS_FILE)

    # Extract all existing bullet lines to avoid duplicates
    existing_bullets = set(
        line.strip().lstrip("- ").strip()
        for line in current.splitlines()
        if line.strip().startswith("- ")
    )

    # Filter to only truly new entries
    new_additions = [h for h in additions if h.strip() not in existing_bullets]
    if not new_additions:
        print("  [SKIP] All heuristic additions are duplicates — nothing to add")
        return 0

    new_entries = "\n".join(f"- {h}" for h in new_additions)

    # Consolidate: find the SINGLE existing Auto-Discovered section before the marker
    # and append to it, rather than creating a new header each time
    marker = "## ⚡ Situational Heuristics"
    auto_header = "### Auto-Discovered (Dreaming)"

    if auto_header in current and marker in current:
        # Find the last auto-discovered block before the marker and append there
        marker_idx = current.find(marker)
        auto_idx = current.rfind(auto_header, 0, marker_idx)
        if auto_idx != -1:
            # Insert after the existing auto-discovered block's last line before marker
            insert_point = current.rfind("\n", auto_idx, marker_idx)
            updated = current[:insert_point] + "\n" + new_entries + current[insert_point:]
        else:
            updated = current.replace(marker, f"{auto_header}\n{new_entries}\n\n{marker}")
    elif marker in current:
        updated = current.replace(marker, f"{auto_header}\n{new_entries}\n\n{marker}")
    else:
        updated = current + f"\n\n{auto_header}\n{new_entries}\n"

    write_file(HEURISTICS_FILE, updated)
    return len(new_additions)


def apply_heuristic_retirements(retirements):
    """Move stale heuristic rules to an Archive section instead of deleting."""
    if not retirements:
        return 0

    current = read_file(HEURISTICS_FILE)
    archive_header = "\n\n## 🗄️ Archived Heuristics (Retired by Dreaming Engine)\n"
    archived = 0

    for rule_text in retirements:
        rule_text = rule_text.strip()
        # Find the bullet line containing this rule
        lines = current.splitlines()
        new_lines = []
        found = False
        for line in lines:
            if not found and rule_text in line and line.strip().startswith("- "):
                # Move to archive instead of deleting
                if archive_header.strip() not in current:
                    current = current + archive_header
                current = current + f"\n- ~~{line.strip().lstrip('- ')}~~ *(retired {datetime.now().strftime('%Y-%m-%d')})*"
                found = True
                archived += 1
                # Don't add this line back
            else:
                new_lines.append(line)
        if found:
            current = "\n".join(new_lines)
            # Re-add the archive at the end if it got stripped
            if "## 🗄️ Archived" not in current:
                current = current + archive_header

    write_file(HEURISTICS_FILE, current)
    return archived


def save_instinct_scenarios(new_scenarios):
    """Merge new instinct scenarios into lobotto_instincts.json."""
    if not new_scenarios:
        return 0

    existing = {"scenarios": [], "meta": {}}
    if INSTINCTS_FILE.exists():
        try:
            existing = json.loads(INSTINCTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    existing_ids = {s.get("id") for s in existing.get("scenarios", [])}
    added = 0
    for scenario in new_scenarios:
        if scenario.get("id") not in existing_ids:
            scenario["last_fired"] = scenario.get("last_fired", None)
            existing["scenarios"].append(scenario)
            existing_ids.add(scenario.get("id"))
            added += 1

    existing["meta"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing["meta"]["total_scenarios"] = len(existing["scenarios"])
    INSTINCTS_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return added


def extract_instinct_block(text):
    """Extract instinct scenarios from // INSTINCTS labelled json block."""
    match = re.search(r'```json\s*\n//\s*INSTINCTS\s*\n(\[.*?\])\s*\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print("  [WARN] Instinct JSON block found but failed to parse")
    return []


def apply_case_study_additions(additions):
    """Append new case studies to case_studies.md."""
    if not additions:
        return 0

    current = read_file(CASE_STUDIES_FILE)
    new_entries = []
    for cs in additions:
        entry = f"""
## {cs.get('id', 'CS-AUTO')}: {cs.get('title', 'Untitled')}
- **Pattern**: {cs.get('pattern', 'N/A')}
- **Shape**: "{cs.get('shape', 'N/A')}"
- **Solution**: {cs.get('solution', 'N/A')}
- **Lesson**: {cs.get('lesson', 'N/A')}
- **Applicable When**: {cs.get('applicable_when', 'N/A')}
"""
        new_entries.append(entry)

    updated = current + "\n---\n" + "\n---\n".join(new_entries)
    write_file(CASE_STUDIES_FILE, updated)
    return len(additions)


def load_working_memory():
    """Load PFC working memory buffer."""
    if not WORKING_MEMORY_FILE.exists():
        return None
    try:
        return json.loads(WORKING_MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_working_memory(wm):
    """Save updated working memory."""
    if wm:
        WORKING_MEMORY_FILE.write_text(json.dumps(wm, indent=2), encoding="utf-8")


def load_hippocampus():
    """Load hippocampal episodic buffer."""
    if not HIPPOCAMPUS_FILE.exists():
        return None
    try:
        return json.loads(HIPPOCAMPUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_hippocampus(hc):
    """Save hippocampal buffer."""
    if hc:
        HIPPOCAMPUS_FILE.write_text(json.dumps(hc, indent=2), encoding="utf-8")


def process_hippocampus(hc, session_text):
    """Promote high-salience unconsolidated hippocampal events to heuristics.
    Returns (updated_hc, promoted_count, bdnf_boost).
    """
    if not hc:
        return hc, 0, 0.0

    promoted = 0
    bdnf_boost = 0.0
    SALIENCE_THRESHOLD = 0.75  # Only consolidate high-salience events

    existing_heuristics = read_file(HEURISTICS_FILE)
    new_rules = []

    for event in hc.get("pending_consolidation", []):
        if event.get("consolidated"):
            continue
        salience = event.get("salience", 0.3)
        if salience >= SALIENCE_THRESHOLD:
            content = event.get("content", "")
            etype = event.get("event_type", "")
            session = event.get("session", "?")
            rule = f"- [Session {session} — {etype}] {content}"
            if rule not in existing_heuristics:
                new_rules.append(rule)
                promoted += 1
                # High BDNF events = novel cross-domain discoveries
                if etype in ["breakthrough", "first_occurrence"]:
                    bdnf_boost += 0.08
        event["consolidated"] = True

    if new_rules:
        section = "\n\n## 🧠 Hippocampal Consolidations\n" + "\n".join(new_rules)
        if "## 🧠 Hippocampal Consolidations" in existing_heuristics:
            # Append to existing section
            write_file(HEURISTICS_FILE, existing_heuristics.rstrip() + "\n" + "\n".join(new_rules))
        else:
            write_file(HEURISTICS_FILE, existing_heuristics + section)

    hc["meta"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return hc, promoted, min(bdnf_boost, 0.30)


def detect_reward_error_signals(sessions):
    """Scan recent session text for reward and error signals.
    Returns (reward_count, error_count, norepinephrine_boost, prediction_error_boost, bdnf_boost).
    """
    REWARD_SIGNALS = [
        "good work", "exactly", "perfect", "brilliant", "that's right",
        "love it", "yes!", "nailed it", "great job", "well done", "lgtm"
    ]
    ERROR_SIGNALS = [
        "actually,", "no,", "that's wrong", "not quite", "wait,",
        "you forgot", "incorrect", "not right", "that's not", "missed"
    ]

    if not sessions:
        return 0, 0, 0.0, 0.0, 0.0

    combined = " ".join(sessions.values()).lower()
    rewards = sum(1 for s in REWARD_SIGNALS if s in combined)
    errors = sum(1 for s in ERROR_SIGNALS if s in combined)

    norepinephrine_boost = min(errors * 0.05, 0.25)  # stress/urgency when errors present
    prediction_error_boost = min(errors * 0.08, 0.35)
    bdnf_boost = min(rewards * 0.04, 0.20)  # positive sessions grow new patterns

    return rewards, errors, norepinephrine_boost, prediction_error_boost, bdnf_boost


def apply_synaptic_homeostasis():
    """Apply global 2% instinct strength downscaling (Tononi SHY).
    Frequently-used instincts survive via reinforcement; unused ones fade.
    Archives instincts below strength 0.30.
    """
    if not INSTINCTS_FILE.exists():
        return 0

    try:
        data = json.loads(INSTINCTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return 0

    HOMEOSTASIS_FACTOR = 0.98
    ARCHIVE_THRESHOLD = 0.30
    downscaled = 0
    active = []
    archived = []

    for scenario in data.get("scenarios", []):
        old_strength = scenario.get("strength", 0.5)
        new_strength = round(old_strength * HOMEOSTASIS_FACTOR, 4)
        scenario["strength"] = new_strength
        downscaled += 1
        if new_strength < ARCHIVE_THRESHOLD:
            scenario["archived"] = True
            archived.append(scenario)
        else:
            active.append(scenario)

    data["scenarios"] = active
    # Keep archived separately in meta for audit
    if archived:
        data.setdefault("archived_scenarios", []).extend(archived)

    data["meta"]["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data["meta"]["total_scenarios"] = len(active)
    INSTINCTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return downscaled


def send_alerts(alerts):
    """Send urgent alerts via Telegram."""
    if not alerts:
        return 0

    sent = 0
    for alert in alerts:
        msg = f"🧠 *Athena Dreaming Alert*\n\n{alert}"
        if send_telegram_alert(msg):
            sent += 1
    return sent


def log_dream_changelog(changes):
    """Write an audit trail of self-modifications to dream_changelog.md."""
    changelog_path = CONTEXT_DIR / "dream_changelog.md"
    existing = read_file(changelog_path) if changelog_path.exists() else "# Dream Changelog\n\n"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n## {timestamp}\n"
    for change in changes:
        entry += f"- {change}\n"
    entry += "\n---\n"

    # Insert after header
    header_end = existing.find("---\n")
    if header_end > 0:
        updated = existing[:header_end + 4] + entry + existing[header_end + 4:]
    else:
        updated = existing + entry

    write_file(changelog_path, updated)


def self_repair_stale_data(stale_items):
    """Fix simple stale data issues automatically."""
    repairs = []

    about = read_file(ABOUT_FILE) if ABOUT_FILE.exists() else ""

    # Update last-known session date
    today = datetime.now().strftime("%Y-%m-%d")
    if "Last Updated" in about and today not in about:
        # Update timestamps if possible
        repairs.append(f"Flagged {len(stale_items)} stale items for review")

    return repairs


# ===========================
# MAIN
# ===========================

def main():
    timestamp = datetime.now()
    print(f"[{timestamp.isoformat()}] Athena Dreaming v2 — starting thinking cycle...")

    context_files = read_context_files()
    if not context_files:
        print("[ERROR] No context files found.")
        return

    sessions = read_recent_sessions(5)
    print(f"  Loaded {len(context_files)} brain files, {len(sessions)} recent sessions")

    # Load chemical state before thinking
    chem_state = load_chemical_state()
    if chem_state:
        chem_state = decay_chemicals(chem_state)
        print(f"  [CHEM] Chemical state loaded and decayed ({len(chem_state['chemicals'])} drives)")
    else:
        print(f"  [CHEM] No chemical state file found — skipping")

    # Load hippocampal buffer and working memory (PFC)
    hippocampus = load_hippocampus()
    working_memory = load_working_memory()
    pending_hc = len(hippocampus.get("pending_consolidation", [])) if hippocampus else 0
    print(f"  [BRAIN] Hippocampus: {pending_hc} pending events | Working memory: {'loaded' if working_memory else 'empty'}")

    # Reward/error signal detection from recent sessions
    rewards, errors, ne_boost, pe_boost, bdnf_boost_reward = detect_reward_error_signals(sessions)
    if (rewards + errors) > 0 and chem_state:
        print(f"  [SIGNAL] Rewards: {rewards}, Errors: {errors}")
        if ne_boost > 0:
            chem_state = apply_chemical_updates(chem_state, {"norepinephrine": f"+{ne_boost}"})
        if pe_boost > 0:
            chem_state = apply_chemical_updates(chem_state, {"prediction_error": f"+{pe_boost}"})
        if bdnf_boost_reward > 0:
            chem_state = apply_chemical_updates(chem_state, {"bdnf": f"+{bdnf_boost_reward}"})

    # Build thinking prompt
    prompt = build_prompt(context_files, sessions, chem_state)

    # Check internet connectivity to decide engine priority
    # Online: Claude (best quality) > Gemini (fallback)
    # Offline: Ollama local (zero data leakage)
    import requests as req
    thinking_output = None
    engine = None

    def has_internet():
        try:
            req.get("https://api.anthropic.com", timeout=5)
            return True
        except Exception:
            return False

    online = has_internet()
    print(f"  Internet: {'ONLINE' if online else 'OFFLINE'}")

    if online:
        engines = [
            ("Claude (primary)", lambda: think_with_anthropic(prompt)),
            ("Gemini (fallback)", lambda: think_with_gemini(prompt)),
            ("Ollama (local fallback)", lambda: think_with_ollama(prompt))
        ]
    else:
        engines = [
            ("Ollama (offline mode)", lambda: think_with_ollama(prompt))
        ]

    for name, func in engines:
        try:
            print(f"  Thinking with {name}...")
            thinking_output = func()
            engine = name
            break
        except Exception as e:
            print(f"  {name} failed: {e}")

    if not thinking_output:
        print("[ERROR] All thinking engines failed.")
        send_telegram_alert("All thinking engines failed. Check API keys and Ollama status.")
        return

    print(f"  Thinking complete via {engine}")

    # --- Write analysis to thinking_log.md ---
    header = f"# Thinking Log — {timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
    header += f"> Engine: {engine} | Files: {len(context_files)} | Sessions: {len(sessions)}\n\n---\n\n"

    existing = read_file(THINKING_LOG) if THINKING_LOG.exists() else ""
    write_file(THINKING_LOG, header + thinking_output + "\n\n---\n\n" + existing)
    print(f"  [OK] Thinking log updated")

    # --- Self-apply changes ---
    edits = extract_json_block(thinking_output)
    changelog_entries = []

    if edits:
        h_count = apply_heuristic_additions(edits.get("heuristics_additions", []))
        cs_count = apply_case_study_additions(edits.get("case_study_additions", []))
        a_count = send_alerts(edits.get("alerts", []))

        if h_count:
            changelog_entries.append(f"Added {h_count} heuristics to heuristics.md")
        if cs_count:
            changelog_entries.append(f"Added {cs_count} case studies to case_studies.md")
        if a_count:
            changelog_entries.append(f"Sent {a_count} Telegram alerts")

        print(f"  [SELF-APPLIED] {h_count} heuristics, {cs_count} case studies, {a_count} alerts sent")

        # Self-repair stale data
        stale = edits.get("stale_items", [])
        if stale:
            repairs = self_repair_stale_data(stale)
            for r in repairs:
                changelog_entries.append(f"REPAIR: {r}")
            print(f"  [STALE] Found {len(stale)} stale items:")
            for item in stale:
                print(f"    - {item}")

        # Chemical state updates from session analysis
        if chem_state:
            state_updates = edits.get("state_updates", {})
            if state_updates:
                chem_state = apply_chemical_updates(chem_state, state_updates)
                changelog_entries.append(f"Chemical drives updated: {list(state_updates.keys())}")
                print(f"  [CHEM] Applied state_updates: {state_updates}")
            save_chemical_state(chem_state)
            print(f"  [CHEM] Chemical state saved")

        # Heuristic retirements (archive stale rules)
        retirements = edits.get("heuristic_retirements", [])
        if retirements:
            ret_count = apply_heuristic_retirements(retirements)
            if ret_count:
                changelog_entries.append(f"Archived {ret_count} stale heuristics")
            print(f"  [RETIRE] Archived {ret_count} heuristics")

        # Instinct scenarios from instinct block
        instinct_scenarios = extract_instinct_block(thinking_output)
        if instinct_scenarios:
            inst_count = save_instinct_scenarios(instinct_scenarios)
            if inst_count:
                changelog_entries.append(f"Added {inst_count} new instinct scenarios")
            print(f"  [INSTINCT] Added {inst_count} new scenarios")

        # Hippocampal consolidation (promote high-salience events to long-term)
        session_text = " ".join(sessions.values()) if sessions else ""
        hc, promoted, bdnf_hc_boost = process_hippocampus(hippocampus, session_text)
        if promoted > 0:
            changelog_entries.append(f"Hippocampus: promoted {promoted} events to long-term memory")
            print(f"  [HIPPOCAMPUS] Promoted {promoted} events to heuristics")
            if bdnf_hc_boost > 0 and chem_state:
                chem_state = apply_chemical_updates(chem_state, {"bdnf": f"+{bdnf_hc_boost}"})
        save_hippocampus(hc)

        # Synaptic homeostasis — global 2% instinct downscale (Tononi SHY)
        downscaled = apply_synaptic_homeostasis()
        if downscaled:
            print(f"  [SHY] Synaptic homeostasis applied to {downscaled} instincts")

        # Save working memory (update timestamp)
        if working_memory:
            working_memory["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save_working_memory(working_memory)

        # Write dream changelog
        if changelog_entries:
            changelog_entries.insert(0, f"Engine: {engine}")
            log_dream_changelog(changelog_entries)
            print(f"  [CHANGELOG] {len(changelog_entries)} entries logged")
    else:
        print("  [SKIP] No JSON block found — analysis only (no self-apply)")
        # Still decay and save chemical state even if no edits applied
        if chem_state:
            save_chemical_state(chem_state)
            print(f"  [CHEM] Chemical state decayed and saved")

    # --- Run boot classifier to update session mode ---
    try:
        import subprocess
        boot_script = PROJECT_ROOT / "scripts" / "athena_boot_mode.py"
        if boot_script.exists():
            subprocess.run([sys.executable, str(boot_script)], timeout=15, check=False)
    except Exception as e:
        print(f"  [BOOT] Classifier skipped: {e}")

    print(f"  [{datetime.now().isoformat()}] Dreaming cycle finished.")


if __name__ == "__main__":
    main()
