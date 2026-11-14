@echo off
setlocal
pushd "%~dp0labirent-ajan" || exit /b 1

if exist ".venv314\Scripts\pythonw.exe" (
    start "" ".venv314\Scripts\pythonw.exe" -B main.py
    popd
    exit /b
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -B main.py
) else (
    python -B main.py
)
set "launch_status=%errorlevel%"
if not "%launch_status%"=="0" (
    echo Labirent acilamadi. README.md dosyasindaki kurulum adimlarini kontrol et.
    pause
)
popd
exit /b %launch_status%
