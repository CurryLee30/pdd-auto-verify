"""
异常处理模块
"""
from typing import Optional


class PddAutoVerifyException(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class APIException(PddAutoVerifyException):
    """API调用异常"""
    pass


class AuthenticationException(PddAutoVerifyException):
    """认证异常"""
    pass


class OrderException(PddAutoVerifyException):
    """订单相关异常"""
    pass


class VerificationException(PddAutoVerifyException):
    """核销相关异常"""
    pass


class DatabaseException(PddAutoVerifyException):
    """数据库异常"""
    pass


class ConfigurationException(PddAutoVerifyException):
    """配置异常"""
    pass


class NotificationException(PddAutoVerifyException):
    """通知异常"""
    pass
