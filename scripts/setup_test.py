"""
快速启动测试环境脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_test_environment():
    """设置测试环境"""
    print("拼多多自动核销系统 - 测试环境设置")
    print("="*50)
    
    # 检查是否存在测试配置文件
    test_env_file = Path("test.env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and test_env_file.exists():
        print("创建测试环境配置文件...")
        env_file.write_text(test_env_file.read_text(encoding='utf-8'), encoding='utf-8')
        print("✓ 测试环境配置文件已创建")
    elif env_file.exists():
        print("✓ 环境配置文件已存在")
    else:
        print("✗ 未找到测试环境配置文件")
        return False
    
    # 创建必要目录
    directories = ["logs", "data", "backup"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    # 安装依赖
    print("安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        return False
    
    # 初始化数据库
    print("初始化数据库...")
    try:
        from models.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库初始化完成")
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False
    
    print("\n" + "="*50)
    print("测试环境设置完成！")
    print("="*50)
    print("现在可以运行以下命令进行测试:")
    print("1. python scripts/test_mode.py          # 交互式测试")
    print("2. python scripts/test_mode.py full      # 完整测试")
    print("3. python scripts/test_mode.py setup     # 设置测试数据")
    print("4. python main.py web                    # 启动Web服务器")
    print("="*50)
    
    return True

def main():
    """主函数"""
    if setup_test_environment():
        print("\n是否现在运行测试? (y/N): ", end="")
        response = input().strip().lower()
        if response == 'y':
            print("启动测试模式...")
            subprocess.run([sys.executable, "scripts/test_mode.py"])
    else:
        print("测试环境设置失败，请检查错误信息")

if __name__ == "__main__":
    main()
