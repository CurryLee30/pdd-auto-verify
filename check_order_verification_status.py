#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order, VerificationRecord

def check_order_verification_status():
    """检查订单核销状态与核销记录的一致性"""
    db = SessionLocal()
    
    try:
        print("订单核销状态与核销记录对比:")
        orders = db.query(Order).filter(Order.order_sn.like("TEST%")).all()
        
        for order in orders:
            # 查找对应的核销记录
            verification_record = db.query(VerificationRecord).filter(
                VerificationRecord.order_sn == order.order_sn
            ).first()
            
            order_verification_status = "已核销" if order.verification_status else "未核销"
            record_status = "成功" if verification_record and verification_record.verification_status else "失败/无记录"
            
            print(f"  订单: {order.order_sn}")
            print(f"    订单核销状态: {order_verification_status}")
            print(f"    核销记录状态: {record_status}")
            if verification_record:
                print(f"    核销结果: {verification_record.verification_result}")
            print()
            
        # 检查未核销的订单
        unverified_orders = [o for o in orders if not o.verification_status]
        print(f"未核销的订单数量: {len(unverified_orders)}")
        for order in unverified_orders:
            print(f"  {order.order_sn} - 状态: {order.order_status}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_order_verification_status()
