Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python -m http.server", 0, False
Set WshShell = Nothing