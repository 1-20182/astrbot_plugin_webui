"""
用户管理系统 - 支持管理员和普通用户（QQ号）
"""
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

from astrbot.api import logger
from astrbot.core.utils.astrbot_path import get_astrbot_data_path


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.data_dir = Path(get_astrbot_data_path()) / "webui_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.users_file = self.data_dir / "users.json"
        self.user_plugins_file = self.data_dir / "user_plugins.json"
        self.group_plugins_file = self.data_dir / "group_plugins.json"
        
        # 用户数据 {qq: {"password_hash": str, "created_at": str, "created_by": str}}
        self.users: Dict[str, dict] = {}
        
        # 用户-插件配置 {qq: {"allowed_plugins": [str], "denied_plugins": [str]}}
        self.user_plugins: Dict[str, dict] = {}
        
        # 群组-插件配置 {group_id: {"allowed_plugins": [str], "denied_plugins": [str]}}
        self.group_plugins: Dict[str, dict] = {}
        
        self._load_data()
    
    def _load_data(self):
        """加载用户数据"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            
            if self.user_plugins_file.exists():
                with open(self.user_plugins_file, 'r', encoding='utf-8') as f:
                    self.user_plugins = json.load(f)
            
            if self.group_plugins_file.exists():
                with open(self.group_plugins_file, 'r', encoding='utf-8') as f:
                    self.group_plugins = json.load(f)
                    
            logger.info(f"[UserManager] 已加载 {len(self.users)} 个用户")
        except Exception as e:
            logger.error(f"[UserManager] 加载数据失败: {e}")
    
    def _save_data(self):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            with open(self.user_plugins_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_plugins, f, ensure_ascii=False, indent=2)
            
            with open(self.group_plugins_file, 'w', encoding='utf-8') as f:
                json.dump(self.group_plugins, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[UserManager] 保存数据失败: {e}")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希（使用 MD5 与 AstrBot 兼容）"""
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    
    def verify_user(self, qq: str, password: str) -> bool:
        """验证用户密码"""
        if qq not in self.users:
            return False
        password_hash = self._hash_password(password)
        return password_hash == self.users[qq].get('password_hash', '')
    
    def add_user(self, qq: str, password: str, created_by: str = 'admin') -> bool:
        """添加用户（仅管理员可操作）"""
        # 验证QQ号格式（5-11位数字）
        if not qq.isdigit() or not (5 <= len(qq) <= 11):
            logger.warning(f"[UserManager] 无效的QQ号格式: {qq}")
            return False
        
        if qq in self.users:
            logger.warning(f"[UserManager] 用户 {qq} 已存在")
            return False
        
        self.users[qq] = {
            'password_hash': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'created_by': created_by
        }
        
        # 初始化用户插件配置
        self.user_plugins[qq] = {
            'allowed_plugins': [],  # 白名单模式，空列表表示允许所有
            'denied_plugins': []    # 黑名单
        }
        
        self._save_data()
        logger.info(f"[UserManager] 已添加用户 {qq}")
        return True
    
    def delete_user(self, qq: str) -> bool:
        """删除用户"""
        if qq not in self.users:
            return False
        
        del self.users[qq]
        if qq in self.user_plugins:
            del self.user_plugins[qq]
        
        self._save_data()
        logger.info(f"[UserManager] 已删除用户 {qq}")
        return True
    
    def update_user_password(self, qq: str, new_password: str) -> bool:
        """更新用户密码"""
        if qq not in self.users:
            return False
        
        self.users[qq]['password_hash'] = self._hash_password(new_password)
        self._save_data()
        return True
    
    def get_all_users(self) -> List[dict]:
        """获取所有用户列表"""
        users = []
        for qq, data in self.users.items():
            users.append({
                'qq': qq,
                'created_at': data.get('created_at', ''),
                'created_by': data.get('created_by', '')
            })
        return users
    
    def get_user_groups(self, qq: str) -> List[dict]:
        """获取用户所在的群组列表（从AstrBot获取）
        
        第三阶段：从AstrBot平台适配器获取真实的群组信息
        """
        groups = []
        try:
            # 从存储的群组信息中获取（由主程序定期更新）
            user_groups_file = self.data_dir / "user_groups.json"
            if user_groups_file.exists():
                with open(user_groups_file, 'r', encoding='utf-8') as f:
                    all_user_groups = json.load(f)
                    groups = all_user_groups.get(qq, [])
        except Exception as e:
            logger.error(f"[UserManager] 获取用户群组失败: {e}")
        return groups
    
    def save_user_groups(self, qq: str, groups: List[dict]):
        """保存用户的群组信息（由主程序调用）"""
        try:
            user_groups_file = self.data_dir / "user_groups.json"
            all_user_groups = {}
            if user_groups_file.exists():
                with open(user_groups_file, 'r', encoding='utf-8') as f:
                    all_user_groups = json.load(f)
            
            all_user_groups[qq] = groups
            
            with open(user_groups_file, 'w', encoding='utf-8') as f:
                json.dump(all_user_groups, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[UserManager] 保存用户群组失败: {e}")
    
    def set_user_plugin_config(self, qq: str, group_id: str, 
                               allowed_plugins: List[str] = None,
                               denied_plugins: List[str] = None) -> bool:
        """设置用户在特定群组的插件配置"""
        if qq not in self.users:
            return False
        
        key = f"{qq}:{group_id}"
        
        if key not in self.user_plugins:
            self.user_plugins[key] = {}
        
        if allowed_plugins is not None:
            self.user_plugins[key]['allowed_plugins'] = allowed_plugins
        
        if denied_plugins is not None:
            self.user_plugins[key]['denied_plugins'] = denied_plugins
        
        self._save_data()
        return True
    
    def get_user_plugin_config(self, qq: str, group_id: str) -> dict:
        """获取用户在特定群组的插件配置"""
        key = f"{qq}:{group_id}"
        return self.user_plugins.get(key, {
            'allowed_plugins': [],
            'denied_plugins': []
        })
    
    def is_plugin_allowed_for_user(self, qq: str, group_id: str, plugin_name: str) -> bool:
        """检查插件是否允许用户在特定群组使用"""
        config = self.get_user_plugin_config(qq, group_id)
        
        allowed = config.get('allowed_plugins', [])
        denied = config.get('denied_plugins', [])
        
        # 如果有白名单，优先检查白名单
        if allowed:
            return plugin_name in allowed
        
        # 否则检查黑名单
        return plugin_name not in denied
    
    def get_user_accessible_plugins(self, qq: str, group_id: str, 
                                    all_plugins: List[str]) -> List[str]:
        """获取用户在特定群组可以访问的插件列表"""
        config = self.get_user_plugin_config(qq, group_id)
        allowed = config.get('allowed_plugins', [])
        denied = config.get('denied_plugins', [])
        
        if allowed:
            # 白名单模式
            return [p for p in all_plugins if p in allowed]
        else:
            # 黑名单模式
            return [p for p in all_plugins if p not in denied]
