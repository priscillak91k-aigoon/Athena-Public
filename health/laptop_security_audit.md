# 🔒 Nuclear Security Audit — Priscilla's Laptop

> **Date**: 2026-03-04 | **OS**: Windows 11 Pro Build 26200  
> **BIOS**: American Megatrends E17E2IWS.116 (May 2020)  
> **Auditor**: Athena Session 29

---

## 🚨 CRITICAL FINDINGS (Fix Immediately)

### 1. ⛔ BitLocker is OFF — Your Entire Drive is Unencrypted
- **Status**: `FullyDecrypted`, Protection: `Off`
- **Risk**: If this laptop is lost or stolen, anyone can pull the drive and read **everything** — DNA data, .env files with API keys, health records, all of it.
- **Fix**: Enable BitLocker with TPM (your TPM 2.0 is present and ready). This is a one-click operation in Settings.
- **Severity**: 🔴 CRITICAL — This is the #1 finding.

### 2. ⛔ `plex` Account Has No Password
- **Status**: `PasswordRequired: False`, last login 2026-02-07
- **Risk**: Anyone with physical access can log in as `plex` with no friction. If `plex` has admin rights, they own the machine.
- **Fix**: Set a strong password on the `plex` account, or disable it if unused.
- **Severity**: 🔴 CRITICAL

### 3. ⛔ No Full Defender Scan Has EVER Been Run
- **Status**: `FullScanAge: 4294967295` (maxint = never)
- **Risk**: If malware entered before Defender was active, it's been here undetected.
- **Fix**: Run a full scan immediately.
- **Severity**: 🔴 CRITICAL

### 4. ⛔ Last Security Update: November 2025 (3+ months ago)
- **Latest hotfix**: KB5077371 (Feb 2026) is a general update, but last **security** update is KB5068861 from Nov 2025.
- **Risk**: 3 months of unpatched vulnerabilities. Known exploits may exist.
- **Fix**: Windows Update immediately + enable automatic security updates.
- **Severity**: 🔴 CRITICAL

---

## 🟠 HIGH PRIORITY FINDINGS

### 5. McAfee Security Scan Plus is Installed
- **Risk**: McAfee SSP is bloatware that conflicts with Windows Defender. It installs via Java/Adobe bundling. It's also modifying your hosts file (`0.0.0.1 mssplus.mcafee.com`).
- **Fix**: Uninstall McAfee Security Scan Plus completely. You already have Defender (which is better).
- **Severity**: 🟠 HIGH

### 6. Remote Assistance is Enabled
- **Status**: `fAllowToGetHelp = 1`
- **Risk**: Allows remote users to connect and view/control your screen if you accept an invitation. Attack vector for social engineering.
- **Fix**: Disable Remote Assistance in System Properties → Remote.
- **Severity**: 🟠 HIGH

### 7. Windows Defender Advanced Features Are All OFF
| Feature | Status | Should Be |
|---------|--------|-----------|
| Cloud Block Level | 0 (Default) | 2 (High) or 4 (High+) |
| PUA Protection | 0 (Off) | 1 (Enabled) |
| Network Protection | 0 (Off) | 1 (Enabled) |
| Attack Surface Reduction Rules | None configured | Should have rules |
- **Risk**: You're running Defender at minimum protection. It's like having a security guard who's asleep.
- **Fix**: Enable all of these via PowerShell (script provided below).
- **Severity**: 🟠 HIGH

### 8. Virtualization-Based Security (VBS) / Credential Guard is OFF
- **Status**: `VirtualizationBasedSecurityStatus: 0`, `SecurityServicesRunning: {0}`
- **Risk**: Without VBS, credential theft attacks (Mimikatz-style) can extract passwords from memory.
- **Fix**: Enable via Group Policy or registry. Your hardware supports it (Secure Boot + TPM present).
- **Severity**: 🟠 HIGH

### 9. 31 Stored Credentials in Credential Manager
- **Risk**: Each stored credential is a target. If malware gets user-level access, it can dump all of these.
- **Fix**: Audit and remove any you don't actively need. Use a proper password manager (Bitwarden, 1Password) instead.
- **Severity**: 🟠 HIGH

### 10. Print Spooler is Running
- **Service**: `Spooler` — auto-start, running as LocalSystem
- **Risk**: PrintNightmare (CVE-2021-34527) used the Print Spooler for remote code execution. If you don't print, disable it.
- **Fix**: Disable the Print Spooler service if no printer is connected.
- **Severity**: 🟠 HIGH

---

## 🟡 MEDIUM PRIORITY FINDINGS

### 11. UAC is at Default Level (Not Maximum)
- **Status**: `ConsentPromptBehaviorAdmin: 5` (Prompt only for non-Windows binaries)
- **Better**: Set to `2` (Always prompt, even for Windows binaries) + require Ctrl+Alt+Del for credential entry.
- **Severity**: 🟡 MEDIUM

