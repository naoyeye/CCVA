@echo off
REM CCVA 卸载脚本 (Windows)

echo 🗑️  开始卸载 CCVA...

REM 检查是否已安装
CCVA --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  CCVA 似乎未安装或不在 PATH 中。
    set /p continue="是否继续卸载？(y/N): "
    if /i not "%continue%"=="y" (
        echo 卸载已取消。
        pause
        exit /b 0
    )
)

REM 卸载 CCVA
echo 📦 正在卸载 CCVA...
pip uninstall ccva -y

if %errorlevel% equ 0 (
    echo ✅ CCVA 卸载成功！
) else (
    echo ❌ 卸载失败。请检查错误信息。
    pause
    exit /b 1
)

pause
