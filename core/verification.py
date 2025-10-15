"""
虚拟商品核销模块
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from core.api_client import get_api_client
from core.exceptions import VerificationException, APIException
from models.order import Order, VerificationRecord, OrderStatus
from services.verification_service import VerificationService


class VirtualGoodsVerifier:
    """虚拟商品核销器"""
    
    def __init__(self):
        self.api_client = get_api_client()
        self.verification_service = VerificationService()
        
    def verify_order(self, order_sn: str, verification_code: str) -> Dict[str, Any]:
        """核销订单"""
        try:
            logger.info(f"开始核销订单: {order_sn}, 核销码: {verification_code}")
            
            # 验证核销码格式
            if not self._validate_verification_code(verification_code):
                raise VerificationException("核销码格式不正确")
            
            # 检查订单状态
            order = self.verification_service.get_order_by_sn(order_sn)
            if not order:
                raise VerificationException(f"订单 {order_sn} 不存在")
            
            # 只允许已发货的订单进行核销
            if order.order_status != OrderStatus.SHIPPED.value:
                raise VerificationException(f"订单 {order_sn} 状态不正确，无法核销")
            
            if order.verification_status:
                raise VerificationException(f"订单 {order_sn} 已经核销过了")
            
            # 验证核销码
            if order.verification_code != verification_code:
                raise VerificationException("核销码不匹配")
            
            # 调用拼多多API进行核销
            result = self.api_client.verify_virtual_goods(order_sn, verification_code)
            
            # 检查核销结果
            if result.get("virtual_goods_verify_response", {}).get("success"):
                # 更新订单状态
                self._update_order_verification_status(order, True)
                
                # 记录核销记录
                self._create_verification_record(order_sn, verification_code, True, "api")
                
                logger.info(f"订单 {order_sn} 核销成功")
                
                return {
                    "success": True,
                    "message": "核销成功",
                    "order_sn": order_sn,
                    "verification_time": datetime.now().isoformat()
                }
            else:
                # 记录失败的核销记录
                self._create_verification_record(order_sn, verification_code, False, "api", "API核销失败")
                
                logger.error(f"订单 {order_sn} 核销失败")
                
                return {
                    "success": False,
                    "message": "核销失败",
                    "order_sn": order_sn
                }
                
        except VerificationException as e:
            logger.error(f"核销验证失败: {e}")
            raise
        except APIException as e:
            logger.error(f"API调用失败: {e}")
            raise VerificationException(f"API调用失败: {e}")
        except Exception as e:
            logger.error(f"核销过程中发生未知错误: {e}")
            raise VerificationException(f"核销过程中发生未知错误: {e}")
    
    def batch_verify_orders(self, verification_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """批量核销订单"""
        try:
            logger.info(f"开始批量核销，共 {len(verification_list)} 个订单")
            
            success_count = 0
            failed_count = 0
            results = []
            
            for item in verification_list:
                order_sn = item.get("order_sn")
                verification_code = item.get("verification_code")
                
                try:
                    result = self.verify_order(order_sn, verification_code)
                    if result["success"]:
                        success_count += 1
                    else:
                        failed_count += 1
                    results.append(result)
                except Exception as e:
                    failed_count += 1
                    results.append({
                        "success": False,
                        "message": str(e),
                        "order_sn": order_sn
                    })
            
            logger.info(f"批量核销完成，成功: {success_count}, 失败: {failed_count}")
            
            return {
                "total": len(verification_list),
                "success": success_count,
                "failed": failed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"批量核销失败: {e}")
            raise VerificationException(f"批量核销失败: {e}")
    
    def get_verification_records(self, 
                                 order_sn: Optional[str] = None,
                                 start_time: Optional[str] = None,
                                 end_time: Optional[str] = None,
                                 page: int = 1,
                                 page_size: int = 20) -> Dict[str, Any]:
        """获取核销记录"""
        try:
            logger.info(f"获取核销记录: order_sn={order_sn}, page={page}")
            
            # 从数据库获取核销记录
            records = self.verification_service.get_verification_records(
                order_sn=order_sn,
                start_time=start_time,
                end_time=end_time,
                page=page,
                page_size=page_size
            )
            
            # 转换为字典格式
            record_list = [record.to_dict() for record in records]
            
            return {
                "records": record_list,
                "page": page,
                "page_size": page_size,
                "total": len(record_list)
            }
            
        except Exception as e:
            logger.error(f"获取核销记录失败: {e}")
            raise VerificationException(f"获取核销记录失败: {e}")
    
    def _validate_verification_code(self, verification_code: str) -> bool:
        """验证核销码格式"""
        if not verification_code:
            return False
        
        # 核销码长度检查
        if len(verification_code) < 8 or len(verification_code) > 32:
            return False
        
        # 核销码字符检查（只允许字母和数字）
        if not verification_code.isalnum():
            return False
        
        return True
    
    def _update_order_verification_status(self, order: Order, verified: bool):
        """更新订单核销状态"""
        try:
            order.verification_status = verified
            order.verification_time = datetime.now()
            
            if verified:
                order.order_status = OrderStatus.FINISHED.value
                order.finished_at = datetime.now()
            
            self.verification_service.update_order(order)
            
        except Exception as e:
            logger.error(f"更新订单核销状态失败: {e}")
            raise VerificationException(f"更新订单核销状态失败: {e}")
    
    def _create_verification_record(self, 
                                   order_sn: str, 
                                   verification_code: str, 
                                   success: bool,
                                   method: str,
                                   result: Optional[str] = None):
        """创建核销记录"""
        try:
            record = VerificationRecord(
                order_sn=order_sn,
                verification_code=verification_code,
                verification_status=success,
                verification_time=datetime.now() if success else None,
                verification_method=method,
                verification_result=result or ("成功" if success else "失败")
            )
            
            self.verification_service.create_verification_record(record)
            
        except Exception as e:
            logger.error(f"创建核销记录失败: {e}")
            raise VerificationException(f"创建核销记录失败: {e}")
    
    def auto_verify_orders(self):
        """自动核销订单"""
        try:
            logger.info("开始自动核销订单")
            
            # 获取已发货但未核销的订单
            unverified_orders = self.verification_service.get_unverified_orders()
            
            verified_count = 0
            for order in unverified_orders:
                try:
                    # 这里可以根据业务逻辑自动生成核销码或从其他地方获取
                    # 示例：使用订单号作为核销码
                    verification_code = order.order_sn[-8:]  # 使用订单号后8位作为核销码
                    
                    result = self.verify_order(order.order_sn, verification_code)
                    if result["success"]:
                        verified_count += 1
                        
                except Exception as e:
                    logger.error(f"自动核销订单 {order.order_sn} 失败: {e}")
            
            logger.info(f"自动核销完成，成功核销 {verified_count} 个订单")
            
        except Exception as e:
            logger.error(f"自动核销失败: {e}")
            raise VerificationException(f"自动核销失败: {e}")
