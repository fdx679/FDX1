@echo off
title 智能招聘简历筛选系统 - 一键打开
echo ==========================================
echo   智能招聘简历筛选系统
echo ==========================================
echo.
cd /d "C:\Users\ZLLSE15\Doubao\chats\2026-08-29\new-chat\FDX1"

rem 第1步：检查服务是否已经在运行（监听 5000 端口）
netstat -ano | findstr "127.0.0.1:5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo 系统已在运行，正在打开网页...
    start "" "http://127.0.0.1:5000"
    exit /b
)

rem 第2步：检查依赖是否安装
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未检测到依赖，正在安装，请稍候...
    pip install -r requirements.txt
)

rem 第3步：启动服务并打开浏览器
echo 正在启动服务，请稍候...
echo 看到 Running on http://127.0.0.1:5000 即启动完成
start "" "http://127.0.0.1:5000"
timeout /t 2 >nul
python run.py
pause
