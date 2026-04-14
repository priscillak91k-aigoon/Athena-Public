# Disable startup items via StartupApproved registry
# This is what Task Manager reads/writes when you disable startup items

$approvedPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
$approvedPathLM = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"

# The disabled value is a byte array starting with 03 (disabled) vs 02 (enabled)
$disabledValue = [byte[]](0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

Write-Host "=== DISABLING STARTUP ITEMS ===" -ForegroundColor Yellow

# Items to disable
$toDisable = @(
    "MicrosoftEdgeAutoLaunch_571C56BF1A74061710EBB036ABB17796",
    "Adobe Acrobat Synchronizer"
)

foreach ($item in $toDisable) {
    if (Test-Path $approvedPath) {
        $current = Get-ItemProperty $approvedPath -Name $item -ErrorAction SilentlyContinue
        if ($current) {
            Set-ItemProperty -Path $approvedPath -Name $item -Value $disabledValue -Type Binary
            Write-Host "  > Disabled: $item" -ForegroundColor Green
        } else {
            Write-Host "  > Not found in HKCU: $item" -ForegroundColor Gray
        }
    }
}

# Separately handle Ollama — it may be in a different StartupApproved key
# Check all StartupApproved paths
$paths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
)

Write-Host ""
Write-Host "=== SEARCHING ALL STARTUP APPROVED KEYS ===" -ForegroundColor Yellow
foreach ($p in $paths) {
    if (Test-Path $p) {
        $props = Get-ItemProperty $p -ErrorAction SilentlyContinue
        $props.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
            $isDisabled = $false
            if ($_.Value -is [byte[]]) {
                $isDisabled = $_.Value[0] -eq 3
            }
            $status = if ($isDisabled) { "[DISABLED]" } else { "[ENABLED]" }
            Write-Host "  $status $($_.Name) in $p" -ForegroundColor $(if ($isDisabled) { "Gray" } else { "White" })
            
            if ($_.Name -match 'ollama') {
                Set-ItemProperty -Path $p -Name $_.Name -Value $disabledValue -Type Binary
                Write-Host "  > DISABLED Ollama startup entry" -ForegroundColor Green
            }
        }
    }
}

Write-Host ""
Write-Host "=== CURRENT RAM ===" -ForegroundColor Yellow
$free = [math]::Round((Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
$total = [math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
Write-Host "  Free: ${free} GB of ${total} GB total" -ForegroundColor Green

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "NOTE: Ollama startup changes take effect after next reboot." -ForegroundColor Cyan
Write-Host "To use Ollama again, just run: ollama serve  (it stays off at boot)" -ForegroundColor Cyan
