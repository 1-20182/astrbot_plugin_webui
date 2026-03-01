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
import html
import json
import os
import platform
import secrets
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 🎀 尝试导入依赖
try:
    import aiohttp
    from aiohttp import web
    import certifi
    import ssl
    import bcrypt
    AIOHTTP_AVAILABLE = True
except ImportError as e:
    AIOHTTP_AVAILABLE = False
    AIOHTTP_ERROR = str(e)

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

from .user_manager import UserManager
from .templates import get_html_template

# 🖥️ 操作系统检测
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'


class AstrBotDashboard(Star):
    """
    🌸 AstrBot 梦幻 WebUI 插件
    💕 多用户管理面板，安全又可爱~
    """
    
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
        
        # 🔐 CSRF token 管理
        self.csrf_tokens: Dict[str, str] = {}
        
        # 数据目录
        try:
            from astrbot.core.star.star_tools import StarTools
            self.data_dir = Path(StarTools.get_data_dir())
        except Exception:
            self.data_dir = Path(getattr(context, 'data_dir', 'data/plugins/webui'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户管理
        self.user_manager = UserManager(str(self.data_dir))
        
        # 会话管理
        self.sessions: Dict[str, dict] = {}
        
        # Web 服务器
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        logger.info("✨ [Dashboard] 梦幻 WebUI 插件初始化完成~")
    
    def _generate_csrf_token(self) -> str:
        """🔐 生成 CSRF token"""
        return secrets.token_urlsafe(32)
    
    async def _validate_csrf_token(self, request: web.Request) -> bool:
        """🔐 验证 CSRF token"""
        try:
            csrf_token = request.headers.get('X-CSRF-Token', '')
            if not csrf_token:
                data = await request.json()
                csrf_token = data.get('csrf_token', '')
            
            session_id = request.cookies.get('session_id', '')
            if not session_id or session_id not in self.csrf_tokens:
                return False
            
            expected_token = self.csrf_tokens.get(session_id, '')
            return secrets.compare_digest(csrf_token, expected_token)
        except Exception:
            return False
    
    def _escape_html(self, text: str) -> str:
        """🛡️ 转义 HTML（防止 XSS 攻击~）"""
        if not isinstance(text, str):
            text = str(text)
        return html.escape(text, quote=True)
    
    async def _get_local_ip(self) -> str:
        """🌐 获取本地 IP（异步版本~）"""
        try:
            import asyncio
            import socket
            loop = asyncio.get_event_loop()
            
            def _sync_get_ip():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(2)
                    try:
                        s.connect(('8.8.8.8', 80))
                        ip = s.getsockname()[0]
                    except Exception:
                        ip = '127.0.0.1'
                    finally:
                        s.close()
                    return ip
                except Exception:
                    return '127.0.0.1'
            
            ip = await loop.run_in_executor(None, _sync_get_ip)
            return ip
        except Exception as e:
            logger.warning(f"⚠️ 获取本地 IP 失败: {e}")
            return '127.0.0.1'
    
    async def initialize(self):
        """初始化"""
        if self._disabled:
            return
        
        try:
            await self._start_server()
            
            local_ip = await self._get_local_ip()
            
            logger.info("=" * 60)
            logger.info("✅ AstrBot 多用户管理面板启动成功！")
            logger.info("")
            logger.info("🌐 访问地址:")
            logger.info(f"   本机: http://127.0.0.1:{self.port}")
            if local_ip != '127.0.0.1':
                logger.info(f"   局域网: http://{local_ip}:{self.port}")
            logger.info("")
            
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
        
        # 用户管理
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
    
    # ========== 页面处理函数 ==========
    
    async def _handle_index(self, request: web.Request):
        """主页面"""
        return web.Response(text=get_html_template(), content_type='text/html')
    
    # ========== 认证相关 API ==========
    
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
                
                csrf_token = self._generate_csrf_token()
                self.csrf_tokens[session_id] = csrf_token
                
                response = web.json_response({
                    'success': True,
                    'message': '登录成功',
                    'data': {
                        'username': user['username'],
                        'role': user['role'],
                        'csrf_token': csrf_token
                    }
                })
                response.set_cookie(
                    'session_id', 
                    session_id, 
                    httponly=True,
                    secure=False,
                    samesite='Lax',
                    max_age=self.session_timeout
                )
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
    
    # ========== 用户管理 API ==========
    
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
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
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
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
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
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
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
    
    # ========== 插件管理 API ==========
    
    async def _handle_get_plugins(self, request: web.Request):
        """获取已安装的插件列表"""
        error = self._check_auth(request)
        if error:
            return error
        
        try:
            plugins = []
            plugin_names = set()
            
            # 方式1: 从 star_registry 获取
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
            except Exception as e:
                logger.warning(f"[Dashboard] 从 star_registry 获取失败: {e}")
            
            # 方式2: 从插件目录扫描
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
                except Exception as e:
                    logger.warning(f"[Dashboard] 从插件目录扫描失败: {e}")
            
            return web.json_response({'success': True, 'data': plugins})
        except Exception as e:
            logger.error(f"[Dashboard] 获取插件失败: {e}")
            return web.json_response({'success': False, 'message': '获取失败'})
    
    async def _handle_toggle_plugin(self, request: web.Request):
        """切换插件状态"""
        error = self._check_auth(request)
        if error:
            return error
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            activated = data.get('activated')
            
            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager:
                if activated:
                    if hasattr(plugin_manager, 'turn_on_plugin'):
                        await plugin_manager.turn_on_plugin(plugin_name)
                else:
                    if hasattr(plugin_manager, 'turn_off_plugin'):
                        await plugin_manager.turn_off_plugin(plugin_name)
                
                return web.json_response({'success': True, 'message': '操作成功'})
            
            return web.json_response({'success': False, 'message': '插件管理功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 切换插件状态失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
        
    async def _handle_install_plugin(self, request: web.Request):
        """安装插件"""
        error = self._check_auth(request)
        if error:
            logger.warning(f"[Dashboard] 安装插件 - 认证失败: {error}")
            return error
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            logger.warning("[Dashboard] 安装插件 - CSRF 验证失败")
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            logger.warning(f"[Dashboard] 安装插件 - 用户 {user.get('username')} 无权限")
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            repo_url = data.get('repo')
            
            logger.info(f"[Dashboard] 开始安装插件: {plugin_name}, 仓库: {repo_url}")
            
            if not repo_url:
                return web.json_response({'success': False, 'message': '缺少插件仓库地址'})
            
            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager:
                logger.info(f"[Dashboard] _star_manager 类型: {type(plugin_manager)}")
                if hasattr(plugin_manager, 'install_plugin'):
                    logger.info(f"[Dashboard] 调用 install_plugin: {repo_url}")
                    try:
                        result = await plugin_manager.install_plugin(repo_url)
                        logger.info(f"[Dashboard] install_plugin 返回: {result}")
                        # AstrBot 的 install_plugin 下载成功但加载失败时返回 None
                        # 只要没抛异常，就认为安装成功
                        logger.info(f"[Dashboard] 插件 {plugin_name} 安装成功")
                        return web.json_response({'success': True, 'message': '插件安装成功，请重启 AstrBot 完成加载'})
                    except Exception as install_error:
                        logger.error(f"[Dashboard] install_plugin 抛出异常: {install_error}")
                        return web.json_response({'success': False, 'message': f'安装失败: {str(install_error)}'})
                else:
                    logger.error("[Dashboard] _star_manager 没有 install_plugin 方法")
            else:
                logger.error(f"[Dashboard] context 没有 _star_manager，可用属性: {[attr for attr in dir(self.context) if not attr.startswith('__')]}")
            
            return web.json_response({'success': False, 'message': '插件安装功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 安装插件失败: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_uninstall_plugin(self, request: web.Request):
        """卸载插件"""
        error = self._check_auth(request)
        if error:
            logger.warning(f"[Dashboard] 卸载插件 - 认证失败: {error}")
            return error
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            logger.warning("[Dashboard] 卸载插件 - CSRF 验证失败")
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            logger.warning(f"[Dashboard] 卸载插件 - 用户 {user.get('username')} 无权限")
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            
            logger.info(f"[Dashboard] 开始卸载插件: {plugin_name}")
            
            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager:
                logger.info(f"[Dashboard] _star_manager 类型: {type(plugin_manager)}")
                if hasattr(plugin_manager, 'uninstall_plugin'):
                    logger.info(f"[Dashboard] 调用 uninstall_plugin: {plugin_name}")
                    await plugin_manager.uninstall_plugin(plugin_name)
                    logger.info(f"[Dashboard] 插件 {plugin_name} 卸载成功")
                    return web.json_response({'success': True, 'message': '插件卸载成功'})
                else:
                    logger.error("[Dashboard] _star_manager 没有 uninstall_plugin 方法")
            else:
                logger.error(f"[Dashboard] context 没有 _star_manager")
            
            return web.json_response({'success': False, 'message': '插件卸载功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 卸载插件失败: {e}")
            logger.error(traceback.format_exc())
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_update_plugin(self, request: web.Request):
        """更新单个插件"""
        error = self._check_auth(request)
        if error:
            return error
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            data = await request.json()
            plugin_name = data.get('name')
            
            if not plugin_name:
                return web.json_response({'success': False, 'message': '缺少插件名称'})
            
            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager and hasattr(plugin_manager, 'update_plugin'):
                await plugin_manager.update_plugin(plugin_name)
                logger.info(f"[Dashboard] 插件 {plugin_name} 更新成功")
                return web.json_response({'success': True, 'message': '🎉 插件更新成功啦~'})
            
            return web.json_response({'success': False, 'message': '插件更新功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 更新插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_update_all_plugins(self, request: web.Request):
        """更新所有插件"""
        error = self._check_auth(request)
        if error:
            return error
        
        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)
        
        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)
        
        try:
            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager:
                # 获取所有可更新的插件
                plugins = []
                try:
                    from astrbot.core.star.context import star_registry
                    for star in star_registry:
                        if getattr(star, 'repo', None) and not getattr(star, 'reserved', False):
                            plugins.append(getattr(star, 'name', ''))
                except Exception as e:
                    logger.warning(f"[Dashboard] 获取插件列表失败: {e}")
                
                updated = []
                failed = []
                for plugin_name in plugins:
                    try:
                        if hasattr(plugin_manager, 'update_plugin'):
                            await plugin_manager.update_plugin(plugin_name)
                            updated.append(plugin_name)
                    except Exception as e:
                        failed.append(f"{plugin_name}: {str(e)}")
                
                if failed and not updated:
                    return web.json_response({'success': False, 'message': f'所有插件更新失败: {"; ".join(failed)}'})
                elif failed:
                    return web.json_response({'success': True, 'message': f'更新完成！成功 {len(updated)} 个，失败 {len(failed)} 个'})
                else:
                    logger.info("[Dashboard] 所有插件更新成功")
                    return web.json_response({'success': True, 'message': '🎉 所有插件都更新成功啦~'})
            
            return web.json_response({'success': False, 'message': '批量更新功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 批量更新插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _handle_install_custom_plugin(self, request: web.Request):
        """从自定义 URL 安装插件"""
        error = self._check_auth(request)
        if error:
            return error

        # 验证 CSRF token
        if not await self._validate_csrf_token(request):
            return web.json_response({'success': False, 'message': 'CSRF token 验证失败'}, status=403)

        user = self._get_current_user(request)
        if user['role'] != 'admin':
            return web.json_response({'success': False, 'message': '无权限'}, status=403)

        try:
            data = await request.json()
            repo_url = data.get('url')

            if not repo_url:
                return web.json_response({'success': False, 'message': '请输入插件仓库地址哦~'})

            if not (repo_url.startswith('http://') or repo_url.startswith('https://')):
                return web.json_response({'success': False, 'message': '仓库地址格式不正确'})

            # 尝试获取 plugin_manager（AstrBot 存储在 _star_manager 中）
            plugin_manager = getattr(self.context, '_star_manager', None)
            if plugin_manager and hasattr(plugin_manager, 'install_plugin'):
                try:
                    result = await plugin_manager.install_plugin(repo_url)
                    logger.info(f"[Dashboard] install_plugin 返回: {result}")
                    # AstrBot 的 install_plugin 下载成功但加载失败时返回 None
                    # 只要没抛异常，就认为安装成功
                    logger.info(f"[Dashboard] 第三方插件安装成功: {repo_url}")
                    return web.json_response({'success': True, 'message': '🎉 第三方插件安装成功啦~请重启 AstrBot 完成加载'})
                except Exception as install_error:
                    logger.error(f"[Dashboard] install_plugin 抛出异常: {install_error}")
                    return web.json_response({'success': False, 'message': f'安装失败: {str(install_error)}'})

            return web.json_response({'success': False, 'message': '插件安装功能暂不可用'})
        except Exception as e:
            logger.error(f"[Dashboard] 安装第三方插件失败: {e}")
            return web.json_response({'success': False, 'message': str(e)})
    
    # ========== 插件市场 API ==========
    
    async def _handle_get_market(self, request: web.Request):
        """获取远程插件市场"""
        error = self._check_auth(request)
        if error:
            return error
        
        plugins = []
        
        try:
            data_dir = get_astrbot_data_path()
            cache_file = os.path.join(data_dir, "plugins.json")
            
            # 尝试从缓存读取
            try:
                if os.path.exists(cache_file):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        if isinstance(cache_data, dict) and 'data' in cache_data:
                            data_content = cache_data['data']
                            if isinstance(data_content, list):
                                plugins = data_content
                            elif isinstance(data_content, dict):
                                plugins = list(data_content.values())
                        elif isinstance(cache_data, list):
                            plugins = cache_data
            except Exception as e:
                logger.error(f"[Dashboard] 读取缓存失败: {e}")
            
            # 从网络获取
            if not plugins:
                urls = [
                    "https://api.soulter.top/astrbot/plugins",
                    "https://github.com/AstrBotDevs/AstrBot_Plugins_Collection/raw/refs/heads/main/plugin_cache_original.json",
                ]
                
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                
                for url in urls:
                    try:
                        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10, limit_per_host=5)
                        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
                            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                                if response.status == 200:
                                    try:
                                        data = await response.json()
                                    except:
                                        text = await response.text()
                                        data = json.loads(text)
                                    
                                    if isinstance(data, list) and len(data) > 0:
                                        plugins = data
                                        break
                                    elif isinstance(data, dict):
                                        if 'data' in data:
                                            data_content = data['data']
                                            if isinstance(data_content, list):
                                                plugins = data_content
                                            elif isinstance(data_content, dict):
                                                plugins = list(data_content.values())
                                            break
                                        else:
                                            plugins = list(data.values())
                                            break
                    except Exception as e:
                        logger.error(f"[Dashboard] 从 {url} 获取失败: {e}")
                        continue
            
            # 格式化插件数据
            formatted_plugins = []
            if plugins:
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
            
            return web.json_response({'success': True, 'data': formatted_plugins})
        except Exception as e:
            logger.error(f"[Dashboard] 获取插件市场失败: {e}")
            return web.json_response({'success': False, 'message': f'获取失败: {str(e)}'})
    
    # ========== 人格管理 API ==========
    
    async def _handle_get_personas(self, request: web.Request):
        """获取人格列表"""
        error = self._check_auth(request)
        if error:
            return error
        
        try:
            personas = []
            
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
            
            if not personas:
                return web.json_response({
                    'success': True,
                    'data': [],
                    'message': '还没有人格配置哦，快去创建一个吧~'
                })
            
            return web.json_response({'success': True, 'data': personas})
        except Exception as e:
            logger.error(f"[Dashboard] 获取人格列表失败: {e}")
            return web.json_response({'success': False, 'message': '获取失败'})
    
    # ========== 背景图片 API ==========
    
    async def _handle_get_backgrounds(self, request: web.Request):
        """获取背景图片列表"""
        try:
            # 背景图片在插件根目录的 background/ 文件夹
            bg_dir = Path(__file__).parent.parent / 'background'
            if not bg_dir.exists():
                return web.json_response({'success': True, 'data': [], 'message': '背景文件夹不存在'})
            
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
            
            # 安全检查
            if '..' in filename or '/' in filename or '\\' in filename:
                return web.json_response({'success': False, 'message': '非法文件名'})
            
            # 背景图片在插件根目录的 background/ 文件夹
            bg_dir = Path(__file__).parent.parent / 'background'
            image_path = bg_dir / filename
            
            if not image_path.exists() or not image_path.is_file():
                return web.json_response({'success': False, 'message': '图片不存在'})
            
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
