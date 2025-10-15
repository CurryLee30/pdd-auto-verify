"""
商家部署脚本
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_system_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查操作系统
    system = platform.system()
    print(f"✅ 操作系统: {system}")
    
    # 检查磁盘空间
    try:
        import shutil
        free_space = shutil.disk_usage('.').free
        free_gb = free_space / (1024**3)
        if free_gb < 1:
            print("❌ 磁盘空间不足，需要至少1GB空间")
            return False
        print(f"✅ 可用磁盘空间: {free_gb:.1f}GB")
    except:
        print("⚠️ 无法检查磁盘空间")
    
    return True

def install_dependencies():
    """安装依赖包"""
    print("安装依赖包...")
    
    try:
        # 升级pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def setup_environment():
    """设置环境"""
    print("设置环境配置...")
    
    # 创建必要目录
    directories = ["logs", "data", "backup", "config"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")
    
    # 检查配置文件
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("创建环境配置文件...")
            try:
                with open(env_example, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ 环境配置文件已创建")
            except Exception as e:
                print(f"❌ 创建配置文件失败: {e}")
                return False
        else:
            print("❌ 未找到环境配置文件模板")
            return False
    else:
        print("✅ 环境配置文件已存在")
    
    return True

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    try:
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from models.database import init_database
        init_database()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def create_startup_scripts():
    """创建启动脚本"""
    print("创建启动脚本...")
    
    # Windows启动脚本
    if platform.system() == "Windows":
        startup_script = """@echo off
echo 启动拼多多自动核销系统...
cd /d "%~dp0"
python main.py
pause
"""
        with open("start.bat", "w", encoding="utf-8") as f:
            f.write(startup_script)
        print("✅ 创建Windows启动脚本: start.bat")
        
        # Web服务启动脚本
        web_script = """@echo off
echo 启动Web管理界面...
cd /d "%~dp0"
python main.py web
pause
"""
        with open("start_web.bat", "w", encoding="utf-8") as f:
            f.write(web_script)
        print("✅ 创建Web服务启动脚本: start_web.bat")
    
    # Linux/Mac启动脚本
    else:
        startup_script = """#!/bin/bash
echo "启动拼多多自动核销系统..."
cd "$(dirname "$0")"
python3 main.py
"""
        with open("start.sh", "w", encoding="utf-8") as f:
            f.write(startup_script)
        os.chmod("start.sh", 0o755)
        print("✅ 创建Linux/Mac启动脚本: start.sh")
        
        # Web服务启动脚本
        web_script = """#!/bin/bash
echo "启动Web管理界面..."
cd "$(dirname "$0")"
python3 main.py web
"""
        with open("start_web.sh", "w", encoding="utf-8") as f:
            f.write(web_script)
        os.chmod("start_web.sh", 0o755)
        print("✅ 创建Web服务启动脚本: start_web.sh")

def create_service_scripts():
    """创建系统服务脚本"""
    print("创建系统服务脚本...")
    
    if platform.system() == "Windows":
        # Windows服务脚本
        service_script = """@echo off
echo 安装Windows服务...
nssm install PddAutoVerify "%~dp0python.exe" "%~dp0main.py"
nssm set PddAutoVerify AppDirectory "%~dp0"
nssm set PddAutoVerify DisplayName "拼多多自动核销系统"
nssm set PddAutoVerify Description "拼多多虚拟商品自动核销系统"
nssm start PddAutoVerify
echo 服务安装完成！
pause
"""
        with open("install_service.bat", "w", encoding="utf-8") as f:
            f.write(service_script)
        print("✅ 创建Windows服务安装脚本: install_service.bat")
    
    else:
        # Linux systemd服务
        service_content = """[Unit]
Description=拼多多自动核销系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={working_dir}
ExecStart={python_path} main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
""".format(
            working_dir=os.getcwd(),
            python_path=sys.executable
        )
        
        with open("pdd-auto-verify.service", "w", encoding="utf-8") as f:
            f.write(service_content)
        print("✅ 创建Linux systemd服务文件: pdd-auto-verify.service")

def create_config_guide():
    """创建配置指南"""
    print("创建配置指南...")
    
    config_guide = """# 拼多多自动核销系统 - 配置指南