### 12. PowerShell Execution Policy is Undefined
- **Status**: All scopes `Undefined` (defaults to `Restricted` but easily bypassed)
- **Risk**: Any script can run with `-ExecutionPolicy Bypass`. This is a weak control but worth setting.
- **Fix**: Set `LocalMachine` to `RemoteSigned` as a baseline.
- **Severity**: 🟡 MEDIUM

### 13. PowerShell v2 Status Unknown
- The audit didn't find `MicrosoftWindowsPowerShellV2` in optional features, but it should be explicitly confirmed disabled. PSv2 bypasses modern logging/AMSI.
- **Severity**: 🟡 MEDIUM

### 14. Surfshark VPN Installed (Good) — But Verify Kill Switch
- Surfshark is present. Verify the **kill switch** is enabled so traffic doesn't leak if VPN drops.
- **Severity**: 🟡 MEDIUM

### 15. NVIDIA Telemetry Client Running
- **Service**: `NVIDIA Telemetry Client 19.5.6.0` — sends hardware/usage data to NVIDIA.
- **Fix**: Disable via NVIDIA App settings or services panel.
- **Severity**: 🟡 MEDIUM

### 16. Samsung Mobile Connectivity Services (x2) Running
- Two services running as LocalSystem. Unless you actively connect a Samsung phone, disable these.
- **Severity**: 🟡 LOW-MEDIUM

### 17. Wi-Fi Network Set to "Public" Profile
- **Current**: `Simply the Breast 2.4 3` → `Public`
- **Note**: Public is actually **more restrictive** (blocks discovery/sharing). This is correct for a home network if you don't need file sharing. If it's your own network, `Private` + firewall rules is better practice.
- **Severity**: 🟡 INFO

---

## ✅ THINGS THAT ARE ALREADY GOOD

| Check | Status |
|-------|--------|
| Windows Defender Real-Time Protection | ✅ Active |
| All Firewall Profiles (Domain/Private/Public) | ✅ Enabled |
| SMBv1 Protocol | ✅ Disabled |
| Telnet Client | ✅ Disabled |
| TFTP Client | ✅ Disabled |
| Remote Desktop (RDP) | ✅ Disabled |
| Secure Boot | ✅ Enabled |
| TPM 2.0 | ✅ Present, Ready, Activated |
| DNS | ✅ Quad9 (9.9.9.9) on Ethernet, Cloudflare (1.1.1.1) on Wi-Fi |
| Windows Recall | ✅ Not installed |
| Auto-Login | ✅ Not configured |
| No custom SMB shares | ✅ Only default admin shares |
| Defender signatures | ✅ Updated today |
| `prisc` account | ✅ Has password set |
| Surfshark VPN | ✅ Installed |

---

## 🔧 HARDENING SCRIPT

The following script will fix the items I can safely automate. **Items requiring manual action** (BitLocker, McAfee uninstall, credential audit) are listed separately below.

Save as `scripts/security_harden.ps1` and run as **Administrator**:

