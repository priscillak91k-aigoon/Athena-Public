#!/usr/bin/env python3
import os
import re
import socket
import traceback
import subprocess
import urllib.request
import urllib.error
import json
from datetime import datetime

# ==========================================
# ATOM NODE - ENTERPRISE HEALTH REPORTER (v3.0 - AUDITED)
# ==========================================

COMPOSE_PATH = "/home/sj/Athena-Public/infrastructure/sj_atom/docker-compose-ai.yml"

HTTP_ENDPOINTS = {
    "Open WebUI": "http://127.0.0.1:3000/",
    "Sovereign LLM (llama.cpp)": "http://127.0.0.1:8080/v1/models",
    "Jellyfin": "http://127.0.0.1:8096/web/index.html",
    "Audiobookshelf": "http://127.0.0.1:13378/",
    "EdgeTTS": "http://127.0.0.1:7860/"
}

def get_telegram_creds():
    token, chat_id = "8878217823:AAHvwnBXXbtH20nzh9tbr0G35Ac_Y9hWKgI", "8309108979"
    try:
        if os.path.exists(COMPOSE_PATH):
            with open(COMPOSE_PATH, "r") as f:
                content = f.read()
                token_match = re.search(r"TELEGRAM_TOKEN=(.+)", content)
                chat_match = re.search(r"ALLOWED_CHAT_ID=(.+)", content)
                if not chat_match:
                    chat_match = re.search(r"TELEGRAM_CHAT_ID=(.+)", content)
                if token_match: token = token_match.group(1).strip()
                if chat_match: chat_id = chat_match.group(1).strip()
    except Exception:
        pass
    return token, chat_id

def send_telegram(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}\nMessage: {message}")

def run_command(cmd_list, timeout=10):
    try:
        result = subprocess.run(cmd_list, text=True, capture_output=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip()
        return f"ERROR: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "ERROR: COMMAND_TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)}"

def check_http_endpoint(name, url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            return f"🟢 {name} - OK ({status})"
    except urllib.error.HTTPError as e:
        return f"🟢 {name} - OK ({e.code})"
    except urllib.error.URLError:
        return f"🔴 {name} - CONNECTION REFUSED"
    except socket.timeout:
        return f"🔴 {name} - TIMEOUT"
    except Exception:
        return f"🔴 {name} - ERROR"

def get_system_metrics():
    mem_info = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    mem_info[parts[0].strip()] = int(parts[1].strip().split()[0])
        total_mem = mem_info.get("MemTotal", 0) / 1024 / 1024
        free_mem = mem_info.get("MemAvailable", 0) / 1024 / 1024
        used_mem = total_mem - free_mem
        mem_percent = (used_mem / total_mem) * 100 if total_mem else 0
        mem_str = f"{used_mem:.1f}GB / {total_mem:.1f}GB ({mem_percent:.1f}%)"
    except Exception as e:
        mem_str = f"ERROR: {e}"

    try:
        st = os.statvfs("/")
        total_disk = (st.f_blocks * st.f_frsize) / (1024**3)
        free_disk = (st.f_bavail * st.f_frsize) / (1024**3)
        used_disk = total_disk - free_disk
        disk_percent = (used_disk / total_disk) * 100 if total_disk else 0
        disk_str = f"{used_disk:.1f}GB / {total_disk:.1f}GB ({disk_percent:.1f}%)"
    except Exception as e:
        disk_str = f"ERROR: {e}"

    mount_target = "/mnt/media/data"
    if os.path.exists(mount_target) and os.path.ismount(mount_target):
        media_mount = "🟢 ACTIVE"
    else:
        media_mount = "🔴 DISCONNECTED/UNMOUNTED"

    return f"🧠 **RAM:** {mem_str}\n💾 **Root Disk:** {disk_str}\n💿 **11TB QNAP Array:** {media_mount}"

def get_docker_status():
    cmd = ["/usr/bin/docker", "ps", "-a", "--format", "{{.Names}}|{{.State}}|{{.Status}}"]
    output = run_command(cmd, timeout=15)
    
    if output.startswith("ERROR:"):
        return f"⚠️ Docker Daemon Offline or Hung ({output})"
        
    containers = output.split('\n')
    dead_containers = []
    total = running = 0
    
    for c in containers:
        if not c.strip(): continue
        total += 1
        parts = c.split('|')
        if len(parts) >= 2:
            name, state = parts[0], parts[1]
            if state == "running":
                running += 1
            else:
                dead_containers.append(f"- {name} ({state})")
                
    status = f"🐋 **Docker:** {running}/{total} Containers Running\n"
    if dead_containers:
        status += "🔴 **Offline Containers:**\n" + "\n".join(dead_containers)
    else:
        status += "🟢 All Containers Online"
        
    return status

def get_systemd_status():
    output = run_command(["/bin/systemctl", "is-active", "atom-llm.service"], timeout=5)
    if output == "active":
        return "🟢 `atom-llm.service`: Active"
    else:
        return f"🔴 `atom-llm.service`: {output}"

def main():
    token, chat_id = get_telegram_creds()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"🤖 **ATOM NODE DAILY REPORT (v3.0)** 🤖\n⏱️ {date_str}\n\n"
    report += "**--- SYSTEM RESOURCES ---**\n" + get_system_metrics() + "\n\n"
    report += "**--- CORE SERVICES ---**\n" + get_systemd_status() + "\n"
    
    for name, url in HTTP_ENDPOINTS.items():
        report += check_http_endpoint(name, url) + "\n"
            
    report += "\n**--- DOCKER MATRIX ---**\n" + get_docker_status()
    
    send_telegram(report, token, chat_id)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        token, chat_id = "8878217823:AAHvwnBXXbtH20nzh9tbr0G35Ac_Y9hWKgI", "8309108979"
        error_trace = traceback.format_exc()
        msg = f"🚨 **ATOM HEALTH MONITOR CRASHED** 🚨\n```python\n{error_trace}\n```"
        send_telegram(msg, token, chat_id)
        print(msg)
