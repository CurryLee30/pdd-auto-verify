"""
拼多多API客户端
"""
import hashlib
import hmac
import json
import time
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
from loguru import logger

from config.settings import settings, APIConfig
from core.exceptions import APIException, AuthenticationException
from services.auth_service import AuthService


def get_api_client():
    """获取API客户端（根据环境选择真实或模拟客户端）"""
    test_mode = getattr(settings, 'test_mode', False)
    
    if test_mode:
        from core.mock_api_client import MockPddAPIClient
        return MockPddAPIClient()
    else:
        return PddAPIClient()


class PddAPIClient:
    """拼多多开放平台API客户端"""
    
    def __init__(self):
        self.app_id = settings.pdd_app_id
        self.app_secret = settings.pdd_app_secret
        # 优先从授权存储读取 access_token（生产多店铺可扩展为按店铺选择）
        self.access_token = settings.pdd_access_token
        try:
            auth_service = AuthService()
            auth = auth_service.get_active_auth()
            if auth and auth.access_token:
                self.access_token = auth.access_token
            auth_service.close()
        except Exception:
            # 读取失败时，回退到 settings
            pass
        self.base_url = APIConfig.BASE_URL
        self.timeout = APIConfig.TIMEOUT
        self.max_retries = APIConfig.MAX_RETRIES
        
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成API签名"""
        # 按参数名排序
        sorted_params = sorted(params.items())
        # 拼接参数字符串
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        # 添加app_secret
        sign_string = f"{self.app_secret}{param_string}{self.app_secret}"
        # 生成MD5签名
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        return signature
    
    def _prepare_request_params(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """准备请求参数"""
        # 基础参数
        request_params = {
            "type": method,
            "client_id": self.app_id,
            "access_token": self.access_token,
            "timestamp": str(int(time.time())),
            "data_type": "JSON",
        }
        
        # 添加业务参数
        if params:
            request_params.update(params)
        
        # 生成签名
        signature = self._generate_signature(request_params)
        request_params["sign"] = signature
        
        return request_params
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送API请求"""
        if params is None:
            params = {}
            
        # 准备请求参数
        request_params = self._prepare_request_params(method, params)
        
        # 发送请求
        for attempt in range(self.max_retries):
            try:
                logger.info(f"发送API请求: {method}, 参数: {params}")
                
                response = requests.post(
                    self.base_url,
                    data=request_params,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                response.raise_for_status()
                result = response.json()
                
                # 检查API响应
                if result.get("error_response"):
                    error_info = result["error_response"]
                    error_msg = f"API错误: {error_info.get('error_msg', '未知错误')}"
                    logger.error(error_msg)
                    raise APIException(error_msg)
                
                logger.info(f"API请求成功: {method}")
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise APIException(f"API请求失败: {e}")
                time.sleep(2 ** attempt)  # 指数退避
    
    def get_order_list(self, 
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      order_status: Optional[int] = None,
                      page: int = 1,
                      page_size: int = 20) -> Dict[str, Any]:
        """获取订单列表"""
        params = {
            "page": page,
            "page_size": page_size,
        }
        
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if order_status is not None:
            params["order_status"] = order_status
            
        return self._make_request(APIConfig.ORDER_APIS["get_order_list"], params)
    
    def get_order_detail(self, order_sn: str) -> Dict[str, Any]:
        """获取订单详情"""
        params = {"order_sn": order_sn}
        return self._make_request(APIConfig.ORDER_APIS["get_order_detail"], params)
    
    def update_order_status(self, order_sn: str, status: int) -> Dict[str, Any]:
        """更新订单状态"""
        params = {
            "order_sn": order_sn,
            "status": status
        }
        return self._make_request(APIConfig.ORDER_APIS["update_order_status"], params)
    
    def send_order_goods(self, order_sn: str, goods_info: Dict[str, Any]) -> Dict[str, Any]:
        """订单发货"""
        params = {
            "order_sn": order_sn,
            "goods_info": json.dumps(goods_info)
        }
        return self._make_request(APIConfig.ORDER_APIS["send_order_goods"], params)
    
    def confirm_order(self, order_sn: str) -> Dict[str, Any]:
        """确认订单"""
        params = {"order_sn": order_sn}
        return self._make_request(APIConfig.ORDER_APIS["confirm_order"], params)

    # -------- 授权相关（OAuth）最小实现：以真实接口名占位 --------
    def exchange_token(self, code: str) -> Dict[str, Any]:
        """用授权回调的 code 换取 token（占位，需用实际开放平台接口替换）"""
        # 真实实现：调用 pdd 的 pop.auth.token.create
        params = {
            "code": code,
            "redirect_uri": settings.pdd_redirect_uri or "",
        }
        # 这里先用商品列表接口占位，实际项目需换成真实授权接口
        return self._make_request("pop.auth.token.create", params)

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新 token（占位，需用实际开放平台接口替换）"""
        params = {"refresh_token": refresh_token}
        return self._make_request("pop.auth.token.refresh", params)
    
    def verify_virtual_goods(self, order_sn: str, verification_code: str) -> Dict[str, Any]:
        """虚拟商品核销"""
        params = {
            "order_sn": order_sn,
            "verification_code": verification_code
        }
        return self._make_request(APIConfig.VERIFICATION_APIS["verify_virtual_goods"], params)
    
    def get_verification_record(self, 
                               order_sn: Optional[str] = None,
                               start_time: Optional[str] = None,
                               end_time: Optional[str] = None,
                               page: int = 1,
                               page_size: int = 20) -> Dict[str, Any]:
        """获取核销记录"""
        params = {
            "page": page,
            "page_size": page_size,
        }
        
        if order_sn:
            params["order_sn"] = order_sn
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
            
        return self._make_request(APIConfig.VERIFICATION_APIS["get_verification_record"], params)
    
    def get_product_list(self, 
                        page: int = 1,
                        page_size: int = 20,
                        goods_status: Optional[int] = None) -> Dict[str, Any]:
        """获取商品列表"""
        params = {
            "page": page,
            "page_size": page_size,
        }
        
        if goods_status is not None:
            params["goods_status"] = goods_status
            
        return self._make_request(APIConfig.PRODUCT_APIS["get_product_list"], params)
    
    def get_product_detail(self, goods_id: int) -> Dict[str, Any]:
        """获取商品详情"""
        params = {"goods_id": goods_id}
        return self._make_request(APIConfig.PRODUCT_APIS["get_product_detail"], params)
    
    def update_product_stock(self, goods_id: int, quantity: int) -> Dict[str, Any]:
        """更新商品库存"""
        params = {
            "goods_id": goods_id,
            "quantity": quantity
        }
        return self._make_request(APIConfig.PRODUCT_APIS["update_product_stock"], params)
