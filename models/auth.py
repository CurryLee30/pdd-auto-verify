"""
店铺授权模型
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from models.database import Base


class ShopAuth(Base):
    __tablename__ = "shop_auth"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(String(64), index=True, nullable=True)
    shop_name = Column(String(255), nullable=True)

    access_token = Column(String(1024), nullable=False)
    refresh_token = Column(String(1024), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() >= self.expires_at


