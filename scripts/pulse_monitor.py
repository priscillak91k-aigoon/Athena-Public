#!/usr/bin/env python3
"""
Pulse Monitor (The Watcher)
Monitors the health of critical Athena nodes (Discord Bot, Reaper Loop).
Restarts them if they die and logs traumas.
"""
import os
import sys
import time
import json
import subprocess
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(BASE_DIR, ".context", "state")
STATE_FILE = os.path.join(STATE_DIR, "pulse.json")

# Scripts to monitor
SCRIPTS_TO_MONITOR = {
    "discord_bot": os.path.join(BASE_DIR, "scripts", "discord_bot.py"),
    "reaper_loop": os.path.join(BASE_DIR, "bounty_ops", "reaper_loop.py")
}

def load_state():
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR, exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state
        except Exception as e:
            print(f"Error loading state: {e}")
    return {"traumas": {"discord_bot": 0, "reaper_loop": 0}, "last_pulse": ""}

def save_state(state):
    state["last_pulse"] = datetime.now().isoformat()
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

def is_running(script_name):
    """Check if a python process is running this specific script name via WMI commandline."""
    try:
        output = subprocess.check_output(
            'wmic process where "name=\'python.exe\' or name=\'pwsh.exe\' or name=\'powershell.exe\'" get commandline', 
            shell=True, 
            text=True
        )
        return script_name in output
    except Exception as e:
        print(f"Error checking process: {e}")
        return False

def restart_script(name, path):
    print(f"[{datetime.now()}] Restarting {name}...")
    try:
        if os.name == 'nt':
            cmd = f'Start-Process -FilePath "python" -ArgumentList "{path}" -WindowStyle Hidden'
            subprocess.Popen(["powershell", "-Command", cmd])
        else:
            subprocess.Popen(["python", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Failed to restart {name}: {e}")
        return False

def monitor():
    print("Starting Pulse Monitor...")
    while True:
        state = load_state()
        
        for name, path in SCRIPTS_TO_MONITOR.items():
            script_filename = os.path.basename(path)
            if not is_running(script_filename):
                print(f"[{datetime.now()}] ALARM: {name} is DEAD. Initiating revive sequence.")
                if restart_script(name, path):
                    if name not in state["traumas"]:
                        state["traumas"][name] = 0
                    state["traumas"][name] += 1
                    time.sleep(5) # Give it time to boot before checking others
        
        save_state(state)
        time.sleep(60) # Pulse check every 60 seconds

if __name__ == "__main__":
    monitor()
