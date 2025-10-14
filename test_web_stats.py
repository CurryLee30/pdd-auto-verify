#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.order_service import OrderService
from services.verification_service import VerificationService

# 初始化服务
order_service = OrderService()
verification_service = VerificationService()

print("测试Web界面数据获取逻辑:")

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

print(f"总核销记录数: {total_verifications}")
print(f"成功核销数: {successful_verifications}")

# 关闭连接
order_service.close()
verification_service.close()
