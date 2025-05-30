@echo off
cd /d %~dp0
call conda activate deblur_gs
python src\main.py
pause
