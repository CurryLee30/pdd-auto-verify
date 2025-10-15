"""
订单管理模块
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from core.api_client import get_api_client
from core.exceptions import OrderException, APIException
from models.order import Order, OrderStatus
from services.order_service import OrderService


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.api_client = get_api_client()
        self.order_service = OrderService()
        
    def get_pending_orders(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取待处理订单"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 格式化时间
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"获取待处理订单: {start_time_str} - {end_time_str}")
            
            # 获取订单列表
            result = self.api_client.get_order_list(
                start_time=start_time_str,
                end_time=end_time_str,
                order_status=OrderStatus.PAID.value,  # 已支付状态
                page_size=100
            )
            
            orders = result.get("order_list_get_response", {}).get("order_list", [])
            logger.info(f"获取到 {len(orders)} 个待处理订单")
            
            return orders
            
        except APIException as e:
            logger.error(f"获取待处理订单失败: {e}")
            raise OrderException(f"获取待处理订单失败: {e}")
    
    def process_order(self, order_data: Dict[str, Any]) -> bool:
        """处理单个订单"""
        try:
            order_sn = order_data.get("order_sn")
            if not order_sn:
                logger.error("订单号为空")
                return False
            
            logger.info(f"开始处理订单: {order_sn}")
            
            # 获取订单详情
            order_detail = self.api_client.get_order_detail(order_sn)
            order_info = order_detail.get("order_detail_get_response", {}).get("order", {})
            
            # 检查订单状态
            order_status = order_info.get("order_status")
            if order_status != OrderStatus.PAID.value:
                logger.warning(f"订单 {order_sn} 状态不是已支付: {order_status}")
                return False
            
            # 检查是否为虚拟商品
            if not self._is_virtual_goods_order(order_info):
                logger.info(f"订单 {order_sn} 不是虚拟商品订单，跳过处理")
                return False
            
            # 保存订单到数据库
            order = self._save_order_to_db(order_info)
            
            # 执行自动发货
            success = self._auto_ship_order(order)
            
            if success:
                logger.info(f"订单 {order_sn} 处理成功")
                return True
            else:
                logger.error(f"订单 {order_sn} 处理失败")
                return False
                
        except Exception as e:
            logger.error(f"处理订单失败: {e}")
            return False
    
    def _is_virtual_goods_order(self, order_info: Dict[str, Any]) -> bool:
        """判断是否为虚拟商品订单"""
        # 检查商品类型
        goods_list = order_info.get("goods_list", [])
        for goods in goods_list:
            goods_type = goods.get("goods_type")
            # 虚拟商品类型标识
            if goods_type in [1, 2, 3]:  # 根据拼多多API文档调整
                return True
        return False
    
    def _save_order_to_db(self, order_info: Dict[str, Any]) -> Order:
        """保存订单到数据库"""
        try:
            order_sn = order_info.get("order_sn")
            
            # 检查订单是否已存在
            existing_order = self.order_service.get_order_by_sn(order_sn)
            if existing_order:
                logger.info(f"订单 {order_sn} 已存在，更新信息")
                return existing_order
            
            # 创建新订单记录
            order = Order(
                order_sn=order_sn,
                buyer_id=order_info.get("buyer_id"),
                buyer_name=order_info.get("buyer_name"),
                order_status=order_info.get("order_status"),
                pay_time=order_info.get("pay_time"),
                order_amount=order_info.get("order_amount"),
                goods_info=order_info.get("goods_list", []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.order_service.create_order(order)
            logger.info(f"订单 {order_sn} 保存到数据库成功")
            
            return order
            
        except Exception as e:
            logger.error(f"保存订单到数据库失败: {e}")
            raise OrderException(f"保存订单到数据库失败: {e}")
    
    def _auto_ship_order(self, order: Order) -> bool:
        """自动发货"""
        try:
            order_sn = order.order_sn
            
            # 生成虚拟商品信息
            goods_info = self._generate_virtual_goods_info(order)
            
            # 调用发货API
            result = self.api_client.send_order_goods(order_sn, goods_info)
            
            # 检查发货结果
            if result.get("order_goods_send_response", {}).get("success"):
                # 更新订单状态
                order.order_status = OrderStatus.SHIPPED.value
                order.shipped_at = datetime.now()
                order.goods_info = json.dumps(goods_info)  # 转换为JSON字符串
                self.order_service.update_order(order)
                
                logger.info(f"订单 {order_sn} 自动发货成功")
                return True
            else:
                logger.error(f"订单 {order_sn} 自动发货失败")
                return False
                
        except Exception as e:
            logger.error(f"自动发货失败: {e}")
            return False
    
    def _generate_virtual_goods_info(self, order: Order) -> Dict[str, Any]:
        """生成虚拟商品信息"""
        # 这里需要根据具体的虚拟商品类型来生成相应的信息
        # 例如：卡密、兑换码、账号信息等
        
        goods_info = {
            "goods_type": "virtual",
            "delivery_method": "auto",
            "delivery_content": {
                "type": "card_password",  # 卡密类型
                "content": self._generate_card_password(),  # 生成卡密
                "instructions": "请妥善保管您的卡密信息"
            },
            "delivery_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return goods_info
    
    def _generate_card_password(self) -> str:
        """生成卡密"""
        import random
        import string
        
        # 生成16位随机卡密
        characters = string.ascii_uppercase + string.digits
        card_password = ''.join(random.choice(characters) for _ in range(16))
        
        return card_password
    
    def monitor_orders(self):
        """监控订单状态"""
        try:
            logger.info("开始监控订单状态")
            
            # 获取待处理订单
            pending_orders = self.get_pending_orders()
            
            # 处理每个订单
            success_count = 0
            for order_data in pending_orders:
                if self.process_order(order_data):
                    success_count += 1
            
            logger.info(f"订单监控完成，成功处理 {success_count}/{len(pending_orders)} 个订单")
            
        except Exception as e:
            logger.error(f"订单监控失败: {e}")
            raise OrderException(f"订单监控失败: {e}")
