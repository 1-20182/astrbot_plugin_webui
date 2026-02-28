# 🌸 AstrBot 梦幻 WebUI 插件 ✨  
  
[![AstrBot]    (https://img.shields.io/badge/AstrBot-Plugin-pink)]  (https://github.com/Soulter/AstrBot)
[![Python](https://img.shields.io/badge/Python-3.8+-ff69b4)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-ff69b4)](LICENSE)
[![Developer](https://img.shields.io/badge/Developer-飞翔的死猪-ff69b4)](https://github.com/your-repo)

> 💖 嗨嗨~ 这是一个超级可爱的 AstrBot 多用户管理面板喵！
> 
> ✨ 支持实时插件管理、人格配置、第三方插件安装，让管理变得萌萌哒~！
> 
> 🐷 由 **飞翔的死猪** 精心打造~

![Preview](https://img.shields.io/badge/Preview-Available-ff69b4)

---

## 🎀 有什么好玩的功能呀？

### 💕 双角色系统
- **👑 管理员大大**: 使用 AstrBot 账号密码登录，拥有全部权限喵~
- **👤 普通小伙伴**: 使用独立账号登录，查看插件状态~

### 🎒 魔法道具箱（插件管理）
- ✨ 实时获取 AstrBot 已安装插件~
- 🔄 一键更新单个或所有插件，超方便！
- 🗑️ 卸载不需要的插件~
- 🌟 安装第三方插件（支持 GitHub/Git 仓库）
- 💤 启用/禁用插件，随心切换~

### 🛒 魔法商店街（插件市场）
- 📦 浏览官方插件市场，发现新宝贝~
- 🎁 一键安装插件，so easy！
- 🔍 查看插件详情，了解清楚再下手~

### 🎨 换装小屋（人格管理）
- 📝 查看所有人格配置~
- 🎭 实时同步 AstrBot 人格数据~

### 👫 小伙伴名单（用户管理）
- ➕ 添加新用户，欢迎新伙伴~
- 🗑️ 删除用户，说再见~
- 🔄 重置密码，帮小伙伴找回账号~

### 🌈 超可爱界面
- 🎀 粉色梦幻主题，少女心爆棚！
- ✨ 丰富的表情包，萌萌哒~
- 🌸 动态背景图片，美轮美奂~
- 💖 流畅动画效果，丝滑体验~

---

## 🚀 快来一起玩吧！

### 1️⃣ 安装插件

将插件文件夹复制到 AstrBot 的插件目录：
```bash
# 克隆或下载插件
git clone https://github.com/your-repo/astrbot-webui.git

# 复制到 AstrBot 插件目录
cp -r astrbot-webui /path/to/astrbot/data/plugins/webui
```

### 2️⃣ 安装依赖

```bash
# 使用 pip 安装依赖
pip install -r requirements.txt

# 或手动安装
pip install aiohttp certifi
```

### 3️⃣ 重启 AstrBot

```bash
# 重启 AstrBot
python -m astrbot
```

### 4️⃣ 访问 WebUI

- 查看 AstrBot 日志中的访问地址~
- 用浏览器打开地址（默认 http://localhost:6180）
- 用管理员账号登录，开始管理之旅~

---

## 💻 系统安装指南

### 🪟 Windows 系统

#### 方法一：使用安装脚本（推荐）

1. **右键点击安装脚本**，选择"以管理员身份运行"
   ```
   data/plugins/webui/install_windows.bat
   ```

2. **脚本会自动完成：**
   - ✅ 检查 Python 环境
   - ✅ 安装依赖包
   - ✅ 配置 Windows 防火墙
   - ✅ 创建启动脚本

3. **重启 AstrBot**，查看日志中的访问地址，冲鸭！

#### 方法二：手动安装

```cmd
# 安装依赖
pip install -r requirements.txt

# 配置防火墙（以管理员身份运行 PowerShell）
New-NetFirewallRule -DisplayName "AstrBot WebUI" -Direction Inbound -Protocol TCP -LocalPort 6180 -Action Allow
```

---

### 🐧 Linux 系统

#### 方法一：使用安装脚本（推荐）

```bash
# 进入 AstrBot 目录
cd /path/to/astrbot

# 运行安装脚本
bash data/plugins/webui/install_linux.sh
```

#### 方法二：手动安装

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3-pip
pip3 install -r requirements.txt
```

**防火墙配置:**
```bash
# ufw (Ubuntu/Debian)
sudo ufw allow 6180/tcp

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=6180/tcp
sudo firewall-cmd --reload
```

---

## 🎮 使用指南

### 👑 管理员登录

1. 访问 WebUI 界面（默认 http://localhost:6180）
2. 使用 AstrBot 管理员账号登录~
3. 进入"👫 小伙伴名单"管理用户，当个好管家~

### 👤 普通用户

1. 使用管理员创建的账号登录~
2. 查看"🎒 魔法道具箱"管理插件~
3. 浏览"🛒 魔法商店街"安装新插件~

### 🌟 安装第三方插件

1. 进入"🎒 魔法道具箱"
2. 在"🌟 安装第三方插件"区域输入 GitHub 仓库地址~
3. 点击"🚀 安装"按钮~
4. 等待安装完成，叮！安装成功~

### 🔄 更新插件

**单个更新:**
- 在插件列表中找到有 🆕 标记的插件~
- 点击"🆕 更新"按钮，一键更新~

**批量更新:**
- 点击右上角的"🔄 一键更新所有插件"按钮~
- 喝杯茶等待更新完成~

---

## ⚙️ 配置说明

编辑 `_conf_schema.json` 文件：

```json
{
  "port": 6180,
  "host": "0.0.0.0",
  "enable_https": false,
  "public_domain": ""
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `port` | 服务端口 | 6180 |
| `host` | 绑定地址 | 0.0.0.0 |
| `enable_https` | 启用 HTTPS | false |
| `public_domain` | 公网域名 | "" |

---

## 🎨 个性化设置

### 自定义背景图片

将图片放入 `data/plugins/webui/background/` 目录：
- 支持格式: jpg, jpeg, png, gif, webp, bmp
- 推荐尺寸: 1920x1080 或更大
- 系统会自动随机切换背景，每次都有新惊喜~

---

## 🐛 遇到问题怎么办？

### 端口被占用

```bash
# Windows
netstat -ano | findstr :6180

# Linux/Mac
lsof -i :6180

# 更换端口：修改 _conf_schema.json 中的 port
```

### 防火墙阻止

```bash
# Windows (PowerShell 管理员)
New-NetFirewallRule -DisplayName "AstrBot WebUI" -Direction Inbound -Protocol TCP -LocalPort 6180 -Action Allow

# Linux
sudo ufw allow 6180/tcp
```

### 插件无法获取

1. 确保 AstrBot 已正确启动~
2. 检查日志中的错误信息~
3. 尝试重启 AstrBot，重启大法好~

---

## 📁 文件结构

```
data/plugins/webui/
├── main.py                 # 主程序（核心代码在这里~）
├── README.md               # 本文件（就是你在看的这个~）
├── requirements.txt        # 依赖列表（需要安装的东东~）
├── _conf_schema.json       # 配置文件（可以改端口啥的~）
├── install_windows.bat     # Windows 安装脚本
├── install_linux.sh        # Linux 安装脚本
└── background/             # 背景图片目录（放你喜欢的图~）
    ├── bg1.jpg
    ├── bg2.png
    └── ...
```

---

## 🔧 技术说明

### 数据存储
- 用户数据: `data/webui_data/users.json`
- 会话数据: 内存存储（重启后清空~）

### API 接口
- 插件管理: `/api/plugins/*`
- 插件市场: `/api/market`
- 人格管理: `/api/personas`
- 用户管理: `/api/users/*`
- 背景图片: `/api/backgrounds`, `/api/background/{filename}`

### 实时对接
- 插件状态实时同步 AstrBot~
- 人格配置实时读取~
- 安装/卸载/更新即时生效~

---

## 💖 支持的平台

### 🪟 Windows 系统
| 系统版本 | 支持状态 | 说明 |
|---------|---------|------|
| Windows 11 | ✅ 完美支持 | 推荐使用最新版本 |
| Windows 10 | ✅ 完美支持 | 版本 1809+ |
| Windows Server 2022 | ✅ 支持 | 服务器版本 |
| Windows Server 2019 | ✅ 支持 | 服务器版本 |

### 🐧 Linux 发行版
| 发行版 | 版本要求 | 支持状态 | 包管理器 |
|--------|---------|---------|---------|
| Ubuntu | 18.04 / 20.04 / 22.04 / 24.04 LTS | ✅ 完美支持 | apt |
| Debian | 9 / 10 / 11 / 12 | ✅ 完美支持 | apt |
| CentOS | 7 / Stream 8 / Stream 9 | ✅ 支持 | yum/dnf |
| RHEL | 7 / 8 / 9 | ✅ 支持 | yum/dnf |
| Fedora | 36+ | ✅ 支持 | dnf |
| Arch Linux | 最新滚动版本 | ✅ 支持 | pacman |
| openSUSE | Leap 15+ / Tumbleweed | ✅ 支持 | zypper |
| Alpine Linux | 3.14+ | ✅ 支持 | apk |

### 🍎 macOS 系统
| 版本 | 支持状态 | 说明 |
|------|---------|------|
| macOS Sonoma 14 | ✅ 完美支持 | Apple Silicon / Intel |
| macOS Ventura 13 | ✅ 完美支持 | Apple Silicon / Intel |
| macOS Monterey 12 | ✅ 支持 | Intel 推荐 |
| macOS Big Sur 11 | ✅ 支持 | Intel 推荐 |

### 🐳 容器化部署
| 平台 | 支持状态 | 说明 |
|------|---------|------|
| Docker | ✅ 完美支持 | 推荐使用官方镜像 |
| Docker Compose | ✅ 完美支持 | 支持多容器编排 |
| Kubernetes | ✅ 支持 | 可使用 Helm Chart |
| Podman | ✅ 支持 | 无根容器支持 |

### ☁️ 云服务器
| 云服务商 | 支持状态 | 说明 |
|---------|---------|------|
| 阿里云 ECS | ✅ 完美支持 | 全系列实例 |
| 腾讯云 CVM | ✅ 完美支持 | 全系列实例 |
| 华为云 ECS | ✅ 完美支持 | 全系列实例 |
| AWS EC2 | ✅ 完美支持 | 全系列实例 |
| Azure VM | ✅ 完美支持 | 全系列实例 |
| Google Cloud | ✅ 完美支持 | 全系列实例 |
| Vultr | ✅ 完美支持 | 全系列实例 |
| DigitalOcean | ✅ 完美支持 | 全系列实例 |

### 🖥️ 硬件架构
| 架构 | 支持状态 | 说明 |
|------|---------|------|
| x86_64 / AMD64 | ✅ 完美支持 | 主流桌面和服务器 |
| ARM64 / AArch64 | ✅ 完美支持 | Apple Silicon, ARM 服务器 |
| ARMv7 | ✅ 支持 | 树莓派等 ARM 设备 |
| RISC-V | ⚠️ 实验性支持 | 部分功能可能受限 |

### 📱 移动设备（通过浏览器访问）
| 设备类型 | 支持状态 | 说明 |
|---------|---------|------|
| iOS Safari | ✅ 完美支持 | iPhone / iPad |
| Android Chrome | ✅ 完美支持 | 手机 / 平板 |
| Android Firefox | ✅ 支持 | 手机 / 平板 |

### 🌐 浏览器兼容性
| 浏览器 | 版本要求 | 支持状态 |
|--------|---------|---------|
| Chrome | 90+ | ✅ 完美支持 |
| Firefox | 88+ | ✅ 完美支持 |
| Safari | 14+ | ✅ 完美支持 |
| Edge | 90+ | ✅ 完美支持 |
| Opera | 76+ | ✅ 支持 |

---

## ⚙️ 系统要求

### 最低配置
- **CPU**: 1 核
- **内存**: 512 MB RAM
- **磁盘**: 100 MB 可用空间
- **Python**: 3.8+
- **网络**: 可访问 AstrBot 服务

### 推荐配置
- **CPU**: 2 核及以上
- **内存**: 1 GB RAM 及以上
- **磁盘**: 500 MB 可用空间（用于背景图片和日志）
- **Python**: 3.10+
- **网络**: 稳定的网络连接

---

## 📝 更新日志  

### v1.0.0  
- 🎉 初始版本发布，撒花~
- ✨ 多用户权限管理~
- 🎀 可爱粉色主题~
- 🔄 实时插件管理~
- 🌟 第三方插件安装~
- 🎨 人格配置查看~

---

## 🤝 贡献  

欢迎提交 Issue 和 Pull Request！
让我们一起把这个插件做得更好更可爱~

## 📄 许可证  

AGPL-3.0 License

---

<p align="center">
  Made with 💖 by <strong>飞翔的死猪</strong> 🐷
  <br>
  <small>感谢使用，要开心哦~ 🌸</small>

 

