Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Save location - Antigravity can access this
$saveDir = "C:\Users\prisc\Documents\Athena-Public\.nosey_nutter\screenshots"
if (!(Test-Path $saveDir)) { New-Item -ItemType Directory -Path $saveDir -Force | Out-Null }

# Timestamp filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$filename = Join-Path $saveDir "screen_$timestamp.png"

# Capture entire screen
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)

# Save
$bitmap.Save($filename, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

# Also copy to clipboard
[System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile($filename))

Write-Host "Screenshot saved: $filename"
