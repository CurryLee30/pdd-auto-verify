#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.order_service import OrderService
from services.verification_service import VerificationService

def test_web_display():
    """测试Web界面显示的数据"""
    order_service = OrderService()
    verification_service = VerificationService()
    
    try:
        print("Web界面数据获取测试:")
        
        # 获取订单统计
        pending_orders = len(order_service.get_orders_by_status(1, limit=1000))  # 已支付
        shipped_orders = len(order_service.get_orders_by_status(2, limit=1000))  # 已发货
        finished_orders = len(order_service.get_orders_by_status(4, limit=1000))  # 已完成
        total_orders = pending_orders + shipped_orders + finished_orders
        
        print(f"已支付订单: {pending_orders}")
        print(f"已发货订单: {shipped_orders}")
        print(f"已完成订单: {finished_orders}")
        print(f"总订单数: {total_orders}")
        
        # 获取核销统计
        verification_records = verification_service.get_verification_records(page=1, page_size=1000)
        total_verifications = len(verification_records)
        successful_verifications = len([r for r in verification_records if r.verification_status])
        
        print(f"总核销记录: {total_verifications}")
        print(f"成功核销: {successful_verifications}")
        
        # 获取可以核销的订单（已发货且未核销）
        verifiable_orders = order_service.get_orders_by_status(2, limit=1000)  # 已发货
        verifiable_orders = [o for o in verifiable_orders if not o.verification_status]  # 未核销
        verifiable_count = len(verifiable_orders)
        
        print(f"可核销订单: {verifiable_count}")
        for order in verifiable_orders:
            print(f"  {order.order_sn} - 核销码: {order.verification_code}")
            
    finally:
        order_service.close()
        verification_service.close()

if __name__ == "__main__":
    test_web_display()
