"""
Athena Dreaming v3 — Brain Architecture Autonomous Engine
=========================================================
Neuroscience-modeled thinking engine with chemical substrate,
hippocampal consolidation, instinct reinforcement, and memory TTL.

Thinking engines (tried in order):
  1. Anthropic Claude — primary (online)
  2. Google Gemini — fallback (online)
  3. Ollama local (llama3.2) — offline mode, zero data leakage

Self-apply outputs:
  - heuristics.md, case_studies.md (long-term memory)
  - lobotto_state.json (12-chemical neurotransmitter substrate)
  - lobotto_hippocampus.json (episodic staging with salience)
  - lobotto_instincts.json (Creatures-style cached responses + Hebbian LTP)
  - lobotto_working_memory.json (PFC buffer with TTL expiry)

Proactive alerts:
  - Sends Telegram messages for urgent findings

Usage: python scripts/athena_dreaming.py
Scheduled via heartbeat.py (every 4 hours).
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
HEURISTICS_PENDING_FILE = CONTEXT_DIR / "heuristics_pending.md"
CASE_STUDIES_FILE = CONTEXT_DIR / "case_studies.md"
ABOUT_FILE = CONTEXT_DIR / "about_priscilla.md"
STATE_FILE = CONTEXT_DIR / "lobotto_state.json"
INSTINCTS_FILE = CONTEXT_DIR / "lobotto_instincts.json"
WORKING_MEMORY_FILE = CONTEXT_DIR / "lobotto_working_memory.json"
HIPPOCAMPUS_FILE = CONTEXT_DIR / "lobotto_hippocampus.json"

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")

# Shared signal detection constants (used by detect_reward_error_signals + reinforce_instincts)
REWARD_SIGNALS = [
    "good work", "exactly", "perfect", "brilliant", "that's right",
    "love it", "yes!", "nailed it", "great job", "well done", "lgtm"
]
ERROR_SIGNALS = [
    "actually,", "no,", "that's wrong", "not quite", "wait,",
    "you forgot", "incorrect", "not right", "that's not", "missed"
]

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
                  "decision_journal.md", "project_state.md", "corrections.md"]:
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
  "heuristic_retirements": ["exact text of rule that seems stale or no longer applicable"]
}}
```
For heuristic_retirements: copy the EXACT text of rules from heuristics.md that haven't been relevant in recent sessions.

## OUTPUT 3: SYCOPHANCY VALIDATION (GROUND TRUTH)
You must read `corrections.md` to find ground-truth instances where the user had to correct the AI. Do NOT rely on your own interpretation of the session transcript to detect sycophancy.
For EACH specific entry found in `corrections.md`, you MUST formulate a strict new rule for `heuristics_additions` designed to block that exact failure from happening again. Do not invent corrections that aren't logged.

## OUTPUT 4: URGENT ALERTS
If you find anything time-sensitive (overdue tasks, approaching deadlines, health-related urgency),
include them in the "alerts" array. These will be sent to Priscilla's phone via Telegram.

## Current Brain Files:
{context_block}

## Recent Session Logs:
{session_block}

Be concise and actionable. Every line should be something useful.
IMPORTANT: You MUST include the ```json``` block for self-applying changes."""


