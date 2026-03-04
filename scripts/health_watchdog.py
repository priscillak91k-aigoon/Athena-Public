"""
Athena Health Watchdog — Supplement Reminders
==============================================
Sends timed Telegram nudges based on the supplement protocol.

Scheduled runs:
  - 6:25 AM  → "NAC time (empty stomach)"
  - 6:55 AM  → "Breakfast supps reminder"
  - 6:25 PM  → "Evening Fish Oil + D3"
  - 8:55 PM  → "Magnesium time"

Usage: python scripts/health_watchdog.py --check
  Checks current time and sends appropriate reminder if within window.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")


def send_telegram(message):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_USER_ID,
        "text": message,
        "parse_mode": "Markdown"
    }, timeout=10)


# Reminder windows: (hour, minute, message)
REMINDERS = [
    (6, 25, "💊 *NAC time* — 1200mg (2 caps), empty stomach. Take before breakfast."),
    (6, 55, "🍳 *Breakfast supps:*\n• K2 MK-7 (2 caps)\n• Fish Oil + D3 (1 cap)\n• B-Complex + L-Theanine (1 cap)\n• Turmeric (2 caps)\n• Even Blood Sugar Babe (4g)\n• Phloe (2 caps)"),
    (18, 25, "🌙 *Evening Fish Oil + D3* — 10,000IU (2 caps) with dinner."),
    (20, 55, "😴 *Magnesium time* — Mag Glycinate 400mg elemental before bed."),
]


def check_and_send():
    now = datetime.now()
    current_h = now.hour
    current_m = now.minute

    for hour, minute, message in REMINDERS:
        # Send if within 5-minute window of reminder time
        if current_h == hour and minute <= current_m <= minute + 5:
            send_telegram(message)
            print(f"[{now.isoformat()}] Sent reminder: {message[:50]}...")
            return True

    print(f"[{now.isoformat()}] No reminders due at {current_h:02d}:{current_m:02d}")
    return False


def main():
    check_and_send()


if __name__ == "__main__":
    main()
