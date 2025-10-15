"""
测试环境模拟API客户端
"""
import json
import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from config.settings import settings
from core.exceptions import APIException


class MockPddAPIClient:
    """模拟拼多多API客户端（测试环境）"""
    
    def __init__(self):
        self.app_id = settings.pdd_app_id
        self.app_secret = settings.pdd_app_secret
        self.access_token = settings.pdd_access_token
        self.test_mode = getattr(settings, 'test_mode', True)
        
        # 模拟数据存储
        self.mock_orders = self._generate_mock_orders()
        self.mock_products = self._generate_mock_products()
        self.verification_records = []
        
        logger.info("模拟API客户端初始化完成（测试模式）")
    
    def _generate_mock_orders(self) -> List[Dict[str, Any]]:
        """生成模拟订单数据"""
        orders = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(getattr(settings, 'test_order_count', 10)):
            order_sn = f"TEST{datetime.now().strftime('%Y%m%d')}{i:04d}"
            order = {
                "order_sn": order_sn,
                "buyer_id": f"buyer_{i:04d}",
                "buyer_name": f"测试买家{i}",
                "order_status": random.choice([0, 1, 2]),  # 未支付、已支付、已发货
                "pay_time": (base_time + timedelta(minutes=i*30)).strftime("%Y-%m-%d %H:%M:%S"),
                "order_amount": round(random.uniform(10, 100), 2),
                "goods_list": [
                    {
                        "goods_id": f"goods_{i}",
                        "goods_name": f"测试虚拟商品{i}",
                        "goods_type": random.choice([1, 2, 3]),  # 虚拟商品类型
                        "quantity": 1,
                        "price": round(random.uniform(10, 100), 2)
                    }
                ],
                "created_at": (base_time + timedelta(minutes=i*30)).strftime("%Y-%m-%d %H:%M:%S")
            }
            orders.append(order)
        
        return orders
    
    def _generate_mock_products(self) -> List[Dict[str, Any]]:
        """生成模拟商品数据"""
        products = []
        
        for i in range(5):
            product = {
                "goods_id": f"goods_{i}",
                "goods_name": f"测试虚拟商品{i}",
                "goods_type": random.choice([1, 2, 3]),
                "goods_status": 1,  # 上架状态
                "price": round(random.uniform(10, 100), 2),
                "stock": random.randint(100, 1000),
                "description": f"这是测试虚拟商品{i}的描述"
            }
            products.append(product)
        
        return products
    
    def _simulate_api_delay(self):
        """模拟API调用延迟"""
        time.sleep(random.uniform(0.1, 0.5))
    
    def _make_mock_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """模拟API请求"""
        if params is None:
            params = {}
        
        logger.info(f"[模拟API] 调用方法: {method}, 参数: {params}")
        
        # 模拟API延迟
        self._simulate_api_delay()
        
        # 模拟API响应
        if method == "pdd.order.list.get":
            return self._mock_get_order_list(params)
        elif method == "pdd.order.detail.get":
            return self._mock_get_order_detail(params)
        elif method == "pdd.order.status.update":
            return self._mock_update_order_status(params)
        elif method == "pdd.order.goods.send":
            return self._mock_send_order_goods(params)
        elif method == "pdd.order.confirm":
            return self._mock_confirm_order(params)
        elif method == "pdd.virtual.goods.verify":
            return self._mock_verify_virtual_goods(params)
        elif method == "pdd.verification.record.get":
            return self._mock_get_verification_record(params)
        elif method == "pdd.goods.list.get":
            return self._mock_get_product_list(params)
        elif method == "pdd.goods.detail.get":
            return self._mock_get_product_detail(params)
        elif method == "pdd.goods.stock.update":
            return self._mock_update_product_stock(params)
        else:
            return {"error_response": {"error_msg": f"未知的API方法: {method}"}}
    
    def _mock_get_order_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟获取订单列表"""
        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        order_status = params.get("order_status")
        
        # 过滤订单
        filtered_orders = self.mock_orders
        if order_status is not None:
            filtered_orders = [order for order in self.mock_orders if order["order_status"] == order_status]
        
        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_orders = filtered_orders[start_idx:end_idx]
        
        return {
            "order_list_get_response": {
                "order_list": page_orders,
                "total_count": len(filtered_orders),
                "page": page,
                "page_size": page_size
            }
        }
    
    def _mock_get_order_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟获取订单详情"""
        order_sn = params.get("order_sn")
        
        order = next((o for o in self.mock_orders if o["order_sn"] == order_sn), None)
        if not order:
            return {"error_response": {"error_msg": f"订单 {order_sn} 不存在"}}
        
        return {
            "order_detail_get_response": {
                "order": order
            }
        }
    
    def _mock_update_order_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟更新订单状态"""
        order_sn = params.get("order_sn")
        status = params.get("status")
        
        order = next((o for o in self.mock_orders if o["order_sn"] == order_sn), None)
        if not order:
            return {"error_response": {"error_msg": f"订单 {order_sn} 不存在"}}
        
        order["order_status"] = status
        logger.info(f"[模拟API] 订单 {order_sn} 状态更新为 {status}")
        
        return {
            "order_status_update_response": {
                "success": True,
                "message": "订单状态更新成功"
            }
        }
    
    def _mock_send_order_goods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟订单发货"""
        order_sn = params.get("order_sn")
        goods_info = params.get("goods_info")
        
        order = next((o for o in self.mock_orders if o["order_sn"] == order_sn), None)
        if not order:
            return {"error_response": {"error_msg": f"订单 {order_sn} 不存在"}}
        
        # 更新订单状态为已发货
        order["order_status"] = 2
        order["shipped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"[模拟API] 订单 {order_sn} 发货成功")
        
        return {
            "order_goods_send_response": {
                "success": True,
                "message": "发货成功",
                "delivery_info": goods_info
            }
        }
    
    def _mock_confirm_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟确认订单"""
        order_sn = params.get("order_sn")
        
        order = next((o for o in self.mock_orders if o["order_sn"] == order_sn), None)
        if not order:
            return {"error_response": {"error_msg": f"订单 {order_sn} 不存在"}}
        
        order["order_status"] = 3  # 已收货
        order["received_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info(f"[模拟API] 订单 {order_sn} 确认成功")
        
        return {
            "order_confirm_response": {
                "success": True,
                "message": "订单确认成功"
            }
        }
    
    def _mock_verify_virtual_goods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟虚拟商品核销"""
        order_sn = params.get("order_sn")
        verification_code = params.get("verification_code")
        
        order = next((o for o in self.mock_orders if o["order_sn"] == order_sn), None)
        if not order:
            return {"error_response": {"error_msg": f"订单 {order_sn} 不存在"}}
        
        # 模拟核销成功/失败
        success = random.choice([True, True, True, False])  # 75%成功率
        
        if success:
            order["order_status"] = 4  # 已完成
            order["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 记录核销记录
            self.verification_records.append({
                "order_sn": order_sn,
                "verification_code": verification_code,
                "success": True,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            logger.info(f"[模拟API] 订单 {order_sn} 核销成功")
            
            return {
                "virtual_goods_verify_response": {
                    "success": True,
                    "message": "核销成功"
                }
            }
        else:
            logger.info(f"[模拟API] 订单 {order_sn} 核销失败")
            
            return {
                "virtual_goods_verify_response": {
                    "success": False,
                    "message": "核销失败，请检查核销码"
                }
            }
    
    def _mock_get_verification_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟获取核销记录"""
        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_records = self.verification_records[start_idx:end_idx]
        
        return {
            "verification_record_get_response": {
                "records": page_records,
                "total_count": len(self.verification_records),
                "page": page,
                "page_size": page_size
            }
        }
    
    def _mock_get_product_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟获取商品列表"""
        page = params.get("page", 1)
        page_size = params.get("page_size", 20)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_products = self.mock_products[start_idx:end_idx]
        
        return {
            "goods_list_get_response": {
                "goods_list": page_products,
                "total_count": len(self.mock_products),
                "page": page,
                "page_size": page_size
            }
        }
    
    def _mock_get_product_detail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟获取商品详情"""
        goods_id = params.get("goods_id")
        
        product = next((p for p in self.mock_products if p["goods_id"] == goods_id), None)
        if not product:
            return {"error_response": {"error_msg": f"商品 {goods_id} 不存在"}}
        
        return {
            "goods_detail_get_response": {
                "goods": product
            }
        }
    
    def _mock_update_product_stock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟更新商品库存"""
        goods_id = params.get("goods_id")
        quantity = params.get("quantity")
        
        product = next((p for p in self.mock_products if p["goods_id"] == goods_id), None)
        if not product:
            return {"error_response": {"error_msg": f"商品 {goods_id} 不存在"}}
        
        product["stock"] = quantity
        logger.info(f"[模拟API] 商品 {goods_id} 库存更新为 {quantity}")
        
        return {
            "goods_stock_update_response": {
                "success": True,
                "message": "库存更新成功"
            }
        }
    
    # 实现与真实API客户端相同的接口
    def get_order_list(self, **kwargs):
        return self._make_mock_request("pdd.order.list.get", kwargs)
    
    def get_order_detail(self, order_sn: str):
        return self._make_mock_request("pdd.order.detail.get", {"order_sn": order_sn})
    
    def update_order_status(self, order_sn: str, status: int):
        return self._make_mock_request("pdd.order.status.update", {"order_sn": order_sn, "status": status})
    
    def send_order_goods(self, order_sn: str, goods_info: Dict[str, Any]):
        return self._make_mock_request("pdd.order.goods.send", {"order_sn": order_sn, "goods_info": goods_info})
    
    def confirm_order(self, order_sn: str):
        return self._make_mock_request("pdd.order.confirm", {"order_sn": order_sn})
    
    def verify_virtual_goods(self, order_sn: str, verification_code: str):
        return self._make_mock_request("pdd.virtual.goods.verify", {"order_sn": order_sn, "verification_code": verification_code})
    
    def get_verification_record(self, **kwargs):
        return self._make_mock_request("pdd.verification.record.get", kwargs)
    
    def get_product_list(self, **kwargs):
        return self._make_mock_request("pdd.goods.list.get", kwargs)
    
    def get_product_detail(self, goods_id: int):
        return self._make_mock_request("pdd.goods.detail.get", {"goods_id": goods_id})
    
    def update_product_stock(self, goods_id: int, quantity: int):
        return self._make_mock_request("pdd.goods.stock.update", {"goods_id": goods_id, "quantity": quantity})
