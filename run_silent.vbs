Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "start_server.bat", 0, False
Set WshShell = Nothing