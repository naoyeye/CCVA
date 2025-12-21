@echo off
REM CCVA 安装脚本 (Windows)
REM 此脚本将 CCVA 安装为全局命令行工具

echo 🚀 开始安装 CCVA...

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python。请先安装 Python 3.8 或更高版本。
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查 pip 是否安装
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 pip。请先安装 pip。
    pause
    exit /b 1
)

REM 检查 ffmpeg 是否安装
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  警告: 未找到 ffmpeg。CCVA 需要 ffmpeg 来处理音频。
    echo 请从 https://ffmpeg.org/download.html 下载并安装 ffmpeg
    echo 确保 ffmpeg 在系统 PATH 中。
    echo.
    set /p continue="是否继续安装 CCVA？(y/N): "
    if /i not "%continue%"=="y" (
        echo 安装已取消。
        pause
        exit /b 1
    )
)

REM 进入脚本所在目录
cd /d "%~dp0"

REM 安装 CCVA
echo 📦 正在安装 CCVA...
pip install -e .

if %errorlevel% equ 0 (
    echo ✅ CCVA 安装成功！
    echo.
    echo 现在你可以在任意目录下使用以下命令：
    echo   CCVA --url ^<视频链接^>
    echo   CCVA --url ^<视频链接^> --start ^<开始时间^> --end ^<结束时间^>
    echo   CCVA --url ^<视频链接^> --format mp3 --output ^<输出路径^>
    echo.
    echo 使用 'CCVA --help' 查看所有可用选项。
) else (
    echo ❌ 安装失败。请检查错误信息并重试。
)

pause
