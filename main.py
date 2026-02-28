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

🎀 这是插件的入口文件，主要逻辑已拆分到 webui/ 目录下的各个模块中~
"""

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger

from .webui import AstrBotDashboard


class WebUIPlugin(Star):
    """
    🌸 AstrBot WebUI 插件入口
    💕 负责初始化和生命周期管理~
    """
    
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.context = context
        self.config = config or {}
        
        # 创建 Dashboard 实例
        self.dashboard = AstrBotDashboard(context, config)
        
        logger.info("✨ [WebUIPlugin] 插件入口初始化完成~")
    
    async def initialize(self):
        """🚀 插件初始化时调用"""
        await self.dashboard.initialize()
    
    async def terminate(self):
        """🛑 插件关闭时调用"""
        await self.dashboard.terminate()


# 导出插件类
__all__ = ['WebUIPlugin', 'AstrBotDashboard']
