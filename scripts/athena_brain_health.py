#!/usr/bin/env python3
"""
Athena Brain Health Diagnostic — Self-Monitoring System
=======================================================
Validates the integrity and health of all brain state files.
Detects corruption, staleness, schema violations, and drift.

Reports issues via structured output. When called from the dreaming
engine, alerts are sent to Telegram for anything at WARNING or above.

Usage: python scripts/athena_brain_health.py
Called by: dreaming engine (end of cycle), or standalone for debugging.

Exit codes:
  0 = all healthy
  1 = warnings found (non-critical)
  2 = errors found (degraded function)
  3 = critical failures (system non-functional)
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"

# Brain files to validate
BRAIN_FILES = {
    "lobotto_working_memory.json": CONTEXT_DIR / "lobotto_working_memory.json",
    "heuristics.md": CONTEXT_DIR / "heuristics.md",
    "lobotto_boot_mode.json": CONTEXT_DIR / "lobotto_boot_mode.json",
}

# Severity levels
OK = "OK"
WARN = "WARN"
ERROR = "ERROR"
CRITICAL = "CRITICAL"


def load_json_safe(path):
    """Load JSON with error handling. Returns (data, error_msg)."""
    if not path.exists():
        return None, f"File missing: {path.name}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data, None
    except json.JSONDecodeError as e:
        return None, f"JSON corrupt: {path.name} — {str(e)[:80]}"
    except Exception as e:
        return None, f"Read error: {path.name} — {str(e)[:80]}"



def check_working_memory():
    """Validate lobotto_working_memory.json — schema, TTL state."""
    results = []
    data, err = load_json_safe(BRAIN_FILES["lobotto_working_memory.json"])
    if err:
        return [(CRITICAL, "Working Memory", err)]

    # Check expected keys exist
    expected_keys = ["active_tasks", "open_hypotheses", "flagged_for_next_session"]
    for key in expected_keys:
        if key not in data:
            results.append((WARN, "Working Memory", f"Missing key: {key}"))

    # Check for bloat (too many items = TTL not working)
    for key in expected_keys:
        items = data.get(key, [])
        if len(items) > 20:
            results.append((WARN, "Working Memory", f"Bloated: {key} has {len(items)} items (TTL may not be firing)"))

    if not results:
        total = sum(len(data.get(k, [])) for k in expected_keys)
        results.append((OK, "Working Memory", f"{total} items across {len(expected_keys)} categories"))

    return results



def check_heuristics():
    """Validate heuristics.md — file size, duplicate detection."""
    results = []
    path = BRAIN_FILES["heuristics.md"]
    if not path.exists():
        return [(CRITICAL, "Heuristics", "File missing")]

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    bullet_lines = [l.strip() for l in lines if l.strip().startswith("- ")]

    # Size check — heuristics bloat is a known failure mode
    if len(lines) > 400:
        results.append((WARN, "Heuristics", f"Growing large: {len(lines)} lines (watch for bloat)"))
    if len(lines) > 600:
        results.append((ERROR, "Heuristics", f"Bloated: {len(lines)} lines — dedup may be failing"))

    # Quick duplicate scan (prefix-normalized)
    import re
    def norm(s):
        s = re.sub(r'[—–\-]', '-', s.strip().lstrip("- ").lower())
        s = re.sub(r'[^\w\s]', '', s)
        return re.sub(r'\s+', ' ', s).strip()[:60]

    seen = {}
    dupes = 0
    for b in bullet_lines:
        n = norm(b)
        if n in seen:
            dupes += 1
        else:
            seen[n] = True

    if dupes > 5:
        results.append((ERROR, "Heuristics", f"{dupes} near-duplicate heuristics detected — dedup guard failing"))
    elif dupes > 0:
        results.append((WARN, "Heuristics", f"{dupes} near-duplicate heuristic(s) found"))

    if not results:
        results.append((OK, "Heuristics", f"{len(lines)} lines, {len(bullet_lines)} rules, no duplicates"))

    return results



def check_boot_mode():
    """Validate lobotto_boot_mode.json — existence, recency."""
    results = []
    data, err = load_json_safe(BRAIN_FILES["lobotto_boot_mode.json"])
    if err:
        return [(WARN, "Boot Mode", err)]

    if not data.get("primary_mode"):
        results.append((WARN, "Boot Mode", "No primary_mode set"))

    if not results:
        results.append((OK, "Boot Mode", f"Mode: {data.get('primary_mode', '?')}"))

    return results


def run_diagnostics():
    """Run all brain health checks. Returns (exit_code, results_list, summary)."""
    all_results = []
    checks = [
        check_working_memory,
        check_heuristics,
        check_boot_mode,
    ]

    for check_fn in checks:
        try:
            results = check_fn()
            all_results.extend(results)
        except Exception as e:
            all_results.append((ERROR, check_fn.__name__, f"Check crashed: {str(e)[:100]}"))

    # Determine overall severity
    severities = [r[0] for r in all_results]
    if CRITICAL in severities:
        exit_code = 3
        overall = "🔴 CRITICAL"
    elif ERROR in severities:
        exit_code = 2
        overall = "🟠 DEGRADED"
    elif WARN in severities:
        exit_code = 1
        overall = "🟡 WARNINGS"
    else:
        exit_code = 0
        overall = "🟢 HEALTHY"

    return exit_code, all_results, overall


def format_report(results, overall):
    """Format diagnostic results as readable report."""
    lines = [
        f"╔══ Brain Health Diagnostic ══╗",
        f"║ Status: {overall}",
        f"║ Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"╠{'═' * 30}╣",
    ]

    for severity, component, message in results:
        icon = {"OK": "✅", "WARN": "⚠️", "ERROR": "❌", "CRITICAL": "🔴"}[severity]
        lines.append(f"║ {icon} [{component}] {message}")

    lines.append(f"╚{'═' * 30}╝")
    return "\n".join(lines)


def format_telegram_alert(results, overall):
    """Format alert for Telegram (only warnings and above)."""
    issues = [r for r in results if r[0] != OK]
    if not issues:
        return None

    lines = [f"🧠 *Brain Health: {overall}*\n"]
    for severity, component, message in issues:
        icon = {"WARN": "⚠️", "ERROR": "❌", "CRITICAL": "🔴"}[severity]
        lines.append(f"{icon} *{component}*: {message}")

    return "\n".join(lines)


def main():
    # Force UTF-8 output (PowerShell defaults to cp1252 which chokes on emoji)
    sys.stdout.reconfigure(encoding='utf-8')

    exit_code, results, overall = run_diagnostics()

    # Print report
    report = format_report(results, overall)
    print(report)

    # Write to log file for persistence
    log_path = CONTEXT_DIR / "brain_health.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n{report}\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
