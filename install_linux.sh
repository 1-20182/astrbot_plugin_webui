#!/bin/bash
# AstrBot WebUI 插件 - Linux 安装脚本
# 支持 Ubuntu, Debian, CentOS, RHEL, Arch 等主流发行版

set -e

echo "=============================================="
echo "🌐 AstrBot WebUI 插件 - Linux 安装脚本"
echo "=============================================="
echo ""

# 检测发行版
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$NAME
        DISTRO_ID=$ID
    elif type lsb_release >/dev/null 2>&1; then
        DISTRO=$(lsb_release -si)
        DISTRO_ID=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
        DISTRO_ID=$DISTRIB_ID
    else
        DISTRO="Unknown"
        DISTRO_ID="unknown"
    fi
    
    echo "📦 检测到系统: $DISTRO"
}

# 安装依赖
install_dependencies() {
    echo ""
    echo "📦 正在安装依赖..."
    
    case $DISTRO_ID in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3-pip python3-venv
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y python3-pip
            else
                yum install -y python3-pip
            fi
            ;;
        arch|manjaro)
            pacman -Sy --noconfirm python-pip
            ;;
        alpine)
            apk add --no-cache py3-pip
            ;;
        *)
            echo "⚠️  未知的发行版，请手动安装 python3-pip"
            ;;
    esac
    
    echo "✅ 系统依赖安装完成"
}

# 安装 Python 依赖
install_python_deps() {
    echo ""
    echo "🐍 正在安装 Python 依赖..."
    
    # 检测是否在虚拟环境中
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✅ 检测到虚拟环境: $VIRTUAL_ENV"
        pip install aiohttp certifi
    elif [ -d "venv" ]; then
        echo "✅ 检测到 venv 目录，激活虚拟环境..."
        source venv/bin/activate
        pip install aiohttp certifi
    else
        echo "⚠️  未检测到虚拟环境，尝试使用系统 Python..."
        pip3 install --user aiohttp certifi
    fi
    
    echo "✅ Python 依赖安装完成"
}

# 检查防火墙
check_firewall() {
    echo ""
    echo "🔥 检查防火墙状态..."
    
    PORT=6180
    
    # 检查 ufw
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            echo "📋 ufw 防火墙已启用"
            echo "💡 如需开放端口 $PORT，请执行:"
            echo "   sudo ufw allow $PORT/tcp"
        else
            echo "✅ ufw 防火墙未启用"
        fi
    fi
    
    # 检查 firewalld
    if command -v firewall-cmd &> /dev/null; then
        if systemctl is-active --quiet firewalld; then
            echo "📋 firewalld 防火墙已启用"
            echo "💡 如需开放端口 $PORT，请执行:"
            echo "   sudo firewall-cmd --permanent --add-port=$PORT/tcp"
            echo "   sudo firewall-cmd --reload"
        fi
    fi
    
    # 检查 iptables
    if command -v iptables &> /dev/null; then
        echo "💡 如果使用 iptables，请执行:"
        echo "   sudo iptables -I INPUT -p tcp --dport $PORT -j ACCEPT"
    fi
}

# 创建 systemd 服务文件
create_systemd_service() {
    echo ""
    echo "🔧 创建 systemd 服务文件..."
    
    # 获取当前用户和路径
    CURRENT_USER=$(whoami)
    ASTRBOT_PATH=$(pwd)
    
    cat > /tmp/astrbot-webui.service << EOF
[Unit]
Description=AstrBot WebUI Plugin
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$ASTRBOT_PATH
ExecStart=$ASTRBOT_PATH/venv/bin/python -m astrbot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ 服务文件已创建: /tmp/astrbot-webui.service"
    echo ""
    echo "💡 如需安装为系统服务，请执行:"
    echo "   sudo cp /tmp/astrbot-webui.service /etc/systemd/system/"
    echo "   sudo systemctl daemon-reload"
    echo "   sudo systemctl enable astrbot-webui"
    echo "   sudo systemctl start astrbot-webui"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=============================================="
    echo "✅ 安装完成！"
    echo "=============================================="
    echo ""
    echo "🚀 快速开始:"
    echo "   1. 重启 AstrBot"
    echo "   2. 查看日志中的访问地址"
    echo "   3. 用浏览器打开地址"
    echo "   4. 用管理员账号登录"
    echo ""
    echo "📖 更多信息:"
    echo "   - 配置文件: data/plugins/webui/_conf_schema.json"
    echo "   - 用户数据: data/webui_data/"
    echo "   - 日志查看: 查看 AstrBot 控制台输出"
    echo ""
    echo "❓ 遇到问题？"
    echo "   - 端口被占用：修改配置文件中的 port"
    echo "   - 无法访问：检查防火墙设置"
    echo "   - 其他问题：查看 AstrBot 日志"
    echo ""
    echo "=============================================="
}

# 主函数
main() {
    detect_distro
    
    echo ""
    read -p "是否安装系统依赖? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
    fi
    
    install_python_deps
    check_firewall
    create_systemd_service
    show_usage
}

# 运行主函数
main
