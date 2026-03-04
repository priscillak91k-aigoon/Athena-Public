# Test dreaming v2 and update scheduled task
Write-Host "=== TESTING ATHENA DREAMING v2 ==="

# Run the upgraded dreaming script
python "C:\Users\prisc\Documents\Athena-Public\scripts\athena_dreaming.py" 2>&1 | ForEach-Object { Write-Host $_ }

# Update scheduled task to check more frequently (every 4 hours)
Write-Host ""
Write-Host "=== UPDATING SCHEDULED TASK ==="
$taskName = "AthenaDreaming"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "  Removed old task"
}

$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\prisc\Documents\Athena-Public\scripts\athena_dreaming.py" -WorkingDirectory "C:\Users\prisc\Documents\Athena-Public"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 4)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Athena AI v2 - self-applying dreams with Telegram alerts (every 4 hours)" | Out-Null
Write-Host "[OK] Scheduled task updated (every 4 hours, runs even offline)"

Write-Host ""
Write-Host "=== TEST COMPLETE ==="
