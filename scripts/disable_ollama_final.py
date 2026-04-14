import subprocess, os, shutil

output = []

# ── 1. Disable Ollama tray by renaming 'ollama app.exe'
# 'ollama.exe' (the CLI) stays untouched — you can still run it manually
localapp = os.environ.get('LOCALAPPDATA', r'C:\Users\prisc\AppData\Local')
tray = os.path.join(localapp, 'Programs', 'Ollama', 'ollama app.exe')
tray_disabled = tray + '.disabled'

output.append("=== DISABLING OLLAMA TRAY AUTO-START ===")
if os.path.exists(tray):
    if not os.path.exists(tray_disabled):
        os.rename(tray, tray_disabled)
        output.append(f"  > Renamed: 'ollama app.exe' -> 'ollama app.exe.disabled'")
        output.append(f"  > Ollama will NO LONGER auto-start on boot")
        output.append(f"  > Ollama CLI still works: just run 'ollama serve' in terminal")
    else:
        output.append(f"  > Already disabled (ollama app.exe.disabled exists)")
else:
    output.append(f"  > ollama app.exe not found at: {tray}")

# ── 2. Remove Adobe Acrobat Synchronizer from startup
output.append("\n=== REMOVING ADOBE ACROBAT SYNCHRONIZER FROM STARTUP ===")
r = subprocess.run(
    r'reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Adobe Acrobat Synchronizer" /f',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
if r.returncode == 0:
    output.append("  > Adobe Acrobat Synchronizer removed from startup")
else:
    output.append(f"  > Not found or already removed: {r.stderr.strip()}")

# ── 3. Disable OneDrive from startup via StartupApproved (already disabled from earlier)
output.append("\n=== ONEDRIVE STARTUP STATUS ===")
output.append("  > Already disabled via StartupApproved registry (done earlier this session)")

# ── 4. Kill any remaining Ollama processes NOW
output.append("\n=== KILLING OLLAMA PROCESSES ===")
r2 = subprocess.run('taskkill /F /IM "ollama app.exe" /T', shell=True, capture_output=True, text=True)
r3 = subprocess.run('taskkill /F /IM "ollama.exe" /T', shell=True, capture_output=True, text=True)
if r2.returncode == 0:
    output.append("  > 'ollama app.exe' killed")
else:
    output.append("  > 'ollama app.exe' not running")
if r3.returncode == 0:
    output.append("  > 'ollama.exe' killed")
else:
    output.append("  > 'ollama.exe' not running")

# ── 5. RAM after
import ctypes
class MEMSTATUS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = MEMSTATUS()
ms.dwLength = ctypes.sizeof(ms)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
free_gb = round(ms.ullAvailPhys / (1024**3), 1)
total_gb = round(ms.ullTotalPhys / (1024**3), 1)
output.append(f"\n=== RAM STATUS ===")
output.append(f"  Free: {free_gb} GB of {total_gb} GB")

result_path = r'c:\Users\prisc\Documents\Athena-Public\tmp_disable_result.txt'
with open(result_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print('\n'.join(output))
