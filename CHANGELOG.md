# 📝 更新日志喵~

## 🌸 v1.0.1 (2025-03-01)

### 🐛 修复了好多小bug喵~

#### ✨ 插件管理功能复活啦！
- **插件安装/卸载/更新终于可以用了喵！**
  - 原来是找错了地方喵~ AstrBot 的 plugin_manager 藏在 `context._star_manager` 里，不是 `context.plugin_manager` 喵~
  - 把所有插件接口都改成正确的地址了喵~
  - 修复了返回值处理，现在能正确识别安装成功啦~
  - 只要没报错就认为安装成功，更贴心了喵~

#### 🛡️ CSRF 安全验证加强！
- **给所有修改操作都加上了 CSRF token 验证喵~**
  - 保护这些接口：
    - `POST /api/plugins/install` - 安装插件
    - `POST /api/plugins/uninstall` - 卸载插件
    - `POST /api/plugins/update` - 更新插件
    - `POST /api/plugins/update-all` - 批量更新
    - `POST /api/plugins/install-custom` - 安装第三方插件
    - `POST /api/plugins/toggle` - 切换插件状态
    - `POST /api/users` - 创建用户
    - `DELETE /api/users/{username}` - 删除用户
    - `POST /api/users/{username}/reset_password` - 重置密码

#### 🎨 前端也修好了喵~
- **第三方插件安装和插件开关功能复活！**
  - `installCustomPlugin()` 改用 `apiRequest()` 发送请求，带上 CSRF token 啦~
  - `togglePlugin()` 也改用 `apiRequest()`，安全可靠喵~

#### 🔄 批量更新功能重做！
- **`update_all_plugins` 重新实现喵~**
  - 原来 AstrBot 里没有这个方法，现在自己实现了喵~
  - 遍历所有非保留插件，一个一个更新~
  - 会告诉你成功几个、失败几个，超贴心！

### 📄 README 变漂亮了！
- **修复了换行符问题喵~**
  - 把 CRLF 换成 LF，GitHub 上显示终于不乱七八糟了~

### 📝 日志更详细了！
- 插件安装/卸载都有详细日志了喵~
  - 方便排查问题，一眼就能看出哪里出错了~

---

## 🎉 v1.0.0 (2024)

### ✨ 初次见面请多关照喵~
- 🎊 第一个版本发布啦！
- 👥 多用户权限管理，管理员和普通用户分开~
- 🎀 粉粉嫩嫩的主题，少女心爆棚！
- 🔄 实时插件管理，方便又快捷~
- 🌟 支持安装第三方插件，扩展性满满~
- 🎭 人格配置查看，一目了然~

---

<p align="center">Made with 💖 by 飞翔的死猪 🐷</p>
