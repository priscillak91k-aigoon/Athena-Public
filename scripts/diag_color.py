import subprocess

output = []

# Current display config
r = subprocess.run(
    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command',
     'Get-WmiObject Win32_VideoController | Select-Object Name,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate,VideoModeDescription | Format-List'],
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    cwd='c:/Users/prisc/Documents/Athena-Public'
)
output.append("=== DISPLAY CONFIG ===")
output.append(r.stdout)

# Check NVIDIA color range setting in registry
# HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968...}\0000 (or 0001)
r2 = subprocess.run(
    'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e968-e325-11ce-bfc1-08002be10318}\\0000" /v "ColorVibranceEnable" 2>&1',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
output.append("=== NVIDIA COLOR VIBRANCE ===")
output.append(r2.stdout or r2.stderr)

# Check the NVFBC / output color range via NVAPI registry (what NVCP writes)
r3 = subprocess.run(
    r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000" 2>&1',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
# Filter for color-related keys
color_lines = [l for l in r3.stdout.splitlines() if any(k in l.lower() for k in ['color','range','dynamic','vibrance','output','depth','yuv','rgb'])]
output.append("=== NVIDIA COLOR-RELATED REGISTRY KEYS ===")
output.extend(color_lines if color_lines else ["(none found in 0000)"])

# Also check 0001 (second GPU instance)
r4 = subprocess.run(
    r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0001" 2>&1',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
color_lines2 = [l for l in r4.stdout.splitlines() if any(k in l.lower() for k in ['color','range','dynamic','vibrance','output','depth','yuv','rgb'])]
output.append("=== NVIDIA COLOR KEYS (0001) ===")
output.extend(color_lines2 if color_lines2 else ["(none found in 0001)"])

with open('c:/Users/prisc/Documents/Athena-Public/tmp_color_diag.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print('Written to tmp_color_diag.txt')
