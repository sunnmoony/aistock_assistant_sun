@echo off
chcp 65001 >nul
title A股智能助手 - 标准模式

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║       A股智能助手 - 标准模式启动                  ║
echo ╠══════════════════════════════════════════════════╣
echo ║  包含完整功能，适合内存 ≥ 4GB 的电脑             ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 清除代理设置
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

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
echo [启动] A股智能助手（标准模式）...
echo.
echo ════════════════════════════════════════════════════
echo   提示：如果是第一次运行，可能需要几秒钟初始化
echo ════════════════════════════════════════════════════
echo.

python main.py

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
