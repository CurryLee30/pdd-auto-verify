"""
订单数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from models.database import Base


class OrderStatus(Enum):
    """订单状态枚举"""
    UNPAID = 0      # 未支付
    PAID = 1         # 已支付
    SHIPPED = 2      # 已发货
    RECEIVED = 3     # 已收货
    FINISHED = 4     # 已完成
    CANCELLED = 5    # 已取消
    REFUNDED = 6     # 已退款


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_sn = Column(String(50), unique=True, index=True, nullable=False)  # 订单号
    buyer_id = Column(String(50), nullable=False)  # 买家ID
    buyer_name = Column(String(100), nullable=False)  # 买家姓名
    order_status = Column(Integer, nullable=False, default=OrderStatus.UNPAID.value)  # 订单状态
    pay_time = Column(DateTime)  # 支付时间
    shipped_at = Column(DateTime)  # 发货时间
    received_at = Column(DateTime)  # 收货时间
    finished_at = Column(DateTime)  # 完成时间
    order_amount = Column(Float, nullable=False)  # 订单金额
    goods_info = Column(Text)  # 商品信息(JSON格式)
    delivery_info = Column(Text)  # 发货信息(JSON格式)
    verification_code = Column(String(100))  # 核销码
    verification_status = Column(Boolean, default=False)  # 核销状态
    verification_time = Column(DateTime)  # 核销时间
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "order_sn": self.order_sn,
            "buyer_id": self.buyer_id,
            "buyer_name": self.buyer_name,
            "order_status": self.order_status,
            "pay_time": self.pay_time.isoformat() if self.pay_time else None,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "order_amount": self.order_amount,
            "goods_info": self.goods_info,
            "delivery_info": self.delivery_info,
            "verification_code": self.verification_code,
            "verification_status": self.verification_status,
            "verification_time": self.verification_time.isoformat() if self.verification_time else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Product(Base):
    """商品模型"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(String(50), unique=True, index=True, nullable=False)  # 商品ID
    goods_name = Column(String(200), nullable=False)  # 商品名称
    goods_type = Column(Integer, nullable=False)  # 商品类型
    goods_status = Column(Integer, nullable=False)  # 商品状态
    price = Column(Float, nullable=False)  # 价格
    stock = Column(Integer, nullable=False, default=0)  # 库存
    description = Column(Text)  # 商品描述
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "goods_id": self.goods_id,
            "goods_name": self.goods_name,
            "goods_type": self.goods_type,
            "goods_status": self.goods_status,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class VerificationRecord(Base):
    """核销记录模型"""
    __tablename__ = "verification_records"
    
    id = Column(Integer, primary_key=True, index=True)
    order_sn = Column(String(50), nullable=False, index=True)  # 订单号
    verification_code = Column(String(100), nullable=False)  # 核销码
    verification_status = Column(Boolean, default=False)  # 核销状态
    verification_time = Column(DateTime)  # 核销时间
    verification_method = Column(String(50))  # 核销方式
    verification_result = Column(Text)  # 核销结果
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "order_sn": self.order_sn,
            "verification_code": self.verification_code,
            "verification_status": self.verification_status,
            "verification_time": self.verification_time.isoformat() if self.verification_time else None,
            "verification_method": self.verification_method,
            "verification_result": self.verification_result,
            "created_at": self.created_at.isoformat()
        }
