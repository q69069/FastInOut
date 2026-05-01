@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo FastInOut 快消品进销存 - 启动脚本
echo ========================================

echo.
echo [1/3] 启动后端服务...
cd /d E:\FastInOut\server
start "FastInOut-Backend" python -m uvicorn main:app --host 0.0.0.0 --port 8000
timeout /t 3 >nul
echo 后端服务已启动 http://127.0.0.1:8000

echo.
echo [2/3] 启动PC端...
cd /d E:\FastInOut\pc
start "FastInOut-PC" cmd /k "npm run dev"
echo PC端启动中 http://localhost:5173

echo.
echo [3/3] 启动Web端...
cd /d E:\FastInOut\web
start "FastInOut-Web" cmd /k "npm run dev"
echo Web端启动中 http://localhost:5174

echo.
echo ========================================
echo 所有服务已启动！
echo 后端API: http://127.0.0.1:8000
echo PC端: http://localhost:5173
echo Web端: http://localhost:5174
echo API文档: http://127.0.0.1:8000/docs
echo ========================================
pause
