#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal
from models.order import VerificationRecord

def check_verification_records():
    """检查核销记录状态"""
    db = SessionLocal()
    
    try:
        print("所有核销记录:")
        records = db.query(VerificationRecord).all()
        
        successful_count = 0
        failed_count = 0
        
        for record in records:
            status_text = "成功" if record.verification_status else "失败"
            if record.verification_status:
                successful_count += 1
            else:
                failed_count += 1
                
            print(f"  订单: {record.order_sn}, 核销状态: {status_text}, 创建时间: {record.created_at}")
        
        print(f"\n核销记录统计:")
        print(f"  总核销记录数: {len(records)}")
        print(f"  成功核销数: {successful_count}")
        print(f"  失败核销数: {failed_count}")
        
        # 检查失败的核销记录
        failed_records = [r for r in records if not r.verification_status]
        if failed_records:
            print(f"\n失败的核销记录:")
            for record in failed_records:
                print(f"  订单: {record.order_sn}, 失败原因: {record.verification_result}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_verification_records()
