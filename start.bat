@echo off
title 智能招聘简历筛选系统 - 一键打开
echo ==========================================
echo   智能招聘简历筛选系统
echo ==========================================
echo.
cd /d "C:\Users\ZLLSE15\Doubao\chats\2026-08-29\new-chat\FDX1"

rem 指定已安装全部依赖的Python解释器（避免命中WindowsApps占位符导致pip不可用）
set "PY=C:\Users\ZLLSE15\AppData\Local\Doubao\User Data\sandbox_runtime\bases\9f6d27f23933fb44a3a1c728c88a5ce4\python\python.exe"

rem 第1步：检查服务是否已经在运行（监听 5000 端口）
netstat -ano | findstr "127.0.0.1:5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo 系统已在运行，正在打开网页...
    start "" "http://127.0.0.1:5000"
    exit /b
)

rem 第2步：检查依赖是否安装
"%PY%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [提示] 未检测到依赖，正在安装，请稍候...
    "%PY%" -m pip install -r requirements.txt
)

rem 第3步：后台启动服务（最小化窗口，不阻塞本脚本）
echo 正在启动服务，请稍候...
start "ResumeService" /min "%PY%" run.py

rem 第4步：等待服务就绪（最多约30秒），就绪后自动打开网页
set /a tries=0
:wait
timeout /t 2 >nul
netstat -ano | findstr "127.0.0.1:5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto up
set /a tries+=1
if %tries% lss 15 goto wait
echo [错误] 服务启动超时，请检查上方窗口的输出信息
pause
exit /b

:up
echo 服务已就绪，正在打开网页...
start "" "http://127.0.0.1:5000"
exit /b
