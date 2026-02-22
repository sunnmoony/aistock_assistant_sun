@echo off
chcp 65001 >nul
title A股智能助手 - 轻量模式

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║       A股智能助手 - 轻量模式启动                  ║
echo ╠══════════════════════════════════════════════════╣
echo ║  内存优化，适合低配置电脑（内存 < 4GB）         ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 清除代理设置
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

:: 设置轻量模式
set AISTOCK_LITE_MODE=1

:: 检测Python
echo [检查] Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未检测到Python！
    echo.
    echo 请先运行 install.bat 安装依赖
    echo.
    pause
    exit /b 1
)
echo [OK] Python已就绪
echo.

:: 启动程序
echo [启动] A股智能助手（轻量模式）...
echo.
echo ════════════════════════════════════════════════════
echo   提示：轻量模式已启用，将占用更少系统资源
echo ════════════════════════════════════════════════════
echo.

python main.py --lite

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，错误代码: %errorlevel%
    echo.
    echo 请检查日志文件或运行 check_and_run.bat 进行诊断
    echo.
)

echo.
echo 感谢使用A股智能助手！
pause
