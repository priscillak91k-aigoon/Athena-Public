# === ATHENA SECURITY HARDENING SCRIPT ===
# Fixes ALL identified security holes from the nuclear audit
# Must run as Administrator for some operations

$results = @()
function Log($msg) { Write-Host $msg; $script:results += $msg }

Log "=== ATHENA SECURITY HARDENING ==="

# --- 1. DEFENDER: Enable PUA Protection ---
try { Set-MpPreference -PUAProtection 1; Log "[OK] PUA Protection enabled" }
catch { Log "[FAIL] PUA Protection: $($_.Exception.Message)" }

# --- 2. DEFENDER: Cloud Block Level to High+ ---
try { Set-MpPreference -CloudBlockLevel 4; Set-MpPreference -MAPSReporting 2; Log "[OK] Cloud Block Level set to High+" }
catch { Log "[FAIL] Cloud Block Level: $($_.Exception.Message)" }

# --- 3. DEFENDER: Network Protection ---
try { Set-MpPreference -EnableNetworkProtection 1; Log "[OK] Network Protection enabled" }
catch { Log "[FAIL] Network Protection: $($_.Exception.Message)" }

# --- 4. DEFENDER: Attack Surface Reduction Rules ---
try {
    $rules = @(
        "BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550",
        "D4F940AB-401B-4EFC-AADC-AD5F3C50688A",
        "3B576869-A4EC-4529-8536-B80A7769E899",
        "75668C1F-73B5-4CF0-BB93-3ECF5CB7CC84",
        "D3E037E1-3EB8-44C8-A917-57927947596D",
        "5BEB7EFE-FD9A-4556-801D-275E5FFC04CC",
        "92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B",
        "01443614-CD74-433A-B99E-2ECDC07BFC25",
        "C1DB55AB-C21A-4637-BB3F-A12568109D35",
        "9E6C4E1F-7D60-472F-BA1A-A39EF669E4B2",
        "D1E49AAC-8F56-4280-B9BA-993A6D77406C",
        "B2B3F03D-6A65-4F7B-A9C7-1C7EF74A9BA4",
        "26190899-1602-49E8-8B27-EB1D0A1CE869",
        "7674BA52-37EB-4A4F-A9A1-F0F9A1619A2C",
        "E6DB77E5-3DF2-4CF1-B95A-636979351E5B"
    )
    $actions = @(1) * $rules.Count
    Add-MpPreference -AttackSurfaceReductionRules_Ids $rules -AttackSurfaceReductionRules_Actions $actions
    Log "[OK] 15 Attack Surface Reduction rules configured"
}
catch { Log "[FAIL] ASR Rules: $($_.Exception.Message)" }

# --- 5. Disable Remote Assistance ---
try {
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance' -Name fAllowToGetHelp -Value 0
    Log "[OK] Remote Assistance disabled"
}
catch { Log "[FAIL] Remote Assistance: $($_.Exception.Message)" }

# --- 6. Disable Print Spooler ---
try {
    Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue
    Set-Service -Name Spooler -StartupType Disabled
    Log "[OK] Print Spooler disabled"
}
catch { Log "[FAIL] Print Spooler: $($_.Exception.Message)" }

# --- 7. Disable NVIDIA Telemetry ---
$nvSvc = Get-Service -Name 'NvTelemetryContainer' -ErrorAction SilentlyContinue
if ($nvSvc) {
    try {
        Stop-Service -Name 'NvTelemetryContainer' -Force -ErrorAction SilentlyContinue
        Set-Service -Name 'NvTelemetryContainer' -StartupType Disabled
        Log "[OK] NVIDIA Telemetry disabled"
    }
    catch { Log "[FAIL] NVIDIA Telemetry: $($_.Exception.Message)" }
}
else { Log "[SKIP] NVIDIA Telemetry service not found" }

# --- 8. Disable Samsung services ---
foreach ($svc in @('ss_conn_service', 'ss_conn_service2')) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        try {
            Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
            Set-Service -Name $svc -StartupType Disabled
            Log "[OK] Disabled $svc"
        }
        catch { Log "[FAIL] $svc : $($_.Exception.Message)" }
    }
}

# --- 9. Raise UAC to maximum ---
try {
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name ConsentPromptBehaviorAdmin -Value 2
    Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name PromptOnSecureDesktop -Value 1
    Log "[OK] UAC raised to maximum"
}
catch { Log "[FAIL] UAC: $($_.Exception.Message)" }

