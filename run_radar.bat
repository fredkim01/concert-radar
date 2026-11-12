@echo off
cd /d "C:\Users\frede\OneDrive\Documents\concert-radar"
echo ===== %date% %time% ===== >> radar.log
".venv\Scripts\python.exe" concert_radar.py >> radar.log 2>&1
