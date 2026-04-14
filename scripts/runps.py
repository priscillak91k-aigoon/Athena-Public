#!/usr/bin/env python3
"""Run a PS1 script and print full output cleanly."""
import subprocess, sys

script = sys.argv[1] if len(sys.argv) > 1 else "scripts/disable_ollama_startup.ps1"
r = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd="c:/Users/prisc/Documents/Athena-Public"
)
print(r.stdout)
if r.stderr:
    print("STDERR:", r.stderr[:500])
print(f"Exit code: {r.returncode}")
