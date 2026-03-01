"""
🎨 HTML 模板模块
💕 存放所有可爱的前端页面代码~
"""

def get_html_template() -> str:
    """获取 HTML 页面模板"""
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
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes scaleIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
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
        .login-btn:disabled { 
            opacity: 0.6; cursor: not-allowed;
            transform: none;
            box-shadow: none;
            background: linear-gradient(135deg, #ddd 0%, #ccc 100%);
        }
        .error-msg { color: #ff6b6b; font-size: 14px; margin-top: 10px; text-align: center; font-weight: 500; }
        .success-msg { color: #69db7c; font-size: 14px; margin-top: 10px; text-align: center; font-weight: 500; }
        
        /* 主界面 */
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
        
        /* 导航 */
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
        
        /* 内容区 */
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
        
        /* 插件列表 */
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
        
        /* 安装按钮 */
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
        
        /* 插件市场卡片 */
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
            <button class="nav-btn active" onclick="showPage('welcome', this)">🏠 温馨小窝</button>
            <button class="nav-btn" onclick="showPage('plugins', this)">🎒 魔法道具箱</button>
            <button class="nav-btn" onclick="showPage('market', this)">🛒 魔法商店街</button>
            <button class="nav-btn" onclick="showPage('personas', this)">🎨 换装小屋</button>
            <button id="usersNavBtn" class="nav-btn hidden" onclick="showPage('users', this)">👫 小伙伴名单</button>
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

        <!-- 用户管理 -->
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
        let csrfToken = '';
        let localBgImages = [];
        let currentBgIndex = -1;
        let usedBgIndices = [];
        let bgPreloadImage = new Image();
        
        async function loadLocalBackgrounds() {
            try {
                const res = await fetch('/api/backgrounds');
                const data = await res.json();
                if (data.success && data.data.length > 0) {
                    localBgImages = data.data;
                } else {
                    localBgImages = [];
                }
            } catch (e) {
                localBgImages = [];
            }
        }
        
        function getRandomBg() {
            if (localBgImages.length === 0) return null;
            if (usedBgIndices.length >= localBgImages.length) usedBgIndices = [];
            let availableIndices = [];
            for (let i = 0; i < localBgImages.length; i++) {
                if (!usedBgIndices.includes(i)) availableIndices.push(i);
            }
            const randomIndex = availableIndices[Math.floor(Math.random() * availableIndices.length)];
            usedBgIndices.push(randomIndex);
            currentBgIndex = randomIndex;
            return '/api/background/' + localBgImages[randomIndex];
        }
        
        function changeBackground() {
            const bgContainer = document.getElementById('bgContainer');
            if (bgContainer && localBgImages.length > 0) {
                bgContainer.style.opacity = '0';
                setTimeout(() => {
                    const newBg = getRandomBg();
                    if (newBg) {
                        bgContainer.style.backgroundImage = `url(${newBg})`;
                        bgContainer.style.opacity = '1';
                    }
                }, 300);
            }
        }
        
        function setLoginBackground() {
            const loginBg = document.getElementById('loginBg');
            const setupBg = document.getElementById('setupBg');
            if (localBgImages.length > 0) {
                const randomBg = '/api/background/' + localBgImages[Math.floor(Math.random() * localBgImages.length)];
                if (loginBg) loginBg.style.backgroundImage = `url(${randomBg})`;
                if (setupBg) setupBg.style.backgroundImage = `url(${randomBg})`;
            }
        }
        
        async function initBackground() {
            await loadLocalBackgrounds();
            changeBackground();
            setLoginBackground();
        }

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
                }
            } catch (e) {
                error.textContent = '网络错误';
                btn.disabled = false;
            }
        }

        function escapeHtml(text) {
            if (typeof text !== 'string') return text;
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function apiRequest(url, options = {}) {
            const defaultHeaders = {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            };
            options.headers = {...defaultHeaders, ...options.headers};
            const res = await fetch(url, options);
            return res;
        }
        
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
                    csrfToken = data.data.csrf_token || '';
                    showMainPage();
                } else {
                    error.textContent = escapeHtml(data.message) || '登录失败';
                    btn.disabled = false;
                    btn.textContent = '🚀 冲呀！登录';
                }
            } catch (e) {
                error.textContent = '网络错误';
                btn.disabled = false;
                btn.textContent = '🚀 冲呀！登录';
            }
        }

        function showMainPage() {
            document.getElementById('loginPage').classList.add('hidden');
            document.getElementById('mainPage').classList.remove('hidden');
            document.getElementById('currentUser').textContent = currentUser;
            document.getElementById('welcomeUser').textContent = currentUser;
            
            const roleBadge = document.getElementById('userRole');
            roleBadge.textContent = currentRole === 'admin' ? '管理员' : '普通用户';
            roleBadge.className = 'user-role ' + currentRole;
            
            if (currentRole === 'admin') {
                document.getElementById('usersNavBtn').classList.remove('hidden');
                document.getElementById('welcomeText').textContent = '作为管理员，您可以管理所有插件和用户。';
            } else {
                document.getElementById('welcomeText').textContent = '您可以查看插件信息和人格配置。';
            }
            
            initBackground();
            loadStats();
        }

        function showPage(page, clickedBtn = null) {
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(page + 'Page').classList.add('active');
            const navBtn = clickedBtn || document.querySelector(`.nav-btn[onclick*="showPage('${page}')"]`);
            if (navBtn) navBtn.classList.add('active');
            changeBackground();
            if (page === 'plugins') loadPlugins();
            if (page === 'market') loadMarket();
            if (page === 'personas') loadPersonas();
            if (page === 'users') loadUsers();
        }

        async function logout() {
            await fetch('/api/logout', {method: 'POST'});
            location.reload();
        }

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

        async function loadPlugins() {
            const list = document.getElementById('pluginList');
            list.innerHTML = '<p>🎀 正在召唤道具...</p>';
            try {
                const res = await fetch('/api/plugins');
                const data = await res.json();
                if (data.success && data.data.length > 0) {
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
                    let updateAllHtml = '';
                    if (currentRole === 'admin') {
                        updateAllHtml = `
                            <div style="margin-bottom: 20px; text-align: right;">
                                <button class="install-btn" onclick="updateAllPlugins()">🔄 一键更新所有插件</button>
                            </div>
                        `;
                    }
                    list.innerHTML = updateAllHtml + customInstallHtml + data.data.map(p => {
                        return `
                        <div class="plugin-item">
                            <div class="plugin-info">
                                <h4>${p.name} ${p.reserved ? '🔒' : ''}</h4>
                                <p>${p.description || '这个插件还没有描述呢~'}</p>
                                <div class="plugin-meta">
                                    💕 作者: ${p.author || '神秘作者'} | 📌 版本: ${p.version || '1.0.0'}
                                    ${p.repo ? `| 🔗 <a href="${p.repo}" target="_blank">去看看</a>` : ''}
                                </div>
                            </div>
                            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">
                                ${currentRole === 'admin' ? `
                                    <button class="toggle-btn ${p.activated ? 'on' : 'off'}" 
                                            onclick="togglePlugin('${p.name}', ${!p.activated})">
                                        ${p.activated ? '✨ 运行中' : '💤 已停止'}
                                    </button>
                                    ${!p.reserved ? `<button class="toggle-btn off" onclick="uninstallPlugin('${p.name}')">🗑️ 卸载</button>` : ''}
                                ` : `<span class="toggle-btn ${p.activated ? 'on' : 'off'}">${p.activated ? '✨ 运行中' : '💤 已停止'}</span>`}
                            </div>
                        </div>
                    `}).join('');
                } else {
                    list.innerHTML = '<p>🎀 还没有插件哦，快去商店看看吧~</p>';
                }
            } catch (e) {
                list.innerHTML = '<p>😢 加载失败了，请稍后再试~</p>';
            }
        }
        
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
        
        async function installCustomPlugin() {
            const url = document.getElementById('customPluginUrl').value.trim();
            if (!url) {
                alert('😢 请输入插件仓库地址哦~');
                return;
            }
            if (!confirm(`确定要安装这个插件吗？\n仓库: ${url}`)) return;
            try {
                const res = await apiRequest('/api/plugins/install-custom', {
                    method: 'POST',
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

        async function togglePlugin(name, activate) {
            try {
                await apiRequest('/api/plugins/toggle', {
                    method: 'POST',
                    body: JSON.stringify({name, activated: activate})
                });
                loadPlugins();
                loadStats();
            } catch (e) {
                alert('😢 操作失败了，请稍后再试~');
            }
        }

        async function uninstallPlugin(name) {
            if (!confirm(`确定要卸载插件 ${escapeHtml(name)} 吗？卸载后就见不到它了哦~ 😢`)) return;
            try {
                const res = await apiRequest('/api/plugins/uninstall', {
                    method: 'POST',
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
                                <div class="author">💕 ${p.author || '神秘作者'}</div>
                                <div>📌 v${p.version || '1.0.0'}</div>
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

        async function installPlugin(name, repo) {
            if (!repo) {
                alert('😢 这个插件没有提供仓库地址，暂时无法安装呢~');
                return;
            }
            if (!confirm(`确定要安装插件 ${escapeHtml(name)} 吗？\n仓库: ${escapeHtml(repo)}`)) return;
            try {
                const res = await apiRequest('/api/plugins/install', {
                    method: 'POST',
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

        checkFirstRun();
    </script>
</body>
</html>'''
