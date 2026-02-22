# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 默认搜索引擎
===================================

职责:
1. 提供无需API Key的备用搜索功能
2. 支持多数据源搜索
3. 返回标准化的搜索结果
"""

import logging
import requests
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class DefaultSearchEngine:
    """
    默认搜索引擎 - 无需API Key的备用搜索
    
    支持:
    - 百度搜索
    - 必应搜索
    - 东方财富搜索
    """

    def __init__(self):
        """初始化默认搜索引擎"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        self._timeout = 15

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        results = []
        
        results = self._search_eastmoney(query, max_results)
        
        if not results:
            results = self._search_bing(query, max_results)
        
        if not results:
            results = self._search_baidu(query, max_results)
        
        return results[:max_results]

    def _search_eastmoney(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """搜索东方财富"""
        try:
            url = f"https://searchapi.eastmoney.com/bussiness/web/QuotationLabelSearch"
            params = {
                "keyword": query,
                "type": "news",
                "pi": 1,
                "ps": max_results
            }
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self._timeout
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            if data.get("Data") and data["Data"].get("News"):
                for item in data["Data"]["News"][:max_results]:
                    results.append({
                        "title": item.get("Title", ""),
                        "url": item.get("Url", ""),
                        "snippet": item.get("Content", "")[:200],
                        "published_date": item.get("ShowTime", ""),
                        "source": "东方财富",
                        "sentiment": self._analyze_sentiment(item.get("Content", ""))
                    })
            
            if results:
                logger.info(f"东方财富搜索成功: {len(results)} 条结果")
            
            return results
            
        except Exception as e:
            logger.warning(f"东方财富搜索失败: {e}")
            return []

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """搜索必应"""
        try:
            url = f"https://www.bing.com/search"
            params = {
                "q": query + " 股票 新闻",
                "count": max_results,
                "setlang": "zh-CN"
            }
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self._timeout
            )
            
            if response.status_code != 200:
                return []
            
            results = []
            html = response.text
            
            pattern = r'<li class="b_algo"[^>]*>.*?<h2><a href="([^"]+)"[^>]*>([^<]+)</a></h2>.*?<p>([^<]+)</p>'
            matches = re.findall(pattern, html, re.DOTALL)
            
            for url, title, snippet in matches[:max_results]:
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                
                results.append({
                    "title": clean_title,
                    "url": url,
                    "snippet": clean_snippet[:200],
                    "published_date": "",
                    "source": "必应",
                    "sentiment": self._analyze_sentiment(clean_snippet)
                })
            
            if results:
                logger.info(f"必应搜索成功: {len(results)} 条结果")
            
            return results
            
        except Exception as e:
            logger.warning(f"必应搜索失败: {e}")
            return []

    def _search_baidu(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """搜索百度"""
        try:
            url = f"https://www.baidu.com/s"
            params = {
                "wd": query + " 股票 新闻",
                "rn": max_results
            }
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self._timeout
            )
            
            if response.status_code != 200:
                return []
            
            results = []
            html = response.text
            
            pattern = r'<h3 class="t[^"]*"[^>]*><a href="([^"]+)"[^>]*>([^<]+)</a></h3>.*?<div class="c-abstract[^"]*"[^>]*>([^<]+)</div>'
            matches = re.findall(pattern, html, re.DOTALL)
            
            for url, title, snippet in matches[:max_results]:
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                
                results.append({
                    "title": clean_title,
                    "url": url,
                    "snippet": clean_snippet[:200],
                    "published_date": "",
                    "source": "百度",
                    "sentiment": self._analyze_sentiment(clean_snippet)
                })
            
            if results:
                logger.info(f"百度搜索成功: {len(results)} 条结果")
            
            return results
            
        except Exception as e:
            logger.warning(f"百度搜索失败: {e}")
            return []

    def _analyze_sentiment(self, text: str) -> str:
        """简单情感分析"""
        positive_keywords = ['上涨', '利好', '突破', '增长', '盈利', '强势', '领涨']
        negative_keywords = ['下跌', '利空', '回调', '亏损', '弱势', '领跌']
        
        positive_count = sum(1 for kw in positive_keywords if kw in text)
        negative_count = sum(1 for kw in negative_keywords if kw in text)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"

    def search_stock_news(self, stock_code: str, stock_name: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索股票相关新闻
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            max_results: 最大结果数
            
        Returns:
            新闻列表
        """
        query = f"{stock_name} {stock_code}" if stock_name else stock_code
        return self.search(query + " 股票 新闻", max_results)

    def search_market_news(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索市场新闻
        
        Args:
            max_results: 最大结果数
            
        Returns:
            新闻列表
        """
        return self.search("A股 市场 行情 今日", max_results)
