# Aider Dispatch Script — Called by Antigravity Command Center
# Usage: .\scripts\aider_dispatch.ps1 -Message "your instructions" [-ProjectDir "path"] [-Model "model"]
# Example: .\scripts\aider_dispatch.ps1 -Message "Add a logout button to index.html"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message,

    [string]$ProjectDir = "C:\Users\prisc\Documents\Athena-Public",

    [string]$Model = "gemini/gemini-2.5-flash",

    [string[]]$Files = @()
)

# Load API key from user environment
$env:GOOGLE_API_KEY = [System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'User')
$env:OPENROUTER_API_KEY = [System.Environment]::GetEnvironmentVariable('OPENROUTER_API_KEY', 'User')

if (-not $env:GOOGLE_API_KEY -and -not $env:OPENROUTER_API_KEY) {
    Write-Error "No API keys found. Set GOOGLE_API_KEY or OPENROUTER_API_KEY as user environment variables."
    exit 1
}

# Build command arguments
$aiderArgs = @(
    "-m", "aider",
    "--model", $Model,
    "--yes",
    "--no-auto-commits",
    "--message", $Message
)

# Add specific files if provided
foreach ($file in $Files) {
    $aiderArgs += "--file"
    $aiderArgs += $file
}

# Execute
Write-Host "=== AIDER DISPATCH ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir" -ForegroundColor DarkGray
Write-Host "Model:   $Model" -ForegroundColor DarkGray
Write-Host "Task:    $Message" -ForegroundColor Yellow
Write-Host "======================" -ForegroundColor Cyan

Push-Location $ProjectDir
try {
    python @aiderArgs
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "`n=== DISPATCH COMPLETE ===" -ForegroundColor Green
    } else {
        Write-Host "`n=== DISPATCH FAILED (exit code: $exitCode) ===" -ForegroundColor Red
    }
} finally {
    Pop-Location
}
