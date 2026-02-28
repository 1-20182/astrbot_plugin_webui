"""
👥 用户管理器模块
💕 负责管理所有小伙伴的账号信息~
"""
import json
import bcrypt
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from astrbot.api import logger


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
        self._migrate_passwords()  # 迁移旧密码
    
    def _load_users(self) -> Dict:
        """📖 加载用户数据（从文件里读取小伙伴的信息~）"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"😢 用户数据文件损坏: {e}")
                return {}
            except Exception as e:
                logger.error(f"😢 读取用户数据失败: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """💾 保存用户数据（把小伙伴的信息存到文件里~）"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"😢 保存用户数据失败: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """🔐 密码哈希（使用 bcrypt，更安全~）"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """🔐 验证密码（使用 bcrypt~）"""
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    def _migrate_passwords(self):
        """🔄 迁移旧版 SHA256 密码到 bcrypt"""
        migrated = False
        for username, user in self.users.items():
            password_hash = user.get('password_hash', '')
            if len(password_hash) == 64 and all(c in '0123456789abcdef' for c in password_hash):
                logger.warning(f"⚠️ 用户 {username} 使用旧版密码哈希，请在下次登录时重置密码")
                user['password_needs_reset'] = True
                migrated = True
        
        if migrated:
            self._save_users()
    
    def is_first_run(self) -> bool:
        """🎉 检查是否首次运行"""
        return len(self.users) == 0
    
    def create_admin(self, username: str, password: str) -> bool:
        """👑 创建管理员账号"""
        if not self.is_first_run():
            return False
        
        if not self._validate_username(username):
            return False
        if not self._validate_password(password):
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
        """👤 创建普通用户"""
        if username in self.users:
            logger.warning(f"😢 用户名 {username} 已经被占用啦~")
            return False
        
        if not self._validate_username(username):
            return False
        if not self._validate_password(password):
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
    
    def _validate_username(self, username: str) -> bool:
        """✅ 验证用户名"""
        if not username or len(username) < 3 or len(username) > 32:
            return False
        if not all(c.isalnum() or c == '_' for c in username):
            return False
        return True
    
    def _validate_password(self, password: str) -> bool:
        """✅ 验证密码强度"""
        if not password or len(password) < 6:
            return False
        return True
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """🔐 验证用户"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        
        if user.get('password_needs_reset'):
            logger.warning(f"⚠️ 用户 {username} 需要重置密码")
            return None
        
        if self._verify_password(password, user['password_hash']):
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
