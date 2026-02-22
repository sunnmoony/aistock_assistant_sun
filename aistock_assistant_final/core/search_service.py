# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 新闻搜索服务
===================================

职责:
1. 集成多个搜索引擎(Tavily/SerpAPI/Bocha/Brave)
2. 实现新闻搜索结果缓存
3. 新闻摘要和情感分析
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .default_search_engine import DefaultSearchEngine

logger = logging.getLogger(__name__)


class SearchService:
    """
    新闻搜索服务

    职责:
    1. 集成多个搜索引擎
    2. 实现搜索结果缓存
    3. 新闻摘要和情感分析
    """

    def __init__(self, tavily_keys: List[str] = None,
                 serpapi_keys: List[str] = None,
                 bocha_keys: List[str] = None,
                 brave_keys: List[str] = None):
        """
        初始化新闻搜索服务

        Args:
            tavily_keys: Tavily API Keys列表
            serpapi_keys: SerpAPI Keys列表
            bocha_keys: Bocha API Keys列表
            brave_keys: Brave Search API Keys列表
        """
        self.tavily_keys = tavily_keys or []
        self.serpapi_keys = serpapi_keys or []
        self.bocha_keys = bocha_keys or []
        self.brave_keys = brave_keys or []

        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 缓存1小时

        self._current_tavily_index = 0
        self._current_serpapi_index = 0
        self._current_bocha_index = 0
        self._current_brave_index = 0

        self.default_search_engine = DefaultSearchEngine()

        logger.info(f"新闻搜索服务初始化完成,共 {len(self._get_all_keys())} 个API Key")

    def _get_all_keys(self) -> List[str]:
        """获取所有API Key"""
        return self.tavily_keys + self.serpapi_keys + self.bocha_keys + self.brave_keys

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索新闻(别名方法)

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            新闻列表
        """
        return self.search_news(query, max_results)

    def search_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索新闻

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            新闻列表
        """
        # 检查缓存
        cache_key = f"news_{query}_{max_results}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            cache_time = cached_result.get('timestamp', 0)

            if time.time() - cache_time < self.cache_ttl:
                logger.info(f"使用缓存结果: {query}")
                return cached_result['results']

        # 按优先级搜索
        all_keys = self._get_all_keys()
        if not all_keys:
            logger.warning("没有配置任何搜索引擎API Key")
            return []

        # Tavily (最高优先级)
        if self.tavily_keys:
            results = self._search_tavily(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # SerpAPI
        if self.serpapi_keys:
            results = self._search_serpapi(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # Bocha
        if self.bocha_keys:
            results = self._search_bocha(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # Brave
        if self.brave_keys:
            results = self._search_brave(query, max_results)
            if results:
                self._cache_result(cache_key, results)
                return results

        # 使用默认搜索引擎
        logger.info(f"使用默认搜索引擎: {query}")
        results = self.default_search_engine.search(query, max_results)
        if results:
            self._cache_result(cache_key, results)
            return results

        logger.warning(f"所有搜索引擎都失败: {query}")
        return []

    def _search_tavily(self, query: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """使用 Tavily 搜索"""
        try:
            import requests

            api_key = self.tavily_keys[self._current_tavily_index]
            url = "https://api.tavily.com/search"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_domains": ["eastmoney.com", "finance.sina.com.cn", "10jqka.com"],
                "days": 7
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'results' not in result:
                return None

            articles = []
            for item in result['results'][:max_results]:
                articles.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('content', ''),
                    "published_date": item.get('publishedDate', ''),
                    "source": "Tavily",
                    "sentiment": self._analyze_sentiment(item.get('content', ''))
                })

            logger.info(f"Tavily 搜索成功: {len(articles)} 条结果")
            self._rotate_tavily_index()
            return articles

        except Exception as e:
            logger.error(f"Tavily 搜索失败: {e}")
            self._rotate_tavily_index()
            return None

    def _search_serpapi(self, query: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """使用 SerpAPI 搜索"""
        try:
            import requests

            api_key = self.serpapi_keys[self._current_serpapi_index]
            url = f"https://serpapi.com/search"

            params = {
                "engine": "google",
                "q": query,
                "num": max_results,
                "api_key": api_key,
                "tbs": "nws"
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'organic_results' not in result:
                return None

            articles = []
            for item in result['organic_results'][:max_results]:
                articles.append({
                    "title": item.get('title', ''),
                    "url": item.get('link', ''),
                    "snippet": item.get('snippet', ''),
                    "published_date": '',
                    "source": "SerpAPI",
                    "sentiment": self._analyze_sentiment(item.get('snippet', ''))
                })

            logger.info(f"SerpAPI 搜索成功: {len(articles)} 条结果")
            self._rotate_serpapi_index()
            return articles

        except Exception as e:
            logger.error(f"SerpAPI 搜索失败: {e}")
            self._rotate_serpapi_index()
            return None

    def _search_bocha(self, query: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """使用 Bocha 搜索"""
        try:
            import requests

            api_key = self.bocha_keys[self._current_bocha_index]
            url = "https://api.bocha.cn/api/v1/search"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "query": query,
                "max_results": max_results,
                "search_type": "web",
                "ai_summary": True
            }

            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'data' not in result or 'web_pages' not in result['data']:
                return None

            web_pages = result['data'].get('web_pages', [])
            articles = []
            for item in web_pages[:max_results]:
                articles.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('ai_summary', ''),
                    "published_date": '',
                    "source": "Bocha",
                    "sentiment": self._analyze_sentiment(item.get('ai_summary', ''))
                })

            logger.info(f"Bocha 搜索成功: {len(articles)} 条结果")
            self._rotate_bocha_index()
            return articles

        except Exception as e:
            logger.error(f"Bocha 搜索失败: {e}")
            self._rotate_bocha_index()
            return None

    def _search_brave(self, query: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """使用 Brave Search 搜索"""
        try:
            import requests

            api_key = self.brave_keys[self._current_brave_index]
            url = "https://api.search.brave.com/res/v1/web/search"

            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }

            params = {
                "q": query,
                "count": max_results,
                "text_decorations": False,
                "search_lang": "zh-CN"
            }

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'web' not in result:
                return None

            articles = []
            for item in result['web']['results'][:max_results]:
                articles.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "snippet": item.get('snippet', ''),
                    "published_date": '',
                    "source": "Brave",
                    "sentiment": self._analyze_sentiment(item.get('snippet', ''))
                })

            logger.info(f"Brave 搜索成功: {len(articles)} 条结果")
            self._rotate_brave_index()
            return articles

        except Exception as e:
            logger.error(f"Brave 搜索失败: {e}")
            self._rotate_brave_index()
            return None

    def _analyze_sentiment(self, text: str) -> str:
        """
        简单情感分析

        Args:
            text: 文本内容

        Returns:
            情感: positive/negative/neutral
        """
        positive_keywords = ['上涨', '利好', '突破', '增长', '盈利', '增长', '强势', '领涨']
        negative_keywords = ['下跌', '利空', '回调', '亏损', '下跌', '弱势', '领跌']

        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)

        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"

    def _cache_result(self, key: str, results: List[Dict[str, Any]]):
        """缓存搜索结果"""
        self.cache[key] = {
            'timestamp': time.time(),
            'results': results
        }

    def _rotate_tavily_index(self):
        """轮换 Tavily Key"""
        self._current_tavily_index = (self._current_tavily_index + 1) % len(self.tavily_keys)

    def _rotate_serpapi_index(self):
        """轮换 SerpAPI Key"""
        self._current_serpapi_index = (self._current_serpapi_index + 1) % len(self.serpapi_keys)

    def _rotate_bocha_index(self):
        """轮换 Bocha Key"""
        self._current_bocha_index = (self._current_bocha_index + 1) % len(self.bocha_keys)

    def _rotate_brave_index(self):
        """轮换 Brave Key"""
        self._current_brave_index = (self._current_brave_index + 1) % len(self.brave_keys)

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("新闻搜索缓存已清空")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'total_keys': len(self._get_all_keys()),
            'tavily_keys': len(self.tavily_keys),
            'serpapi_keys': len(self.serpapi_keys),
            'bocha_keys': len(self.bocha_keys),
            'brave_keys': len(self.brave_keys),
            'cache_size': len(self.cache),
            'current_tavily_index': self._current_tavily_index,
            'current_serpapi_index': self._current_serpapi_index,
            'current_bocha_index': self._current_bocha_index,
            'current_brave_index': self._current_brave_index
        }