```powershell
# === ATHENA SECURITY HARDENING SCRIPT ===
# Run as Administrator

# 1. Enable PUA Protection
Set-MpPreference -PUAProtection 1
Write-Host "[OK] PUA Protection enabled"

# 2. Set Cloud Block Level to High+
Set-MpPreference -CloudBlockLevel 4
Set-MpPreference -MAPSReporting 2
Write-Host "[OK] Cloud Block Level set to High+"

# 3. Enable Network Protection
Set-MpPreference -EnableNetworkProtection 1
Write-Host "[OK] Network Protection enabled"

# 4. Enable Attack Surface Reduction Rules (CIS recommended set)
$rules = @(
    "BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550",  # Block executable content from email
    "D4F940AB-401B-4EFC-AADC-AD5F3C50688A",  # Block Office apps from creating child processes
    "3B576869-A4EC-4529-8536-B80A7769E899",  # Block Office apps from creating executable content
    "75668C1F-73B5-4CF0-BB93-3ECF5CB7CC84",  # Block Office apps from injecting into other processes
    "D3E037E1-3EB8-44C8-A917-57927947596D",  # Block JavaScript/VBScript from launching downloaded content
    "5BEB7EFE-FD9A-4556-801D-275E5FFC04CC",  # Block execution of potentially obfuscated scripts
    "92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B",  # Block Win32 API calls from Office macros
    "01443614-CD74-433A-B99E-2ECDC07BFC25",  # Block executable files from running unless they meet criteria
    "C1DB55AB-C21A-4637-BB3F-A12568109D35",  # Block use of copied or impersonated system tools
    "9E6C4E1F-7D60-472F-BA1A-A39EF669E4B2",  # Block credential stealing from LSASS
    "D1E49AAC-8F56-4280-B9BA-993A6D77406C",  # Block process creations from PSExec and WMI
    "B2B3F03D-6A65-4F7B-A9C7-1C7EF74A9BA4",  # Block untrusted/unsigned processes from USB
    "26190899-1602-49E8-8B27-EB1D0A1CE869",  # Block Office comm apps from creating child processes
    "7674BA52-37EB-4A4F-A9A1-F0F9A1619A2C",  # Block Adobe Reader from creating child processes
    "E6DB77E5-3DF2-4CF1-B95A-636979351E5B"   # Block persistence through WMI event subscription
)
$actions = @(1) * $rules.Count  # 1 = Block
Add-MpPreference -AttackSurfaceReductionRules_Ids $rules -AttackSurfaceReductionRules_Actions $actions
Write-Host "[OK] Attack Surface Reduction rules configured"

# 5. Disable Remote Assistance
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Remote Assistance' -Name fAllowToGetHelp -Value 0
Write-Host "[OK] Remote Assistance disabled"

# 6. Disable Print Spooler (if no printer needed)
Stop-Service -Name Spooler -Force -ErrorAction SilentlyContinue
Set-Service -Name Spooler -StartupType Disabled
Write-Host "[OK] Print Spooler disabled"

# 7. Disable NVIDIA Telemetry
$nvTelemetry = Get-Service -Name 'NvTelemetryContainer' -ErrorAction SilentlyContinue
if ($nvTelemetry) {
    Stop-Service -Name 'NvTelemetryContainer' -Force -ErrorAction SilentlyContinue
    Set-Service -Name 'NvTelemetryContainer' -StartupType Disabled
    Write-Host "[OK] NVIDIA Telemetry disabled"
} else {
    Write-Host "[SKIP] NVIDIA Telemetry service not found"
}

# 8. Disable Samsung services
$samsung = @('ss_conn_service', 'ss_conn_service2')
foreach ($s in $samsung) {
    $svc = Get-Service -Name $s -ErrorAction SilentlyContinue
    if ($svc) {
        Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
        Set-Service -Name $s -StartupType Disabled
        Write-Host "[OK] Disabled $s"
    }
}

# 9. Raise UAC to maximum
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name ConsentPromptBehaviorAdmin -Value 2
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System' -Name PromptOnSecureDesktop -Value 1
Write-Host "[OK] UAC raised to maximum"

# 10. Set PowerShell execution policy
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
Write-Host "[OK] PowerShell execution policy set to RemoteSigned"

# 11. Disable PowerShell v2 (if enabled)
$psv2 = Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root -ErrorAction SilentlyContinue
if ($psv2 -and $psv2.State -eq 'Enabled') {
    Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root -NoRestart
    Write-Host "[OK] PowerShell v2 disabled"
} else {
    Write-Host "[SKIP] PowerShell v2 already disabled or not found"
}

# 12. Enable DNS over HTTPS for both adapters
# (Quad9 already supports DoH)
Write-Host "[INFO] DNS over HTTPS should be enabled in Settings > Network > Ethernet/Wi-Fi > DNS"

# 13. Start a full Defender scan
Start-MpScan -ScanType FullScan
Write-Host "[RUNNING] Full Defender scan started (runs in background)"

Write-Host "`n=== HARDENING COMPLETE ==="
Write-Host "Manual steps still required:"
Write-Host "  1. Enable BitLocker (Settings > Privacy & Security > Device Encryption)"
Write-Host "  2. Uninstall McAfee Security Scan Plus (Settings > Apps)"
Write-Host "  3. Set password on 'plex' account (Settings > Accounts)"
Write-Host "  4. Audit Credential Manager (Control Panel > Credential Manager)"
Write-Host "  5. Run Windows Update (Settings > Windows Update)"
Write-Host "  6. Enable VBS (Settings > Privacy & Security > Core Isolation > Memory Integrity)"
Write-Host "  7. Verify Surfshark kill switch is ON"
```

---

## 📋 MANUAL ACTION ITEMS

These require GUI interaction or explicit decisions:

- [ ] **Enable BitLocker** — Settings → Privacy & Security → Device Encryption → Turn on
- [ ] **Set password on `plex` account** — or disable the account entirely
- [ ] **Uninstall McAfee Security Scan Plus** — Settings → Apps → Installed apps → McAfee → Uninstall
- [ ] **Run Windows Update** — Settings → Windows Update → Check for updates
- [ ] **Enable Core Isolation / Memory Integrity** — Settings → Privacy & Security → Core Isolation → Toggle ON
- [ ] **Audit Credential Manager** — Control Panel → Credential Manager → Remove stale entries
- [ ] **Verify Surfshark kill switch** — Surfshark app → Settings → Kill Switch → ON
- [ ] **Enable DNS over HTTPS** — Settings → Network → Ethernet → DNS → toggle DoH for 9.9.9.9

---

*Audit script: `scripts/security_audit.ps1` | Results: `scripts/security_audit_results.txt`*
