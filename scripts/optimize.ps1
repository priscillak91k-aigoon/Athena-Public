# PC optimization script — GFN + speed
# Run as: powershell -ExecutionPolicy Bypass -File scripts\optimize.ps1
# For Admin-required steps (power plan), right-click gfn_boost.bat -> Run as Administrator

param([switch]$Silent)

function Log($msg, $color="White") {
    if (-not $Silent) { Write-Host $msg -ForegroundColor $color }
}

Log "" 
Log "  ==========================================" "Cyan"
Log "   GFN BOOST v1.1  |  Lobotto Framework"     "Cyan"
Log "   Samsung Odyssey  2560x1440 @ 119Hz"        "Cyan"
Log "  ==========================================" "Cyan"
Log ""

# ── PHASE 1: Kill RAM hogs ──────────────────────────────────────────────────
Log "[1/5] Killing RAM hogs..." "Yellow"

# Ollama — holds loaded LLM model in RAM (4-16GB depending on model)
# Top RAM killer on this system. Safe to kill, auto-restarts on next use.
$ollama = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollama) {
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $freed = [math]::Round(($ollama | Measure-Object WorkingSet -Sum).Sum / 1GB, 1)
    Log "  > Ollama killed (freed ~${freed}GB RAM)" "Green"
} else {
    Log "  > Ollama not running" "Gray"
}

# Surfshark — adds latency overhead to GFN stream; kill for gaming
$surf = Get-Process -Name "Surfshark" -ErrorAction SilentlyContinue
if ($surf) {
    Stop-Process -Name "Surfshark" -Force -ErrorAction SilentlyContinue
    Stop-Service -Name "SurfsharkService" -Force -ErrorAction SilentlyContinue
    Log "  > Surfshark killed (lower GFN latency)" "Green"
} else {
    Log "  > Surfshark not running" "Gray"
}

# OneDrive — pause background sync / disk I/O
$od = Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue
if ($od) {
    Stop-Process -Name "OneDrive" -Force -ErrorAction SilentlyContinue
    Log "  > OneDrive paused (stops background disk I/O)" "Green"
} else {
    Log "  > OneDrive not running" "Gray"
}

# SearchIndexer — background disk I/O during gaming
Stop-Process -Name "SearchIndexer" -Force -ErrorAction SilentlyContinue | Out-Null

# Phone Link — no value during gaming
Stop-Process -Name "PhoneExperienceHost" -Force -ErrorAction SilentlyContinue | Out-Null

# Logitech LGHUB — RGB animation chews CPU/RAM
Stop-Process -Name "LGHUB" -Force -ErrorAction SilentlyContinue | Out-Null
Stop-Process -Name "LGHUBUpdater" -Force -ErrorAction SilentlyContinue | Out-Null

# Adobe background sync
Stop-Process -Name "armsvc" -Force -ErrorAction SilentlyContinue | Out-Null
Stop-Process -Name "AdobeUpdateService" -Force -ErrorAction SilentlyContinue | Out-Null

# Check RAM after kills
Start-Sleep -Seconds 1
$freeMB = [math]::Round((Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
Log "  > RAM free now: ${freeMB} GB" "Green"
Log ""

# ── PHASE 2: Power plan ─────────────────────────────────────────────────────
Log "[2/5] Setting power plan..." "Yellow"
# Try Ultimate Performance first, fall back to High Performance
$ultimate = "e9a42b02-d5df-448d-aa00-03f14749eb61"
$highperf = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
$result = powercfg /setactive $ultimate 2>&1
if ($LASTEXITCODE -eq 0) {
    Log "  > Ultimate Performance plan activated" "Green"
} else {
    powercfg /setactive $highperf 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Log "  > High Performance plan activated" "Green"
    } else {
        Log "  > Could not set power plan (run as Admin)" "Red"
    }
}
# Prevent CPU throttling
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMIN 100 2>&1 | Out-Null
powercfg /setactive SCHEME_CURRENT 2>&1 | Out-Null
Log "  > CPU min frequency: 100% (no throttle)" "Green"
Log ""

# ── PHASE 3: Display config check ───────────────────────────────────────────
Log "[3/5] Display check..." "Yellow"
$gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.CurrentHorizontalResolution -gt 0 } | Select-Object -First 1
if ($gpu) {
    Log "  > Display: $($gpu.CurrentHorizontalResolution)x$($gpu.CurrentVerticalResolution) @ $($gpu.CurrentRefreshRate)Hz" "Green"
    if ($gpu.CurrentRefreshRate -lt 119) {
        Log "  > WARNING: Refresh rate below 119Hz. Check Windows Display Settings." "Red"
    }
} else {
    Log "  > Could not read display info" "Gray"
}
Log "  > GFN Optimal Settings for Samsung Odyssey:" "Cyan"
Log "      Resolution : 2560x1440 (set in Windows Display Settings)" "White"
Log "      Refresh    : 120Hz stream profile (Odyssey native = 119Hz)" "White"
Log "      Upscale    : NVIDIA AI (RTX Video Super Resolution)" "White"
Log "      RTX ON     : Enable in GFN app BEFORE launching game" "White"
Log "      Bitrate    : 50 Mbps+ (Ultimate plan)" "White"
Log ""

# ── PHASE 4: Network ────────────────────────────────────────────────────────
Log "[4/5] Network optimisation..." "Yellow"
ipconfig /flushdns 2>&1 | Out-Null
Log "  > DNS cache flushed" "Green"
netsh interface tcp set global autotuninglevel=normal 2>&1 | Out-Null
netsh interface tcp set global nagle=disabled 2>&1 | Out-Null
Log "  > TCP optimised (autotuning normal, nagle disabled)" "Green"
Log ""

# ── PHASE 5: Final RAM report ────────────────────────────────────────────────
Log "[5/5] Final RAM check..." "Yellow"
$freeFinal = [math]::Round((Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
$total = [math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
Log "  > RAM: ${freeFinal} GB free of ${total} GB total" "Green"
Log ""

# ── DONE ────────────────────────────────────────────────────────────────────
Log "  ==========================================" "Cyan"
Log "   DONE. PC optimized for GFN gaming." "Green"
Log "  ==========================================" "Cyan"
Log ""
Log "  To restore Ollama: just run 'ollama serve' in terminal" "Gray"
Log "  To restore OneDrive: launch from Start menu" "Gray"
Log ""
