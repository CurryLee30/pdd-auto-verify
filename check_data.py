#!/usr/bin/env python3
"""
检查数据库中的数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import Order, Product, VerificationRecord
from sqlalchemy import func

def check_database_data():
    """检查数据库中的数据"""
    db = SessionLocal()
    
    try:
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
        
        # 检查核销状态分布
        verification_status_counts = db.query(VerificationRecord.verification_status, func.count(VerificationRecord.id)).group_by(VerificationRecord.verification_status).all()
        print('核销状态分布:')
        for status, count in verification_status_counts:
            print(f'  核销状态 {status}: {count} 个')
        
        # 显示最近的几个订单
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        print('\n最近的订单:')
        for order in recent_orders:
            print(f'  订单号: {order.order_sn}, 状态: {order.order_status}, 创建时间: {order.created_at}')
        
        # 显示最近的几个核销记录
        recent_verifications = db.query(VerificationRecord).order_by(VerificationRecord.created_at.desc()).limit(5).all()
        print('\n最近的核销记录:')
        for record in recent_verifications:
            print(f'  订单号: {record.order_sn}, 核销状态: {record.verification_status}, 创建时间: {record.created_at}')
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database_data()
