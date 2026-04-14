#!/usr/bin/env python3
"""Run PS1 and write output to file for clean reading."""
import subprocess

script = "scripts/disable_ollama_startup.ps1"
r = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd="c:/Users/prisc/Documents/Athena-Public"
)
out = r.stdout + ("\nSTDERR: " + r.stderr if r.stderr else "")
out += f"\nExit: {r.returncode}"

with open("c:/Users/prisc/Documents/Athena-Public/tmp_ollama_check.txt", "w", encoding="utf-8") as f:
    f.write(out)

print("Written to tmp_ollama_check.txt")
