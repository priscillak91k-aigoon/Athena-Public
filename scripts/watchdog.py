"""
Athena Watchdog — monitors bot processes, restarts dead ones, sends Telegram alerts.
Runs every 5 minutes via Task Scheduler.
"""
import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

TOKEN = os.getenv("TELEGRAM_ARCHITECT_TOKEN")
USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID")
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
LOG_FILE = os.path.join(ROOT_DIR, "scripts", "watchdog.log")

# Bots to monitor: (name, script filename, search string in cmdline)
BOTS = [
    ("Telegram", "lobotto_telegram.py", "lobotto_telegram"),
    ("Discord",  "discord_bot.py",      "discord_bot"),
]


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        # Keep log file under 500 lines
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 500:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines[-200:])
    except:
        pass


def send_telegram_alert(msg):
    """Send an alert directly via Telegram HTTP API (no library needed)."""
    if not TOKEN or not USER_ID:
        log("Cannot send alert: missing TOKEN or USER_ID")
        return
    try:
        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": USER_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }).encode()
        urllib.request.urlopen(url, data, timeout=10)
        log(f"Alert sent to Telegram")
    except Exception as e:
        log(f"Failed to send Telegram alert: {e}")


def get_running_python_commands():
    """Get list of command lines for all running Python processes."""
    try:
        output = subprocess.check_output(
            'wmic process where "name=\'python.exe\' or name=\'python3.exe\'" get commandline /format:list',
            shell=True, text=True, timeout=10
        )
        return output.lower()
    except Exception as e:
        log(f"Failed to query processes: {e}")
        return ""


def restart_bot(name, script):
    """Restart a bot script in a minimized window."""
    script_path = os.path.join(SCRIPTS_DIR, script)
    if not os.path.exists(script_path):
        log(f"Script not found: {script_path}")
        return False
    try:
        subprocess.Popen(
            f'start "Athena-{name}" /min python "{script_path}"',
            shell=True, cwd=ROOT_DIR
        )
        log(f"Restarted {name} bot")
        return True
    except Exception as e:
        log(f"Failed to restart {name}: {e}")
        return False


def main():
    running = get_running_python_commands()
    dead_bots = []
    alive_bots = []

    for name, script, search in BOTS:
        if search.lower() in running:
            alive_bots.append(name)
        else:
            dead_bots.append((name, script))

    if not dead_bots:
        log(f"All bots alive: {', '.join(alive_bots)}")
        return

    # Restart dead bots
    restarted = []
    failed = []
    for name, script in dead_bots:
        log(f"⚠️ {name} bot is DEAD. Restarting...")
        if restart_bot(name, script):
            restarted.append(name)
        else:
            failed.append(name)

    # Send Telegram alert
    alert_parts = [f"🚨 *Watchdog Alert*"]
    if restarted:
        alert_parts.append(f"♻️ Restarted: {', '.join(restarted)}")
    if failed:
        alert_parts.append(f"❌ Failed to restart: {', '.join(failed)}")
    if alive_bots:
        alert_parts.append(f"✅ Still alive: {', '.join(alive_bots)}")

    send_telegram_alert("\n".join(alert_parts))


if __name__ == "__main__":
    main()
