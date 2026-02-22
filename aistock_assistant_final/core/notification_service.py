# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 通知服务模块
===================================

职责:
1. 统一管理多种通知渠道
2. 支持微信、飞书、Telegram、邮件等通知
3. 提供消息发送和状态跟踪
"""

import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    """通知发送结果"""
    success: bool
    channel: str
    message: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class NotificationService:
    """
    通知服务 - 统一管理多种通知渠道
    
    支持渠道:
    - 企业微信 Webhook
    - 飞书 Webhook
    - Telegram Bot
    - 邮件 SMTP
    - Pushover
    - ServerChan
    - PushPlus
    - 自定义 Webhook
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化通知服务
        
        Args:
            config: 配置字典，包含各渠道的配置信息
        """
        self.config = config or {}
        self._enabled_channels = self._detect_enabled_channels()
        logger.info(f"通知服务初始化完成，启用渠道: {self._enabled_channels}")

    def _detect_enabled_channels(self) -> List[str]:
        """检测已启用的通知渠道"""
        channels = []
        
        if self.config.get("wechat_webhook_url"):
            channels.append("wechat")
        if self.config.get("feishu_webhook_url"):
            channels.append("feishu")
        if self.config.get("telegram_bot_token") and self.config.get("telegram_chat_id"):
            channels.append("telegram")
        if self.config.get("email_sender") and self.config.get("email_password"):
            channels.append("email")
        if self.config.get("pushover_user_key") and self.config.get("pushover_api_token"):
            channels.append("pushover")
        if self.config.get("serverchan3_sendkey"):
            channels.append("serverchan")
        if self.config.get("pushplus_token"):
            channels.append("pushplus")
        if self.config.get("custom_webhook_urls"):
            channels.append("custom")
        
        return channels

    def send(
        self,
        title: str,
        content: str,
        channels: List[str] = None,
        **kwargs
    ) -> List[NotificationResult]:
        """
        发送通知
        
        Args:
            title: 通知标题
            content: 通知内容
            channels: 指定发送渠道列表，None表示发送到所有已启用渠道
            **kwargs: 额外参数
            
        Returns:
            发送结果列表
        """
        results = []
        target_channels = channels or self._enabled_channels
        
        if not target_channels:
            logger.warning("没有可用的通知渠道")
            return [NotificationResult(False, "none", "没有可用的通知渠道")]
        
        for channel in target_channels:
            try:
                result = self._send_to_channel(channel, title, content, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"发送通知到 {channel} 失败: {e}")
                results.append(NotificationResult(False, channel, str(e)))
        
        return results

    def _send_to_channel(
        self,
        channel: str,
        title: str,
        content: str,
        **kwargs
    ) -> NotificationResult:
        """发送到指定渠道"""
        handlers = {
            "wechat": self._send_wechat,
            "feishu": self._send_feishu,
            "telegram": self._send_telegram,
            "email": self._send_email,
            "pushover": self._send_pushover,
            "serverchan": self._send_serverchan,
            "pushplus": self._send_pushplus,
            "custom": self._send_custom_webhook
        }
        
        handler = handlers.get(channel)
        if not handler:
            return NotificationResult(False, channel, f"不支持的通知渠道: {channel}")
        
        return handler(title, content, **kwargs)

    def _send_wechat(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送企业微信通知"""
        webhook_url = self.config.get("wechat_webhook_url")
        if not webhook_url:
            return NotificationResult(False, "wechat", "未配置企业微信Webhook")
        
        try:
            msg_type = self.config.get("wechat_msg_type", "markdown")
            max_bytes = self.config.get("wechat_max_bytes", 4096)
            
            if len(content.encode("utf-8")) > max_bytes:
                content = content[:max_bytes // 3]
            
            if msg_type == "markdown":
                data = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"**{title}**\n\n{content}"
                    }
                }
            else:
                data = {
                    "msgtype": "text",
                    "text": {
                        "content": f"{title}\n\n{content}"
                    }
                }
            
            response = requests.post(webhook_url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return NotificationResult(True, "wechat", "发送成功")
            else:
                return NotificationResult(False, "wechat", result.get("errmsg", "发送失败"))
                
        except Exception as e:
            return NotificationResult(False, "wechat", str(e))

    def _send_feishu(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送飞书通知"""
        webhook_url = self.config.get("feishu_webhook_url")
        if not webhook_url:
            return NotificationResult(False, "feishu", "未配置飞书Webhook")
        
        try:
            max_bytes = self.config.get("feishu_max_bytes", 30720)
            if len(content.encode("utf-8")) > max_bytes:
                content = content[:max_bytes // 3]
            
            data = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
                        }
                    ]
                }
            }
            
            response = requests.post(webhook_url, json=data, timeout=10)
            result = response.json()
            
            if result.get("StatusCode") == 0:
                return NotificationResult(True, "feishu", "发送成功")
            else:
                return NotificationResult(False, "feishu", result.get("msg", "发送失败"))
                
        except Exception as e:
            return NotificationResult(False, "feishu", str(e))

    def _send_telegram(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送Telegram通知"""
        bot_token = self.config.get("telegram_bot_token")
        chat_id = self.config.get("telegram_chat_id")
        message_thread_id = self.config.get("telegram_message_thread_id")
        
        if not bot_token or not chat_id:
            return NotificationResult(False, "telegram", "未配置Telegram Bot")
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            text = f"*{title}*\n\n{content}"
            
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            if message_thread_id:
                data["message_thread_id"] = message_thread_id
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("ok"):
                return NotificationResult(True, "telegram", "发送成功")
            else:
                return NotificationResult(False, "telegram", result.get("description", "发送失败"))
                
        except Exception as e:
            return NotificationResult(False, "telegram", str(e))

    def _send_email(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送邮件通知"""
        sender = self.config.get("email_sender")
        password = self.config.get("email_password")
        receivers = self.config.get("email_receivers", [])
        
        if not sender or not password or not receivers:
            return NotificationResult(False, "email", "未配置邮件发送")
        
        if isinstance(receivers, str):
            receivers = [receivers]
        
        try:
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = ", ".join(receivers)
            msg["Subject"] = title
            msg.attach(MIMEText(content, "plain", "utf-8"))
            
            with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receivers, msg.as_string())
            
            return NotificationResult(True, "email", "发送成功")
            
        except Exception as e:
            return NotificationResult(False, "email", str(e))

    def _send_pushover(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送Pushover通知"""
        user_key = self.config.get("pushover_user_key")
        api_token = self.config.get("pushover_api_token")
        
        if not user_key or not api_token:
            return NotificationResult(False, "pushover", "未配置Pushover")
        
        try:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "user": user_key,
                "token": api_token,
                "title": title,
                "message": content
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("status") == 1:
                return NotificationResult(True, "pushover", "发送成功")
            else:
                return NotificationResult(False, "pushover", result.get("errors", ["发送失败"])[0])
                
        except Exception as e:
            return NotificationResult(False, "pushover", str(e))

    def _send_serverchan(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送ServerChan通知"""
        sendkey = self.config.get("serverchan3_sendkey")
        
        if not sendkey:
            return NotificationResult(False, "serverchan", "未配置ServerChan")
        
        try:
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
            data = {
                "title": title,
                "desp": content
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                return NotificationResult(True, "serverchan", "发送成功")
            else:
                return NotificationResult(False, "serverchan", result.get("message", "发送失败"))
                
        except Exception as e:
            return NotificationResult(False, "serverchan", str(e))

    def _send_pushplus(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送PushPlus通知"""
        token = self.config.get("pushplus_token")
        
        if not token:
            return NotificationResult(False, "pushplus", "未配置PushPlus")
        
        try:
            url = "http://www.pushplus.plus/send"
            data = {
                "token": token,
                "title": title,
                "content": content,
                "template": "html"
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 200:
                return NotificationResult(True, "pushplus", "发送成功")
            else:
                return NotificationResult(False, "pushplus", result.get("msg", "发送失败"))
                
        except Exception as e:
            return NotificationResult(False, "pushplus", str(e))

    def _send_custom_webhook(self, title: str, content: str, **kwargs) -> NotificationResult:
        """发送自定义Webhook通知"""
        urls = self.config.get("custom_webhook_urls", [])
        bearer_token = self.config.get("custom_webhook_bearer_token")
        
        if not urls:
            return NotificationResult(False, "custom", "未配置自定义Webhook")
        
        if isinstance(urls, str):
            urls = [urls]
        
        results = []
        for url in urls:
            try:
                headers = {"Content-Type": "application/json"}
                if bearer_token:
                    headers["Authorization"] = f"Bearer {bearer_token}"
                
                data = {
                    "title": title,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    results.append(True)
                else:
                    results.append(False)
                    
            except Exception as e:
                logger.error(f"自定义Webhook发送失败 {url}: {e}")
                results.append(False)
        
        if all(results):
            return NotificationResult(True, "custom", "全部发送成功")
        elif any(results):
            return NotificationResult(True, "custom", f"部分发送成功 ({sum(results)}/{len(results)})")
        else:
            return NotificationResult(False, "custom", "全部发送失败")

    def get_enabled_channels(self) -> List[str]:
        """获取已启用的通知渠道"""
        return self._enabled_channels.copy()

    def test_channel(self, channel: str) -> NotificationResult:
        """测试通知渠道"""
        return self.send(
            title="测试通知",
            content="这是一条测试消息，用于验证通知渠道是否正常工作。",
            channels=[channel]
        )[0]
