# Disable Ollama from auto-starting and kill current process
# Ollama on Windows runs as a user-space tray app, not a service
# It registers via HKCU Run key or the tray launcher

Write-Host "=== KILLING OLLAMA NOW ===" -ForegroundColor Yellow
$procs = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($procs) {
    $ramGB = [math]::Round(($procs | Measure-Object WorkingSet -Sum).Sum / 1GB, 1)
    Stop-Process -Name "ollama" -Force
    Write-Host "  > Killed. Freed ~${ramGB}GB RAM." -ForegroundColor Green
} else {
    Write-Host "  > Ollama not running." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== DISABLING OLLAMA STARTUP ===" -ForegroundColor Yellow

# 1. Check & remove from HKCU Run
$runPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runKey = Get-ItemProperty $runPath -ErrorAction SilentlyContinue
$runKey.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
    Write-Host "  Found: $($_.Name) = $($_.Value)" -ForegroundColor Cyan
    if ($_.Value -match 'ollama') {
        Remove-ItemProperty -Path $runPath -Name $_.Name -Force
        Write-Host "  > Removed '$($_.Name)' from startup" -ForegroundColor Green
    }
}

# 2. Check Task Manager startup (HKCU\...\StartupApproved\Run)
$approvedPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
if (Test-Path $approvedPath) {
    $approved = Get-ItemProperty $approvedPath -ErrorAction SilentlyContinue
    $approved.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
        Write-Host "  Startup Approved: $($_.Name)" -ForegroundColor Cyan
    }
}

# 3. Disable via Task Manager startup list (WMI method)
$startupItems = Get-CimInstance -ClassName Win32_StartupCommand -ErrorAction SilentlyContinue
$startupItems | ForEach-Object {
    Write-Host "  Startup Item: $($_.Name) -> $($_.Command)" -ForegroundColor Cyan
    if ($_.Command -match 'ollama') {
        Write-Host "  > Found Ollama in startup commands!" -ForegroundColor Red
    }
}

# 4. Check Ollama's own startup folder shortcut
$startupFolder = [System.Environment]::GetFolderPath('Startup')
$ollamaShortcut = Get-ChildItem $startupFolder | Where-Object { $_.Name -match 'ollama' }
if ($ollamaShortcut) {
    Remove-Item $ollamaShortcut.FullName -Force
    Write-Host "  > Removed startup shortcut: $($ollamaShortcut.Name)" -ForegroundColor Green
} else {
    Write-Host "  > No startup shortcut found in: $startupFolder" -ForegroundColor Gray
}

# 5. Disable via Ollama's own tray config (it sets a registry key)
$ollamaConfig = "$env:APPDATA\ollama"
if (Test-Path $ollamaConfig) {
    Write-Host "  > Ollama config dir found: $ollamaConfig" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== RECOMMENDATION ===" -ForegroundColor Yellow
Write-Host "  To permanently stop Ollama from auto-starting:" -ForegroundColor White
Write-Host "  1. Open Task Manager (Ctrl+Shift+Esc)" -ForegroundColor White
Write-Host "  2. Go to Startup Apps tab" -ForegroundColor White
Write-Host "  3. Find Ollama -> Right-click -> Disable" -ForegroundColor White
Write-Host ""
Write-Host "Done." -ForegroundColor Green