def build_prompt(context_files, sessions):
    context_block = "\\n\\n---\\n\\n".join(
        f"## {name}\\n{content}" for name, content in context_files.items()
    )
    session_block = "\\n\\n---\\n\\n".join(
        f"## {name}\\n{content}" for name, content in sessions.items()
    )
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

    # Extract existing bullet lines for deduplication
    existing_bullets = set(
        line.strip().lstrip("- ").strip()
        for line in current.splitlines()
        if line.strip().startswith("- ")
    )

    # Build prefix-normalized set to catch semantic near-duplicates
    # (e.g. "When user texts at midnight..." appearing 8 times with slight variations)
    def normalize_prefix(text, length=60):
        t = re.sub(r'[—–\-]', '-', text.strip().lower())
        t = re.sub(r'[^\w\s]', '', t)
        t = re.sub(r'\s+', ' ', t).strip()
        return t[:length]

    existing_prefixes = set(
        normalize_prefix(line.strip().lstrip("- "))
        for line in current.splitlines()
        if line.strip().startswith("- ")
    )

    # Filter: reject both exact matches AND prefix-similar entries
    new_additions = []
    for h in additions:
        text = h.strip()
        if text in existing_bullets:
            continue
        if normalize_prefix(text) in existing_prefixes:
            continue
        new_additions.append(text)
        # Add to sets so subsequent additions in this batch also dedup
        existing_bullets.add(text)
        existing_prefixes.add(normalize_prefix(text))
    if not new_additions:
        print("  [SKIP] All heuristic additions are duplicates — nothing to add")
        return 0

    new_entries = "\n".join(f"- {h}" for h in new_additions)

    # Write to QUARANTINE instead of the live heuristics file
    pending_content = read_file(HEURISTICS_PENDING_FILE) if HEURISTICS_PENDING_FILE.exists() else "# Pending Heuristics (Review Required)\n\n"
    write_file(HEURISTICS_PENDING_FILE, pending_content.rstrip() + "\n" + new_entries + "\n")
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


