@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title A股智能助手 - 一键安装

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║       A股智能助手 - 一键安装程序 v2.0           ║
echo ╠══════════════════════════════════════════════════╣
echo ║  免费股票分析工具 | 新手友好 | 无需配置API      ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 检查Python环境
echo [步骤 1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ╔══════════════════════════════════════════════════╗
    echo ║  [错误] 未检测到Python环境                       ║
    echo ╠══════════════════════════════════════════════════╣
    echo ║  请按以下步骤安装Python:                         ║
    echo ║  1. 访问 https://www.python.org/downloads/      ║
    echo ║  2. 下载Python 3.8或更高版本                    ║
    echo ║  3. 安装时勾选 "Add Python to PATH"            ║
    echo ║  4. 重新运行此脚本                              ║
    echo ╚══════════════════════════════════════════════════╝
    goto :end
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo     [OK] Python %PY_VER% 已安装

:: 检查pip
echo.
echo [步骤 2/4] 检查pip包管理器...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo     [!] pip未安装，正在安装...
    python -m ensurepip --upgrade
)
echo     [OK] pip已就绪

:: 升级pip
echo.
echo [步骤 3/4] 升级pip到最新版本...
python -m pip install --upgrade pip -q
echo     [OK] pip已升级

:: 安装依赖
echo.
echo [步骤 4/4] 安装项目依赖...
echo     这可能需要几分钟，请耐心等待...
echo.

:: 使用引号包裹版本号，避免批处理语法错误
python -m pip install "PyQt5>=5.15" -q
python -m pip install "pandas>=2.0.0" -q
python -m pip install "numpy>=1.24.0" -q
python -m pip install "requests>=2.28" -q
python -m pip install "pyyaml>=6.0.1" -q
python -m pip install "APScheduler>=3.10" -q
python -m pip install "matplotlib>=3.7.0" -q
python -m pip install "mplfinance>=0.12.10b0" -q
python -m pip install "scipy>=1.10.0" -q
python -m pip install "pytdx>=1.72" -q

if errorlevel 1 (
    echo.
    echo     [!] 部分依赖安装失败，尝试使用国内镜像...
    python -m pip install "PyQt5>=5.15" "pandas>=2.0.0" "numpy>=1.24.0" "requests>=2.28" "pyyaml>=6.0.1" "APScheduler>=3.10" "matplotlib>=3.7.0" "mplfinance>=0.12.10b0" "scipy>=1.10.0" "pytdx>=1.72" -i https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 创建必要目录
if not exist "data" mkdir data
if not exist "logs" mkdir logs

:: 创建默认配置文件
if not exist "config.yaml" (
    echo.
    echo     正在创建默认配置文件...
    (
        echo # A股智能助手配置文件
        echo # 自动生成，可根据需要修改
        echo.
        echo app:
        echo   name: A股智能助手
        echo   version: "2.0"
        echo   language: zh-CN
        echo.
        echo data:
        echo   auto_refresh: true
        echo   refresh_interval: 30
        echo   cache_enabled: true
        echo.
        echo data_sources:
        echo   pytdx:
        echo     enabled: true
        echo     priority: 0
        echo   akshare:
        echo     enabled: true
        echo     priority: 1
        echo   mock:
        echo     enabled: true
        echo     priority: 2
        echo.
        echo ai:
        echo   api_key: ""
        echo   api_url: https://api.siliconflow.cn/v1
        echo   model: deepseek-ai/DeepSeek-V3
        echo.
        echo notification:
        echo   enabled: true
        echo   sound: true
    ) > config.yaml
    echo     [OK] 配置文件已创建
)

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║           安装完成！                             ║
echo ╠══════════════════════════════════════════════════╣
echo ║  下一步操作:                                     ║
echo ║  1. 双击 run.bat 启动程序（标准模式）           ║
echo ║  2. 双击 run_lite.bat 启动（轻量模式）          ║
echo ║  3. 双击 check_and_run.bat 自动检测启动         ║
echo ╠══════════════════════════════════════════════════╣
echo ║  AI功能配置（可选）:                            ║
echo ║  1. 访问 https://siliconflow.cn/ 注册账号       ║
echo ║  2. 获取免费API密钥                             ║
echo ║  3. 在config.yaml中填写api_key                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

:end
echo 按任意键退出...
pause >nul
