import subprocess, winreg

output = []

# NVIDIA stores color output settings per-display in a complex EDID-keyed path
# The simpler path: set it via the NVIDIA Control Panel API using NvAPI
# But we can try the known registry path that NVCP uses

# First, find all NVIDIA display adapter registry paths
output.append("=== SEARCHING NVIDIA DISPLAY ADAPTER KEYS ===")

try:
    base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as k:
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(k, i)
                if subkey_name.isdigit():
                    try:
                        with winreg.OpenKey(k, subkey_name) as sk:
                            try:
                                desc = winreg.QueryValueEx(sk, "DriverDesc")[0]
                                output.append(f"  [{subkey_name}] {desc}")
                                if 'nvidia' in desc.lower() or 'quadro' in desc.lower():
                                    output.append(f"    >>> This is the NVIDIA key: {base}\\{subkey_name}")
                                    # List all values in this key
                                    j = 0
                                    while True:
                                        try:
                                            name, val, vtype = winreg.EnumValue(sk, j)
                                            if any(x in name.lower() for x in ['color','range','dynamic','vibrance','depth','output','yuv','rgb','gamma']):
                                                output.append(f"    {name} = {val}")
                                            j += 1
                                        except OSError:
                                            break
                            except OSError:
                                pass
                    except OSError:
                        pass
                i += 1
            except OSError:
                break
except Exception as e:
    output.append(f"Error: {e}")

# The actual fix for washed out colors:
# NVIDIA Control Panel -> Display -> Change Resolution -> 
#   Output color format: RGB
#   Output color depth: 8 bpc
#   Output dynamic range: Full
#
# This can also be set via a specific registry path per-monitor EDID
# Let's find the monitor's EDID key

output.append("\n=== MONITOR EDID KEYS ===")
try:
    mon_base = r"SYSTEM\CurrentControlSet\Enum\DISPLAY"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, mon_base) as k:
        i = 0
        while True:
            try:
                mon_name = winreg.EnumKey(k, i)
                output.append(f"  Monitor: {mon_name}")
                i += 1
            except OSError:
                break
except Exception as e:
    output.append(f"Error: {e}")

with open('c:/Users/prisc/Documents/Athena-Public/tmp_nvidia_color.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print('Written.')
