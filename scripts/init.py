"""
启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """创建必要的目录"""
    directories = [
        "logs",
        "data",
        "backup"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"创建目录: {directory}")

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        sys.exit(1)

def setup_environment():
    """设置环境"""
    env_file = Path(".env")
    env_example_file = Path("env.example")
    
    if not env_file.exists() and env_example_file.exists():
        print("创建环境配置文件...")
        env_file.write_text(env_example_file.read_text())
        print("请编辑 .env 文件，填写正确的配置信息")
    elif not env_file.exists():
        print("警告: 未找到环境配置文件，请手动创建 .env 文件")

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    try:
        from models.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

def main():
    """主函数"""
    print("拼多多自动核销系统 - 初始化脚本")
    print("=" * 50)
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    install_dependencies()
    
    # 设置环境
    setup_environment()
    
    # 初始化数据库
    init_database()
    
    print("=" * 50)
    print("初始化完成！")
    print("请编辑 .env 文件，填写正确的配置信息后运行:")
    print("python main.py")

if __name__ == "__main__":
    main()
