@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title A股智能助手 - 智能启动

echo.
echo ==================================================
echo        A股智能助手 - 智能启动检测
echo ==================================================
echo   自动检测系统配置 | 推荐最佳启动模式
echo ==================================================
echo.

:: 清除代理设置
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

:: 检测Python
echo [检测] Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ==================================================
    echo   [错误] 未安装Python
    echo ==================================================
    echo   请先运行 install.bat 安装Python依赖
    echo ==================================================
    goto :end
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo     [OK] Python %PY_VER%

:: 检测内存
echo.
echo [检测] 系统内存...
set MEM_MB=0
for /f "skip=1" %%p in ('wmic OS get TotalVisibleMemorySize /value 2^>nul') do (
    set MEM=%%p
    if "!MEM:~0,4!"=="Tota" (
        for /f "tokens=2 delims==" %%a in ("%%p") do set MEM_KB=%%a
    )
)
if defined MEM_KB (
    set /a MEM_MB=!MEM_KB!/1024
)

if !MEM_MB! LSS 2000 (
    echo     [!] 内存较低: !MEM_MB! MB - 推荐轻量模式
    set RECOMMEND=lite
) else if !MEM_MB! LSS 4000 (
    echo     [OK] 内存适中: !MEM_MB! MB - 推荐标准模式
    set RECOMMEND=standard
) else (
    echo     [OK] 内存充足: !MEM_MB! MB - 可使用完整功能
    set RECOMMEND=standard
)

:: 检测依赖
echo.
echo [检测] 必要依赖...
set DEPS_OK=1

python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo     [X] PyQt5 未安装
    set DEPS_OK=0
) else (
    echo     [OK] PyQt5
)

python -c "import pandas" 2>nul
if errorlevel 1 (
    echo     [X] pandas 未安装
    set DEPS_OK=0
) else (
    echo     [OK] pandas
)

python -c "import pytdx" 2>nul
if errorlevel 1 (
    echo     [X] pytdx 未安装
    set DEPS_OK=0
) else (
    echo     [OK] pytdx
)

if !DEPS_OK!==0 (
    echo.
    echo [提示] 检测到缺少依赖，正在安装...
    call install.bat
)

:: 显示选择菜单
echo.
echo ==================================================
echo    系统检测完成 - 推荐模式: !RECOMMEND!
echo ==================================================
echo.
echo 请选择启动方式:
echo.
echo   [1] 标准模式 - 完整功能，适合大多数电脑
echo   [2] 轻量模式 - 内存优化，适合低配置电脑
echo   [3] 配置数据源 - 运行数据源配置向导
echo   [4] 退出
echo.

set /p CHOICE="请输入选择 [1/2/3/4]: "

if "%CHOICE%"=="1" (
    echo.
    echo [启动] 标准模式...
    python main.py
) else if "%CHOICE%"=="2" (
    echo.
    echo [启动] 轻量模式...
    set AISTOCK_LITE_MODE=1
    python main.py --lite
) else if "%CHOICE%"=="3" (
    echo.
    echo [启动] 数据源配置向导...
    python data_source_wizard.py
) else (
    echo.
    echo 再见！
    goto :end
)

:end
echo.
pause
