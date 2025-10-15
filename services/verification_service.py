"""
核销服务模块
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from models.order import Order, VerificationRecord
from models.database import Base
from config.settings import settings
from core.exceptions import DatabaseException


class VerificationService:
    """核销服务"""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
    
    def create_verification_record(self, record: VerificationRecord) -> VerificationRecord:
        """创建核销记录"""
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"创建核销记录失败: {e}")
    
    def get_verification_records(self, 
                                order_sn: Optional[str] = None,
                                start_time: Optional[str] = None,
                                end_time: Optional[str] = None,
                                page: int = 1,
                                page_size: int = 20) -> List[VerificationRecord]:
        """获取核销记录"""
        try:
            query = self.db.query(VerificationRecord)
            
            if order_sn:
                query = query.filter(VerificationRecord.order_sn == order_sn)
            
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                query = query.filter(VerificationRecord.created_at >= start_dt)
            
            if end_time:
                end_dt = datetime.fromisoformat(end_time)
                query = query.filter(VerificationRecord.created_at <= end_dt)
            
            offset = (page - 1) * page_size
            return query.offset(offset).limit(page_size).all()
            
        except Exception as e:
            raise DatabaseException(f"获取核销记录失败: {e}")
    
    def get_order_by_sn(self, order_sn: str) -> Optional[Order]:
        """根据订单号获取订单"""
        try:
            return self.db.query(Order).filter(Order.order_sn == order_sn).first()
        except Exception as e:
            raise DatabaseException(f"获取订单失败: {e}")
    
    def update_order(self, order: Order) -> Order:
        """更新订单"""
        try:
            order.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"更新订单失败: {e}")
    
    def get_unverified_orders(self) -> List[Order]:
        """获取未核销的订单"""
        try:
            return self.db.query(Order).filter(
                and_(
                    Order.order_status == 2,  # 已发货状态
                    Order.verification_status == False
                )
            ).all()
        except Exception as e:
            raise DatabaseException(f"获取未核销订单失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
