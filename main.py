"""
主程序入口
"""
import asyncio
import schedule
import time
from datetime import datetime
from loguru import logger
from typing import Optional

from config.settings import settings
from core.order_manager import OrderManager
from core.verification import VirtualGoodsVerifier
from utils.logger import setup_logger
from services.notification_service import NotificationService


class PddAutoVerifyApp:
    """拼多多自动核销应用"""
    
    def __init__(self):
        # 设置日志
        setup_logger()
        
        # 初始化组件
        self.order_manager = OrderManager()
        self.verifier = VirtualGoodsVerifier()
        self.notification_service = NotificationService()
        
        logger.info("拼多多自动核销系统初始化完成")
    
    def start_order_monitoring(self):
        """启动订单监控"""
        try:
            logger.info("开始订单监控")
            self.order_manager.monitor_orders()
        except Exception as e:
            logger.error(f"订单监控失败: {e}")
            self.notification_service.send_error_notification(f"订单监控失败: {e}")
    
    def start_auto_verification(self):
        """启动自动核销"""
        try:
            logger.info("开始自动核销")
            self.verifier.auto_verify_orders()
        except Exception as e:
            logger.error(f"自动核销失败: {e}")
            self.notification_service.send_error_notification(f"自动核销失败: {e}")
    
    def run_scheduled_tasks(self):
        """运行定时任务"""
        # 设置定时任务
        schedule.every(settings.order_check_interval).seconds.do(self.start_order_monitoring)
        schedule.every(30).minutes.do(self.start_auto_verification)
        
        logger.info(f"定时任务已设置，订单检查间隔: {settings.order_check_interval}秒")
        
        # 运行定时任务
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("收到停止信号，正在关闭系统...")
                break
            except Exception as e:
                logger.error(f"定时任务执行失败: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    def run_once(self):
        """运行一次（用于测试）"""
        logger.info("执行一次性任务")
        
        # 执行订单监控
        self.start_order_monitoring()
        
        # 执行自动核销
        self.start_auto_verification()
        
        logger.info("一次性任务执行完成")
    
    def run_web_server(self):
        """运行Web服务器"""
        try:
            from web.interface import create_web_interface
            
            # 创建Web界面
            web_interface = create_web_interface()
            
            logger.info("Web服务器启动中...")
            # 启动Web服务器
            web_interface.run(host="0.0.0.0", port=8001)
            
        except Exception as e:
            logger.error(f"Web服务器启动失败: {e}")
            raise


def main():
    """主函数"""
    app = PddAutoVerifyApp()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "monitor":
            app.start_order_monitoring()
        elif command == "verify":
            app.start_auto_verification()
        elif command == "once":
            app.run_once()
        elif command == "web":
            app.run_web_server()
        else:
            print("可用命令: monitor, verify, once, web")
    else:
        # 默认运行定时任务
        app.run_scheduled_tasks()


if __name__ == "__main__":
    main()
