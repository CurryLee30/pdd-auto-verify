"""
订单服务模块
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from models.order import Order, OrderStatus
from models.database import Base
from config.settings import settings
from core.exceptions import DatabaseException


class OrderService:
    """订单服务"""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
    
    def create_order(self, order: Order) -> Order:
        """创建订单"""
        try:
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            return order
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"创建订单失败: {e}")
    
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
    
    def get_orders_by_status(self, status: int, limit: int = 100) -> List[Order]:
        """根据状态获取订单列表"""
        try:
            return self.db.query(Order).filter(Order.order_status == status).limit(limit).all()
        except Exception as e:
            raise DatabaseException(f"获取订单列表失败: {e}")
    
    def get_unverified_orders(self) -> List[Order]:
        """获取未核销的订单"""
        try:
            return self.db.query(Order).filter(
                and_(
                    Order.order_status == OrderStatus.SHIPPED.value,
                    Order.verification_status == False
                )
            ).all()
        except Exception as e:
            raise DatabaseException(f"获取未核销订单失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
