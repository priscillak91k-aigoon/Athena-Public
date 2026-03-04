# === CHECK OLLAMA AND INSTALL IF NEEDED ===
# Also installs the google-genai package for updated Gemini support

Write-Host "=== OLLAMA SETUP CHECK ==="

# 1. Check if Ollama is installed
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaPath) {
    Write-Host "[OK] Ollama found at: $($ollamaPath.Source)"
    $version = ollama --version 2>&1
    Write-Host "  Version: $version"
}
else {
    Write-Host "[INSTALLING] Ollama not found. Downloading installer..."
    $installerUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "[OK] Downloaded installer"
        Write-Host "[RUNNING] Installing Ollama (this may take a minute)..."
        Start-Process -FilePath $installerPath -ArgumentList "/VERYSILENT" -Wait
        Write-Host "[OK] Ollama installed"
    }
    catch {
        Write-Host "[FAIL] Could not download/install Ollama: $($_.Exception.Message)"
        Write-Host "  Manual install: https://ollama.com/download"
    }
}

# 2. Check if a model is available
$ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaCheck) {
    $models = ollama list 2>&1
    Write-Host ""
    Write-Host "Current models:"
    Write-Host $models
    
    # Pull a small efficient model for thinking tasks
    $hasModel = $models | Select-String "llama3.2"
    if (-not $hasModel) {
        Write-Host ""
        Write-Host "[PULLING] Downloading llama3.2 (3B - small, fast, good for analysis)..."
        ollama pull llama3.2 2>&1 | ForEach-Object { Write-Host "  $_" }
        Write-Host "[OK] llama3.2 ready"
    }
    else {
        Write-Host "[OK] llama3.2 already available"
    }
}

# 3. Install/upgrade Python packages
Write-Host ""
Write-Host "Installing Python packages..."
python -m pip install --upgrade google-genai anthropic python-dotenv requests 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "[OK] Python packages ready"

Write-Host ""
Write-Host "=== SETUP COMPLETE ==="
