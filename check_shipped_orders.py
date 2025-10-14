#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order

def check_shipped_orders():
    """检查已发货且可核销的订单"""
    db = SessionLocal()
    
    try:
        print("所有测试订单状态:")
        orders = db.query(Order).filter(Order.order_sn.like("TEST%")).all()
        
        verifiable_orders = []
        for order in orders:
            can_verify = (
                order.order_status == 2 and  # 只允许已发货
                not order.verification_status     # 未核销
            )
            
            status_text = {
                1: "已支付",
                2: "已发货", 
                3: "已收货",
                4: "已完成",
                5: "已取消"
            }.get(order.order_status, f"未知状态{order.order_status}")
            
            print(f"  {order.order_sn}: {status_text}, 核销状态: {order.verification_status}, 可核销: {can_verify}")
            
            if can_verify:
                verifiable_orders.append(order)
        
        print(f"\n可以核销的订单数量: {len(verifiable_orders)}")
        for order in verifiable_orders:
            print(f"  {order.order_sn} - 核销码: {order.verification_code}")
            
        # 检查特定订单 TEST202510140000
        print(f"\n检查订单 TEST202510140000:")
        order = db.query(Order).filter(Order.order_sn == "TEST202510140000").first()
        if order:
            status_text = {
                1: "已支付",
                2: "已发货", 
                3: "已收货",
                4: "已完成",
                5: "已取消"
            }.get(order.order_status, f"未知状态{order.order_status}")
            
            print(f"  状态: {status_text} ({order.order_status})")
            print(f"  核销状态: {order.verification_status}")
            print(f"  核销码: {order.verification_code}")
            print(f"  是否可以核销: {order.order_status == 2 and not order.verification_status}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_shipped_orders()
