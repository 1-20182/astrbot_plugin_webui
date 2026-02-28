"""
🌸 AstrBot 梦幻 WebUI 插件 ✨
═══════════════════════════════════════
💕 一个超级可爱的多用户管理面板喵！
💕 支持多用户独立登录，首次使用需要设置管理员哦~
💕 让 AstrBot 管理变得萌萌哒~
═══════════════════════════════════════
🐷 开发者: 飞翔的死猪
📧 GitHub: https://github.com/your-repo
📅 创建时间: 2024
📝 许可证: AGPL-3.0
═══════════════════════════════════════
"""
import asyncio
import hashlib
import json
import os
import platform
import socket
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 🎀 尝试导入依赖（这些是我们需要的好东东~）
try:
    import aiohttp
    from aiohttp import web
    import certifi
    import ssl
    AIOHTTP_AVAILABLE = True
    # ✨ 太好了，所有依赖都安装成功啦！
except ImportError as e:
    AIOHTTP_AVAILABLE = False
    AIOHTTP_ERROR = str(e)
    # 😢 哎呀，有些依赖没安装呢，需要运行 pip install -r requirements.txt

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

# 🖥️ 操作系统检测（看看我们在什么系统上运行~）
IS_WINDOWS = platform.system() == 'Windows'  # 🪟 Windows 系统
IS_LINUX = platform.system() == 'Linux'      # 🐧 Linux 系统


class UserManager:
    """
    👥 用户管理器
    💕 负责管理所有小伙伴的账号信息~
    """
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / 'users.json'
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """📖 加载用户数据（从文件里读取小伙伴的信息~）"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # 😢 读取失败了，返回空字典
                pass
        return {}
    
    def _save_users(self):
        """💾 保存用户数据（把小伙伴的信息存到文件里~）"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """🔐 密码哈希（把密码变成乱乱的样子，保护隐私~）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_first_run(self) -> bool:
        """🎉 检查是否首次运行（看看是不是第一次使用~）"""
        return len(self.users) == 0
    
    def create_admin(self, username: str, password: str) -> bool:
        """👑 创建管理员账号（第一个用户就是管理员大大~）"""
        if not self.is_first_run():
            return False
        
        self.users[username] = {
            'username': username,
            'password_hash': self._hash_password(password),
            'role': 'admin',
            'created_at': datetime.now().isoformat(),
            'permissions': ['all']
        }
        self._save_users()
        logger.info(f"✨ 管理员账号 {username} 创建成功啦~")
        return True
    
    def create_user(self, username: str, password: str, created_by: str) -> bool:
        """👤 创建普通用户（欢迎新小伙伴加入~）"""
        if username in self.users:
            logger.warning(f"😢 用户名 {username} 已经被占用啦~")
            return False
        
        self.users[username] = {
            'username': username,
            'password_hash': self._hash_password(password),
            'role': 'user',
            'created_at': datetime.now().isoformat(),
            'created_by': created_by,
            'permissions': ['view_plugins', 'manage_own_data']
        }
        self._save_users()
        logger.info(f"✨ 新用户 {username} 创建成功啦~ 由 {created_by} 邀请加入~")
        return True
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """验证用户"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if user['password_hash'] == self._hash_password(password):
            return {
                'username': username,
                'role': user['role'],
                'permissions': user['permissions']
            }
        return None
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户"""
        return [
            {
                'username': u['username'],
                'role': u['role'],
                'created_at': u.get('created_at', ''),
                'created_by': u.get('created_by', 'system')
            }
            for u in self.users.values()
        ]
    
    def delete_user(self, username: str) -> bool:
        """删除用户"""
        if username in self.users and self.users[username]['role'] != 'admin':
            del self.users[username]
            self._save_users()
            return True
        return False
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """重置密码"""
        if username in self.users:
            self.users[username]['password_hash'] = self._hash_password(new_password)
            self._save_users()
            return True
        return False


