Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\prisc\Documents\Athena-Public\scripts\TakeScreenshot.ps1""", 0, False