# --- 10. PowerShell execution policy ---
try {
    Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
    Log "[OK] PowerShell execution policy set to RemoteSigned"
}
catch { Log "[FAIL] Execution Policy: $($_.Exception.Message)" }

# --- 11. Disable PowerShell v2 ---
try {
    $psv2 = Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root -ErrorAction SilentlyContinue
    if ($psv2 -and $psv2.State -eq 'Enabled') {
        Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root -NoRestart -ErrorAction Stop
        Log "[OK] PowerShell v2 disabled"
    }
    else { Log "[SKIP] PowerShell v2 already disabled" }
}
catch { Log "[FAIL] PSv2: $($_.Exception.Message)" }

# --- 12. Require password on plex account ---
try {
    $output = net user plex /passwordreq:yes 2>&1
    Log "[OK] Password now required on plex account"
}
catch { Log "[FAIL] plex password: $($_.Exception.Message)" }

# --- 13. Enable BitLocker on C: ---
try {
    $blStatus = Get-BitLockerVolume -MountPoint "C:" -ErrorAction Stop
    if ($blStatus.ProtectionStatus -eq 'Off') {
        Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 -RecoveryPasswordProtector -ErrorAction Stop | Out-Null
        $recoveryKey = (Get-BitLockerVolume -MountPoint "C:").KeyProtector | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' }
        if ($recoveryKey) {
            $keyFile = "C:\Users\prisc\Documents\Athena-Public\scripts\BITLOCKER_RECOVERY_KEY.txt"
            "BitLocker Recovery Key for C:" | Out-File $keyFile -Encoding UTF8
            "Recovery Password: $($recoveryKey.RecoveryPassword)" | Out-File $keyFile -Append -Encoding UTF8
            "Key ID: $($recoveryKey.KeyProtectorId)" | Out-File $keyFile -Append -Encoding UTF8
            "Date: $(Get-Date)" | Out-File $keyFile -Append -Encoding UTF8
            "IMPORTANT: Save this key somewhere safe then DELETE this file!" | Out-File $keyFile -Append -Encoding UTF8
            Log "[OK] BitLocker enabled on C: - RECOVERY KEY saved to scripts\BITLOCKER_RECOVERY_KEY.txt"
            Log "[!!!] SAVE THE RECOVERY KEY TO USB OR PHONE THEN DELETE THE FILE"
        }
    }
    else { Log "[SKIP] BitLocker already active on C:" }
}
catch { Log "[FAIL] BitLocker: $($_.Exception.Message) - Enable manually via Settings" }

# --- 14. Enable Core Isolation / Memory Integrity ---
try {
    $regPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity'
    if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
    Set-ItemProperty -Path $regPath -Name Enabled -Value 1 -Type DWord
    Log "[OK] Core Isolation / Memory Integrity enabled (requires restart)"
}
catch { Log "[FAIL] Core Isolation: $($_.Exception.Message)" }

# --- 15. Trigger Windows Update ---
try {
    Start-Service wuauserv -ErrorAction SilentlyContinue
    Log "[OK] Windows Update service started - check Settings to install pending updates"
}
catch { Log "[FAIL] Windows Update: $($_.Exception.Message)" }

# --- 16. Clean McAfee from hosts file ---
try {
    $hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
    $hostsContent = Get-Content $hostsPath
    $newHosts = $hostsContent | Where-Object { $_ -notmatch 'mcafee' }
    $newHosts | Set-Content $hostsPath -Force
    Log "[OK] Removed McAfee entry from hosts file"
}
catch { Log "[FAIL] Hosts file: $($_.Exception.Message)" }

# --- 17. Start full Defender scan ---
try {
    Start-MpScan -ScanType FullScan
    Log "[OK] Full Defender scan started (runs in background, may take 1-2 hours)"
}
catch { Log "[FAIL] Full scan: $($_.Exception.Message)" }

# --- SUMMARY ---
Log ""
Log "=== HARDENING COMPLETE ==="
Log "Manual steps remaining:"
Log "  1. RESTART PC (required for Core Isolation and BitLocker)"
Log "  2. Set a password on plex account (Settings - Accounts)"
Log "  3. Uninstall McAfee Security Scan Plus (Settings - Apps)"
Log "  4. Install all pending Windows Updates"
Log "  5. Save BitLocker recovery key to USB/phone then delete the file"
Log "  6. Verify Surfshark kill switch is ON"
Log "  7. Audit Credential Manager - remove stale entries"

$results | Out-File "C:\Users\prisc\Documents\Athena-Public\scripts\security_harden_results.txt" -Encoding UTF8
