"""
系统配置模块
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """系统配置类"""
    
    # 拼多多开放平台配置
    pdd_app_id: str = Field(..., env="PDD_APP_ID")
    pdd_app_secret: str = Field(..., env="PDD_APP_SECRET")
    pdd_access_token: Optional[str] = Field(None, env="PDD_ACCESS_TOKEN")
    pdd_redirect_uri: Optional[str] = Field(None, env="PDD_REDIRECT_URI")
    
    # 数据库配置
    database_url: str = Field("sqlite:///./pdd_auto_verify.db", env="DATABASE_URL")
    
    # Redis配置
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # 日志配置
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/pdd_auto_verify.log", env="LOG_FILE")
    
    # 系统配置
    debug: bool = Field(False, env="DEBUG")
    test_mode: bool = Field(False, env="TEST_MODE")
    api_timeout: int = Field(30, env="API_TIMEOUT")
    order_check_interval: int = Field(60, env="ORDER_CHECK_INTERVAL")
    max_retry_times: int = Field(3, env="MAX_RETRY_TIMES")
    
    # 通知配置
    notification_enabled: bool = Field(True, env="NOTIFICATION_ENABLED")
    email_smtp_server: Optional[str] = Field(None, env="EMAIL_SMTP_SERVER")
    email_smtp_port: int = Field(587, env="EMAIL_SMTP_PORT")
    email_username: Optional[str] = Field(None, env="EMAIL_USERNAME")
    email_password: Optional[str] = Field(None, env="EMAIL_PASSWORD")
    email_to: Optional[str] = Field(None, env="EMAIL_TO")
    
    # 安全配置
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    
    # 测试配置
    test_order_count: int = Field(10, env="TEST_ORDER_COUNT")
    test_verification_code_length: int = Field(16, env="TEST_VERIFICATION_CODE_LENGTH")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()


class APIConfig:
    """API配置类"""
    
    # 拼多多开放平台API基础URL
    BASE_URL = "https://gw-api.pinduoduo.com/api/router"
    
    # API版本
    VERSION = "V1"
    
    # 请求超时时间
    TIMEOUT = settings.api_timeout
    
    # 最大重试次数
    MAX_RETRIES = settings.max_retry_times
    
    # 订单相关API接口
    ORDER_APIS = {
        "get_order_list": "pdd.order.list.get",  # 获取订单列表
        "get_order_detail": "pdd.order.detail.get",  # 获取订单详情
        "update_order_status": "pdd.order.status.update",  # 更新订单状态
        "send_order_goods": "pdd.order.goods.send",  # 订单发货
        "confirm_order": "pdd.order.confirm",  # 确认订单
    }
    
    # 商品相关API接口
    PRODUCT_APIS = {
        "get_product_list": "pdd.goods.list.get",  # 获取商品列表
        "get_product_detail": "pdd.goods.detail.get",  # 获取商品详情
        "update_product_stock": "pdd.goods.stock.update",  # 更新商品库存
    }
    
    # 虚拟商品核销相关API
    VERIFICATION_APIS = {
        "verify_virtual_goods": "pdd.virtual.goods.verify",  # 虚拟商品核销
        "get_verification_record": "pdd.verification.record.get",  # 获取核销记录
    }
