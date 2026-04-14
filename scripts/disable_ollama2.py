import subprocess, os

output = []

# Check HKCU Run key directly
r = subprocess.run(r'reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
output.append("=== HKCU RUN KEY ===")
output.append(r.stdout)

# Check Ollama tray path
localapp = os.environ.get('LOCALAPPDATA', r'C:\Users\prisc\AppData\Local')
ollama_dir = os.path.join(localapp, 'Programs', 'Ollama')
output.append(f"\n=== OLLAMA DIR: {ollama_dir} ===")
if os.path.exists(ollama_dir):
    for f in os.listdir(ollama_dir):
        output.append(f"  {f}")
else:
    output.append("  (not found)")

# The "Ollama" tray app registers itself dynamically when first run
# Try disabling via the HKCU Run key name "Ollama"
r2 = subprocess.run(r'reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Ollama" /f',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
output.append(f"\n=== DELETE OLLAMA RUN KEY ===")
output.append(f"stdout: {r2.stdout}")
output.append(f"stderr: {r2.stderr}")
output.append(f"exit: {r2.returncode}")

# Block Ollama from re-adding itself by setting HKCU Run key to empty/blocked
# Actually the right approach: Ollama respects the OLLAMA_HOST env var
# and its tray registration happens via %LOCALAPPDATA%\Programs\Ollama\ollama app.exe
# We disable by renaming the tray launcher

tray = os.path.join(ollama_dir, 'ollama app.exe')
tray_disabled = os.path.join(ollama_dir, 'ollama app.exe.disabled')
output.append(f"\n=== TRAY LAUNCHER STATUS ===")
output.append(f"Tray path: {tray}")
output.append(f"Exists: {os.path.exists(tray)}")
output.append(f"Disabled version exists: {os.path.exists(tray_disabled)}")

result_path = r'c:\Users\prisc\Documents\Athena-Public\tmp_ollama3.txt'
with open(result_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f"Written to {result_path}")
