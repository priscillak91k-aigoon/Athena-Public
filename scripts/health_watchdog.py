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
import traceback
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / ".context" / "watchdog_errors.log"

load_dotenv(PROJECT_ROOT / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")


def log_error(msg: str):
    """Write error to log file with timestamp."""
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")


def send_telegram(message: str) -> bool:
    """Send Telegram message. Returns True on success, False on failure."""
    import requests
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_USER_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=15)
        resp.raise_for_status()
        return True
    except requests.exceptions.ConnectionError as e:
        log_error(f"send_telegram CONNECTION ERROR: {e}")
        return False
    except requests.exceptions.Timeout:
        log_error("send_telegram TIMEOUT after 15s")
        return False
    except requests.exceptions.HTTPError as e:
        log_error(f"send_telegram HTTP ERROR {resp.status_code}: {e}")
        return False
    except Exception as e:
        log_error(f"send_telegram UNEXPECTED: {traceback.format_exc()}")
        return False


def send_error_alert(context: str):
    """Attempt to send a self-error alert via Telegram."""
    msg = f"⚠️ *Athena Watchdog Error*\n`{context}`\nCheck `.context/watchdog_errors.log`"
    send_telegram(msg)  # best-effort only — if this fails too, it's logged


# Reminder windows: (hour, minute, message)
REMINDERS = [
    (6, 25, "💊 *NAC time* — 1200mg (2 caps), empty stomach. Take before breakfast."),
    (6, 55, "🍳 *Breakfast supps:*\n• K2 MK-7 (2 caps)\n• Fish Oil + D3 (1 cap)\n• B-Complex + L-Theanine (1 cap)\n• Turmeric (2 caps)\n• Even Blood Sugar Babe (4g)\n• Phloe (2 caps)"),
    (18, 25, "🌙 *Evening Fish Oil + D3* — 10,000IU (1 cap) with dinner."),
    (20, 55, "😴 *Magnesium time* — Mag Glycinate 400mg elemental before bed."),
]


def check_and_send():
    now = datetime.now()
    current_h = now.hour
    current_m = now.minute

    for hour, minute, message in REMINDERS:
        if current_h == hour and minute <= current_m <= minute + 5:
            success = send_telegram(message)
            if success:
                print(f"[{now.isoformat()}] ✅ Sent reminder: {message[:50]}...")
            else:
                err = f"Failed to send reminder at {current_h:02d}:{current_m:02d}"
                log_error(err)
                send_error_alert(err)
                print(f"[{now.isoformat()}] ❌ {err}")
                sys.exit(1)
            return True

    print(f"[{now.isoformat()}] No reminders due at {current_h:02d}:{current_m:02d}")
    return False


def main():
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_USER_ID:
            log_error("Missing TELEGRAM_ARCHITECT_TOKEN or TELEGRAM_ALLOWED_USER_ID in .env")
            sys.exit(1)
        check_and_send()
    except Exception as e:
        err = f"Unhandled exception: {traceback.format_exc()}"
        log_error(err)
        send_error_alert(f"health_watchdog crash: {str(e)[:100]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
