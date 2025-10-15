"""
授权服务：读写店铺授权信息
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from models.database import Base
from models.auth import ShopAuth


class AuthService:
    def __init__(self) -> None:
        self.engine = create_engine(settings.database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()

    def get_active_auth(self) -> Optional[ShopAuth]:
        return (
            self.db.query(ShopAuth)
            .filter(ShopAuth.is_active == True)
            .order_by(desc(ShopAuth.updated_at))
            .first()
        )

    def save_or_update_auth(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in_seconds: Optional[int] = None,
        shop_id: Optional[str] = None,
        shop_name: Optional[str] = None,
    ) -> ShopAuth:
        auth = self.get_active_auth()
        if auth is None:
            auth = ShopAuth(access_token=access_token)
            self.db.add(auth)
        else:
            auth.access_token = access_token

        auth.refresh_token = refresh_token
        if expires_in_seconds is not None:
            auth.expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        if shop_id:
            auth.shop_id = shop_id
        if shop_name:
            auth.shop_name = shop_name

        auth.updated_at = datetime.utcnow()
        auth.is_active = True
        self.db.commit()
        self.db.refresh(auth)
        return auth

    def deactivate_all(self) -> None:
        self.db.query(ShopAuth).update({ShopAuth.is_active: False})
        self.db.commit()

    def close(self) -> None:
        self.db.close()


