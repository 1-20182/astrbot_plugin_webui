"""
🌸 AstrBot WebUI 模块包 ✨
═══════════════════════════════════════
💕 包含所有 WebUI 相关的功能模块~
═══════════════════════════════════════
"""

from .user_manager import UserManager
from .dashboard import AstrBotDashboard
from .templates import get_html_template

__all__ = [
    'UserManager',
    'AstrBotDashboard', 
    'get_html_template',
]
