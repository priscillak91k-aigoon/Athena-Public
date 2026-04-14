#!/usr/bin/env python3
"""Quick system diagnostics — display config, RAM/CPU hogs."""
import subprocess, sys

def ps(cmd):
    r = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, encoding='utf-8')
    return r.stdout.strip()

# Display info
print("=== DISPLAY ===")
disp = ps("Get-WmiObject -Class Win32_VideoController | ForEach-Object { Write-Output \"$($_.Name) | $($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)@$($_.CurrentRefreshRate)Hz\" }")
print(disp or "No output")

# Total RAM
print("\n=== RAM TOTAL ===")
ram = ps("(Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB")
print(f"Total RAM: {float(ram.strip()):.1f} GB" if ram.strip() else "Unknown")

# Available RAM
avail = ps("[math]::Round((Get-WmiObject -Class Win32_OperatingSystem).FreePhysicalMemory / 1MB, 0)")
print(f"Free RAM: ~{avail} MB")

# Top processes by RAM
print("\n=== TOP RAM HOGS ===")
proc = ps("""Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 20 | ForEach-Object {
    $name = $_.Name.PadRight(30)
    $ram = [math]::Round($_.WorkingSet/1MB, 0)
    $cpu = [math]::Round($_.CPU, 1)
    Write-Output "$name RAM:${ram}MB  CPU:${cpu}s"
}""")
print(proc)

# Startup programs
print("\n=== STARTUP ITEMS ===")
startup = ps("Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | ForEach-Object { Write-Output \"$($_.Name): $($_.Command)\" }")
print(startup or "None found")

print("\n=== DONE ===")
