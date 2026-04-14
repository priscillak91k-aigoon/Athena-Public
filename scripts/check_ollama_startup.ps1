# Check all places Ollama might auto-start
Write-Host "=== SCHEDULED TASKS ===" -ForegroundColor Cyan
Get-ScheduledTask | Where-Object { $_.TaskName -match 'ollama|llama' } | Select-Object TaskName, State | Format-Table -AutoSize

Write-Host "=== STARTUP REGISTRY (HKCU) ===" -ForegroundColor Cyan
$run = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
$run.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' -and ($_.Value -match 'ollama' -or $_.Name -match 'ollama') } | Format-Table Name, Value -AutoSize

Write-Host "=== STARTUP REGISTRY (HKLM) ===" -ForegroundColor Cyan
$runm = Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
$runm.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' -and ($_.Value -match 'ollama' -or $_.Name -match 'ollama') } | Format-Table Name, Value -AutoSize

Write-Host "=== ALL STARTUP REGISTRY (HKCU) ===" -ForegroundColor Yellow
$run.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | Format-Table Name, Value -AutoSize

Write-Host "=== WINDOWS SERVICES ===" -ForegroundColor Cyan
Get-Service | Where-Object { $_.Name -match 'ollama|llama' } | Select-Object Name, Status, StartType | Format-Table -AutoSize

Write-Host "=== RUNNING OLLAMA PROCESSES ===" -ForegroundColor Cyan
Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Format-Table Name, Id, CPU, WorkingSet -AutoSize

Write-Host "Done." -ForegroundColor Green
