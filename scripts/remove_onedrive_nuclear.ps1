# Nuclear OneDrive Extraction Script
# Lobotto Framework | Safe Data Migration Protocol

$ErrorActionPreference = "Stop"

function Log($msg, $color="White") {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $msg" -ForegroundColor $color
}

Log "--- NUCLEAR ONEDRIVE EXTRACTION START ---" "Cyan"

# 1. IDENTIFY PATHS
$userProfile = [System.Environment]::GetFolderPath("UserProfile")
$oneDrivePath = Join-Path $userProfile "OneDrive"
$localDesktop = Join-Path $userProfile "Desktop"
$localDocuments = Join-Path $userProfile "Documents"
$localPictures = Join-Path $userProfile "Pictures"

Log "Mapped OneDrive: $oneDrivePath" "Gray"
Log "Target Desktop:  $localDesktop" "Gray"
Log "Target Documents: $localDocuments" "Gray"

# 2. STATUS CHECK (Online Only files)
if (Test-Path $oneDrivePath) {
    Log "Checking for potential 'Online-Only' files..." "Yellow"
    $onlineFiles = Get-ChildItem -Path $oneDrivePath -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Attributes -match "RecallOnDataAccess" -or $_.Attributes -match "Offline" }
    if ($onlineFiles) {
        Log "WARNING: Found $($onlineFiles.Count) files that may be online-only." "Red"
        Log "These might not move correctly if not downloaded. Proceeding with caution." "Yellow"
    } else {
        Log "No online-only files detected (Hebbian verification passed)." "Green"
    }
}

# 3. KILL ONEDRIVE
Log "Terminating OneDrive processes..." "Yellow"
Stop-Process -Name "OneDrive" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 4. RESTORE REGISTRY SHELL FOLDERS
Log "Updating Registry Shell Folders..." "Yellow"
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
Set-ItemProperty -Path $regPath -Name "Desktop" -Value "%USERPROFILE%\Desktop"
Set-ItemProperty -Path $regPath -Name "Personal" -Value "%USERPROFILE%\Documents"
Set-ItemProperty -Path $regPath -Name "My Pictures" -Value "%USERPROFILE%\Pictures"
# Downloads is usually safe but checking
# Set-ItemProperty -Path $regPath -Name "{374DE290-123F-4565-9164-39C4925E467B}" -Value "%USERPROFILE%\Downloads"

Log "Registry updated. (Reboot/Explorer restart required for full visual effect, but paths are now SOVEREIGN)." "Green"

# 5. DATA MIGRATION
function Migrate-Folder($src, $dest) {
    if (Test-Path $src) {
        if (-not (Test-Path $dest)) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        }
        Log "Migrating $src -> $dest" "Yellow"
        Get-ChildItem -Path $src -Recurse | ForEach-Object {
            $targetPath = $_.FullName.Replace($src, $dest)
            if ($_.PsIsContainer) {
                if (-not (Test-Path $targetPath)) {
                    New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
                }
            } else {
                if (-not (Test-Path $targetPath)) {
                    Move-Item -Path $_.FullName -Destination $targetPath -Force
                } else {
                    Log "  ! Skip: $($_.Name) (exists in target)" "Gray"
                }
            }
        }
    }
}

Migrate-Folder (Join-Path $oneDrivePath "Desktop") $localDesktop
Migrate-Folder (Join-Path $oneDrivePath "Documents") $localDocuments
Migrate-Folder (Join-Path $oneDrivePath "Pictures") $localPictures

# 6. UNINSTALL ONEDRIVE
Log "Uninstalling Microsoft OneDrive app..." "Yellow"
winget uninstall --id "Microsoft.OneDrive" --silent --accept-source-agreements --accept-package-agreements
if ($LASTEXITCODE -eq 0) {
    Log "OneDrive uninstalled successfully." "Green"
} else {
    Log "Winget uninstall failed or app not found. Trying secondary method..." "Gray"
    $onedrive_exe = Join-Path $env:SystemRoot "SysWOW64\OneDriveSetup.exe"
    if (-not (Test-Path $onedrive_exe)) { $onedrive_exe = Join-Path $env:SystemRoot "System32\OneDriveSetup.exe" }
    if (Test-Path $onedrive_exe) {
        Start-Process $onedrive_exe -ArgumentList "/uninstall" -Wait
        Log "Secondary uninstall triggered." "Green"
    }
}

# 7. CLEANUP
Log "Removing remaining OneDrive registry keys..." "Yellow"
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "OneDrive" -ErrorAction SilentlyContinue

Log "--- NUCLEAR EXTRACTION COMPLETE ---" "Cyan"
Log "Restarting Explorer to refresh paths..." "Yellow"
taskkill /f /im explorer.exe
start explorer.exe
