title INPUTCONTROLLER
:a
if exist ".stop" del .stop&exit
if exist ".pause" ping localhost -n 2 >nul&goto a
taskkill /F /fi "imagename eq GetInput.exe"
ping localhost -n 1 -l 1
ping localhost -n 1 -l 0
ping localhost -n 1 -l 2
ping localhost -n 1 -l 4
ping localhost -n 1 -l 6
ping localhost -n 1 -l 8
ping localhost -n 1 -l 10
goto :a
