@echo off
title 智能招聘简历筛选系统 - 启动器
echo ==========================================
echo   智能招聘简历筛选系统
echo   启动后请访问 http://127.0.0.1:5000
echo ==========================================
echo.
cd /d "C:\Users\ZLLSE15\Doubao\chats\2026-08-29\new-chat\FDX1"
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未检测到依赖，正在安装，请稍候...
    pip install -r requirements.txt
)
echo 正在启动服务，请稍候...
echo 看到 Running on http://127.0.0.1:5000 后即可访问
start "" "http://127.0.0.1:5000"
python run.py
pause
