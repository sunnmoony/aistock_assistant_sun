# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - FastAPI依赖注入
===================================

职责:
1. 实现依赖注入模式
2. 管理全局单例实例
3. 支持配置热重载
"""

from typing import Generator
from fastapi import Depends

from ..core.data_manager import DataManager
from ..core.analyzer_dashboard import GeminiAnalyzer
from ..core.search_service import SearchService
from ..core.notification_service import NotificationService
from ..core.market_review import MarketReview
from ..core.feishu_doc import FeishuDocManager

_data_manager: DataManager = None
_ai_analyzer: GeminiAnalyzer = None
_search_service: SearchService = None
_notification_service: NotificationService = None
_market_review: MarketReview = None
_feishu_doc: FeishuDocManager = None


def get_data_manager() -> DataManager:
    """获取数据管理器单例"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def get_ai_analyzer() -> GeminiAnalyzer:
    """获取AI分析器单例"""
    global _ai_analyzer
    if _ai_analyzer is None:
        _ai_analyzer = GeminiAnalyzer()
    return _ai_analyzer


def get_search_service() -> SearchService:
    """获取搜索服务单例"""
    global _search_service
    if _search_service is None:
        from ..core.config import get_config
        config = get_config()
        _search_service = SearchService(
            tavily_keys=config.tavily_api_keys,
            serpapi_keys=config.serpapi_keys,
            bocha_keys=config.bocha_api_keys,
            brave_keys=config.brave_api_keys
        )
    return _search_service


def get_notification_service() -> NotificationService:
    """获取通知服务单例"""
    global _notification_service
    if _notification_service is None:
        from ..core.config import get_config
        config = get_config()
        _notification_service = NotificationService({
            'wechat_webhook_url': config.wechat_webhook_url,
            'wechat_max_bytes': config.wechat_max_bytes,
            'wechat_msg_type': config.wechat_msg_type,
            'feishu_webhook_url': config.feishu_webhook_url,
            'feishu_max_bytes': config.feishu_max_bytes,
            'telegram_bot_token': config.telegram_bot_token,
            'telegram_chat_id': config.telegram_chat_id,
            'telegram_message_thread_id': config.telegram_message_thread_id,
            'email_sender': config.email_sender,
            'email_password': config.email_password,
            'email_receivers': config.email_receivers,
            'pushover_user_key': config.pushover_user_key,
            'pushover_api_token': config.pushover_api_token,
            'serverchan3_sendkey': config.serverchan3_sendkey,
            'pushplus_token': config.pushplus_token,
            'custom_webhook_urls': config.custom_webhook_urls,
            'custom_webhook_bearer_token': config.custom_webhook_bearer_token
        })
    return _notification_service


def get_market_review() -> MarketReview:
    """获取大盘复盘单例"""
    global _market_review
    if _market_review is None:
        _market_review = MarketReview(
            data_manager=get_data_manager(),
            ai_analyzer=get_ai_analyzer(),
            search_service=get_search_service()
        )
    return _market_review


def get_feishu_doc() -> FeishuDocManager:
    """获取飞书云文档单例"""
    global _feishu_doc
    if _feishu_doc is None:
        from ..core.config import get_config
        config = get_config()
        _feishu_doc = FeishuDocManager(
            app_id=config.feishu_app_id,
            app_secret=config.feishu_app_secret,
            folder_token=config.feishu_folder_token
        )
    return _feishu_doc
