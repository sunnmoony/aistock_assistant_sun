@echo off
chcp 65001 >nul
title A股智能助手 - Anaconda轻量模式

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║       A股智能助手 - Anaconda轻量模式              ║
echo ╠══════════════════════════════════════════════════╣
echo ║  使用Anaconda环境 (akshare_conda)                ║
echo ║  内存优化，适合低配置电脑（内存 < 4GB）          ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 清除代理设置
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

:: 设置轻量模式
set AISTOCK_LITE_MODE=1

:: 设置Anaconda路径（请根据您的安装路径修改）
set CONDA_PATH=F:\Anaconda
set CONDA_ENV=akshare_conda

:: 检查Anaconda是否存在
if not exist "%CONDA_PATH%\Scripts\conda.exe" (
    echo.
    echo [错误] 未找到Anaconda！
    echo.
    echo 请修改脚本中的 CONDA_PATH 变量为您的Anaconda安装路径
    echo 当前设置: %CONDA_PATH%
    echo.
    pause
    exit /b 1
)

echo [检查] Anaconda环境...
echo.

:: 初始化conda
call "%CONDA_PATH%\Scripts\activate.bat" "%CONDA_PATH%"

:: 激活akshare_conda环境
echo [激活] conda环境: %CONDA_ENV%
call conda activate %CONDA_ENV%
if errorlevel 1 (
    echo.
    echo [错误] 无法激活conda环境: %CONDA_ENV%
    echo.
    echo 请确保该环境已创建。创建命令:
    echo   conda create -n akshare_conda python=3.10
    echo   conda activate akshare_conda
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] conda环境已激活: %CONDA_ENV%
echo.

:: 启动程序
echo [启动] A股智能助手（Anaconda轻量模式）...
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
    echo 请检查日志文件或查看上面的错误信息
    echo.
)

echo.
echo 感谢使用A股智能助手！
pause
