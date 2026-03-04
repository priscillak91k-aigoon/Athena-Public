# === MCAFEE COMPLETE REMOVAL SCRIPT ===
# Removes McAfee Security Scan Plus and all traces

$results = @()
function Log($msg) { Write-Host $msg; $script:results += $msg }

Log "=== MCAFEE PURGE ==="

# --- 1. Uninstall via registry (find uninstall string) ---
$mcafeeEntries = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match 'McAfee' }

foreach ($entry in $mcafeeEntries) {
    Log "Found: $($entry.DisplayName)"
    $uninstallString = $entry.UninstallString
    if ($uninstallString) {
        Log "  Uninstall string: $uninstallString"
        try {
            if ($uninstallString -match 'msiexec') {
                $productCode = $uninstallString -replace '.*(\{[A-F0-9-]+\}).*', '$1'
                $proc = Start-Process msiexec.exe -ArgumentList "/x $productCode /qn /norestart" -Wait -PassThru -ErrorAction Stop
                Log "  [OK] MSI uninstall exit code: $($proc.ExitCode)"
            }
            else {
                $proc = Start-Process cmd.exe -ArgumentList "/c `"$uninstallString`" /quiet /norestart" -Wait -PassThru -ErrorAction Stop
                Log "  [OK] Uninstall exit code: $($proc.ExitCode)"
            }
        }
        catch { Log "  [FAIL] Uninstall: $($_.Exception.Message)" }
    }
}

if (-not $mcafeeEntries) { Log "[INFO] No McAfee entries found in Add/Remove Programs" }

# --- 2. Kill any McAfee processes ---
$mcafeeProcs = Get-Process -Name '*mcafee*', '*mssces*', '*sssche*' -ErrorAction SilentlyContinue
foreach ($proc in $mcafeeProcs) {
    try {
        Stop-Process -Id $proc.Id -Force
        Log "[OK] Killed process: $($proc.ProcessName) (PID $($proc.Id))"
    }
    catch { Log "[FAIL] Kill process: $($_.Exception.Message)" }
}

# --- 3. Remove McAfee scheduled tasks ---
$mcafeeTasks = Get-ScheduledTask | Where-Object { $_.TaskName -match 'McAfee|McUpdater|SecurityScanner' }
foreach ($task in $mcafeeTasks) {
    try {
        Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false
        Log "[OK] Removed scheduled task: $($task.TaskName)"
    }
    catch { Log "[FAIL] Task removal: $($_.Exception.Message)" }
}

# --- 4. Remove McAfee services ---
$mcafeeServices = Get-Service -Name '*mcafee*' -ErrorAction SilentlyContinue
foreach ($svc in $mcafeeServices) {
    try {
        Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
        sc.exe delete $svc.Name 2>&1 | Out-Null
        Log "[OK] Removed service: $($svc.Name)"
    }
    catch { Log "[FAIL] Service removal: $($_.Exception.Message)" }
}

# --- 5. Remove McAfee folders ---
$mcafeePaths = @(
    "$env:ProgramFiles\McAfee",
    "$env:ProgramFiles\McAfee Security Scan",
    "${env:ProgramFiles(x86)}\McAfee",
    "${env:ProgramFiles(x86)}\McAfee Security Scan",
    "$env:ProgramData\McAfee",
    "$env:ProgramData\McAfee Security Scan",
    "$env:LOCALAPPDATA\McAfee",
    "$env:APPDATA\McAfee",
    "$env:CommonProgramFiles\McAfee",
    "${env:CommonProgramFiles(x86)}\McAfee"
)

foreach ($path in $mcafeePaths) {
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            Log "[OK] Removed folder: $path"
        }
        catch { Log "[FAIL] Remove folder $path : $($_.Exception.Message)" }
    }
}

# --- 6. Remove McAfee startup entries ---
$startupPaths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
)

foreach ($regPath in $startupPaths) {
    if (Test-Path $regPath) {
        $props = Get-ItemProperty -Path $regPath -ErrorAction SilentlyContinue
        $props.PSObject.Properties | Where-Object { $_.Value -match 'McAfee' } | ForEach-Object {
            try {
                Remove-ItemProperty -Path $regPath -Name $_.Name -Force
                Log "[OK] Removed startup entry: $($_.Name) from $regPath"
            }
            catch { Log "[FAIL] Startup removal: $($_.Exception.Message)" }
        }
    }
}

# --- 7. Clean McAfee registry keys ---
$mcafeeRegKeys = @(
    'HKLM:\Software\McAfee',
    'HKLM:\Software\WOW6432Node\McAfee',
    'HKCU:\Software\McAfee'
)

foreach ($key in $mcafeeRegKeys) {
    if (Test-Path $key) {
        try {
            Remove-Item -Path $key -Recurse -Force -ErrorAction Stop
            Log "[OK] Removed registry key: $key"
        }
        catch { Log "[FAIL] Registry removal $key : $($_.Exception.Message)" }
    }
}

# --- 8. Verify ---
Log ""
Log "=== VERIFICATION ==="
$remainingInstall = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match 'McAfee' }
if ($remainingInstall) { Log "[WARN] McAfee still in installed programs: $($remainingInstall.DisplayName)" }
else { Log "[CONFIRMED] McAfee not found in installed programs" }

$remainingFolders = $mcafeePaths | Where-Object { Test-Path $_ }
if ($remainingFolders) { Log "[WARN] Remaining folders: $($remainingFolders -join ', ')" }
else { Log "[CONFIRMED] No McAfee folders remain" }

$remainingTasks = Get-ScheduledTask | Where-Object { $_.TaskName -match 'McAfee|McUpdater|SecurityScanner' }
if ($remainingTasks) { Log "[WARN] Remaining tasks: $($remainingTasks.TaskName -join ', ')" }
else { Log "[CONFIRMED] No McAfee scheduled tasks remain" }

Log ""
Log "=== MCAFEE PURGE COMPLETE ==="

$results | Out-File "C:\Users\prisc\Documents\Athena-Public\scripts\mcafee_removal_results.txt" -Encoding UTF8
