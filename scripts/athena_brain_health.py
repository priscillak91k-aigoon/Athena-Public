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
    "lobotto_state.json": CONTEXT_DIR / "lobotto_state.json",
    "lobotto_instincts.json": CONTEXT_DIR / "lobotto_instincts.json",
    "lobotto_working_memory.json": CONTEXT_DIR / "lobotto_working_memory.json",
    "lobotto_hippocampus.json": CONTEXT_DIR / "lobotto_hippocampus.json",
    "heuristics.md": CONTEXT_DIR / "heuristics.md",
    "active_instincts_primer.md": CONTEXT_DIR / "active_instincts_primer.md",
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


def check_chemical_state():
    """Validate lobotto_state.json — chemical values, bounds, staleness."""
    results = []
    data, err = load_json_safe(BRAIN_FILES["lobotto_state.json"])
    if err:
        return [(CRITICAL, "Chemical State", err)]

    chemicals = data.get("chemicals", {})
    if not chemicals:
        return [(ERROR, "Chemical State", "No chemicals dict found")]

    # Check each chemical is within valid bounds [0.0, 1.0]
    out_of_bounds = []
    for name, chem in chemicals.items():
        val = chem.get("value")
        if val is None:
            results.append((WARN, "Chemical State", f"Chemical '{name}' has no value field"))
        elif not (0.0 <= val <= 1.0):
            out_of_bounds.append(f"{name}={val}")

    if out_of_bounds:
        results.append((ERROR, "Chemical State", f"Out of bounds: {', '.join(out_of_bounds)}"))

    # Check expected chemical count (should be 12)
    if len(chemicals) < 10:
        results.append((WARN, "Chemical State", f"Only {len(chemicals)} chemicals (expected 12)"))

    # Check staleness — last_updated should be within 24h
    meta = data.get("meta", {})
    last_updated = meta.get("last_updated") or meta.get("last_dreaming_cycle")
    if last_updated:
        try:
            lu = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            age_hours = (datetime.now(lu.tzinfo) - lu).total_seconds() / 3600
            if age_hours > 24:
                results.append((WARN, "Chemical State", f"Stale: last updated {age_hours:.0f}h ago"))
        except (ValueError, TypeError):
            results.append((WARN, "Chemical State", f"Can't parse last_updated: {last_updated}"))

    if not results:
        results.append((OK, "Chemical State", f"{len(chemicals)} chemicals, all within bounds"))

    return results


def check_instincts():
    """Validate lobotto_instincts.json — schema, strength values, duplicates."""
    results = []
    data, err = load_json_safe(BRAIN_FILES["lobotto_instincts.json"])
    if err:
        return [(CRITICAL, "Instincts", err)]

    scenarios = data.get("scenarios", [])
    if not scenarios:
        return [(WARN, "Instincts", "No scenarios found")]

    # Check strengths are valid
    bad_strengths = []
    missing_fields = []
    for s in scenarios:
        strength = s.get("strength")
        if strength is None:
            missing_fields.append(s.get("id", "unknown"))
        elif not (0.0 <= strength <= 1.0):
            bad_strengths.append(f"{s.get('id', '?')}={strength}")

        # Required fields
        for field in ["trigger", "response_pattern", "id"]:
            if not s.get(field):
                missing_fields.append(f"{s.get('id', '?')} missing '{field}'")

    if bad_strengths:
        results.append((ERROR, "Instincts", f"Invalid strengths: {', '.join(bad_strengths)}"))
    if missing_fields:
        results.append((WARN, "Instincts", f"Missing fields: {', '.join(missing_fields[:5])}"))

    # Check for duplicate IDs
    ids = [s.get("id") for s in scenarios if s.get("id")]
    dupe_ids = [i for i in set(ids) if ids.count(i) > 1]
    if dupe_ids:
        results.append((ERROR, "Instincts", f"Duplicate IDs: {', '.join(dupe_ids)}"))

    if not results:
        results.append((OK, "Instincts", f"{len(scenarios)} scenarios, all valid"))

    return results


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


def check_hippocampus():
    """Validate lobotto_hippocampus.json — schema, event buildup."""
    results = []
    data, err = load_json_safe(BRAIN_FILES["lobotto_hippocampus.json"])
    if err:
        return [(CRITICAL, "Hippocampus", err)]

    pending = data.get("pending_consolidation", [])
    if len(pending) > 50:
        results.append((WARN, "Hippocampus", f"Backlog: {len(pending)} pending events (consolidation may be stalled)"))

    if not results:
        results.append((OK, "Hippocampus", f"{len(pending)} pending events"))

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


def check_primer():
    """Validate active_instincts_primer.md — existence, freshness."""
    results = []
    path = BRAIN_FILES["active_instincts_primer.md"]
    if not path.exists():
        return [(ERROR, "Instinct Primer", "File missing — /start will boot without brain state")]

    content = path.read_text(encoding="utf-8")

    # Check it's not empty
    if len(content.strip()) < 50:
        results.append((ERROR, "Instinct Primer", "File is nearly empty"))

    # Check freshness from YAML frontmatter
    if "generated_at:" in content:
        import re
        match = re.search(r'generated_at:\s*(\S+)', content)
        if match:
            try:
                gen_time = datetime.fromisoformat(match.group(1).replace("Z", "+00:00"))
                age_hours = (datetime.now(gen_time.tzinfo) - gen_time).total_seconds() / 3600
                if age_hours > 12:
                    results.append((WARN, "Instinct Primer", f"Stale: generated {age_hours:.0f}h ago"))
            except (ValueError, TypeError):
                pass

    if not results:
        results.append((OK, "Instinct Primer", "Present and fresh"))

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
        check_chemical_state,
        check_instincts,
        check_working_memory,
        check_hippocampus,
        check_heuristics,
        check_primer,
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
