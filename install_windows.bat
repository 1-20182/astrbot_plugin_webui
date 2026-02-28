@echo off
chcp 65001 >nul
title AstrBot WebUI 插件 - Windows 安装脚本

cls
echo ==============================================
echo 🌐 AstrBot WebUI 插件 - Windows 安装脚本
echo ==============================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 已获取管理员权限
) else (
    echo ⚠️  警告：未获取管理员权限
    echo    某些功能可能需要管理员权限
    echo    建议右键点击此脚本，选择"以管理员身份运行"
    echo.
    pause
)

echo.
echo 📦 正在检查 Python 环境...

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python
    echo.
    echo 💡 解决方法：
    echo    1. 访问 https://www.python.org/downloads/
    echo    2. 下载并安装 Python 3.8+
    echo    3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do (
    echo ✅ 检测到: %%a
)

echo.
echo 📦 正在安装依赖...

:: 安装依赖
pip install aiohttp certifi

if errorlevel 1 (
    echo ❌ 依赖安装失败
    echo.
    echo 💡 解决方法：
    echo    1. 检查网络连接
    echo    2. 尝试使用镜像源：
    echo       pip install aiohttp certifi -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

echo.
echo 🔥 正在配置 Windows 防火墙...

:: 添加防火墙规则
netsh advfirewall firewall show rule name="AstrBot WebUI" >nul 2>&1
if errorlevel 1 (
    echo 📝 添加防火墙规则...
    netsh advfirewall firewall add rule name="AstrBot WebUI" dir=in action=allow protocol=tcp localport=6180 >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  防火墙规则添加失败，可能需要手动配置
    ) else (
        echo ✅ 防火墙规则已添加
    )
) else (
    echo ✅ 防火墙规则已存在
)

echo.
echo 🔧 正在创建快捷方式...

:: 获取当前目录
set "SCRIPT_DIR=%~dp0"
set "ASTRBOT_DIR=%SCRIPT_DIR%..\..\.."

:: 创建启动脚本
echo @echo off > "%ASTRBOT_DIR%\start_webui.bat"
echo chcp 65001 ^>nul >> "%ASTRBOT_DIR%\start_webui.bat"
echo echo 正在启动 AstrBot... >> "%ASTRBOT_DIR%\start_webui.bat"
echo cd /d "%ASTRBOT_DIR%" >> "%ASTRBOT_DIR%\start_webui.bat"
echo python -m astrbot >> "%ASTRBOT_DIR%\start_webui.bat"
echo pause >> "%ASTRBOT_DIR%\start_webui.bat"

echo ✅ 启动脚本已创建: %ASTRBOT_DIR%\start_webui.bat

echo.
echo ==============================================
echo ✅ 安装完成！
echo ==============================================
echo.
echo 🚀 快速开始:
echo    1. 重启 AstrBot
echo    2. 查看日志中的访问地址
echo    3. 用浏览器打开地址
echo    4. 用管理员账号登录
echo.
echo 📖 访问地址示例:
echo    本机: http://127.0.0.1:6180
echo    局域网: http://[你的IP]:6180
echo.
echo ❓ 遇到问题？
echo    - 端口被占用：修改 data/plugins/webui/_conf_schema.json 中的 port
echo    - 无法访问：检查 Windows 防火墙设置
echo    - 其他问题：查看 AstrBot 控制台日志
echo.
echo 💡 提示：
echo    - 配置文件: data/plugins/webui/_conf_schema.json
echo    - 用户数据: data/webui_data/
echo    - 启动脚本: start_webui.bat
echo.
echo ==============================================
echo.

pause
