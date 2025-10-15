"""
通知服务模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

from config.settings import settings
from core.exceptions import NotificationException


class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.enabled = settings.notification_enabled
        self.smtp_server = settings.email_smtp_server
        self.smtp_port = settings.email_smtp_port
        self.username = settings.email_username
        self.password = settings.email_password
        self.to_email = settings.email_to
    
    def send_email(self, subject: str, content: str, to_email: Optional[str] = None) -> bool:
        """发送邮件通知"""
        if not self.enabled or not self.smtp_server:
            logger.warning("邮件通知未启用或配置不完整")
            return False
        
        try:
            to_email = to_email or self.to_email
            if not to_email:
                logger.error("收件人邮箱未配置")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = f"[拼多多自动核销] {subject}"
            
            # 添加邮件内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"邮件发送成功: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise NotificationException(f"邮件发送失败: {e}")
    
    def send_success_notification(self, message: str) -> bool:
        """发送成功通知"""
        subject = "操作成功"
        content = f"操作成功完成:\n{message}"
        return self.send_email(subject, content)
    
    def send_error_notification(self, message: str) -> bool:
        """发送错误通知"""
        subject = "系统错误"
        content = f"系统发生错误:\n{message}\n\n请及时检查系统状态。"
        return self.send_email(subject, content)
    
    def send_verification_notification(self, order_sn: str, success: bool) -> bool:
        """发送核销通知"""
        if success:
            subject = "订单核销成功"
            content = f"订单 {order_sn} 核销成功"
        else:
            subject = "订单核销失败"
            content = f"订单 {order_sn} 核销失败，请检查订单状态"
        
        return self.send_email(subject, content)
    
    def send_daily_report(self, stats: dict) -> bool:
        """发送日报"""
        subject = "每日运行报告"
        content = f"""
拼多多自动核销系统每日报告:

订单处理统计:
- 总订单数: {stats.get('total_orders', 0)}
- 成功处理: {stats.get('success_orders', 0)}
- 失败订单: {stats.get('failed_orders', 0)}

核销统计:
- 总核销数: {stats.get('total_verifications', 0)}
- 成功核销: {stats.get('success_verifications', 0)}
- 失败核销: {stats.get('failed_verifications', 0)}

系统状态: 正常运行
报告时间: {stats.get('report_time', '')}
        """
        return self.send_email(subject, content)
