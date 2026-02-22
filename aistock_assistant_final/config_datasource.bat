@echo off
chcp 65001 >nul
title A股智能助手 - 数据源配置向导

echo ========================================
echo    A股智能助手 - 数据源配置向导
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python环境！
    pause
    exit /b 1
)

echo [启动] 数据源配置向导...
echo.

python data_source_wizard.py

echo.
pause