## 1. 拼多多开放平台配置

### 步骤1：申请开发者账号
1. 访问 https://open.pinduoduo.com/
2. 注册开发者账号
3. 完成实名认证

### 步骤2：创建应用
1. 登录开发者后台
2. 创建新应用（选择商家应用）
3. 填写应用信息
4. 设置回调地址：http://your-domain.com/callback

### 步骤3：申请API权限
需要申请以下API权限：
- pdd.order.list.get (获取订单列表)
- pdd.order.detail.get (获取订单详情)
- pdd.order.goods.send (订单发货)
- pdd.virtual.goods.verify (虚拟商品核销)
- pdd.goods.list.get (获取商品列表)

### 步骤4：获取密钥
在应用详情页面获取：
- App ID
- App Secret
- Access Token

## 2. 系统配置

编辑 .env 文件，填写以下配置：

```env
# 拼多多开放平台配置
PDD_APP_ID=your_app_id
PDD_APP_SECRET=your_app_secret
PDD_ACCESS_TOKEN=your_access_token
PDD_REDIRECT_URI=http://your-domain.com/callback

# 生产环境配置
TEST_MODE=False
DEBUG=False

# 数据库配置
DATABASE_URL=sqlite:///./pdd_auto_verify.db

# 系统配置
ORDER_CHECK_INTERVAL=60
MAX_RETRY_TIMES=3

# 通知配置
NOTIFICATION_ENABLED=True
EMAIL_SMTP_SERVER=smtp.your-provider.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-email-password
EMAIL_TO=admin@your-domain.com
```

## 3. 启动系统

### 方式1：使用启动脚本
- Windows: 双击 start.bat
- Linux/Mac: 运行 ./start.sh

### 方式2：命令行启动
```bash
python main.py          # 启动定时任务
python main.py web      # 启动Web管理界面
```

### 方式3：安装为系统服务
- Windows: 运行 install_service.bat
- Linux: 复制 pdd-auto-verify.service 到 /etc/systemd/system/

## 4. 访问管理界面

启动Web服务后，访问：
http://localhost:8000

## 5. 常见问题

### Q: API调用失败怎么办？
A: 检查网络连接、API密钥、调用频率限制

### Q: 数据库连接失败怎么办？
A: 检查数据库配置、服务状态、权限设置

### Q: 订单处理异常怎么办？
A: 查看日志文件、检查订单状态、验证商品配置

## 6. 技术支持

- 查看日志文件：logs/pdd_auto_verify.log
- 技术支持邮箱：support@your-domain.com
- 在线文档：http://your-domain.com/docs
"""
    
    with open("CONFIG_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(config_guide)
    print("✅ 创建配置指南: CONFIG_GUIDE.md")

def main():
    """主函数"""
    print("=" * 60)
    print("拼多多自动核销系统 - 商家部署脚本")
    print("=" * 60)
    
    # 检查系统要求
    if not check_system_requirements():
        print("❌ 系统要求检查失败，请解决上述问题后重试")
        return False
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return False
    
    # 设置环境
    if not setup_environment():
        print("❌ 环境设置失败")
        return False
    
    # 初始化数据库
    if not init_database():
        print("❌ 数据库初始化失败")
        return False
    
    # 创建启动脚本
    create_startup_scripts()
    
    # 创建服务脚本
    create_service_scripts()
    
    # 创建配置指南
    create_config_guide()
    
    print("\n" + "=" * 60)
    print("✅ 部署完成！")
    print("=" * 60)
    print("下一步操作：")
    print("1. 编辑 .env 文件，填写拼多多API配置")
    print("2. 查看 CONFIG_GUIDE.md 了解详细配置步骤")
    print("3. 运行启动脚本启动系统")
    print("4. 访问 http://localhost:8000 进入管理界面")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\n按回车键退出...")
        else:
            input("\n部署失败，按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n部署被用户中断")
    except Exception as e:
        print(f"\n\n部署过程中发生错误: {e}")
        input("按回车键退出...")
