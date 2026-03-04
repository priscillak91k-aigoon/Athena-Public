# === SETUP ATHENA DREAMING ===
# Installs dependencies, tests the script, and creates a Windows scheduled task

Write-Host "=== ATHENA DREAMING SETUP ==="

# 1. Install Python dependencies
Write-Host "[1/3] Installing Python dependencies..."
pip install google-generativeai anthropic python-dotenv 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "[OK] Dependencies installed"

# 2. Test run the dreaming script
Write-Host "[2/3] Running test thinking cycle..."
python "C:\Users\prisc\Documents\Athena-Public\scripts\athena_dreaming.py" 2>&1 | ForEach-Object { Write-Host "  $_" }

# 3. Create Windows Scheduled Task (runs every 6 hours)
Write-Host "[3/3] Creating scheduled task..."
$taskName = "AthenaDreaming"
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "  Removed existing task"
}

$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\prisc\Documents\Athena-Public\scripts\athena_dreaming.py" -WorkingDirectory "C:\Users\prisc\Documents\Athena-Public"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 6)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Athena AI background thinking - reviews and refines brain files every 6 hours" | Out-Null
Write-Host "[OK] Scheduled task 'AthenaDreaming' created (runs every 6 hours)"

Write-Host ""
Write-Host "=== SETUP COMPLETE ==="
Write-Host "The AI will now 'dream' every 6 hours."
Write-Host "Thinking output goes to: .context/thinking_log.md"
Write-Host "This file is loaded at next /start."
