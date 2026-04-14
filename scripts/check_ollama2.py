import subprocess

r = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
     'schtasks /query /fo CSV 2>&1'],
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    cwd='c:/Users/prisc/Documents/Athena-Public'
)
lines = [l for l in r.stdout.splitlines() if 'ollama' in l.lower() or 'llama' in l.lower()]
if lines:
    print("FOUND OLLAMA IN SCHEDULED TASKS:")
    for l in lines:
        print(" ", l)
else:
    print("No Ollama entries in schtasks.")
    print("Ollama likely starts via its own tray app mechanism (AppData startup).")
    
# Check AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
r2 = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
     r'Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" | Format-Table Name -AutoSize'],
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    cwd='c:/Users/prisc/Documents/Athena-Public'
)
print("\nSTARTUP FOLDER CONTENTS:")
print(r2.stdout or "(empty)")

# Check all user startup folder
r3 = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
     r'Get-ChildItem "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp" | Format-Table Name -AutoSize'],
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    cwd='c:/Users/prisc/Documents/Athena-Public'
)
print("ALL USERS STARTUP FOLDER:")
print(r3.stdout or "(empty)")
