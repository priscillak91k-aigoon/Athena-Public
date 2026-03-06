# Antigravity Notification Script — Pings Cilla on Telegram when input is needed
# Usage: .\scripts\notify_cilla.ps1 -Message "Need your input on X"
# Called by Antigravity when it requires user attention during autonomous work

param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

$BOT_TOKEN = [System.Environment]::GetEnvironmentVariable('TELEGRAM_NOTIFY_BOT_TOKEN', 'User')
$CHAT_ID = [System.Environment]::GetEnvironmentVariable('TELEGRAM_NOTIFY_CHAT_ID', 'User')

if (-not $BOT_TOKEN -or -not $CHAT_ID) {
    Write-Error "Telegram notification credentials not set. Run:"
    Write-Error "  [System.Environment]::SetEnvironmentVariable('TELEGRAM_NOTIFY_BOT_TOKEN', 'YOUR_TOKEN', 'User')"
    Write-Error "  [System.Environment]::SetEnvironmentVariable('TELEGRAM_NOTIFY_CHAT_ID', 'YOUR_CHAT_ID', 'User')"
    exit 1
}

$formattedMessage = @"
⚡ *ANTIGRAVITY — Input Required*

$Message

_Reply in Antigravity when ready._
"@

$uri = "https://api.telegram.org/bot$BOT_TOKEN/sendMessage"
$body = @{
    chat_id    = $CHAT_ID
    text       = $formattedMessage
    parse_mode = "Markdown"
}

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ErrorAction Stop
    if ($response.ok) {
        Write-Host "Notification sent to Telegram." -ForegroundColor Green
    }
    else {
        Write-Error "Telegram API returned: $($response | ConvertTo-Json)"
    }
}
catch {
    Write-Error "Failed to send Telegram notification: $_"
}
