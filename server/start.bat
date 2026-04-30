@echo off
cd /d "%~dp0"
echo ========================================
echo   FastInOut 快消品进销存管理系统
echo   启动中...
echo ========================================
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
