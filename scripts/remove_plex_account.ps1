# Disable and remove the plex local account
try {
    # First disable it
    Disable-LocalUser -Name "plex" -ErrorAction Stop
    Write-Host "[OK] plex account disabled"
    
    # Then remove it entirely
    Remove-LocalUser -Name "plex" -ErrorAction Stop
    Write-Host "[OK] plex account removed"
}
catch {
    Write-Host "[FAIL] $($_.Exception.Message)"
}

# Verify
$check = Get-LocalUser -Name "plex" -ErrorAction SilentlyContinue
if ($check) { Write-Host "[WARN] plex account still exists: Enabled=$($check.Enabled)" }
else { Write-Host "[CONFIRMED] plex account no longer exists" }
