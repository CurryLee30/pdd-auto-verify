#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order

def reset_order_verification(order_sn):
    """重置订单核销状态"""
    db = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.order_sn == order_sn).first()
        if order:
            print(f"重置前 - 订单: {order.order_sn}, 核销状态: {order.verification_status}")
            
            # 重置核销状态
            order.verification_status = False
            db.commit()
            
            print(f"重置后 - 订单: {order.order_sn}, 核销状态: {order.verification_status}")
            print("订单核销状态已重置，现在可以重新核销")
        else:
            print(f"未找到订单: {order_sn}")
            
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        order_sn = sys.argv[1]
        reset_order_verification(order_sn)
    else:
        print("用法: python reset_order_verification.py <订单号>")
        print("例如: python reset_order_verification.py TEST202510140000")
