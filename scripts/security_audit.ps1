# ============================================================
# Athena Security Audit Script — Nuclear Deep Dive
# Run as: powershell -ExecutionPolicy Bypass -File security_audit.ps1
# ============================================================

$Report = @()
function Log($section, $data) {
    $script:Report += "`n=== $section ===`n$data"
}

# --- 1. Startup Programs (persistence mechanisms) ---
$startup = Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize | Out-String
Log "STARTUP PROGRAMS" $startup

# --- 2. Scheduled Tasks (non-Microsoft) ---
$tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' -and $_.State -ne 'Disabled' } | Select-Object TaskName, TaskPath, State | Format-Table -AutoSize | Out-String
Log "NON-MICROSOFT SCHEDULED TASKS" $tasks

# --- 3. Services running as SYSTEM or with unusual accounts ---
$services = Get-WmiObject Win32_Service | Where-Object { $_.StartMode -eq 'Auto' -and $_.State -eq 'Running' } | Select-Object Name, DisplayName, StartName, PathName | Format-Table -AutoSize -Wrap | Out-String
Log "AUTO-START RUNNING SERVICES" $services

# --- 4. Installed software ---
$software = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName } | Select-Object DisplayName, DisplayVersion, Publisher | Sort-Object DisplayName | Format-Table -AutoSize | Out-String
Log "INSTALLED SOFTWARE" $software

# --- 5. PowerShell execution policy ---
$execPolicy = Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String
Log "POWERSHELL EXECUTION POLICY" $execPolicy

# --- 6. Credential Guard / Device Guard ---
$devGuard = Get-CimInstance -ClassName Win32_DeviceGuard -Namespace root\Microsoft\Windows\DeviceGuard -ErrorAction SilentlyContinue | Select-Object * | Format-List | Out-String
if (-not $devGuard) { $devGuard = "DeviceGuard WMI class not found" }
Log "DEVICE GUARD / CREDENTIAL GUARD" $devGuard

# --- 7. Secure Boot ---
try {
    $secureBoot = Confirm-SecureBootUEFI
    Log "SECURE BOOT" "Enabled: $secureBoot"
} catch {
    Log "SECURE BOOT" "Could not query (may not be supported or not running as admin)"
}

# --- 8. TPM Status ---
$tpm = Get-Tpm -ErrorAction SilentlyContinue | Select-Object TpmPresent, TpmReady, TpmEnabled, TpmActivated, ManufacturerVersion | Format-List | Out-String
if (-not $tpm) { $tpm = "TPM not found or access denied" }
Log "TPM STATUS" $tpm

# --- 9. Windows Features that should be off ---
$riskyFeatures = @('TelnetClient', 'TFTP', 'SMB1Protocol', 'MicrosoftWindowsPowerShellV2', 'MicrosoftWindowsPowerShellV2Root')
$featureStatus = foreach ($f in $riskyFeatures) {
    $feat = Get-WindowsOptionalFeature -Online -FeatureName $f -ErrorAction SilentlyContinue
    if ($feat) { "$($feat.FeatureName): $($feat.State)" }
}
Log "RISKY OPTIONAL FEATURES" ($featureStatus -join "`n")

# --- 10. DNS configuration ---
$dns = Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object { $_.ServerAddresses } | Select-Object InterfaceAlias, ServerAddresses | Format-Table -AutoSize | Out-String
Log "DNS SERVERS" $dns

# --- 11. Network profiles (Public vs Private) ---
$netProfiles = Get-NetConnectionProfile | Select-Object Name, InterfaceAlias, NetworkCategory | Format-Table -AutoSize | Out-String
Log "NETWORK PROFILES" $netProfiles

# --- 12. Windows Defender Exploit Protection ---
$exploitProt = Get-ProcessMitigation -System -ErrorAction SilentlyContinue | Format-List | Out-String
if (-not $exploitProt) { $exploitProt = "Could not query" }
Log "EXPLOIT PROTECTION (SYSTEM)" $exploitProt

# --- 13. Audit Policy ---
$auditPol = auditpol /get /category:* 2>&1 | Out-String
Log "AUDIT POLICY" $auditPol

# --- 14. Recent failed logins ---
$failedLogins = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 10 -ErrorAction SilentlyContinue | Select-Object TimeCreated, Message | Format-List | Out-String
if (-not $failedLogins) { $failedLogins = "No recent failed login events found (or Security log not accessible)" }
Log "RECENT FAILED LOGINS (last 10)" $failedLogins

# --- 15. Shared folders ---
$shares = Get-SmbShare | Select-Object Name, Path, Description | Format-Table -AutoSize | Out-String
Log "SMB SHARES" $shares

# --- 16. Hosts file check ---
$hosts = Get-Content "$env:SystemRoot\System32\drivers\etc\hosts" -ErrorAction SilentlyContinue | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' }
if ($hosts) { Log "HOSTS FILE (non-comment entries)" ($hosts -join "`n") }
else { Log "HOSTS FILE" "Clean (no custom entries)" }

# --- 17. Credential Manager stored creds ---
$credCount = (cmdkey /list 2>&1 | Select-String "Target:").Count
Log "STORED CREDENTIALS (Credential Manager)" "Total stored credentials: $credCount"

# --- 18. Remote assistance ---
$remoteAssist = Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance' -Name fAllowToGetHelp -ErrorAction SilentlyContinue
Log "REMOTE ASSISTANCE" "Enabled: $(if ($remoteAssist.fAllowToGetHelp -eq 1) {'YES - VULNERABLE'} else {'No (Good)'})"

# --- 19. Windows Recall feature ---
$recall = Get-AppxPackage -Name '*Recall*' -ErrorAction SilentlyContinue
Log "WINDOWS RECALL" $(if ($recall) { "INSTALLED - Review privacy implications" } else { "Not installed (Good)" })

# --- 20. Browser extensions check (Edge) ---
$edgeExtPath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Extensions"
if (Test-Path $edgeExtPath) {
    $edgeExts = (Get-ChildItem $edgeExtPath -Directory -ErrorAction SilentlyContinue).Count
    Log "EDGE EXTENSIONS" "Found $edgeExts extension directories at $edgeExtPath"
} else {
    Log "EDGE EXTENSIONS" "Default Edge profile not found"
}

# --- OUTPUT ---
$outputPath = "C:\Users\prisc\Documents\Athena-Public\scripts\security_audit_results.txt"
$Report | Out-File $outputPath -Encoding UTF8
Write-Host "=== AUDIT COMPLETE ==="
Write-Host "Results saved to: $outputPath"
Write-Host ($Report -join "")