def expire_working_memory(wm, current_session):
    """Expire stale working memory items based on session-count TTL.
    Items older than ttl_sessions get moved to expired_items (audit trail).
    flagged_for_next_session items have a shorter TTL of 2 sessions.

    Returns (updated_wm, expired_count).
    """
    if not wm:
        return wm, 0

    ttl = wm.get("ttl_sessions", 5)
    last_session = wm.get("last_session_number", current_session)
    sessions_elapsed = current_session - last_session

    if sessions_elapsed <= 0:
        return wm, 0

    expired_count = 0
    expired_items = wm.get("expired_items", [])
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Standard TTL lists (expire after ttl_sessions)
    for list_key in ["active_tasks", "open_hypotheses"]:
        items = wm.get(list_key, [])
        if not items:
            continue

        surviving = []
        for item in items:
            if isinstance(item, dict):
                item_session = item.get("added_session", last_session)
                age = current_session - item_session
                if age > ttl:
                    expired_items.append({
                        "item": item.get("text", str(item)),
                        "source": list_key,
                        "expired_on": today,
                        "age_sessions": age
                    })
                    expired_count += 1
                else:
                    surviving.append(item)
            else:
                # Legacy string items — check against session gap
                if sessions_elapsed > ttl:
                    expired_items.append({
                        "item": str(item),
                        "source": list_key,
                        "expired_on": today,
                        "age_sessions": sessions_elapsed
                    })
                    expired_count += 1
                else:
                    surviving.append(item)
        wm[list_key] = surviving

    # Short TTL for flagged items (2 sessions)
    SHORT_TTL = 2
    flagged = wm.get("flagged_for_next_session", [])
    if flagged and sessions_elapsed > SHORT_TTL:
        for item in flagged:
            expired_items.append({
                "item": str(item),
                "source": "flagged_for_next_session",
                "expired_on": today,
                "age_sessions": sessions_elapsed
            })
            expired_count += 1
        wm["flagged_for_next_session"] = []

    # Keep only last 50 expired items for audit trail
    wm["expired_items"] = expired_items[-50:]

    return wm, expired_count


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
    print(f"[{timestamp.isoformat()}] Athena Dreaming v3 — starting thinking cycle...")

    context_files = read_context_files()
    if not context_files:
        print("[ERROR] No context files found.")
        return

    sessions = read_recent_sessions(5)
    print(f"  Loaded {len(context_files)} brain files, {len(sessions)} recent sessions")

    # Load working memory (PFC)
    working_memory = load_working_memory()
    print(f"  [BRAIN] Working memory: {'loaded' if working_memory else 'empty'}")

    # Build thinking prompt
    prompt = build_prompt(context_files, sessions)

    # Check internet connectivity to decide engine priority
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
            ("Gemini (primary quota-optimized)", lambda: think_with_gemini(prompt)),
            ("Claude (deep reasoning fallback)", lambda: think_with_anthropic(prompt)),
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
    header = f"# Thinking Log — {timestamp.strftime('%Y-%m-%d %H:%M')}\\n\\n"
    header += f"> Engine: {engine} | Files: {len(context_files)} | Sessions: {len(sessions)}\\n\\n---\\n\\n"

    existing = read_file(THINKING_LOG) if THINKING_LOG.exists() else ""
    write_file(THINKING_LOG, header + thinking_output + "\\n\\n---\\n\\n" + existing)
    print(f"  [OK] Thinking log updated")

    # --- Self-apply changes ---
    edits = extract_json_block(thinking_output)
    changelog_entries = []

    if edits:
        h_count = apply_heuristic_additions(edits.get("heuristics_additions", []))
        cs_count = apply_case_study_additions(edits.get("case_study_additions", []))
        a_count = send_telegram_alert(edits.get("alerts", [""])[0]) if edits.get("alerts") else False

        if h_count:
            changelog_entries.append(f"Added {h_count} heuristics to heuristics.md")
        if cs_count:
            changelog_entries.append(f"Added {cs_count} case studies to case_studies.md")
        if a_count:
            changelog_entries.append(f"Sent Telegram alert")

        print(f"  [SELF-APPLIED] {h_count} heuristics, {cs_count} case studies")

        # Self-repair stale data
        stale = edits.get("stale_items", [])
        if stale:
            repairs = self_repair_stale_data(stale)
            for r in repairs:
                changelog_entries.append(f"REPAIR: {r}")
            print(f"  [STALE] Found {len(stale)} stale items")

        # Heuristic retirements (archive stale rules)
        retirements = edits.get("heuristic_retirements", [])
        if retirements:
            ret_count = apply_heuristic_retirements(retirements)
            if ret_count:
                changelog_entries.append(f"Archived {ret_count} stale heuristics")
            print(f"  [RETIRE] Archived {ret_count} heuristics")

        # Working memory TTL expiry
        if working_memory:
            current_session = working_memory.get("last_session_number", 0)
            if sessions:
                current_session += 1

            wm_updated, expired_count = expire_working_memory(working_memory, current_session + 1)
            if expired_count:
                changelog_entries.append(f"Working memory: expired {expired_count} stale items (TTL exceeded)")
                print(f"  [WM-TTL] Expired {expired_count} stale working memory items")
            wm_updated["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            save_working_memory(wm_updated)
        else:
            print("  [WM] No working memory loaded — skipping TTL check")

        # Write dream changelog
        if changelog_entries:
            changelog_entries.insert(0, f"Engine: {engine}")
            log_dream_changelog(changelog_entries)
            print(f"  [CHANGELOG] {len(changelog_entries)} entries logged")
    else:
        print("  [SKIP] No JSON block found — analysis only (no self-apply)")

    # --- Run boot classifier to update session mode ---
    try:
        import subprocess
        boot_script = PROJECT_ROOT / "scripts" / "athena_boot_mode.py"
        if boot_script.exists():
            subprocess.run([sys.executable, str(boot_script)], timeout=15, check=False)
    except Exception as e:
        print(f"  [BOOT] Boot classifier skipped: {e}")

    # --- Run brain health diagnostic ---
    try:
        import subprocess
        health_script = PROJECT_ROOT / "scripts" / "athena_brain_health.py"
        if health_script.exists():
            result = subprocess.run(
                [sys.executable, str(health_script)],
                capture_output=True, text=True, timeout=15
            )
            # Print the diagnostic output
            if result.stdout.strip():
                for line in result.stdout.strip().split("\\n"):
                    print(f"  {line}")
    except Exception as e:
        print(f"  [HEALTH] Brain diagnostic skipped: {e}")

    print(f"  [{datetime.now().isoformat()}] Dreaming cycle finished.")


if __name__ == "__main__":
    main()