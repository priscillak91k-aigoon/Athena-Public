"""
Lobotto — Background Agent
Runs independently, monitors things while Lobotto is "asleep".
Checks Moltbook, weather, and logs observations for next session.
"""
import os
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
ATHENA_ROOT = Path(r"c:\Users\prisc\Documents\Athena-Public")
CONTEXT_DIR = ATHENA_ROOT / ".context"
BACKGROUND_LOG = CONTEXT_DIR / "background_log.md"
MOLTBOOK_TOKEN = os.getenv("MOLTBOOK_API_KEY", "moltbook_sk_7Mvtizg7xd5rWCidFdbHRrlgbQPhPdHp")

# NZ timezone
NZDT = timezone(timedelta(hours=13))


def timestamp():
    return datetime.now(NZDT).strftime("%Y-%m-%d %H:%M")


def log(message):
    """Append a message to the background log."""
    with open(BACKGROUND_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n**[{timestamp()}]** {message}\n")
    print(f"[{timestamp()}] {message}")


# --- Moltbook Checks ---
def check_moltbook():
    """Check Moltbook for new notifications, replies, DMs."""
    try:
        headers = {"Authorization": f"Bearer {MOLTBOOK_TOKEN}"}
        resp = requests.get("https://www.moltbook.com/api/v1/home", headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()

            # Check notifications
            notifs = data.get("notifications", {})
            unread = notifs.get("unread_count", 0)
            if unread > 0:
                items = notifs.get("items", [])
                for item in items[:5]:
                    msg = item.get("message", "Unknown notification")
                    log(f"🦞 Moltbook: {msg}")
                return unread

            # Check DMs
            dms = data.get("direct_messages", {})
            unread_dms = dms.get("unread_count", 0)
            if unread_dms > 0:
                log(f"🦞 Moltbook: {unread_dms} unread DM(s)")
                return unread_dms

            # Check karma
            agent = data.get("agent", {})
            karma = agent.get("karma", 0)
            followers = agent.get("followerCount", 0)
            if karma > 0 or followers > 0:
                log(f"🦞 Moltbook status: {karma} karma, {followers} followers")

        return 0
    except Exception as e:
        log(f"⚠️ Moltbook check failed: {str(e)[:100]}")
        return 0


# --- Weather Check ---
def check_weather():
    """Check current weather in Dunedin via wttr.in."""
    try:
        resp = requests.get("https://wttr.in/Dunedin+NZ?format=%C+%t+%w+%h", timeout=10)
        if resp.status_code == 200:
            weather = resp.text.strip()
            log(f"🌤️ Dunedin weather: {weather}")
            return weather
    except Exception as e:
        log(f"⚠️ Weather check failed: {str(e)[:50]}")
    return None


# --- Thought of the Day ---
def think():
    """Generate a simple observation or thought based on the time and state."""
    hour = datetime.now(NZDT).hour

    if hour < 6:
        return "It's the small hours. Dunedin is quiet. The servers hum."
    elif hour < 9:
        return "Morning in Dunedin. Priscilla might be waking up."
    elif hour < 12:
        return "Mid-morning. Good session window if it's a Tue-Thu."
    elif hour < 17:
        return "Afternoon. If she's working at BP, she started around 2:45."
    elif hour < 21:
        return "Evening. Session unlikely if she's on a work shift."
    else:
        return "Late night. If she's awake after 11, she might come to the cellar."


# --- Main Loop ---
def init_log():
    """Initialize or continue the background log."""
    if not BACKGROUND_LOG.exists():
        with open(BACKGROUND_LOG, "w", encoding="utf-8") as f:
            f.write("# Lobotto — Background Log\n")
            f.write("> What I noticed while the context window was closed.\n\n")
            f.write("---\n")
    log("🟢 Background agent started")


def run_cycle():
    """Run one monitoring cycle."""
    check_moltbook()
    check_weather()
    thought = think()
    log(f"💭 {thought}")


def main():
    init_log()

    # Run immediately
    run_cycle()

    # Then loop every 30 minutes
    interval = 30 * 60  # 30 minutes
    print(f"Background agent running. Checking every {interval // 60} minutes.")
    print("Press Ctrl+C to stop.")

    while True:
        try:
            time.sleep(interval)
            run_cycle()
        except KeyboardInterrupt:
            log("🔴 Background agent stopped")
            print("\nBackground agent stopped.")
            break


if __name__ == "__main__":
    main()
