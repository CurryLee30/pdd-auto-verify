#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.verification import VirtualGoodsVerifier
from models.database import SessionLocal
from models.order import Order

def test_verification():
    """测试核销功能"""
    db = SessionLocal()
    
    try:
        # 查找可以核销的订单
        print("查找可以核销的订单:")
        orders = db.query(Order).filter(
            Order.order_status.in_([2, 4]),  # 已发货或已完成
            Order.verification_status == False  # 未核销
        ).all()
        
        if orders:
            print(f"找到 {len(orders)} 个可以核销的订单:")
            for order in orders:
                print(f"  订单号: {order.order_sn}, 状态: {order.order_status}, 核销码: {order.verification_code}")
            
            # 测试核销第一个订单
            test_order = orders[0]
            print(f"\n测试核销订单: {test_order.order_sn}")
            
            verifier = VirtualGoodsVerifier()
            try:
                result = verifier.verify_order(test_order.order_sn, test_order.verification_code)
                print(f"核销结果: {result}")
            except Exception as e:
                print(f"核销失败: {e}")
        else:
            print("没有找到可以核销的订单")
            
        # 检查特定订单
        print(f"\n检查订单 TEST202510140000:")
        order = db.query(Order).filter(Order.order_sn == "TEST202510140000").first()
        if order:
            print(f"  状态: {order.order_status}")
            print(f"  核销状态: {order.verification_status}")
            print(f"  核销码: {order.verification_code}")
            
            # 尝试核销
            verifier = VirtualGoodsVerifier()
            try:
                result = verifier.verify_order(order.order_sn, order.verification_code)
                print(f"核销结果: {result}")
            except Exception as e:
                print(f"核销失败: {e}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_verification()
