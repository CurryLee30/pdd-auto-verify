"""
测试数据生成器
"""
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger

from models.database import SessionLocal
from models.order import Order, OrderStatus, Product, VerificationRecord


class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def generate_test_orders(self, count: int = 10) -> List[Order]:
        """生成测试订单数据"""
        logger.info(f"开始生成 {count} 个测试订单")
        
        orders = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(count):
            order_sn = f"TEST{datetime.now().strftime('%Y%m%d')}{i:04d}"
            
            order = Order(
                order_sn=order_sn,
                buyer_id=f"buyer_{i:04d}",
                buyer_name=f"测试买家{i}",
                order_status=random.choice([OrderStatus.PAID.value, OrderStatus.SHIPPED.value]),
                pay_time=base_time + timedelta(minutes=i*30),
                order_amount=round(random.uniform(10, 100), 2),
                goods_info=f'[{{"goods_id": "goods_{i}", "goods_name": "测试虚拟商品{i}", "goods_type": {random.choice([1, 2, 3])}, "quantity": 1, "price": {round(random.uniform(10, 100), 2)}}}]',
                verification_code=self._generate_verification_code(),
                verification_status=False,
                created_at=base_time + timedelta(minutes=i*30),
                updated_at=datetime.now()
            )
            
            if order.order_status == OrderStatus.SHIPPED.value:
                order.shipped_at = base_time + timedelta(minutes=i*30 + 10)
            
            orders.append(order)
        
        # 保存到数据库
        for order in orders:
            self.db.add(order)
        
        self.db.commit()
        logger.info(f"成功生成 {count} 个测试订单")
        
        return orders
    
    def generate_test_products(self, count: int = 5) -> List[Product]:
        """生成测试商品数据"""
        logger.info(f"开始生成 {count} 个测试商品")
        
        products = []
        
        for i in range(count):
            product = Product(
                goods_id=f"goods_{i}",
                goods_name=f"测试虚拟商品{i}",
                goods_type=random.choice([1, 2, 3]),
                goods_status=1,  # 上架状态
                price=round(random.uniform(10, 100), 2),
                stock=random.randint(100, 1000),
                description=f"这是测试虚拟商品{i}的描述，用于测试自动核销功能",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            products.append(product)
        
        # 保存到数据库
        for product in products:
            self.db.add(product)
        
        self.db.commit()
        logger.info(f"成功生成 {count} 个测试商品")
        
        return products
    
    def generate_test_verification_records(self, orders: List[Order], count: int = 5) -> List[VerificationRecord]:
        """生成测试核销记录"""
        logger.info(f"开始生成 {count} 个测试核销记录")
        
        records = []
        base_time = datetime.now() - timedelta(hours=12)
        
        # 选择一些订单进行核销
        selected_orders = random.sample(orders, min(count, len(orders)))
        
        for i, order in enumerate(selected_orders):
            success = random.choice([True, True, True, False])  # 75%成功率
            
            record = VerificationRecord(
                order_sn=order.order_sn,
                verification_code=order.verification_code,
                verification_status=success,
                verification_time=base_time + timedelta(minutes=i*20) if success else None,
                verification_method="test",
                verification_result="测试核销成功" if success else "测试核销失败",
                created_at=base_time + timedelta(minutes=i*20)
            )
            
            records.append(record)
            
            # 如果核销成功，更新订单状态
            if success:
                order.verification_status = True
                order.verification_time = record.verification_time
                order.order_status = OrderStatus.FINISHED.value
                order.finished_at = record.verification_time
        
        # 保存到数据库
        for record in records:
            self.db.add(record)
        
        self.db.commit()
        logger.info(f"成功生成 {count} 个测试核销记录")
        
        return records
    
    def _generate_verification_code(self, length: int = 16) -> str:
        """生成核销码"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def clear_test_data(self):
        """清除测试数据"""
        logger.info("开始清除测试数据")
        
        try:
            # 删除测试订单
            test_orders = self.db.query(Order).filter(Order.order_sn.like("TEST%")).all()
            for order in test_orders:
                self.db.delete(order)
            
            # 删除测试商品
            test_products = self.db.query(Product).filter(Product.goods_id.like("goods_%")).all()
            for product in test_products:
                self.db.delete(product)
            
            # 删除测试核销记录
            test_records = self.db.query(VerificationRecord).filter(VerificationRecord.order_sn.like("TEST%")).all()
            for record in test_records:
                self.db.delete(record)
            
            self.db.commit()
            logger.info("测试数据清除完成")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"清除测试数据失败: {e}")
    
    def generate_all_test_data(self, order_count: int = 10, product_count: int = 5):
        """生成所有测试数据"""
        logger.info("开始生成所有测试数据")
        
        # 清除现有测试数据
        self.clear_test_data()
        
        # 生成商品
        products = self.generate_test_products(product_count)
        
        # 生成订单
        orders = self.generate_test_orders(order_count)
        
        # 生成核销记录
        verification_records = self.generate_test_verification_records(orders, min(5, order_count))
        
        logger.info("所有测试数据生成完成")
        
        return {
            "products": products,
            "orders": orders,
            "verification_records": verification_records
        }
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