class AstrBotDashboard(Star):
    """AstrBot 多用户管理面板"""
    
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.context = context
        self.config = config or {}
        
        # 检查依赖
        if not AIOHTTP_AVAILABLE:
            logger.error("❌ [Dashboard] 缺少依赖: aiohttp")
            logger.error("   请执行: pip install aiohttp")
            self._disabled = True
            return
        
        self._disabled = False
        
        # 基础配置
        self.port = int(self.config.get('port', 6180))
        self.host = self.config.get('host', '0.0.0.0')
        self.session_timeout = 3600
        
        # 数据目录
        self.data_dir = Path(getattr(context, 'data_dir', 'data/webui_data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户管理
        self.user_manager = UserManager(str(self.data_dir))
        
        # 会话管理
        self.sessions: Dict[str, dict] = {}
        
        # Web 服务器
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        logger.info("[Dashboard] 多用户管理面板初始化完成")
    
    def _get_local_ip(self) -> str:
        """获取本地 IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
            finally:
                s.close()
            return ip
        except:
            return '127.0.0.1'
    
    async def initialize(self):
        """初始化"""
        if self._disabled:
            return
        
        try:
            await self._start_server()
            
            local_ip = self._get_local_ip()
            
            logger.info("=" * 60)
            logger.info("✅ AstrBot 多用户管理面板启动成功！")
            logger.info("")
            logger.info("🌐 访问地址:")
            logger.info(f"   本机: http://127.0.0.1:{self.port}")
            if local_ip != '127.0.0.1':
                logger.info(f"   局域网: http://{local_ip}:{self.port}")
            logger.info("")
            
            # 检查是否首次运行
            if self.user_manager.is_first_run():
                logger.info("⚠️  首次使用，请访问网页设置管理员账号")
            else:
                admin_count = sum(1 for u in self.user_manager.users.values() if u['role'] == 'admin')
                user_count = len(self.user_manager.users) - admin_count
                logger.info(f"👥 用户数: {admin_count} 管理员, {user_count} 普通用户")
            
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ [Dashboard] 启动失败: {e}")
            logger.error(traceback.format_exc())
    
    async def _start_server(self):
        """启动服务器"""
        self.app = web.Application()
        
        # 页面路由
        self.app.router.add_get('/', self._handle_index)
        
        # API 路由
        self.app.router.add_get('/api/check_first_run', self._handle_check_first_run)
        self.app.router.add_post('/api/setup_admin', self._handle_setup_admin)
        self.app.router.add_post('/api/login', self._handle_login)
        self.app.router.add_post('/api/logout', self._handle_logout)
        self.app.router.add_get('/api/check_auth', self._handle_check_auth)
        
        # 用户管理（仅管理员）
        self.app.router.add_get('/api/users', self._handle_get_users)
        self.app.router.add_post('/api/users', self._handle_create_user)
        self.app.router.add_delete('/api/users/{username}', self._handle_delete_user)
        self.app.router.add_post('/api/users/{username}/reset_password', self._handle_reset_password)
        
        # 插件管理
        self.app.router.add_get('/api/plugins', self._handle_get_plugins)
        self.app.router.add_post('/api/plugins/toggle', self._handle_toggle_plugin)
        self.app.router.add_post('/api/plugins/install', self._handle_install_plugin)
        self.app.router.add_post('/api/plugins/uninstall', self._handle_uninstall_plugin)
        self.app.router.add_post('/api/plugins/update', self._handle_update_plugin)
        self.app.router.add_post('/api/plugins/update-all', self._handle_update_all_plugins)
        self.app.router.add_post('/api/plugins/install-custom', self._handle_install_custom_plugin)
        
        # 插件市场
        self.app.router.add_get('/api/market', self._handle_get_market)
        
        # 人格管理
        self.app.router.add_get('/api/personas', self._handle_get_personas)
        
        # 背景图片
        self.app.router.add_get('/api/backgrounds', self._handle_get_backgrounds)
        self.app.router.add_get('/api/background/{filename}', self._handle_get_background_image)
        
        # 启动
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
    
    def _generate_session(self) -> str:
        """生成会话 ID"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _check_auth(self, request: web.Request) -> Optional[web.Response]:
        """检查认证"""
        session_id = request.cookies.get('session_id')
        if not session_id or session_id not in self.sessions:
            return web.json_response({'success': False, 'message': '未登录'}, status=401)
        
        session = self.sessions[session_id]
        if datetime.now() > session['expires']:
            del self.sessions[session_id]
            return web.json_response({'success': False, 'message': '会话已过期'}, status=401)
        
        session['expires'] = datetime.now() + timedelta(seconds=self.session_timeout)
        return None
    
    def _get_current_user(self, request: web.Request) -> Optional[Dict]:
        """获取当前用户"""
        session_id = request.cookies.get('session_id')
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]['user']
        return None
    
    # ========== 处理函数 ==========
    
    async def _handle_index(self, request: web.Request):
        """主页面"""
        return web.Response(text=self._get_html(), content_type='text/html')
    
    async def _handle_check_first_run(self, request: web.Request):
        """检查是否首次运行"""
        return web.json_response({
            'success': True,
            'is_first_run': self.user_manager.is_first_run()
        })
    
    async def _handle_setup_admin(self, request: web.Request):
        """设置管理员"""
        try:
            if not self.user_manager.is_first_run():
                return web.json_response({'success': False, 'message': '管理员已存在'})
            
            data = await request.json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or len(username) < 3:
                return web.json_response({'success': False, 'message': '用户名至少3位'})
            
            if not password or len(password) < 6:
                return web.json_response({'success': False, 'message': '密码至少6位'})
            
            if self.user_manager.create_admin(username, password):
                logger.info(f"[Dashboard] 管理员 {username} 创建成功")
                return web.json_response({'success': True, 'message': '管理员创建成功'})
            else:
                return web.json_response({'success': False, 'message': '创建失败'})
        except Exception as e:
            logger.error(f"[Dashboard] 创建管理员失败: {e}")
            return web.json_response({'success': False, 'message': '创建失败'})
    
    async def _handle_login(self, request: web.Request):
        """登录"""
        try:
            data = await request.json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return web.json_response({'success': False, 'message': '请输入用户名和密码'})
            
            user = self.user_manager.verify_user(username, password)
            if user:
                session_id = self._generate_session()
                self.sessions[session_id] = {
                    'user': user,
                    'expires': datetime.now() + timedelta(seconds=self.session_timeout)
                }
                
                response = web.json_response({
                    'success': True,
                    'message': '登录成功',
                    'data': {
                        'username': user['username'],
                        'role': user['role']
                    }
                })
                response.set_cookie('session_id', session_id, httponly=True, max_age=self.session_timeout)
                logger.info(f"[Dashboard] 用户 {username} 登录成功")
                return response
            else:
                return web.json_response({'success': False, 'message': '用户名或密码错误'})
        except Exception as e:
            logger.error(f"[Dashboard] 登录错误: {e}")
            return web.json_response({'success': False, 'message': '登录失败'})
    
    async def _handle_logout(self, request: web.Request):
        """登出"""
        session_id = request.cookies.get('session_id')
        if session_id and session_id in self.sessions:
            del self.sessions[session_id]
        return web.json_response({'success': True, 'message': '已登出'})
    
    async def _handle_check_auth(self, request: web.Request):
        """检查认证状态"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        return web.json_response({
            'success': True,
            'data': {
                'username': user['username'],
                'role': user['role']
            }
        })
    
    async def _handle_get_users(self, request: web.Request):
        """获取用户列表（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        users = self.user_manager.get_all_users()
        return web.json_response({'success': True, 'data': users})
    
    async def _handle_create_user(self, request: web.Request):
        """创建用户（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or len(username) < 3:
                return web.json_response({'success': False, 'message': '用户名至少3位'})
            
            if not password or len(password) < 6:
                return web.json_response({'success': False, 'message': '密码至少6位'})
            
            if self.user_manager.create_user(username, password, user['username']):
                logger.info(f"[Dashboard] 用户 {username} 创建成功")
                return web.json_response({'success': True, 'message': '用户创建成功'})
            else:
                return web.json_response({'success': False, 'message': '用户名已存在'})
        except Exception as e:
            logger.error(f"[Dashboard] 创建用户失败: {e}")
            return web.json_response({'success': False, 'message': '创建失败'})
    
    async def _handle_delete_user(self, request: web.Request):
        """删除用户（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        username = request.match_info.get('username')
        if username == user['username']:
            return web.json_response({'success': False, 'message': '不能删除自己'})
        
        if self.user_manager.delete_user(username):
            logger.info(f"[Dashboard] 用户 {username} 已删除")
            return web.json_response({'success': True, 'message': '用户已删除'})
        else:
            return web.json_response({'success': False, 'message': '删除失败'})
    
    async def _handle_reset_password(self, request: web.Request):
        """重置密码（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            username = request.match_info.get('username')
            data = await request.json()
            new_password = data.get('new_password', '')
            
            if not new_password or len(new_password) < 6:
                return web.json_response({'success': False, 'message': '密码至少6位'})
            
            if self.user_manager.reset_password(username, new_password):
                logger.info(f"[Dashboard] 用户 {username} 密码已重置")
                return web.json_response({'success': True, 'message': '密码已重置'})
            else:
                return web.json_response({'success': False, 'message': '重置失败'})
        except Exception as e:
            logger.error(f"[Dashboard] 重置密码失败: {e}")
            return web.json_response({'success': False, 'message': '重置失败'})
    
    async def _handle_get_plugins(self, request: web.Request):
        """获取已安装的插件列表 - 多方式获取确保完整"""
        error = self._check_auth(request)
        if error:
            return error
        
        try:
            plugins = []
            plugin_names = set()  # 用于去重
            
            # 方式1: 从 star_registry 获取（AstrBot 全局注册表）
            try:
                from astrbot.core.star.context import star_registry
                for star in star_registry:
                    name = getattr(star, 'name', None) or getattr(star, 'module_path', '').split('/')[-1] or '未知'
                    if name and name not in plugin_names:
                        plugin_names.add(name)
                        plugins.append({
                            'name': name,
                            'description': getattr(star, 'desc', '这个插件还没有描述呢~') or '这个插件还没有描述呢~',
                            'author': getattr(star, 'author', '神秘作者') or '神秘作者',
                            'version': getattr(star, 'version', '1.0.0') or '1.0.0',
                            'activated': getattr(star, 'activated', True),
                            'module_path': getattr(star, 'module_path', ''),
                            'repo': getattr(star, 'repo', None),
                            'reserved': getattr(star, 'reserved', False)
                        })
                logger.info(f"[Dashboard] 从 star_registry 获取到 {len(plugins)} 个插件")
            except Exception as e:
                logger.warning(f"[Dashboard] 从 star_registry 获取失败: {e}")
            
            # 方式2: 从 context.star_context 获取
            if len(plugins) == 0:
                try:
                    star_context = getattr(self.context, 'star_context', None) or getattr(self.context, '_star_context', None)
                    if star_context and hasattr(star_context, 'get_all_stars'):
                        for star in star_context.get_all_stars():
                            name = getattr(star, 'name', None) or '未知'
                            if name and name not in plugin_names:
                                plugin_names.add(name)
                                plugins.append({
                                    'name': name,
                                    'description': getattr(star, 'desc', '这个插件还没有描述呢~') or '这个插件还没有描述呢~',
                                    'author': getattr(star, 'author', '神秘作者') or '神秘作者',
                                    'version': getattr(star, 'version', '1.0.0') or '1.0.0',
                                    'activated': getattr(star, 'activated', True),
                                    'module_path': getattr(star, 'module_path', ''),
                                    'repo': getattr(star, 'repo', None),
                                    'reserved': getattr(star, 'reserved', False)
                                })
                        logger.info(f"[Dashboard] 从 star_context 获取到 {len(plugins)} 个插件")
                except Exception as e:
                    logger.warning(f"[Dashboard] 从 star_context 获取失败: {e}")
            
            # 方式3: 从 plugin_manager 获取
            if len(plugins) == 0:
                try:
                    if hasattr(self.context, 'plugin_manager'):
                        pm = self.context.plugin_manager
                        # 尝试不同的属性名
                        stars = getattr(pm, 'stars', None) or getattr(pm, '_stars', None) or getattr(pm, 'star_registry', None) or []
                        if stars:
                            for star in stars:
                                name = getattr(star, 'name', None) or getattr(star, 'module_path', '').split('/')[-1] or '未知'
                                if name and name not in plugin_names:
                                    plugin_names.add(name)
                                    plugins.append({
                                        'name': name,
                                        'description': getattr(star, 'desc', '这个插件还没有描述呢~') or '这个插件还没有描述呢~',
                                        'author': getattr(star, 'author', '神秘作者') or '神秘作者',
                                        'version': getattr(star, 'version', '1.0.0') or '1.0.0',
                                        'activated': getattr(star, 'activated', True),
                                        'module_path': getattr(star, 'module_path', ''),
                                        'repo': getattr(star, 'repo', None),
                                        'reserved': getattr(star, 'reserved', False)
                                    })
                            logger.info(f"[Dashboard] 从 plugin_manager 获取到 {len(plugins)} 个插件")
                except Exception as e:
                    logger.warning(f"[Dashboard] 从 plugin_manager 获取失败: {e}")
            
            # 方式4: 从插件目录扫描
            if len(plugins) == 0:
                try:
                    from astrbot.core.utils.astrbot_path import get_astrbot_data_path
                    plugins_dir = os.path.join(get_astrbot_data_path(), "plugins")
                    if os.path.exists(plugins_dir):
                        for item in os.listdir(plugins_dir):
                            item_path = os.path.join(plugins_dir, item)
                            if os.path.isdir(item_path) and not item.startswith('.'):
                                if item not in plugin_names:
                                    plugin_names.add(item)
                                    plugins.append({
                                        'name': item,
                                        'description': '从插件目录扫描到的插件~',
                                        'author': '未知',
                                        'version': '1.0.0',
                                        'activated': True,
                                        'module_path': item_path,
                                        'repo': None,
                                        'reserved': False
                                    })
                        logger.info(f"[Dashboard] 从插件目录扫描到 {len(plugins)} 个插件")
                except Exception as e:
                    logger.warning(f"[Dashboard] 从插件目录扫描失败: {e}")
            
            logger.info(f"[Dashboard] 总共获取到 {len(plugins)} 个已安装插件")
            return web.json_response({'success': True, 'data': plugins})
        except Exception as e:
            logger.error(f"[Dashboard] 获取插件失败: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'success': False, 'message': '获取失败'})
    
    async def _handle_toggle_plugin(self, request: web.Request):
        """切换插件状态"""
        error = self._check_auth(request)
        if error:
            return error
        
        # 仅管理员可以操作
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            activated = data.get('activated')
            
            # 调用 AstrBot 的插件管理功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if activated:
                    # 启用插件
                    if hasattr(plugin_manager, 'turn_on_plugin'):
                        await plugin_manager.turn_on_plugin(plugin_name)
                else:
                    # 禁用插件
                    if hasattr(plugin_manager, 'turn_off_plugin'):
                        await plugin_manager.turn_off_plugin(plugin_name)
                
                return web.json_response({'success': True, 'message': '操作成功'})
            
            return web.json_response({'success': False, 'message': '插件管理功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 切换插件状态失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_get_market(self, request: web.Request):
        """获取远程插件市场 - 使用 AstrBot 官方相同的 API"""
        error = self._check_auth(request)
        if error:
            return error
        
        plugins = []
        cache_file = None
        
        try:
            # 使用 AstrBot 官方相同的配置
            data_dir = get_astrbot_data_path()
            cache_file = os.path.join(data_dir, "plugins.json")
            logger.info(f"[Dashboard] 缓存文件路径: {cache_file}")
            
            # 方法1: 尝试从缓存读取
            try:
                if os.path.exists(cache_file):
                    logger.info(f"[Dashboard] 缓存文件存在，正在读取...")
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        logger.info(f"[Dashboard] 缓存数据类型: {type(cache_data)}")
                        
                        # 官方格式: {"data": {"plugin-name": {...}, ...}, "timestamp": "...", "md5": "..."}
                        if isinstance(cache_data, dict):
                            if 'data' in cache_data:
                                data_content = cache_data['data']
                                # data 可能是列表或字典
                                if isinstance(data_content, list):
                                    plugins = data_content
                                    logger.info(f"[Dashboard] 从缓存获取到 {len(plugins)} 个插件(列表格式)")
                                elif isinstance(data_content, dict):
                                    # 将字典转换为列表
                                    plugins = list(data_content.values())
                                    logger.info(f"[Dashboard] 从缓存获取到 {len(plugins)} 个插件(字典格式)")
                        # 有些情况下可能是直接列表
                        elif isinstance(cache_data, list):
                            plugins = cache_data
                            logger.info(f"[Dashboard] 从缓存获取到 {len(plugins)} 个插件(直接列表)")
                else:
                    logger.warning(f"[Dashboard] 缓存文件不存在: {cache_file}")
            except Exception as e:
                logger.error(f"[Dashboard] 读取缓存失败: {e}")
                logger.error(traceback.format_exc())
            
            # 方法2: 从网络获取
            if not plugins:
                logger.info("[Dashboard] 缓存未命中，尝试从网络获取...")
                urls = [
                    "https://api.soulter.top/astrbot/plugins",
                    "https://github.com/AstrBotDevs/AstrBot_Plugins_Collection/raw/refs/heads/main/plugin_cache_original.json",
                ]
                
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                
                for url in urls:
                    try:
                        logger.info(f"[Dashboard] 尝试从 {url} 获取...")
                        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
                            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                                logger.info(f"[Dashboard] {url} 响应状态: {response.status}")
                                if response.status == 200:
                                    try:
                                        data = await response.json()
                                    except:
                                        text = await response.text()
                                        data = json.loads(text)
                                    
                                    logger.info(f"[Dashboard] 响应数据类型: {type(data)}")
                                    
                                    # 官方API返回直接列表
                                    if isinstance(data, list) and len(data) > 0:
                                        plugins = data
                                        logger.info(f"[Dashboard] 从 {url} 获取到 {len(plugins)} 个插件")
                                        break
                                    # 如果是字典格式，可能是插件名作为key的字典
                                    elif isinstance(data, dict):
                                        if 'data' in data:
                                            # 提取data字段
                                            data_content = data['data']
                                            if isinstance(data_content, list):
                                                plugins = data_content
                                            elif isinstance(data_content, dict):
                                                plugins = list(data_content.values())
                                            logger.info(f"[Dashboard] 从 {url} (data字段)获取到 {len(plugins)} 个插件")
                                            break
                                        else:
                                            # 直接是插件字典
                                            plugins = list(data.values())
                                            logger.info(f"[Dashboard] 从 {url} (字典值)获取到 {len(plugins)} 个插件")
                                            break
                    except Exception as e:
                        logger.error(f"[Dashboard] 从 {url} 获取失败: {e}")
                        continue
            
            # 格式化插件数据
            formatted_plugins = []
            if plugins:
                logger.info(f"[Dashboard] 开始格式化 {len(plugins)} 个插件...")
                for plugin in plugins:
                    if isinstance(plugin, dict):
                        formatted_plugins.append({
                            'name': plugin.get('name', plugin.get('display_name', '')),
                            'desc': plugin.get('desc', ''),
                            'author': plugin.get('author', ''),
                            'version': plugin.get('version', ''),
                            'repo': plugin.get('repo', ''),
                            'installed': False
                        })
                logger.info(f"[Dashboard] 成功格式化 {len(formatted_plugins)} 个插件")
            else:
                logger.warning("[Dashboard] 没有获取到任何插件数据")
            
            return web.json_response({'success': True, 'data': formatted_plugins})
        except Exception as e:
            logger.error(f"[Dashboard] 获取插件市场失败: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'success': False, 'message': f'获取失败: {str(e)}'})
    
    async def _handle_install_plugin(self, request: web.Request):
        """安装插件（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            repo_url = data.get('repo')
            
            if not repo_url:
                return web.json_response({'success': False, 'message': '缺少插件仓库地址'})
            
            # 调用 AstrBot 的插件安装功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if hasattr(plugin_manager, 'install_plugin'):
                    success, message = await plugin_manager.install_plugin(repo_url)
                    if success:
                        logger.info(f"[Dashboard] 插件 {plugin_name} 安装成功")
                        return web.json_response({'success': True, 'message': '插件安装成功'})
                    else:
                        return web.json_response({'success': False, 'message': message or '安装失败'})
            
            return web.json_response({'success': False, 'message': '插件安装功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 安装插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_uninstall_plugin(self, request: web.Request):
        """卸载插件（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            
            # 调用 AstrBot 的插件卸载功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if hasattr(plugin_manager, 'uninstall_plugin'):
                    success, message = await plugin_manager.uninstall_plugin(plugin_name)
                    if success:
                        logger.info(f"[Dashboard] 插件 {plugin_name} 卸载成功")
                        return web.json_response({'success': True, 'message': '插件卸载成功'})
                    else:
                        return web.json_response({'success': False, 'message': message or '卸载失败'})
            
            return web.json_response({'success': False, 'message': '插件卸载功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 卸载插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_update_plugin(self, request: web.Request):
        """更新单个插件（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            
            if not plugin_name:
                return web.json_response({'success': False, 'message': '缺少插件名称'})
            
            # 调用 AstrBot 的插件更新功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if hasattr(plugin_manager, 'update_plugin'):
                    success, message = await plugin_manager.update_plugin(plugin_name)
                    if success:
                        logger.info(f"[Dashboard] 插件 {plugin_name} 更新成功")
                        return web.json_response({'success': True, 'message': '🎉 插件更新成功啦~'})
                    else:
                        return web.json_response({'success': False, 'message': message or '更新失败'})
                else:
                    # 尝试使用 install_plugin 重新安装来更新
                    # 先获取插件的 repo
                    plugins = []
                    try:
                        from astrbot.core.star.context import star_registry
                        for star in star_registry:
                            if getattr(star, 'name', '') == plugin_name:
                                repo = getattr(star, 'repo', None)
                                if repo:
                                    success, message = await plugin_manager.install_plugin(repo)
                                    if success:
                                        return web.json_response({'success': True, 'message': '🎉 插件更新成功啦~'})
                                    else:
                                        return web.json_response({'success': False, 'message': message or '更新失败'})
                    except:
                        pass
            
            return web.json_response({'success': False, 'message': '插件更新功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 更新插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_update_all_plugins(self, request: web.Request):
        """更新所有插件（仅管理员）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            # 调用 AstrBot 的批量更新功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if hasattr(plugin_manager, 'update_all_plugins'):
                    success, message = await plugin_manager.update_all_plugins()
                    if success:
                        logger.info("[Dashboard] 所有插件更新成功")
                        return web.json_response({'success': True, 'message': '🎉 所有插件都更新成功啦~'})
                    else:
                        return web.json_response({'success': False, 'message': message or '批量更新失败'})
            
            return web.json_response({'success': False, 'message': '批量更新功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 批量更新插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_install_custom_plugin(self, request: web.Request):
        """从自定义 URL 安装插件（第三方插件）"""
        error = self._check_auth(request)
        if error:
            return error
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            repo_url = data.get('url')
            
            if not repo_url:
                return web.json_response({'success': False, 'message': '请输入插件仓库地址哦~'})
            
            # 验证 URL 格式
            if not (repo_url.startswith('http://') or repo_url.startswith('https://')):
                return web.json_response({'success': False, 'message': '仓库地址格式不正确，需要以 http:// 或 https:// 开头'})
            
            # 调用 AstrBot 的插件安装功能
            if hasattr(self.context, 'plugin_manager'):
                plugin_manager = self.context.plugin_manager
                if hasattr(plugin_manager, 'install_plugin'):
                    success, message = await plugin_manager.install_plugin(repo_url)
                    if success:
                        logger.info(f"[Dashboard] 第三方插件安装成功: {repo_url}")
                        return web.json_response({'success': True, 'message': '🎉 第三方插件安装成功啦~'})
                    else:
                        return web.json_response({'success': False, 'message': message or '安装失败'})
            
            return web.json_response({'success': False, 'message': '插件安装功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 安装第三方插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_get_personas(self, request: web.Request):
        """获取人格列表 - 实时对接 AstrBot"""
        error = self._check_auth(request)
        if error:
            return error
        
        try:
            personas = []
            
            # 从 AstrBot 的 PersonaManager 获取人格列表
            if hasattr(self.context, 'persona_manager'):
                persona_manager = self.context.persona_manager
                if hasattr(persona_manager, 'get_all_personas'):
                    all_personas = await persona_manager.get_all_personas()
                    for persona in all_personas:
                        personas.append({
                            'id': getattr(persona, 'persona_id', ''),
                            'name': getattr(persona, 'persona_id', ''),
                            'description': getattr(persona, 'system_prompt', '')[:50] + '...' if len(getattr(persona, 'system_prompt', '')) > 50 else getattr(persona, 'system_prompt', ''),
                            'system_prompt': getattr(persona, 'system_prompt', ''),
                            'begin_dialogs': getattr(persona, 'begin_dialogs', []),
                            'tools': getattr(persona, 'tools', []),
                            'skills': getattr(persona, 'skills', []),
                            'folder_id': getattr(persona, 'folder_id', None)
                        })
            
            # 如果没有获取到，返回空列表
            if not personas:
                return web.json_response({
                    'success': True,
                    'data': [],
                    'message': '还没有人格配置哦，快去创建一个吧~'
                })
            
            return web.json_response({'success': True, 'data': personas})
        except Exception as e:
            logger.error(f"[Dashboard] 获取人格列表失败: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'success': False, 'message': '获取失败'})
    
    async def _handle_get_backgrounds(self, request: web.Request):
        """获取背景图片列表"""
        try:
            bg_dir = Path(__file__).parent / 'background'
            if not bg_dir.exists():
                return web.json_response({'success': True, 'data': [], 'message': '背景文件夹不存在'})
            
            # 支持的图片格式
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
            images = []
            
            for file in bg_dir.iterdir():
                if file.is_file() and file.suffix.lower() in image_extensions:
                    images.append(file.name)
            
            return web.json_response({'success': True, 'data': images})
        except Exception as e:
            logger.error(f"[Dashboard] 获取背景图片列表失败: {e}")
            return web.json_response({'success': False, 'message': '获取失败'})
    
    async def _handle_get_background_image(self, request: web.Request):
        """获取背景图片"""
        try:
            filename = request.match_info.get('filename')
            if not filename:
                return web.json_response({'success': False, 'message': '未指定文件名'})
            
            # 安全检查：防止目录遍历
            if '..' in filename or '/' in filename or '\\' in filename:
                return web.json_response({'success': False, 'message': '非法文件名'})
            
            bg_dir = Path(__file__).parent / 'background'
            image_path = bg_dir / filename
            
            if not image_path.exists() or not image_path.is_file():
                return web.json_response({'success': False, 'message': '图片不存在'})
            
            # 根据文件扩展名设置Content-Type
            ext = image_path.suffix.lower()
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }
            content_type = content_type_map.get(ext, 'application/octet-stream')
            
            return web.FileResponse(image_path, headers={'Content-Type': content_type})
        except Exception as e:
            logger.error(f"[Dashboard] 获取背景图片失败: {e}")
            return web.json_response({'success': False, 'message': '获取失败'})
    
    def _get_html(self) -> str:
        """获取 HTML 页面"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AstrBot 多用户管理面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background: #f0f2f5;
            min-height: 100vh;
        }
        
        /* 背景图片 */
        .bg-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            transition: opacity 0.5s ease-in-out;
            opacity: 1;
        }
        .bg-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: rgba(0, 0, 0, 0.15);
            pointer-events: none;
        }
        
        /* 全局动画 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes scaleIn {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            25% { transform: translateY(-20px) rotate(1deg); }
            50% { transform: translateY(-10px) rotate(0deg); }
            75% { transform: translateY(-25px) rotate(-1deg); }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-30px) scale(1.05); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10% { transform: translateX(-5px) rotate(-2deg); }
            20% { transform: translateX(5px) rotate(2deg); }
            30% { transform: translateX(-5px) rotate(-2deg); }
            40% { transform: translateX(5px) rotate(2deg); }
            50% { transform: translateX(-3px) rotate(-1deg); }
            60% { transform: translateX(3px) rotate(1deg); }
            70% { transform: translateX(-2px) rotate(-1deg); }
            80% { transform: translateX(2px) rotate(1deg); }
            90% { transform: translateX(-1px) rotate(0deg); }
        }
        
        @keyframes pulse-glow {
            0%, 100% { 
                transform: scale(1); 
                box-shadow: 0 0 20px rgba(255,0,0,0.5), 0 0 40px rgba(255,0,0,0.3);
            }
            50% { 
                transform: scale(1.08); 
                box-shadow: 0 0 40px rgba(0,255,0,0.6), 0 0 80px rgba(0,255,0,0.4);
            }
        }
        
        /* 可爱粉色系动画 */
        @keyframes kawaii-pulse {
            0%, 100% { 
                border-color: rgba(255, 182, 193, 0.9); 
                box-shadow: 0 0 10px rgba(255, 182, 193, 0.5), inset 0 0 8px rgba(255, 182, 193, 0.3); 
            }
            50% { 
                border-color: rgba(255, 105, 180, 0.9); 
                box-shadow: 0 0 15px rgba(255, 105, 180, 0.6), inset 0 0 10px rgba(255, 105, 180, 0.4); 
            }
        }
        
        @keyframes kawaii-glow {
            0%, 100% { box-shadow: 0 0 8px rgba(255, 182, 193, 0.5), 0 0 20px rgba(255, 182, 193, 0.3); }
            50% { box-shadow: 0 0 12px rgba(255, 105, 180, 0.6), 0 0 25px rgba(255, 105, 180, 0.4); }
        }
        
        @keyframes kawaii-text {
            0%, 100% { text-shadow: 0 0 8px rgba(255, 182, 193, 0.8), 0 0 15px rgba(255, 182, 193, 0.5); color: #ffb6c1; }
            50% { text-shadow: 0 0 10px rgba(255, 105, 180, 0.9), 0 0 20px rgba(255, 105, 180, 0.6); color: #ff69b4; }
        }
        
        @keyframes heart-beat {
            0%, 100% { transform: scale(1); }
            25% { transform: scale(1.1); }
            50% { transform: scale(1); }
            75% { transform: scale(1.05); }
        }
        
        @keyframes float-cute {
            0%, 100% { transform: translateY(0px) rotate(-1deg); }
            50% { transform: translateY(-15px) rotate(1deg); }
        }
        
        @keyframes glass-shine {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* 登录页面 */
        .login-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: transparent;
            display: flex; align-items: center; justify-content: center;
            z-index: 1000;
            animation: fadeIn 0.5s ease-out;
        }
        .login-bg {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            z-index: 0;
            transition: opacity 0.5s ease-in-out;
        }
        .login-bg-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.35);
            z-index: 1;
            pointer-events: none;
        }
        .login-box {
            background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.98) 100%);
            padding: 50px; border-radius: 30px;
            width: 100%; max-width: 420px; 
            box-shadow: 
                0 20px 60px rgba(255, 182, 193, 0.4),
                0 0 0 4px rgba(255, 255, 255, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.8),
                inset 0 -1px 0 rgba(255,182,193,0.3);
            animation: scaleIn 0.6s ease-out, float-cute 4s ease-in-out infinite, kawaii-pulse 2s ease-in-out infinite;
            border: 3px solid #ffb6c1;
            transform-style: preserve-3d;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            z-index: 2;
        }
        .login-box::before {
            content: '🌸';
            position: absolute;
            top: 15px; right: 20px;
            font-size: 24px;
            opacity: 0.6;
            animation: heart-beat 1.5s ease-in-out infinite;
        }
        .login-box::after {
            content: '🌸';
            position: absolute;
            bottom: 15px; left: 20px;
            font-size: 20px;
            opacity: 0.5;
            animation: heart-beat 1.5s ease-in-out infinite 0.5s;
        }
        .login-box:hover {
            transform: translateY(-10px) scale(1.03) rotate(1deg);
            box-shadow: 
                0 30px 80px rgba(255, 105, 180, 0.5),
                0 0 0 6px rgba(255, 255, 255, 0.6),
                inset 0 1px 0 rgba(255,255,255,0.9);
            border-color: #ff69b4;
        }
        .login-box h2 { text-align: center; margin-bottom: 10px; color: #ff69b4; font-weight: 700; letter-spacing: 2px; }
        .login-box .subtitle { text-align: center; color: #ff8da1; margin-bottom: 30px; font-size: 14px; font-weight: 500; }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; margin-bottom: 8px; color: #ff8da1; font-size: 14px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .form-group input {
            width: 100%; padding: 14px 18px; border: 2px solid rgba(255, 182, 193, 0.5); 
            border-radius: 15px;
            font-size: 14px; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255, 255, 255, 0.95);
            color: #ff69b4;
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #ff69b4; 
            box-shadow: 0 0 0 4px rgba(255, 105, 180, 0.2), 0 4px 15px rgba(255, 105, 180, 0.2);
            transform: translateY(-3px) scale(1.02);
        }
        .form-group input:focus + label,
        .form-group:focus-within label {
            color: #ff69b4;
            transform: translateY(-2px);
        }
        .login-btn {
            width: 100%; padding: 15px; 
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            color: white; 
            border: none;
            border-radius: 15px; font-size: 16px;
            font-weight: 600;
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: 
                0 6px 20px rgba(255, 105, 180, 0.4),
                0 0 0 2px rgba(255, 255, 255, 0.3);
            letter-spacing: 2px;
        }
        .login-btn::before {
            content: '✨';
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            animation: heart-beat 1.2s ease-in-out infinite;
        }
        .login-btn::after {
            content: '✨';
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 18px;
            animation: heart-beat 1.2s ease-in-out infinite 0.3s;
        }
        .login-btn:hover { 
            background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
            transform: translateY(-3px) scale(1.02);
            box-shadow: 
                0 10px 30px rgba(255, 105, 180, 0.5),
                0 0 0 3px rgba(255, 255, 255, 0.4);
        }
        .login-btn:active {
            transform: translateY(-1px);
        }
        .login-btn:disabled { 
            opacity: 0.6; cursor: not-allowed;
            transform: none;
            box-shadow: none;
            background: linear-gradient(135deg, #ddd 0%, #ccc 100%);
        }
        .error-msg { color: #ff6b6b; font-size: 14px; margin-top: 10px; text-align: center; font-weight: 500; }
        .success-msg { color: #69db7c; font-size: 14px; margin-top: 10px; text-align: center; font-weight: 500; }
        
        /* 主界面 - 可爱风 */
        .header {
            background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.98) 100%);
            padding: 25px 35px; border-radius: 25px;
            margin-bottom: 25px; 
            box-shadow: 
                0 15px 50px rgba(255, 182, 193, 0.3),
                0 0 0 4px rgba(255, 255, 255, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.8);
            display: flex; justify-content: space-between; align-items: center;
            border: 3px solid #ffb6c1;
            animation: slideInLeft 0.8s ease-out, kawaii-pulse 2s ease-in-out infinite;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '🎀';
            position: absolute;
            top: 10px; right: 15px;
            font-size: 28px;
            opacity: 0.7;
            animation: heart-beat 2s ease-in-out infinite;
        }
        .header:hover {
            transform: translateY(-8px) scale(1.01);
            box-shadow: 
                0 25px 70px rgba(255, 105, 180, 0.4),
                0 0 0 6px rgba(255, 255, 255, 0.6),
                inset 0 1px 0 rgba(255,255,255,0.9);
            border-color: #ff69b4;
        }
        .header h1 { color: #ff69b4; font-size: 26px; font-weight: 700; }
        .user-info { display: flex; align-items: center; gap: 15px; }
        .user-role {
            padding: 8px 18px; border-radius: 25px; font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        .user-role.admin { 
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            color: white;
            border: 2px solid rgba(255, 105, 180, 0.8);
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: 
                0 4px 15px rgba(255, 105, 180, 0.4),
                inset 0 1px 0 rgba(255,255,255,0.3);
            animation: heart-beat 2s ease-in-out infinite;
        }
        .user-role.user { 
            background: linear-gradient(135deg, #87ceeb 0%, #6495ed 100%);
            color: white;
            border: 2px solid rgba(100, 149, 237, 0.8);
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: 
                0 4px 15px rgba(100, 149, 237, 0.4),
                inset 0 1px 0 rgba(255,255,255,0.3);
            animation: heart-beat 2s ease-in-out infinite;
        }
        .logout-btn {
            padding: 10px 20px; 
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: white;
            border: 2px solid rgba(255, 154, 158, 0.8); 
            border-radius: 20px; 
            cursor: pointer; 
            font-size: 14px;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: 
                0 4px 15px rgba(255, 154, 158, 0.4),
                inset 0 1px 0 rgba(255,255,255,0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .logout-btn::before {
            content: '👋';
            position: absolute;
            left: 8px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 14px;
        }
        .logout-btn:hover { 
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
            transform: translateY(-4px) scale(1.05);
            box-shadow: 
                0 8px 25px rgba(255, 107, 107, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.5);
            border-color: #ff6b6b;
        }
        
        /* 导航 - 可爱风 */
        .nav {
            display: flex; gap: 12px; margin-bottom: 25px;
            background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.98) 100%);
            padding: 15px; border-radius: 25px;
            box-shadow: 
                0 10px 40px rgba(255, 182, 193, 0.3),
                0 0 0 4px rgba(255, 255, 255, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.8);
            border: 3px solid #ffb6c1;
            animation: slideInRight 0.6s ease-out 0.1s both, kawaii-pulse 2s ease-in-out infinite;
        }
        .nav-btn {
            padding: 12px 24px; 
            border: 2px solid transparent;
            background: rgba(255, 255, 255, 0.6);
            cursor: pointer; 
            border-radius: 20px; 
            font-size: 14px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            color: #ff8da1;
            position: relative;
            overflow: hidden;
            font-weight: 600;
        }
        .nav-btn::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 50%);
            border-radius: 20px;
            pointer-events: none;
        }
        .nav-btn:hover { 
            background: rgba(255, 182, 193, 0.3);
            color: #ff69b4;
            transform: translateY(-3px) scale(1.05);
            border-color: #ffb6c1;
            box-shadow: 0 5px 15px rgba(255, 182, 193, 0.4);
        }
        .nav-btn.active { 
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            color: white;
            border: 2px solid rgba(255, 105, 180, 0.8);
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: 
                0 6px 20px rgba(255, 105, 180, 0.4),
                inset 0 1px 0 rgba(255,255,255,0.3);
            animation: heart-beat 2s ease-in-out infinite;
        }
        .nav-btn.active::after {
            display: none;
        }
        
        /* 内容区 - 可爱风 */
        .content { 
            display: none; 
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.4s ease, transform 0.4s ease;
        }
        .content.active { 
            display: block; 
            opacity: 1;
            transform: translateY(0);
            animation: fadeInUp 0.5s ease-out;
        }
        .card {
            background: linear-gradient(135deg, rgba(255, 250, 252, 0.98) 0%, rgba(255, 240, 245, 0.95) 100%);
            padding: 35px; 
            border-radius: 25px;
            box-shadow: 
                0 10px 40px rgba(255, 182, 193, 0.25),
                0 0 0 4px rgba(255, 255, 255, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.8);
            border: 3px solid #ffb6c1;
            transition: all 0.3s ease;
            animation: kawaii-pulse 2s ease-in-out infinite;
        }
        .card:hover {
            transform: translateY(-5px) scale(1.01);
            box-shadow: 
                0 15px 50px rgba(255, 105, 180, 0.35),
                0 0 0 6px rgba(255, 255, 255, 0.6),
                inset 0 1px 0 rgba(255,255,255,0.9);
            border-color: #ff69b4;
        }
        .card h2 { margin-bottom: 25px; color: #ff69b4; font-weight: 700; font-size: 22px; }
        
        /* 欢迎页 */
        .welcome-stats {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px; margin-top: 25px;
        }
        .stat-card {
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            color: white; padding: 30px; border-radius: 25px;
            text-align: center;
            box-shadow: 
                0 10px 30px rgba(255, 105, 180, 0.4),
                0 0 0 4px rgba(255, 255, 255, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.6s ease-out;
            position: relative;
            overflow: hidden;
            border: 3px solid rgba(255, 255, 255, 0.6);
        }
        .stat-card::before {
            content: '🌸';
            position: absolute;
            top: 10px; right: 15px;
            font-size: 24px;
            opacity: 0.6;
            animation: heart-beat 2s ease-in-out infinite;
        }
        .stat-card::after {
            content: '✨';
            position: absolute;
            bottom: 10px; left: 15px;
            font-size: 18px;
            opacity: 0.5;
            animation: heart-beat 2s ease-in-out infinite 0.5s;
        }
        .stat-card:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 
                0 20px 40px rgba(255, 105, 180, 0.5),
                0 0 0 6px rgba(255, 255, 255, 0.7);
            border-color: #ff69b4;
        }
        .stat-card:nth-child(1) { animation-delay: 0.1s; background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%); }
        .stat-card:nth-child(2) { animation-delay: 0.2s; background: linear-gradient(135deg, #87ceeb 0%, #6495ed 100%); }
        .stat-card:nth-child(3) { animation-delay: 0.3s; background: linear-gradient(135deg, #dda0dd 0%, #da70d6 100%); }
        .stat-card h3 { font-size: 40px; margin-bottom: 10px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); font-weight: 700; }
        .stat-card p { font-size: 14px; opacity: 0.95; letter-spacing: 1px; font-weight: 600; }
        
        /* 插件列表 - 可爱风 */
        .plugin-list { display: grid; gap: 18px; }
        .plugin-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 22px 25px; background: rgba(255, 250, 252, 0.98); border-radius: 20px;
            border: 2px solid rgba(255, 182, 193, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.4s ease-out;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(255, 182, 193, 0.15);
        }
        .plugin-item::before {
            content: '🎀';
            position: absolute;
            left: -20px; top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            opacity: 0;
            transition: all 0.3s ease;
        }
        .plugin-item:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 30px rgba(255, 105, 180, 0.2);
            border-color: #ff69b4;
            padding-left: 45px;
        }
        .plugin-item:hover::before {
            opacity: 1;
            left: 15px;
        }
        .plugin-info h4 { color: #ff69b4; margin-bottom: 6px; font-size: 16px; font-weight: 600; }
        .plugin-info p { color: #ff8da1; font-size: 14px; }
        .plugin-meta { color: #ffb6c1; font-size: 12px; margin-top: 6px; font-weight: 500; }
        .toggle-btn {
            padding: 10px 18px; border: 2px solid transparent; border-radius: 15px;
            cursor: pointer; font-size: 13px; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            font-weight: 600;
            letter-spacing: 1px;
        }
        .toggle-btn.on { 
            background: linear-gradient(135deg, #69db7c 0%, #51cf66 100%);
            color: white;
            border-color: rgba(105, 219, 124, 0.8);
            box-shadow: 0 4px 15px rgba(105, 219, 124, 0.4);
        }
        .toggle-btn.on:hover {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 20px rgba(105, 219, 124, 0.5);
        }
        .toggle-btn.off { 
            background: linear-gradient(135deg, #adb5bd 0%, #868e96 100%);
            color: white;
            border-color: rgba(173, 181, 189, 0.8);
            box-shadow: 0 4px 15px rgba(173, 181, 189, 0.4);
        }
        .toggle-btn.off:hover {
            background: linear-gradient(135deg, #868e96 0%, #6c757d 100%);
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 20px rgba(173, 181, 189, 0.5);
        }
        
        /* 安装按钮 - 可爱风 */
        .install-btn {
            padding: 10px 20px;
            background: linear-gradient(135deg, #ffb6c1 0%, #ff69b4 100%);
            color: white;
            border: 2px solid rgba(255, 105, 180, 0.8);
            border-radius: 15px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(255, 105, 180, 0.4);
        }
        .install-btn:hover {
            background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 20px rgba(255, 105, 180, 0.5);
        }
        
        /* 插件市场卡片 - 可爱风 */
        .market-item {
            display: flex;
            flex-direction: column;
            padding: 25px;
            background: linear-gradient(135deg, rgba(255, 250, 252, 0.98) 0%, rgba(255, 240, 245, 0.95) 100%);
            border-radius: 20px;
            border: 2px solid rgba(255, 182, 193, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: fadeInUp 0.4s ease-out;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(255, 182, 193, 0.15);
        }
        .market-item::before {
            content: '📦';
            position: absolute;
            top: 15px; right: 15px;
            font-size: 24px;
            opacity: 0.6;
            animation: float-cute 3s ease-in-out infinite;
        }
        .market-item:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 15px 35px rgba(255, 105, 180, 0.25);
            border-color: #ff69b4;
        }
        .market-item h4 {
            color: #ff69b4;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 10px;
            padding-right: 30px;
        }
        .market-item .desc {
            color: #ff8da1;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 15px;
            flex-grow: 1;
        }
        .market-item .meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 15px;
            border-top: 1px dashed rgba(255, 182, 193, 0.5);
            font-size: 12px;
            color: #ffb6c1;
        }
        .market-item .author {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        /* 用户管理 */
        .user-form {
            display: flex; gap: 10px; margin-bottom: 20px;
            animation: fadeInUp 0.4s ease-out;
        }
        .user-form input {
            flex: 1; padding: 12px; border: 2px solid rgba(221, 221, 221, 0.5); 
            border-radius: 10px;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.8);
        }
        .user-form input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        .user-table { 
            width: 100%; border-collapse: collapse;
            animation: fadeInUp 0.5s ease-out 0.1s both;
        }
        .user-table th, .user-table td {
            padding: 14px; text-align: left; border-bottom: 1px solid rgba(233, 236, 239, 0.8);
        }
        .user-table th { 
            color: #667eea; font-weight: 600; 
            background: rgba(102, 126, 234, 0.05);
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }
        .user-table tr {
            transition: all 0.3s ease;
        }
        .user-table tr:hover { 
            background: rgba(102, 126, 234, 0.05);
            transform: scale(1.01);
        }
        .action-btn {
            padding: 8px 16px; border: 1px solid rgba(255,255,255,0.4); border-radius: 8px;
            cursor: pointer; font-size: 12px; margin-right: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
            position: relative;
            overflow: hidden;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
            background: rgba(255,255,255,0.15);
            box-shadow: 
                0 2px 8px rgba(0,0,0,0.1),
                inset 0 1px 0 rgba(255,255,255,0.3),
                inset 0 -1px 0 rgba(0,0,0,0.1);
        }
        .action-btn::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.1) 100%);
            border-radius: 8px;
            pointer-events: none;
        }
        .action-btn:hover {
            transform: translateY(-2px);
            background: rgba(255,255,255,0.25);
            box-shadow: 
                0 4px 12px rgba(0,0,0,0.15),
                inset 0 1px 0 rgba(255,255,255,0.4),
                inset 0 -1px 0 rgba(0,0,0,0.1);
        }
        .action-btn.edit { 
            background: rgba(52, 152, 219, 0.2);
            border-color: rgba(52, 152, 219, 0.5);
        }
        .action-btn.edit:hover {
            background: rgba(52, 152, 219, 0.3);
        }
        .action-btn.delete { 
            background: rgba(231, 76, 60, 0.2);
            border-color: rgba(231, 76, 60, 0.5);
        }
        .action-btn.delete:hover {
            background: rgba(231, 76, 60, 0.3);
        }
        
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <!-- 背景图片容器 -->
    <div id="bgContainer" class="bg-container"></div>
    <div class="bg-overlay"></div>
    
    <!-- 首次运行设置管理员 -->
    <div id="setupPage" class="login-overlay hidden">
        <div class="login-bg" id="setupBg"></div>
        <div class="login-bg-overlay"></div>
        <div class="login-box">
            <h2>🎉 欢迎来到 AstrBot 梦幻世界！</h2>
            <p class="subtitle">初次见面，请创建你的专属管理员身份吧~</p>
            <div class="form-group">
                <label>💕 取个可爱的昵称</label>
                <input type="text" id="setupUsername" placeholder="起个萌萌的名字吧~（至少3个字哦）">
            </div>
            <div class="form-group">
                <label>🔐 设置秘密密码</label>
                <input type="password" id="setupPassword" placeholder="设置一个安全的密码喵~（至少6位）">
            </div>
            <div class="form-group">
                <label>🔐 再确认一遍</label>
                <input type="password" id="setupPassword2" placeholder="再输一遍确认一下~">
            </div>
            <button class="login-btn" id="setupBtn" onclick="setupAdmin()">🌟 创建管理员身份</button>
            <div id="setupError" class="error-msg"></div>
        </div>
    </div>

    <!-- 登录界面 -->
    <div id="loginPage" class="login-overlay">
        <div class="login-bg" id="loginBg"></div>
        <div class="login-bg-overlay"></div>
        <div class="login-box">
            <h2>💖 欢迎回家~</h2>
            <p class="subtitle">快快输入信息，我们一起玩耍吧喵！</p>
            <div class="form-group">
                <label>💕 你的昵称</label>
                <input type="text" id="loginUsername" placeholder="输入你的可爱昵称~">
            </div>
            <div class="form-group">
                <label>🔐 秘密密码</label>
                <input type="password" id="loginPassword" placeholder="输入你的专属密码~" onkeypress="if(event.key==='Enter')doLogin()">
            </div>
            <button class="login-btn" id="loginBtn" onclick="doLogin()">🚀 冲呀！登录</button>
            <div id="loginError" class="error-msg"></div>
        </div>
    </div>

    <!-- 主界面 -->
    <div id="mainPage" class="container hidden">
        <div class="header">
            <h1>🌸 AstrBot 梦幻控制中枢</h1>
            <div class="user-info">
                <span id="currentUser"></span>
                <span id="userRole" class="user-role"></span>
                <button class="logout-btn" onclick="logout()">👋 下次见啦~</button>
            </div>
        </div>

        <div class="nav">
            <button class="nav-btn active" onclick="showPage('welcome')">🏠 温馨小窝</button>
            <button class="nav-btn" onclick="showPage('plugins')">🎒 魔法道具箱</button>
            <button class="nav-btn" onclick="showPage('market')">🛒 魔法商店街</button>
            <button class="nav-btn" onclick="showPage('personas')">🎨 换装小屋</button>
            <button id="usersNavBtn" class="nav-btn hidden" onclick="showPage('users')">👫 小伙伴名单</button>
        </div>

        <!-- 欢迎页 -->
        <div id="welcomePage" class="content active">
            <div class="card">
                <h2>🎊 欢迎回家，<span id="welcomeUser"></span>！</h2>
                <p style="color: #ff8da1; line-height: 1.8; font-weight: 500;">
                    这里是 AstrBot 的梦幻世界~<br>
                    <span id="welcomeText">可以整理魔法道具、逛商店街、换装打扮哦~</span>
                </p>
                <div class="welcome-stats">
                    <div class="stat-card">
                        <h3 id="statPlugins">0</h3>
                        <p>🎒 拥有的道具</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="statActive">0</h3>
                        <p>✨ 正在使用</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="statPersonas">0</h3>
                        <p>🎨 收藏装扮</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 插件管理 -->
        <div id="pluginsPage" class="content">
            <div class="card">
                <h2>🎒 魔法道具箱</h2>
                <div id="pluginList" class="plugin-list">
                    <p>🎀 正在召唤道具...</p>
                </div>
            </div>
        </div>

        <!-- 插件市场 -->
        <div id="marketPage" class="content">
            <div class="card">
                <h2>🛒 魔法商店街</h2>
                <div id="marketList" class="plugin-list">
                    <p>🎀 正在打开店门...</p>
                </div>
            </div>
        </div>

        <!-- 人格管理 -->
        <div id="personasPage" class="content">
            <div class="card">
                <h2>👤 人格管理</h2>
                <div id="personaList" class="plugin-list">
                    <p>加载中...</p>
                </div>
            </div>
        </div>

        <!-- 用户管理（仅管理员可见） -->
        <div id="usersPage" class="content">
            <div class="card">
                <h2>👥 用户管理</h2>
                <div class="user-form">
                    <input type="text" id="newUsername" placeholder="新用户名">
                    <input type="password" id="newPassword" placeholder="密码">
                    <button class="login-btn" onclick="createUser()" style="width: auto; padding: 10px 20px;">添加用户</button>
                </div>
                <table class="user-table">
                    <thead>
                        <tr>
                            <th>用户名</th>
                            <th>角色</th>
                            <th>创建时间</th>
                            <th>创建者</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="userTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let currentRole = null;
        
        // 本地背景图片列表
        let localBgImages = [];
        let currentBgIndex = -1;
        let usedBgIndices = [];
        let bgPreloadImage = new Image();
        
        // 加载本地背景图片列表
        async function loadLocalBackgrounds() {
            try {
                const res = await fetch('/api/backgrounds');
                const data = await res.json();
                if (data.success && data.data.length > 0) {
                    localBgImages = data.data;
                    console.log(`加载了 ${localBgImages.length} 张本地背景图片`);
                } else {
                    console.log('本地背景文件夹为空或不存在');
                    localBgImages = [];
                }
            } catch (e) {
                console.error('加载本地背景图片失败:', e);
                localBgImages = [];
            }
        }
        
        // 预加载下一张背景
        function preloadNextBg() {
            if (localBgImages.length === 0) return;
            
            let nextIndex;
            do {
                nextIndex = Math.floor(Math.random() * localBgImages.length);
            } while (nextIndex === currentBgIndex && localBgImages.length > 1);
            
            bgPreloadImage.src = '/api/background/' + localBgImages[nextIndex];
        }
        
        // 获取随机背景图片
        function getRandomBg() {
            if (localBgImages.length === 0) {
                return null;
            }
            
            // 如果所有图片都用过了，重置
            if (usedBgIndices.length >= localBgImages.length) {
                usedBgIndices = [];
            }
            
            // 随机选择一个未使用的索引
            let availableIndices = [];
            for (let i = 0; i < localBgImages.length; i++) {
                if (!usedBgIndices.includes(i)) {
                    availableIndices.push(i);
                }
            }
            
            const randomIndex = availableIndices[Math.floor(Math.random() * availableIndices.length)];
            usedBgIndices.push(randomIndex);
            currentBgIndex = randomIndex;
            
            return '/api/background/' + localBgImages[randomIndex];
        }
        
        // 切换背景图片 - 带淡入效果
        function changeBackground() {
            const bgContainer = document.getElementById('bgContainer');
            if (bgContainer && localBgImages.length > 0) {
                // 先淡出
                bgContainer.style.opacity = '0';
                
                setTimeout(() => {
                    const newBg = getRandomBg();
                    if (newBg) {
                        bgContainer.style.backgroundImage = `url(${newBg})`;
                        // 淡入
                        bgContainer.style.opacity = '1';
                        console.log('背景已切换:', newBg);
                        
                        // 预加载下一张
                        preloadNextBg();
                    }
                }, 300);
            }
        }
        
        // 设置登录页面背景
        function setLoginBackground() {
            const loginBg = document.getElementById('loginBg');
            const setupBg = document.getElementById('setupBg');
            if (localBgImages.length > 0) {
                const randomBg = '/api/background/' + localBgImages[Math.floor(Math.random() * localBgImages.length)];
                if (loginBg) loginBg.style.backgroundImage = `url(${randomBg})`;
                if (setupBg) setupBg.style.backgroundImage = `url(${randomBg})`;
                console.log('登录背景已设置:', randomBg);
            }
        }
        
        // 初始化背景
        async function initBackground() {
            await loadLocalBackgrounds();
            changeBackground();
            setLoginBackground();
        }

        // 检查是否首次运行
        async function checkFirstRun() {
            try {
                await loadLocalBackgrounds();
                setLoginBackground();
                
                const res = await fetch('/api/check_first_run');
                const data = await res.json();
                
                if (data.is_first_run) {
                    document.getElementById('setupPage').classList.remove('hidden');
                    document.getElementById('loginPage').classList.add('hidden');
                } else {
                    document.getElementById('setupPage').classList.add('hidden');
                    document.getElementById('loginPage').classList.remove('hidden');
                    checkAuth();
                }
            } catch (e) {
                console.error('检查首次运行失败:', e);
            }
        }

        // 设置管理员
        async function setupAdmin() {
            const username = document.getElementById('setupUsername').value.trim();
            const password = document.getElementById('setupPassword').value;
            const password2 = document.getElementById('setupPassword2').value;
            const btn = document.getElementById('setupBtn');
            const error = document.getElementById('setupError');
            
            if (!username || username.length < 3) {
                error.textContent = '用户名至少3位';
                return;
            }
            if (!password || password.length < 6) {
                error.textContent = '密码至少6位';
                return;
            }
            if (password !== password2) {
                error.textContent = '两次密码不一致';
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '创建中...';
            error.textContent = '';
            
            try {
                const res = await fetch('/api/setup_admin', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('管理员创建成功！请登录');
                    location.reload();
                } else {
                    error.textContent = data.message || '创建失败';
                    btn.disabled = false;
                    btn.textContent = '创建管理员账号';
                }
            } catch (e) {
                error.textContent = '网络错误';
                btn.disabled = false;
                btn.textContent = '创建管理员账号';
            }
        }

        // 登录
        async function doLogin() {
            const username = document.getElementById('loginUsername').value.trim();
            const password = document.getElementById('loginPassword').value;
            const btn = document.getElementById('loginBtn');
            const error = document.getElementById('loginError');
            
            if (!username || !password) {
                error.textContent = '请输入用户名和密码';
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '登录中...';
            error.textContent = '';
            
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    currentUser = data.data.username;
                    currentRole = data.data.role;
                    showMainPage();
                } else {
                    error.textContent = data.message || '登录失败';
                    btn.disabled = false;
                    btn.textContent = '登录';
                }
            } catch (e) {
                error.textContent = '网络错误';
                btn.disabled = false;
                btn.textContent = '登录';
            }
        }

        // 显示主页面
        function showMainPage() {
            document.getElementById('loginPage').classList.add('hidden');
            document.getElementById('mainPage').classList.remove('hidden');
            
            document.getElementById('currentUser').textContent = currentUser;
            document.getElementById('welcomeUser').textContent = currentUser;
            
            const roleBadge = document.getElementById('userRole');
            roleBadge.textContent = currentRole === 'admin' ? '管理员' : '普通用户';
            roleBadge.className = 'user-role ' + currentRole;
            
            // 管理员显示用户管理
            if (currentRole === 'admin') {
                document.getElementById('usersNavBtn').classList.remove('hidden');
                document.getElementById('welcomeText').textContent = '作为管理员，您可以管理所有插件和用户。';
            } else {
                document.getElementById('welcomeText').textContent = '您可以查看插件信息和人格配置。';
            }
            
            // 初始化背景图片
            initBackground();
            
            loadStats();
        }

        // 页面切换
        function showPage(page) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            
            document.getElementById(page + 'Page').classList.add('active');
            event.target.classList.add('active');
            
            // 切换页面时更换背景图片
            changeBackground();
            
            if (page === 'plugins') loadPlugins();
            if (page === 'market') loadMarket();
            if (page === 'personas') loadPersonas();
            if (page === 'users') loadUsers();
        }

        // 登出
        async function logout() {
            await fetch('/api/logout', {method: 'POST'});
            location.reload();
        }

        // 加载统计
        async function loadStats() {
            try {
                const res = await fetch('/api/plugins');
                const data = await res.json();
                if (data.success) {
                    document.getElementById('statPlugins').textContent = data.data.length;
                    document.getElementById('statActive').textContent = 
                        data.data.filter(p => p.activated).length;
                }
                
                const personaRes = await fetch('/api/personas');
                const personaData = await personaRes.json();
                if (personaData.success) {
                    document.getElementById('statPersonas').textContent = personaData.data.length;
                }
            } catch (e) {
                console.error('加载统计失败:', e);
            }
        }

        // 加载插件
        async function loadPlugins() {
            const list = document.getElementById('pluginList');
            list.innerHTML = '<p>🎀 正在召唤道具...</p>';
            
            try {
                const res = await fetch('/api/plugins');
                const data = await res.json();
                
                if (data.success && data.data.length > 0) {
                    // 添加第三方插件安装入口（仅管理员）
                    let customInstallHtml = '';
                    if (currentRole === 'admin') {
                        customInstallHtml = `
                            <div class="plugin-item" style="background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.98) 100%); border: 2px dashed #ffb6c1;">
                                <div class="plugin-info">
                                    <h4>🌟 安装第三方插件</h4>
                                    <p>输入 GitHub 或其他 Git 仓库地址安装插件~</p>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <input type="text" id="customPluginUrl" placeholder="https://github.com/xxx/xxx" 
                                           style="padding: 8px 12px; border: 2px solid rgba(255, 182, 193, 0.5); border-radius: 10px; width: 250px;">
                                    <button class="install-btn" onclick="installCustomPlugin()">🚀 安装</button>
                                </div>
                            </div>
                        `;
                    }
                    
                    // 添加批量更新按钮（仅管理员）
                    let updateAllHtml = '';
                    if (currentRole === 'admin') {
                        updateAllHtml = `
                            <div style="margin-bottom: 20px; text-align: right;">
                                <button class="install-btn" onclick="updateAllPlugins()">🔄 一键更新所有插件</button>
                            </div>
                        `;
                    }
                    
                    list.innerHTML = updateAllHtml + customInstallHtml + data.data.map(p => {
                        const hasUpdate = p.has_update || false;
                        return `
                        <div class="plugin-item">
                            <div class="plugin-info">
                                <h4>${p.name} ${p.reserved ? '🔒' : ''}</h4>
                                <p>${p.description || '这个插件还没有描述呢~'}</p>
                                <div class="plugin-meta">
                                    💕 作者: ${p.author || '神秘作者'} | 📌 版本: ${p.version || '1.0.0'}
                                    ${p.repo ? `| 🔗 <a href="${p.repo}" target="_blank">去看看</a>` : ''}
                                    ${hasUpdate ? '| 🆕 有新版本' : ''}
                                </div>
                            </div>
                            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">
                                ${currentRole === 'admin' ? `
                                    <button class="toggle-btn ${p.activated ? 'on' : 'off'}" 
                                            onclick="togglePlugin('${p.name}', ${!p.activated})">
                                        ${p.activated ? '✨ 运行中' : '💤 已停止'}
                                    </button>
                                    ${hasUpdate ? `<button class="install-btn" onclick="updatePlugin('${p.name}')">🆕 更新</button>` : ''}
                                    ${!p.reserved ? `<button class="toggle-btn off" onclick="uninstallPlugin('${p.name}')">🗑️ 卸载</button>` : ''}
                                ` : `<span class="toggle-btn ${p.activated ? 'on' : 'off'}">${p.activated ? '✨ 运行中' : '💤 已停止'}</span>`}
                            </div>
                        </div>
                    `}).join('');
                } else {
                    // 没有插件时显示第三方安装入口
                    let html = '<p>🎀 还没有插件哦，快去商店看看吧~</p>';
                    if (currentRole === 'admin') {
                        html += `
                            <div class="plugin-item" style="margin-top: 20px; background: linear-gradient(135deg, rgba(255, 240, 245, 0.95) 0%, rgba(255, 228, 235, 0.98) 100%); border: 2px dashed #ffb6c1;">
                                <div class="plugin-info">
                                    <h4>🌟 安装第三方插件</h4>
                                    <p>输入 GitHub 或其他 Git 仓库地址安装插件~</p>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <input type="text" id="customPluginUrl" placeholder="https://github.com/xxx/xxx" 
                                           style="padding: 8px 12px; border: 2px solid rgba(255, 182, 193, 0.5); border-radius: 10px; width: 250px;">
                                    <button class="install-btn" onclick="installCustomPlugin()">🚀 安装</button>
                                </div>
                            </div>
                        `;
                    }
                    list.innerHTML = html;
                }
            } catch (e) {
                list.innerHTML = '<p>😢 加载失败了，请稍后再试~</p>';
            }
        }
        
        // 更新单个插件
        async function updatePlugin(name) {
            if (!confirm(`确定要更新插件 ${name} 吗？`)) return;
            
            try {
                const res = await fetch('/api/plugins/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('🎉 插件更新成功啦~');
                    loadPlugins();
                    loadStats();
                } else {
                    alert(data.message || '😢 更新失败了');
                }
            } catch (e) {
                alert('😢 网络出错了，请稍后再试~');
            }
        }
        
        // 一键更新所有插件
        async function updateAllPlugins() {
            if (!confirm('确定要更新所有插件吗？这可能需要一些时间哦~')) return;
            
            try {
                const res = await fetch('/api/plugins/update-all', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('🎉 所有插件都更新成功啦~');
                    loadPlugins();
                    loadStats();
                } else {
                    alert(data.message || '😢 批量更新失败了');
                }
            } catch (e) {
                alert('😢 网络出错了，请稍后再试~');
            }
        }
        
        // 安装第三方插件
        async function installCustomPlugin() {
            const url = document.getElementById('customPluginUrl').value.trim();
            if (!url) {
                alert('😢 请输入插件仓库地址哦~');
                return;
            }
            
            if (!confirm(`确定要安装这个插件吗？\n仓库: ${url}`)) return;
            
            try {
                const res = await fetch('/api/plugins/install-custom', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('🎉 第三方插件安装成功啦~');
                    document.getElementById('customPluginUrl').value = '';
                    loadPlugins();
                    loadStats();
                } else {
                    alert(data.message || '😢 安装失败了');
                }
            } catch (e) {
                alert('😢 网络出错了，请稍后再试~');
            }
        }

        // 切换插件
        async function togglePlugin(name, activate) {
            try {
                await fetch('/api/plugins/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, activated: activate})
                });
                loadPlugins();
                loadStats();
            } catch (e) {
                alert('😢 操作失败了，请稍后再试~');
            }
        }

        // 卸载插件
        async function uninstallPlugin(name) {
            if (!confirm(`确定要卸载插件 ${name} 吗？卸载后就见不到它了哦~ 😢`)) return;
            
            try {
                const res = await fetch('/api/plugins/uninstall', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('🎉 插件卸载成功啦~');
                    loadPlugins();
                    loadStats();
                } else {
                    alert(data.message || '😢 卸载失败了');
                }
            } catch (e) {
                alert('😢 网络出错了，请稍后再试~');
            }
        }

        // 加载市场
        async function loadMarket() {
            const list = document.getElementById('marketList');
            list.innerHTML = '<p>🎀 正在加载插件商店...</p>';
            
            try {
                const res = await fetch('/api/market');
                const data = await res.json();
                
                if (data.success && data.data.length > 0) {
                    list.innerHTML = '<div class="market-grid">' + data.data.map((p, index) => {
                        const emojis = ['🌸', '✨', '🎀', '💖', '🌟', '💕', '🎨', '🎪', '🎭', '🎸'];
                        const emoji = emojis[index % emojis.length];
                        return `
                        <div class="market-item" style="animation-delay: ${index * 0.1}s">
                            <h4>${emoji} ${p.name}</h4>
                            <p class="desc">${p.desc || '这个插件还没有描述呢，但看起来很有趣哦~'}</p>
                            <div class="meta">
                                <div class="author">
                                    💕 ${p.author || '神秘作者'}
                                </div>
                                <div>
                                    📌 v${p.version || '1.0.0'}
                                </div>
                            </div>
                            ${currentRole === 'admin' ? 
                                `<button class="install-btn" onclick="installPlugin('${p.name}', '${p.repo}')" style="margin-top: 15px; width: 100%;">🎁 安装这个插件</button>` : 
                                `<span class="toggle-btn off" style="cursor: not-allowed; margin-top: 15px; width: 100%; display: block; text-align: center;" title="只有管理员才能安装插件哦~">🔒 仅管理员可安装</span>`}
                        </div>
                    `}).join('') + '</div>';
                } else {
                    list.innerHTML = '<p>🎀 商店里还没有插件呢，过段时间再来看看吧~</p>';
                }
            } catch (e) {
                list.innerHTML = '<p>😢 加载失败了，请稍后再试~</p>';
            }
        }

        // 安装插件
        async function installPlugin(name, repo) {
            if (!repo) {
                alert('😢 这个插件没有提供仓库地址，暂时无法安装呢~');
                return;
            }
            
            if (!confirm(`确定要安装插件 ${name} 吗？\n仓库: ${repo}`)) return;
            
            try {
                const res = await fetch('/api/plugins/install', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, repo})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('插件安装成功');
                    loadPlugins();
                    loadStats();
                } else {
                    alert(data.message || '安装失败');
                }
            } catch (e) {
                alert('网络错误');
            }
        }

        // 加载人格
        async function loadPersonas() {
            const list = document.getElementById('personaList');
            list.innerHTML = '<p>加载中...</p>';
            
            try {
                const res = await fetch('/api/personas');
                const data = await res.json();
                
                if (data.success && data.data.length > 0) {
                    list.innerHTML = data.data.map(p => `
                        <div class="plugin-item">
                            <div class="plugin-info">
                                <h4>${p.name}</h4>
                                <p>${p.description || '暂无描述'}</p>
                            </div>
                            ${currentRole === 'admin' ? 
                                `<button class="toggle-btn on">编辑</button>` : 
                                ''}
                        </div>
                    `).join('');
                } else {
                    list.innerHTML = '<p>暂无人格配置</p>';
                }
            } catch (e) {
                list.innerHTML = '<p>加载失败</p>';
            }
        }

        // 加载用户列表
        async function loadUsers() {
            const tbody = document.getElementById('userTableBody');
            tbody.innerHTML = '<tr><td colspan="5">加载中...</td></tr>';
            
            try {
                const res = await fetch('/api/users');
                const data = await res.json();
                
                if (data.success && data.data.length > 0) {
                    tbody.innerHTML = data.data.map(u => `
                        <tr>
                            <td>${u.username}</td>
                            <td>${u.role === 'admin' ? '管理员' : '普通用户'}</td>
                            <td>${new Date(u.created_at).toLocaleString()}</td>
                            <td>${u.created_by}</td>
                            <td>
                                ${u.role !== 'admin' ? `
                                    <button class="action-btn edit" onclick="resetPassword('${u.username}')">重置密码</button>
                                    <button class="action-btn delete" onclick="deleteUser('${u.username}')">删除</button>
                                ` : '<span>不可操作</span>'}
                            </td>
                        </tr>
                    `).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="5">暂无用户</td></tr>';
                }
            } catch (e) {
                tbody.innerHTML = '<tr><td colspan="5">加载失败</td></tr>';
            }
        }

        // 创建用户
        async function createUser() {
            const username = document.getElementById('newUsername').value.trim();
            const password = document.getElementById('newPassword').value;
            
            if (!username || !password) {
                alert('请输入用户名和密码');
                return;
            }
            
            try {
                const res = await fetch('/api/users', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('用户创建成功');
                    document.getElementById('newUsername').value = '';
                    document.getElementById('newPassword').value = '';
                    loadUsers();
                } else {
                    alert(data.message || '创建失败');
                }
            } catch (e) {
                alert('网络错误');
            }
        }

        // 删除用户
        async function deleteUser(username) {
            if (!confirm(`确定要删除用户 ${username} 吗？`)) return;
            
            try {
                const res = await fetch(`/api/users/${username}`, {method: 'DELETE'});
                const data = await res.json();
                
                if (data.success) {
                    alert('用户已删除');
                    loadUsers();
                } else {
                    alert(data.message || '删除失败');
                }
            } catch (e) {
                alert('网络错误');
            }
        }

        // 重置密码
        async function resetPassword(username) {
            const newPassword = prompt(`请输入 ${username} 的新密码（至少6位）：`);
            if (!newPassword || newPassword.length < 6) {
                alert('密码至少6位');
                return;
            }
            
            try {
                const res = await fetch(`/api/users/${username}/reset_password`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_password: newPassword})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert('密码已重置');
                } else {
                    alert(data.message || '重置失败');
                }
            } catch (e) {
                alert('网络错误');
            }
        }

        // 检查认证
        async function checkAuth() {
            try {
                const res = await fetch('/api/check_auth');
                const data = await res.json();
                if (data.success) {
                    currentUser = data.data.username;
                    currentRole = data.data.role;
                    showMainPage();
                }
            } catch (e) {
                console.log('未登录');
            }
        }

        // 页面加载时检查
        checkFirstRun();
    </script>
</body>
</html>'''
    
    async def terminate(self):
        """关闭"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("[Dashboard] 管理面板已关闭")
        except Exception as e:
            logger.error(f"[Dashboard] 关闭错误: {e}")
