"""
Athena Resource Watchdog
========================
Runs every 2 hours via Windows Task Scheduler.
Kills stuck/hung processes that are consuming resources unnecessarily.
Logs every action to logs/resource_watchdog.log.

Safe-to-kill rules:
  - Python processes running > 2 hours AND consuming meaningful CPU (hung scripts)
  - Python processes with zero CPU for > 2 hours (zombie/stuck)

Never-kill list:
  - athena_dreaming.py (may legitimately run long on Ollama)
  - telegram_architect_bot.py (persistent service)
  - Any process not in our known script list
"""

import os
import sys
import json
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "resource_watchdog.log"
LOG_DIR.mkdir(exist_ok=True)

# Scripts we intentionally keep running long-term — never kill these
NEVER_KILL_CMDLINE_FRAGMENTS = [
    "athena_dreaming.py",
    "telegram_architect_bot.py",
    "discord_bot.py",
    "heartbeat.py",
    "morning_briefing.py",
    "health_watchdog.py",
]

# Thresholds
HUNG_CPU_THRESHOLD = 1.0        # CPU % — a hung script usually idles near 0 or spikes
HUNG_RUNTIME_HOURS = 2.0        # Must have been running > 2 hours to be considered hung
SPIKE_CPU_THRESHOLD = 80.0      # CPU% — actively spiking for > 2h = stuck in loop
SPIKE_RUNTIME_HOURS = 2.0


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_python_processes():
    """Return list of psutil.Process objects that are Python scripts."""
    results = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time", "cpu_percent"]):
        try:
            name = proc.info["name"] or ""
            if "python" not in name.lower():
                continue
            cmdline = " ".join(proc.info["cmdline"] or [])
            results.append({
                "pid": proc.info["pid"],
                "cmdline": cmdline,
                "create_time": proc.info["create_time"],
                "proc": proc
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return results


def is_protected(cmdline: str) -> bool:
    """Return True if this process should never be killed."""
    cl = cmdline.lower()
    return any(frag.lower() in cl for frag in NEVER_KILL_CMDLINE_FRAGMENTS)


def runtime_hours(create_time: float) -> float:
    return (datetime.now().timestamp() - create_time) / 3600


def sample_cpu(proc, interval=1.0) -> float:
    """Sample actual CPU usage over interval seconds."""
    try:
        return proc.cpu_percent(interval=interval)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0.0


def kill_process(proc_info: dict, reason: str):
    pid = proc_info["pid"]
    cmdline = proc_info["cmdline"][:120]
    try:
        proc_info["proc"].kill()
        log(f"KILLED PID {pid} — {reason} | cmd: {cmdline}")
        return True
    except Exception as e:
        log(f"FAILED to kill PID {pid}: {e}")
        return False


def check_defender_cpu():
    """Log if MsMpEng is spiking — can't kill it, but useful to know."""
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and "MsMpEng" in proc.info["name"]:
                cpu = proc.cpu_percent(interval=0.5)
                if cpu > 20:
                    log(f"NOTICE: MsMpEng (Defender) using {cpu:.1f}% CPU — normal during scan, but worth noting if persistent")
        except Exception:
            pass


def main():
    log("=" * 60)
    log("Resource Watchdog run starting")

    python_procs = get_python_processes()
    log(f"Found {len(python_procs)} Python processes")

    killed = 0
    skipped_protected = 0

    for p in python_procs:
        hours = runtime_hours(p["create_time"])
        cmdline = p["cmdline"]

        if is_protected(cmdline):
            skipped_protected += 1
            log(f"PROTECTED PID {p['pid']} (running {hours:.1f}h) — skipping | {cmdline[:80]}")
            continue

        if hours < HUNG_RUNTIME_HOURS:
            continue  # Too young to be considered hung

        # Sample CPU
        cpu = sample_cpu(p["proc"])

        # Rule 1: Running > 2h and CPU near zero = zombie/stuck
        if cpu < HUNG_CPU_THRESHOLD and hours > HUNG_RUNTIME_HOURS:
            if kill_process(p, f"ZOMBIE: {hours:.1f}h runtime, {cpu:.1f}% CPU"):
                killed += 1

        # Rule 2: Running > 2h and CPU very high = stuck in loop
        elif cpu > SPIKE_CPU_THRESHOLD and hours > SPIKE_RUNTIME_HOURS:
            if kill_process(p, f"SPIKE LOOP: {hours:.1f}h runtime, {cpu:.1f}% CPU"):
                killed += 1

        else:
            log(f"OK PID {p['pid']}: {hours:.1f}h, {cpu:.1f}% CPU | {cmdline[:80]}")

    check_defender_cpu()

    log(f"Done — killed: {killed}, protected: {skipped_protected}")
    log("=" * 60)

    # Summary report for Telegram if anything was killed
    if killed > 0:
        try:
            from dotenv import load_dotenv
            load_dotenv(PROJECT_ROOT / ".env")
            import requests
            token = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
            uid = os.getenv("TELEGRAM_ALLOWED_USER_ID")
            if token and uid:
                msg = f"🔧 *Resource Watchdog*\n\nKilled {killed} hung Python process(es).\nCheck `logs/resource_watchdog.log` for details."
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": uid, "text": msg, "parse_mode": "Markdown"},
                    timeout=10
                )
        except Exception as e:
            log(f"Telegram notify failed: {e}")


if __name__ == "__main__":
    main()
