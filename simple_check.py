#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order, Product, VerificationRecord
from sqlalchemy import func

db = SessionLocal()

# 检查订单数量
total_orders = db.query(func.count(Order.id)).scalar()
print(f"总订单数: {total_orders}")

# 检查商品数量  
total_products = db.query(func.count(Product.id)).scalar()
print(f"总商品数: {total_products}")

# 检查核销记录数量
total_verifications = db.query(func.count(VerificationRecord.id)).scalar()
print(f"总核销记录数: {total_verifications}")

# 检查订单状态分布
status_counts = db.query(Order.order_status, func.count(Order.id)).group_by(Order.order_status).all()
print('订单状态分布:')
for status, count in status_counts:
    print(f'  状态 {status}: {count} 个')

db.close()
