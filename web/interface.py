"""
Web管理界面
"""
import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
try:
    from fastapi.templating import Jinja2Templates
except ImportError:
    # 如果Jinja2Templates不可用，使用简单的HTML响应
    Jinja2Templates = None
from typing import Optional, List
import json
from datetime import datetime

from config.settings import settings
from core.order_manager import OrderManager
from core.verification import VirtualGoodsVerifier
from services.order_service import OrderService
from services.verification_service import VerificationService
from services.auth_service import AuthService
from utils.logger import setup_logger


class WebInterface:
    """Web管理界面"""
    
    def __init__(self):
        # 设置日志
        setup_logger()
        
        # 初始化组件
        self.order_manager = OrderManager()
        self.verifier = VirtualGoodsVerifier()
        self.order_service = OrderService()
        self.verification_service = VerificationService()
        self.auth_service = AuthService()
        
        # 创建FastAPI应用
        self.app = FastAPI(title="拼多多自动核销系统", version="1.0.0")
        
        # 设置模板和静态文件
        import os
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        
        # 暂时禁用Jinja2Templates，使用简单的HTML响应
        self.templates = None
        print("警告: 使用简单的HTML响应模式")
            
        self.app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # 注册路由
        self._register_routes()
    
    def _render_simple_html(self, title: str, content: str) -> str:
        """渲染简单的HTML页面"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .content {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
                .nav a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>拼多多自动核销系统</h1>
                    <div class="nav">
                        <a href="/">仪表板</a>
                        <a href="/orders">订单管理</a>
                        <a href="/verification">核销管理</a>
                        <a href="/logs">日志查看</a>
                        <a href="/settings">系统设置</a>
                    </div>
                </div>
                <div class="content">
                    {content}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _register_routes(self):
        """注册路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """仪表板"""
            try:
                # 获取统计数据
                stats = await self._get_dashboard_stats()
                content = f"""
                <h2>系统仪表板</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 5px;">
                        <h3>总订单数</h3>
                        <p style="font-size: 24px; margin: 10px 0;">{stats.get('total_orders', 0)}</p>
                    </div>
                    <div style="background: #e8f5e8; padding: 20px; border-radius: 5px;">
                        <h3>已核销</h3>
                        <p style="font-size: 24px; margin: 10px 0;">{stats.get('successful_verifications', 0)}</p>
                    </div>
                    <div style="background: #fff3e0; padding: 20px; border-radius: 5px;">
                        <h3>待核销</h3>
                        <p style="font-size: 24px; margin: 10px 0;">{stats.get('verifiable_orders', 0)}</p>
                    </div>
                    <div style="background: #fce4ec; padding: 20px; border-radius: 5px;">
                        <h3>已完成订单</h3>
                        <p style="font-size: 24px; margin: 10px 0;">{stats.get('finished_orders', 0)}</p>
                    </div>
                </div>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 5px;">
                    <h3>系统状态</h3>
                    <p>状态: <span style="color: green;">运行中</span></p>
                    <p>最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("仪表板", content))
            except Exception as e:
                error_content = f"""
                <h2>错误</h2>
                <div style="background: #ffebee; padding: 20px; border-radius: 5px; color: #c62828;">
                    <p><strong>错误信息:</strong> {str(e)}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("错误", error_content))
        
        @self.app.get("/orders", response_class=HTMLResponse)
        async def orders_page(request: Request, page: int = 1, page_size: int = 20):
            """订单管理页面"""
            try:
                # 获取所有订单（分别获取不同状态的订单）
                pending_orders = self.order_service.get_orders_by_status(1, limit=1000)  # 已支付
                shipped_orders = self.order_service.get_orders_by_status(2, limit=1000)  # 已发货
                finished_orders = self.order_service.get_orders_by_status(4, limit=1000)  # 已完成
                
                # 合并所有订单
                all_orders = pending_orders + shipped_orders + finished_orders
                
                # 分页处理
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                page_orders = all_orders[start_idx:end_idx]
                
                # 生成订单列表HTML
                orders_html = ""
                for order in page_orders:
                    status_text = {
                        1: "已支付",
                        2: "已发货", 
                        3: "已收货",
                        4: "已完成",
                        5: "已取消"
                    }.get(order.order_status, f"未知状态{order.order_status}")
                    
                    verification_status = "已核销" if order.verification_status else "未核销"
                    
                    orders_html += f"""
                    <tr>
                        <td>{order.order_sn}</td>
                        <td>{order.buyer_name}</td>
                        <td>{status_text}</td>
                        <td>{order.order_amount}</td>
                        <td>{verification_status}</td>
                        <td>{order.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
                        <td>
                            <button onclick="viewOrder('{order.order_sn}')" class="btn btn-sm btn-info">查看</button>
                            {f'<button onclick="verifyOrder(\'{order.order_sn}\', \'{order.verification_code}\')" class="btn btn-sm btn-success">核销</button>' if order.order_status == 2 and not order.verification_status else ''}
                        </td>
                    </tr>
                    """
                
                content = f"""
                <h2>订单管理</h2>
                <div style="margin-bottom: 20px;">
                    <button onclick="refreshOrders()" class="btn btn-primary">刷新</button>
                    <span style="margin-left: 20px;">共 {len(all_orders)} 个订单</span>
                </div>
                
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="border: 1px solid #ddd; padding: 8px;">订单号</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">买家</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">状态</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">金额</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">核销状态</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">创建时间</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            {orders_html}
                        </tbody>
                    </table>
                </div>
                
                <script>
                function viewOrder(orderSn) {{
                    alert('查看订单: ' + orderSn);
                }}
                
                function verifyOrder(orderSn, verificationCode) {{
                    if (confirm('确认核销订单 ' + orderSn + '?')) {{
                        // 这里可以调用核销API
                        fetch('/api/verify', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                order_sn: orderSn,
                                verification_code: verificationCode
                            }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            alert('核销结果: ' + JSON.stringify(data));
                            location.reload();
                        }})
                        .catch(error => {{
                            alert('核销失败: ' + error);
                        }});
                    }}
                }}
                
                function refreshOrders() {{
                    location.reload();
                }}
                </script>
                """
                
                return HTMLResponse(content=self._render_simple_html("订单管理", content))
            except Exception as e:
                error_content = f"""
                <h2>错误</h2>
                <div style="background: #ffebee; padding: 20px; border-radius: 5px; color: #c62828;">
                    <p><strong>错误信息:</strong> {str(e)}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("错误", error_content))
        
        @self.app.get("/verification", response_class=HTMLResponse)
        async def verification_page(request: Request, page: int = 1, page_size: int = 20):
            """核销管理页面"""
            try:
                records = self.verification_service.get_verification_records(
                    page=page, page_size=page_size
                )
                
                # 生成核销记录列表HTML
                records_html = ""
                for record in records:
                    status_text = "成功" if record.verification_status else "失败"
                    status_color = "#4caf50" if record.verification_status else "#f44336"
                    
                    records_html += f"""
                    <tr>
                        <td>{record.order_sn}</td>
                        <td>{record.verification_code}</td>
                        <td style="color: {status_color};">{status_text}</td>
                        <td>{record.verification_result or '无'}</td>
                        <td>{record.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    """
                
                content = f"""
                <h2>核销管理</h2>
                <div style="margin-bottom: 20px;">
                    <button onclick="refreshRecords()" class="btn btn-primary">刷新</button>
                    <span style="margin-left: 20px;">共 {len(records)} 条核销记录</span>
                </div>
                
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                        <thead>
                            <tr style="background: #f5f5f5;">
                                <th style="border: 1px solid #ddd; padding: 8px;">订单号</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">核销码</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">状态</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">结果</th>
                                <th style="border: 1px solid #ddd; padding: 8px;">时间</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records_html}
                        </tbody>
                    </table>
                </div>
                
                <script>
                function refreshRecords() {{
                    location.reload();
                }}
                </script>
                """
                
                return HTMLResponse(content=self._render_simple_html("核销管理", content))
            except Exception as e:
                error_content = f"""
                <h2>错误</h2>
                <div style="background: #ffebee; padding: 20px; border-radius: 5px; color: #c62828;">
                    <p><strong>错误信息:</strong> {str(e)}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("错误", error_content))

        @self.app.get("/oauth/login")
        async def oauth_login():
            """跳转到拼多多授权页"""
            try:
                client_id = settings.pdd_app_id
                redirect_uri = settings.pdd_redirect_uri or ""
                state = datetime.now().strftime("%Y%m%d%H%M%S")
                auth_url = (
                    "https://mms.pinduoduo.com/open.html?response_type=code"
                    f"&client_id={client_id}&redirect_uri={redirect_uri}&state={state}"
                )
                return RedirectResponse(url=auth_url)
            except Exception as e:
                return HTMLResponse(content=self._render_simple_html("错误", str(e)), status_code=500)

        @self.app.get("/oauth/callback")
        async def oauth_callback(code: str = "", state: str = ""):
            """拼多多授权回调，兑换 access_token"""
            try:
                api = self.order_manager.api_client
                result = api.exchange_token(code)
                access_token = (
                    result.get("access_token")
                    or result.get("pop_auth_token_create_response", {}).get("access_token")
                )
                refresh_token = (
                    result.get("refresh_token")
                    or result.get("pop_auth_token_create_response", {}).get("refresh_token")
                )
                expires_in = (
                    result.get("expires_in")
                    or result.get("pop_auth_token_create_response", {}).get("expires_in")
                )
                shop_id = result.get("shop_id")
                shop_name = result.get("shop_name")

                if not access_token:
                    raise ValueError("授权失败：未获取到 access_token")

                self.auth_service.save_or_update_auth(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in_seconds=expires_in,
                    shop_id=shop_id,
                    shop_name=shop_name,
                )
                content = "授权成功，已保存店铺令牌。可返回设置页查看绑定状态。"
                return HTMLResponse(content=self._render_simple_html("授权成功", content))
            except Exception as e:
                error_content = f"授权失败: {str(e)}"
                return HTMLResponse(content=self._render_simple_html("错误", error_content), status_code=500)
        
        @self.app.get("/settings", response_class=HTMLResponse)
        async def settings_page(request: Request):
            """系统设置页面"""
            try:
                auth = self.auth_service.get_active_auth()
                bind_html = "未绑定"
                if auth:
                    bind_html = f"已绑定{ '（将过期）' if auth.is_expired() else '' }，店铺ID: {auth.shop_id or '-'}"

                content = f"""
                <h2>系统设置</h2>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h3>当前配置</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>测试模式:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{settings.test_mode}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>订单检查间隔:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{settings.order_check_interval}秒</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>通知启用:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{settings.notification_enabled}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>店铺绑定:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{bind_html}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <a href="/oauth/login" class="btn btn-primary">授权店铺</a>
                </div>

                <div style="background: #e3f2fd; padding: 20px; border-radius: 5px;">
                    <h3>说明</h3>
                    <p>系统设置需要修改配置文件后重启服务才能生效。</p>
                    <p>配置文件位置: <code>.env</code></p>
                </div>
                """
                
                return HTMLResponse(content=self._render_simple_html("系统设置", content))
            except Exception as e:
                error_content = f"""
                <h2>错误</h2>
                <div style="background: #ffebee; padding: 20px; border-radius: 5px; color: #c62828;">
                    <p><strong>错误信息:</strong> {str(e)}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("错误", error_content))
        
        @self.app.get("/logs", response_class=HTMLResponse)
        async def logs_page(request: Request):
            """日志查看页面"""
            try:
                # 读取日志文件
                log_content = await self._read_log_file()
                
                content = f"""
                <h2>日志查看</h2>
                <div style="margin-bottom: 20px;">
                    <button onclick="refreshLogs()" class="btn btn-primary">刷新</button>
                    <button onclick="clearLogs()" class="btn btn-warning">清空日志</button>
                </div>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; max-height: 600px; overflow-y: auto;">
{log_content}
                </div>
                
                <script>
                function refreshLogs() {{
                    location.reload();
                }}
                
                function clearLogs() {{
                    if (confirm('确认清空日志文件?')) {{
                        fetch('/api/clear-logs', {{method: 'POST'}})
                        .then(response => response.json())
                        .then(data => {{
                            alert('清空结果: ' + JSON.stringify(data));
                            location.reload();
                        }})
                        .catch(error => {{
                            alert('清空失败: ' + error);
                        }});
                    }}
                }}
                </script>
                """
                
                return HTMLResponse(content=self._render_simple_html("日志查看", content))
            except Exception as e:
                error_content = f"""
                <h2>错误</h2>
                <div style="background: #ffebee; padding: 20px; border-radius: 5px; color: #c62828;">
                    <p><strong>错误信息:</strong> {str(e)}</p>
                </div>
                """
                return HTMLResponse(content=self._render_simple_html("错误", error_content))
        
        # API接口
        @self.app.post("/api/clear-logs")
        async def api_clear_logs():
            try:
                log_path = settings.log_file
                if os.path.exists(log_path):
                    with open(log_path, "w", encoding="utf-8") as f:
                        f.write("")
                return {"success": True}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        @self.app.post("/api/verify")
        async def api_verify_order(request: Request):
            """手动核销订单API"""
            try:
                # 从JSON请求体中获取数据
                body = await request.json()
                order_sn = body.get("order_sn")
                verification_code = body.get("verification_code")
                
                if not order_sn or not verification_code:
                    raise HTTPException(status_code=400, detail="缺少必要参数")
                
                result = self.verifier.verify_order(order_sn, verification_code)
                return result
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/orders")
        async def api_get_orders(page: int = 1, page_size: int = 20):
            """获取订单列表API"""
            try:
                orders = self.order_service.get_orders_by_status(None, limit=page_size)
                return {
                    "orders": [order.to_dict() for order in orders],
                    "page": page,
                    "page_size": page_size,
                    "total": len(orders)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/verification-records")
        async def api_get_verification_records(page: int = 1, page_size: int = 20):
            """获取核销记录API"""
            try:
                result = self.verifier.get_verification_records(page=page, page_size=page_size)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/process-order")
        async def api_process_order(request: Request):
            """手动处理订单API"""
            try:
                # 从JSON请求体中获取数据
                body = await request.json()
                order_sn = body.get("order_sn")
                
                if not order_sn:
                    raise HTTPException(status_code=400, detail="缺少订单号参数")
                
                # 获取订单详情
                order_detail = self.order_manager.api_client.get_order_detail(order_sn)
                order_info = order_detail.get("order_detail_get_response", {}).get("order", {})
                
                # 处理订单
                success = self.order_manager.process_order(order_info)
                
                return {
                    "success": success,
                    "message": "订单处理成功" if success else "订单处理失败"
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/api/stats")
        async def api_get_stats():
            """获取统计数据API"""
            try:
                stats = await self._get_dashboard_stats()
                return stats
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_dashboard_stats(self):
        """获取仪表板统计数据"""
        try:
            # 获取订单统计
            # 由于get_orders_by_status不支持None参数，我们需要分别获取各种状态的订单
            pending_orders = len(self.order_service.get_orders_by_status(1, limit=1000))  # 已支付
            shipped_orders = len(self.order_service.get_orders_by_status(2, limit=1000))  # 已发货
            finished_orders = len(self.order_service.get_orders_by_status(4, limit=1000))  # 已完成
            total_orders = pending_orders + shipped_orders + finished_orders
            
            # 获取核销统计
            verification_records = self.verification_service.get_verification_records(page=1, page_size=1000)
            total_verifications = len(verification_records)
            successful_verifications = len([r for r in verification_records if r.verification_status])
            
            # 获取可以核销的订单（已发货且未核销）
            verifiable_orders = self.order_service.get_orders_by_status(2, limit=1000)  # 已发货
            verifiable_orders = [o for o in verifiable_orders if not o.verification_status]  # 未核销
            verifiable_count = len(verifiable_orders)
            
            return {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "shipped_orders": shipped_orders,
                "finished_orders": finished_orders,
                "verifiable_orders": verifiable_count,  # 可以核销的订单数
                "total_verifications": total_verifications,
                "successful_verifications": successful_verifications,
                "system_status": "running",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                "total_orders": 0,
                "pending_orders": 0,
                "shipped_orders": 0,
                "finished_orders": 0,
                "total_verifications": 0,
                "successful_verifications": 0,
                "system_status": "error",
                "error": str(e)
            }
    
    async def _read_log_file(self):
        """读取日志文件"""
        try:
            log_file = settings.log_file
            if not log_file or not os.path.exists(log_file):
                return "日志文件不存在"
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 只返回最后1000行
            lines = content.split('\n')
            return '\n'.join(lines[-1000:])
        except Exception as e:
            return f"读取日志文件失败: {e}"
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """运行Web服务器"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


def create_web_interface():
    """创建Web界面实例"""
    return WebInterface()
