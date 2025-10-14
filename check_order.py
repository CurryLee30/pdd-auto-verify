#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order, OrderStatus
from sqlalchemy import func

def check_order_details():
    """检查订单详细信息"""
    db = SessionLocal()
    
    try:
        # 查找特定订单
        order = db.query(Order).filter(Order.order_sn == "TEST202510140000").first()
        
        if order:
            print(f"订单号: {order.order_sn}")
            print(f"订单状态: {order.order_status}")
            print(f"买家ID: {order.buyer_id}")
            print(f"买家姓名: {order.buyer_name}")
            print(f"支付时间: {order.pay_time}")
            print(f"发货时间: {order.shipped_at}")
            print(f"订单金额: {order.order_amount}")
            print(f"核销码: {order.verification_code}")
            print(f"核销状态: {order.verification_status}")
            print(f"创建时间: {order.created_at}")
            print(f"更新时间: {order.updated_at}")
            
            # 检查订单状态枚举
            print(f"\n订单状态说明:")
            print(f"  1 = 已支付 (PAID)")
            print(f"  2 = 已发货 (SHIPPED)")  
            print(f"  3 = 已收货 (RECEIVED)")
            print(f"  4 = 已完成 (FINISHED)")
            print(f"  5 = 已取消 (CANCELLED)")
            
            # 检查是否可以核销
            print(f"\n核销条件检查:")
            print(f"  订单状态是否为已发货(2): {order.order_status == 2}")
            print(f"  是否已核销: {order.verification_status}")
            print(f"  是否可以核销: {order.order_status == 2 and not order.verification_status}")
            
        else:
            print("未找到订单 TEST202510140000")
            
        # 显示所有测试订单的状态
        print(f"\n所有测试订单状态:")
        all_orders = db.query(Order).filter(Order.order_sn.like("TEST%")).all()
        for o in all_orders:
            print(f"  {o.order_sn}: 状态={o.order_status}, 核销状态={o.verification_status}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_order_details()
