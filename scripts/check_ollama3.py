import subprocess, os

# Ollama registers its tray app via HKCU Run key as "Ollama"
# The key name is exactly "Ollama" with capital O
# Let's check the raw registry

cmds = [
    # Check exact HKCU Run keys including any casing
    r'reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"',
    # Check if Ollama has its own scheduled task under its namespace
    r'schtasks /query /fo CSV /tn "\Ollama" 2>&1',
    # Check AppData Local Programs
    r'dir "%LOCALAPPDATA%\Programs\Ollama\" /b 2>&1',
]

for cmd in cmds:
    print(f"\n>>> {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(r.stdout or "(no output)")
    if r.stderr: print("ERR:", r.stderr[:200])
