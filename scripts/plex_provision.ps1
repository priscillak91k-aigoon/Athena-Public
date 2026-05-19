<#
.SYNOPSIS
    Automated Plex Media Server Provisioning Script for SJ's NVIDIA AI TOP
.DESCRIPTION
    This script automates the post-format setup of the Plex server environment.
    - Sets power plan to High Performance
    - Downloads and installs the latest Plex Media Server
    - Creates a secure local 'plex' account for security auditing compliance
.NOTES
    Author: Lobotto
    Date: 2026-05-18
#>

Write-Host "🚀 Starting Lobotto Plex Provisioning Protocol..." -ForegroundColor Cyan

# 1. Power Management - Set to High Performance
Write-Host "`n⚡ Step 1: Setting Power Plan to High Performance..." -ForegroundColor Yellow
$HighPerf = powercfg /l | Select-String "High performance"
if ($HighPerf) {
    $guid = ($HighPerf.Line -split '\s+')[3]
    powercfg /s $guid
    Write-Host "✅ Power Plan set to High Performance (prevents PCIe/USB sleep on QNAP)." -ForegroundColor Green
} else {
    Write-Host "⚠️ High Performance plan not found. Duplicating from Balanced..." -ForegroundColor Red
    powercfg -duplicatescheme 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
}

# 2. Download and Install Plex Media Server
Write-Host "`n🎬 Step 2: Downloading and Installing Plex Media Server..." -ForegroundColor Yellow
$PlexUrl = "https://downloads.plex.tv/plex-media-server-new/1.40.2.8395-c67dce28e/windows/PlexMediaServer-1.40.2.8395-c67dce28e-x86_64.exe"
$InstallerPath = "$env:USERPROFILE\Downloads\PlexInstaller.exe"

try {
    Invoke-WebRequest -Uri $PlexUrl -OutFile $InstallerPath -UseBasicParsing
    Write-Host "✅ Download complete. Starting silent installation..." -ForegroundColor Green
    
    # Run installer silently
    $process = Start-Process -FilePath $InstallerPath -ArgumentList "/quiet" -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Plex Media Server installed successfully." -ForegroundColor Green
    } else {
        Write-Host "⚠️ Plex installer exited with code $($process.ExitCode). You may need to run it manually." -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to download Plex. Please install manually." -ForegroundColor Red
}

# 3. Create Secure 'plex' Local Account
Write-Host "`n🔒 Step 3: Securing Local 'plex' Account..." -ForegroundColor Yellow
$Username = "plex"
$PasswordString = "Pl3x!S3cure$((Get-Random -Minimum 1000 -Maximum 9999))"
$Password = ConvertTo-SecureString $PasswordString -AsPlainText -Force

try {
    if (Get-LocalUser -Name $Username -ErrorAction SilentlyContinue) {
        Write-Host "⚠️ Account '$Username' already exists. Updating password..." -ForegroundColor Yellow
        Set-LocalUser -Name $Username -Password $Password
    } else {
        New-LocalUser -Name $Username -Password $Password -FullName "Plex Media Server" -Description "Dedicated Plex Account" | Out-Null
        Add-LocalGroupMember -Group "Users" -Member $Username
    }
    Write-Host "✅ Local account '$Username' secured." -ForegroundColor Green
    Write-Host "🔑 SAVE THIS PASSWORD: $PasswordString" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to create/secure local account. Please run PowerShell as Administrator." -ForegroundColor Red
}

Write-Host "`n🎉 Provisioning Script Complete!" -ForegroundColor Cyan
Write-Host "Next Steps:"
Write-Host "1. Install NVIDIA Studio Drivers manually (for NVENC hardware transcoding)."
Write-Host "2. Connect your QNAP RAID 1 via USB-A."
Write-Host "3. Assign the QNAP to drive P:\ in Disk Management."
Write-Host "4. Launch Plex and configure libraries."
