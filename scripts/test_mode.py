"""
测试模式启动脚本
"""
import os
import sys
import time
from datetime import datetime
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.test_data_generator import TestDataGenerator
from core.order_manager import OrderManager
from core.verification import VirtualGoodsVerifier
from utils.logger import setup_logger


class TestModeRunner:
    """测试模式运行器"""
    
    def __init__(self):
        # 设置日志
        setup_logger()
        
        # 初始化组件
        self.data_generator = TestDataGenerator()
        self.order_manager = OrderManager()
        self.verifier = VirtualGoodsVerifier()
        
        logger.info("测试模式初始化完成")
    
    def setup_test_environment(self):
        """设置测试环境"""
        logger.info("开始设置测试环境")
        
        # 生成测试数据
        test_data = self.data_generator.generate_all_test_data(
            order_count=getattr(settings, 'test_order_count', 10),
            product_count=5
        )
        
        logger.info(f"测试环境设置完成:")
        logger.info(f"- 生成了 {len(test_data['products'])} 个测试商品")
        logger.info(f"- 生成了 {len(test_data['orders'])} 个测试订单")
        logger.info(f"- 生成了 {len(test_data['verification_records'])} 个测试核销记录")
        
        return test_data
    
    def test_order_monitoring(self):
        """测试订单监控功能"""
        logger.info("开始测试订单监控功能")
        
        try:
            # 获取待处理订单
            pending_orders = self.order_manager.get_pending_orders()
            logger.info(f"获取到 {len(pending_orders)} 个待处理订单")
            
            # 处理订单
            success_count = 0
            for order_data in pending_orders:
                if self.order_manager.process_order(order_data):
                    success_count += 1
            
            logger.info(f"订单监控测试完成，成功处理 {success_count}/{len(pending_orders)} 个订单")
            
        except Exception as e:
            logger.error(f"订单监控测试失败: {e}")
    
    def test_verification(self):
        """测试核销功能"""
        logger.info("开始测试核销功能")
        
        try:
            # 获取未核销的订单
            unverified_orders = self.verifier.verification_service.get_unverified_orders()
            logger.info(f"获取到 {len(unverified_orders)} 个未核销订单")
            
            # 测试单个核销
            if unverified_orders:
                order = unverified_orders[0]
                verification_code = order.verification_code or order.order_sn[-8:]
                
                logger.info(f"测试核销订单: {order.order_sn}")
                result = self.verifier.verify_order(order.order_sn, verification_code)
                logger.info(f"核销结果: {result}")
            
            # 测试批量核销
            if len(unverified_orders) > 1:
                verification_list = []
                for order in unverified_orders[:3]:  # 测试前3个订单
                    verification_code = order.verification_code or order.order_sn[-8:]
                    verification_list.append({
                        "order_sn": order.order_sn,
                        "verification_code": verification_code
                    })
                
                logger.info(f"测试批量核销 {len(verification_list)} 个订单")
                batch_result = self.verifier.batch_verify_orders(verification_list)
                logger.info(f"批量核销结果: {batch_result}")
            
            logger.info("核销功能测试完成")
            
        except Exception as e:
            logger.error(f"核销功能测试失败: {e}")
    
    def test_api_client(self):
        """测试API客户端功能"""
        logger.info("开始测试API客户端功能")
        
        try:
            api_client = self.order_manager.api_client
            
            # 测试获取订单列表
            logger.info("测试获取订单列表")
            order_list = api_client.get_order_list(page=1, page_size=5)
            logger.info(f"订单列表: {order_list}")
            
            # 测试获取商品列表
            logger.info("测试获取商品列表")
            product_list = api_client.get_product_list(page=1, page_size=5)
            logger.info(f"商品列表: {product_list}")
            
            # 测试获取核销记录
            logger.info("测试获取核销记录")
            verification_records = api_client.get_verification_record(page=1, page_size=5)
            logger.info(f"核销记录: {verification_records}")
            
            logger.info("API客户端功能测试完成")
            
        except Exception as e:
            logger.error(f"API客户端功能测试失败: {e}")
    
    def run_interactive_test(self):
        """运行交互式测试"""
        logger.info("开始交互式测试")
        
        while True:
            print("\n" + "="*50)
            print("拼多多自动核销系统 - 测试模式")
            print("="*50)
            print("1. 设置测试环境")
            print("2. 测试订单监控")
            print("3. 测试核销功能")
            print("4. 测试API客户端")
            print("5. 运行完整测试")
            print("6. 清除测试数据")
            print("0. 退出")
            print("="*50)
            
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == "1":
                self.setup_test_environment()
            elif choice == "2":
                self.test_order_monitoring()
            elif choice == "3":
                self.test_verification()
            elif choice == "4":
                self.test_api_client()
            elif choice == "5":
                self.run_full_test()
            elif choice == "6":
                self.data_generator.clear_test_data()
                logger.info("测试数据已清除")
            elif choice == "0":
                logger.info("退出测试模式")
                break
            else:
                print("无效选择，请重新输入")
            
            input("\n按回车键继续...")
    
    def run_full_test(self):
        """运行完整测试"""
        logger.info("开始运行完整测试")
        
        try:
            # 设置测试环境
            self.setup_test_environment()
            
            # 等待一下让数据生效
            time.sleep(2)
            
            # 测试API客户端
            self.test_api_client()
            
            # 测试订单监控
            self.test_order_monitoring()
            
            # 测试核销功能
            self.test_verification()
            
            logger.info("完整测试运行完成")
            
        except Exception as e:
            logger.error(f"完整测试失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.data_generator.close()
            logger.info("测试模式清理完成")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")


def main():
    """主函数"""
    print("拼多多自动核销系统 - 测试模式")
    print("="*50)
    
    # 检查是否为测试模式
    test_mode = getattr(settings, 'test_mode', False)
    if not test_mode:
        print("警告: 当前不是测试模式，请设置 TEST_MODE=True")
        print("建议使用测试环境配置文件: cp test.env.example .env")
        response = input("是否继续? (y/N): ").strip().lower()
        if response != 'y':
            print("退出")
            return
    
    runner = TestModeRunner()
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "setup":
                runner.setup_test_environment()
            elif command == "monitor":
                runner.test_order_monitoring()
            elif command == "verify":
                runner.test_verification()
            elif command == "api":
                runner.test_api_client()
            elif command == "full":
                runner.run_full_test()
            elif command == "clear":
                runner.data_generator.clear_test_data()
            else:
                print("可用命令: setup, monitor, verify, api, full, clear")
        else:
            # 交互式模式
            runner.run_interactive_test()
    
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()
