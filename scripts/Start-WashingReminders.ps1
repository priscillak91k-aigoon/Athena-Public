param (
    [int]$HoursToRun = 8
)

$wshell = New-Object -ComObject Wscript.Shell
$wshell.Popup("Washing reminders started! You will be reminded every hour for the next $HoursToRun hours.", 5, "Reminders Active", 0x40)

for ($i = 1; $i -le $HoursToRun; $i++) {
    Start-Sleep -Seconds 3600
    $wshell.Popup("Time to check the washing! It's been an hour. (Reminder $i of $HoursToRun)", 0, "Washing Reminder", 0x40)
}
