"""
Athena Morning Briefing — Daily 6 AM Telegram Message
======================================================
Sends Priscilla a personalized morning briefing covering:
- Supplement checklist for the day
- Overdue action items from brain files
- What the AI has been thinking about
- Any urgent alerts

Scheduled via Windows Task Scheduler at 6:00 AM NZDT daily.
"""

import os
import sys
import traceback
import json
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")
CONTEXT_DIR = PROJECT_ROOT / ".context"


def read_file(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def send_telegram(message):
    import requests
    import time
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        for attempt in range(3):
            try:
                resp = requests.post(url, json={
                    "chat_id": TELEGRAM_USER_ID,
                    "text": chunk,
                    "parse_mode": "Markdown"
                }, timeout=15)
                if resp.status_code == 200:
                    break
            except Exception as e:
                if attempt < 2:
                    time.sleep(5 * (attempt + 1))
                else:
                    print(f"[WARN] Telegram send failed after 3 attempts: {e}")


def get_supplement_checklist():
    return """*Morning Supplements:*
⬜ 6:30 AM — NAC 1200mg (2 caps, empty stomach)
⬜ 7:00 AM — K2 MK-7 200mcg (2 caps)
⬜ 7:00 AM — Fish Oil + D3 10,000IU (1 cap)
⬜ 7:00 AM — B-Complex + L-Theanine (1 cap)
⬜ 7:00 AM — Turmeric 28,000+ (2 caps)
⬜ 7:00 AM — Even Blood Sugar Babe (4g powder)
⬜ 7:00 AM — Phloe (2 caps)

*Evening:*
⬜ 6:30 PM — Fish Oil + D3 10,000IU (2 caps)
⬜ 9:00 PM — Mag Glycinate 400mg elemental"""


def get_overdue_items():
    about = read_file(CONTEXT_DIR / "about_priscilla.md")
    thinking = read_file(CONTEXT_DIR / "thinking_log.md")

    items = []
    # Check for stale action items
    if "ITM Dunedin" in about and "ITM" in thinking:
        items.append("ITM Dunedin call — plywood order still pending")
    if "Vitamin D" in about:
        items.append("Vitamin D blood test — check if 8-12 week window has arrived")
    if "framework versions" in thinking.lower() or "consolidat" in thinking.lower():
        items.append("Framework version consolidation incomplete")

    return items


def get_dream_summary():
    thinking = read_file(CONTEXT_DIR / "thinking_log.md")
    if not thinking:
        return "No recent thinking cycles."

    # Extract first 500 chars of latest thinking log
    lines = thinking.split("\n")
    summary_lines = []
    for line in lines[5:25]:  # Skip header, grab first 20 content lines
        clean = line.strip()
        if clean and not clean.startswith(">") and not clean.startswith("---"):
            summary_lines.append(clean)
        if len(summary_lines) >= 5:
            break

    return "\n".join(summary_lines) if summary_lines else "Thinking cycle ran but no notable insights."


def main():
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %B %Y")

    # Build briefing
    msg_parts = [
        f"*Good morning, Cilla.* ☀️",
        f"_{day_name}, {date_str}_\n",
        get_supplement_checklist(),
    ]

    # Overdue items
    overdue = get_overdue_items()
    if overdue:
        msg_parts.append("\n*⚠️ Overdue Items:*")
        for item in overdue:
            msg_parts.append(f"• {item}")

    # Dream summary
    dream = get_dream_summary()
    if dream:
        msg_parts.append(f"\n*🧠 Overnight Thinking:*\n{dream}")

    # Caffeine reminder based on chronotype
    msg_parts.append("\n☕ _Caffeine cutoff: 10:00 AM_")

    # Sign off
    msg_parts.append(f"\n— Lobotto [Athena Session Auto]")

    message = "\n".join(msg_parts)
    send_telegram(message)
    print(f"[{now.isoformat()}] Morning briefing sent.")


if __name__ == "__main__":
    main()
