# === DEPLOY ALL TIER 2 SCHEDULED TASKS ===
Write-Host "=== DEPLOYING TIER 2 SCHEDULED TASKS ==="

$scriptsPath = "C:\Users\prisc\Documents\Athena-Public\scripts"
$pythonPath = "python"

# --- 1. Morning Briefing (6:00 AM daily) ---
$taskName = "AthenaMorningBriefing"
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) { Unregister-ScheduledTask -TaskName $taskName -Confirm:$false }

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptsPath\morning_briefing.py" -WorkingDirectory "C:\Users\prisc\Documents\Athena-Public"
$trigger = New-ScheduledTaskTrigger -Daily -At "6:00AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Athena morning briefing - daily 6 AM Telegram message with supps, alerts, and insights" | Out-Null
Write-Host "[OK] Morning Briefing scheduled (6:00 AM daily)"

# --- 2. Health Watchdog (4 times daily at supplement times) ---
$watchdogTimes = @(
    @{Name = "AthenaWatchdog_Morning_NAC"; Time = "6:25AM"; Desc = "NAC reminder" },
    @{Name = "AthenaWatchdog_Morning_Supps"; Time = "6:55AM"; Desc = "Breakfast supps reminder" },
    @{Name = "AthenaWatchdog_Evening_Fish"; Time = "6:25PM"; Desc = "Evening Fish Oil reminder" },
    @{Name = "AthenaWatchdog_Night_Mag"; Time = "8:55PM"; Desc = "Magnesium reminder" }
)

foreach ($wd in $watchdogTimes) {
    $existing = Get-ScheduledTask -TaskName $wd.Name -ErrorAction SilentlyContinue
    if ($existing) { Unregister-ScheduledTask -TaskName $wd.Name -Confirm:$false }

    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptsPath\health_watchdog.py" -WorkingDirectory "C:\Users\prisc\Documents\Athena-Public"
    $trigger = New-ScheduledTaskTrigger -Daily -At $wd.Time
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

    Register-ScheduledTask -TaskName $wd.Name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Athena Health Watchdog - $($wd.Desc)" | Out-Null
    Write-Host "[OK] $($wd.Name) scheduled ($($wd.Time))"
}

# --- 3. Test morning briefing right now ---
Write-Host ""
Write-Host "=== TESTING MORNING BRIEFING ==="
python "$scriptsPath\morning_briefing.py" 2>&1 | ForEach-Object { Write-Host $_ }

# --- 4. List all Athena tasks ---
Write-Host ""
Write-Host "=== ALL ATHENA SCHEDULED TASKS ==="
Get-ScheduledTask | Where-Object { $_.TaskName -match 'Athena' } | Select-Object TaskName, State | Format-Table -AutoSize

Write-Host ""
Write-Host "=== DEPLOYMENT COMPLETE ==="
