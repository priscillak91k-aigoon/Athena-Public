# update_and_start_ark.ps1
# Automates ARK: Survival Ascended Server Update and Launch

$STEAMCMD_PATH = "C:\SteamCMD\steamcmd.exe"
$SERVER_DIR = "C:\ASA_MASTER"
$APP_ID = "2430930"

Write-Host "--- ARK AUTO-UPDATE PROTOCOL ACTIVE ---" -ForegroundColor Cyan

# 1. Update Check
Write-Host "[1/2] Checking for server updates via SteamCMD..." -ForegroundColor Yellow
& $STEAMCMD_PATH +force_install_dir $SERVER_DIR +login anonymous +app_update $APP_ID validate +quit

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ SteamCMD reported an error (Exit Code: $LASTEXITCODE). Attempting to boot anyway..." -ForegroundColor Red
} else {
    Write-Host "✅ Update check complete." -ForegroundColor Green
}

# 2. Launch Server
Write-Host "[2/2] Booting Parker's World on TheCenter_WP..." -ForegroundColor Cyan

# We write a deterministic batch file on the fly to bypass ANY powershell quoting string corruption
$BAT_FILE = "$SERVER_DIR\ShooterGame\Binaries\Win64\_launch_game.bat"

$BAT_CONTENT = @"
@echo off
title ASA Server Boot
start "ASA Server" "C:\ASA_MASTER\ShooterGame\Binaries\Win64\ArkAscendedServer.exe" "TheCenter_WP?listen?SessionName=Parker's World?ServerAdminPassword=Quinny1540?ServerPassword=15405?RCONPort=27020" -server -log -nosteamclient -game -crossplay -PublicIPForEpic=203.211.82.104 -port=7777 -peerport=7778
"@

Set-Content -Path $BAT_FILE -Value $BAT_CONTENT
Start-Process -FilePath $BAT_FILE -WorkingDirectory "$SERVER_DIR\ShooterGame\Binaries\Win64"


Write-Host "🚀 Server process launched in background." -ForegroundColor Green
