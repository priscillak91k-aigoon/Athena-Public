# Quick test for Telegram alert and Ollama status

# Test Telegram
Write-Host "=== TELEGRAM TEST ==="
$env:DOTENV = Get-Content "C:\Users\prisc\Documents\Athena-Public\.env" -Raw
python -c @"
import os, requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(r'C:\Users\prisc\Documents\Athena-Public\.env'))
token = os.getenv('TELEGRAM_ARCHITECT_TOKEN')
user_id = os.getenv('TELEGRAM_ALLOWED_USER_ID')
url = f'https://api.telegram.org/bot{token}/sendMessage'
resp = requests.post(url, json={'chat_id': user_id, 'text': 'Test from Athena Dreaming v2. If you see this, proactive alerts are working.', 'parse_mode': 'Markdown'}, timeout=10)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:200]}')
"@ 2>&1 | ForEach-Object { Write-Host $_ }

# Check Ollama
Write-Host ""
Write-Host "=== OLLAMA CHECK ==="
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaCmd) {
    Write-Host "[OK] Ollama found"
    ollama list 2>&1 | ForEach-Object { Write-Host "  $_" }
}
else {
    Write-Host "[PENDING] Ollama not yet available (installer may still be running)"
}
