# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 大盘复盘模块
===================================

功能：
1. 获取主要指数行情（上证指数、深证成指、创业板指、科创50等）
2. 获取市场概况（上涨/下跌/平盘家数、涨停/跌停家数）
3. 获取板块涨跌排行
4. 获取北向资金流向
5. 搜索市场新闻
6. AI生成大盘分析报告
7. 格式化复盘报告

依赖：
- DataManager: 数据管理器，用于获取市场数据
- GeminiAnalyzer: AI分析器，用于生成大盘分析
- SearchService: 搜索服务，用于搜索市场新闻
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .data_manager import DataManager
from .analyzer_dashboard import GeminiAnalyzer
from .search_service import SearchService

logger = logging.getLogger(__name__)


class MarketReview:
    """
    大盘复盘分析器
    
    功能：
    1. 获取主要指数行情（上证指数、深证成指、创业板指、科创50等）
    2. 获取市场概况（上涨/下跌/平盘家数、涨停/跌停家数）
    3. 获取板块涨跌排行
    4. 获取北向资金流向
    5. 搜索市场新闻
    6. AI生成大盘分析报告
    7. 格式化复盘报告
    
    使用场景：
    - 每日收盘后生成大盘复盘报告
    - 实时监控市场动态
    - 辅助投资决策
    """

    def __init__(self, data_manager: DataManager, ai_analyzer: GeminiAnalyzer, search_service: SearchService):
        """
        初始化大盘复盘分析器
        
        参数：
            data_manager: 数据管理器，用于获取市场数据
            ai_analyzer: AI分析器，用于生成大盘分析
            search_service: 搜索服务，用于搜索市场新闻
        
        说明：
            初始化时需要传入三个核心组件，这些组件分别负责数据获取、AI分析和新闻搜索
        """
        self.data_manager = data_manager
        self.ai_analyzer = ai_analyzer
        self.search_service = search_service

    def generate_market_review(self) -> Dict[str, Any]:
        """
        生成大盘复盘报告
        
        返回：
            大盘复盘数据字典，包含：
            - date: 日期
            - indices: 主要指数行情
            - market_summary: 市场概况
            - sector_rank: 板块涨跌排行（前10）
            - fund_flow: 北向资金流向（前10）
            - news: 市场新闻
            - ai_analysis: AI分析结果
            - error: 错误信息（如果生成失败）
        
        流程：
            1. 获取主要指数行情
            2. 获取市场概况
            3. 获取板块涨跌排行
            4. 获取北向资金流向
            5. 搜索市场新闻
            6. AI生成大盘分析
            7. 构建复盘报告
        
        异常处理：
            如果任何步骤失败，返回包含错误信息的字典
        """
        try:
            # 1. 获取主要指数行情
            indices = self.data_manager.get_market_data()

            # 2. 获取市场概况
            market_summary = self.data_manager.get_market_summary()

            # 3. 获取板块涨跌排行
            sector_rank = self.data_manager.get_sector_rank()

            # 4. 获取北向资金流向
            fund_flow = self.data_manager.get_fund_flow()

            # 5. 搜索市场新闻
            news_query = "A股市场 今日行情 涨跌 板块"
            news_results = self.search_service.search_news(news_query, max_results=5)

            # 6. AI生成大盘分析
            analysis_data = {
                "indices": indices,
                "market_summary": market_summary,
                "sector_rank": sector_rank[:10],  # 前10板块
                "fund_flow": fund_flow[:10],  # 前10资金流向
                "news": news_results
            }

            ai_analysis = self.ai_analyzer.analyze(
                stock_code="000001",
                stock_name="上证指数",
                stock_data=analysis_data,
                news_context=self._format_news_context(news_results)
            )

            # 7. 构建复盘报告
            report = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "indices": indices,
                "market_summary": market_summary,
                "sector_rank": sector_rank[:10],
                "fund_flow": fund_flow[:10],
                "news": news_results,
                "ai_analysis": ai_analysis.to_dict() if hasattr(ai_analysis, 'to_dict') else ai_analysis
            }

            logger.info("大盘复盘报告生成完成")
            return report
        except Exception as e:
            logger.error(f"生成大盘复盘报告失败: {e}")
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "error": str(e),
                "indices": {},
                "market_summary": {},
                "sector_rank": [],
                "fund_flow": [],
                "news": [],
                "ai_analysis": {}
            }

    def _format_news_context(self, news_results: List[Dict[str, Any]]) -> str:
        """
        格式化新闻上下文
        
        参数：
            news_results: 新闻列表，每条新闻包含title、snippet、sentiment等字段
        
        返回：
            格式化后的新闻文本，每条新闻一行，格式为：- 标题 (情绪)
        
        说明：
            将新闻列表转换为文本格式，方便AI分析使用
        """
        if not news_results:
            return "暂无相关新闻"

        news_lines = []
        for item in news_results:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            sent = item.get('sentiment', '')
            news_lines.append(f"- {title} ({sent})")

        return "\n".join(news_lines)

    def format_review_report(self, review_data: Dict[str, Any]) -> str:
        """
        格式化复盘报告为Markdown格式
        
        参数：
            review_data: 复盘数据字典，包含indices、market_summary、sector_rank、fund_flow、news、ai_analysis等字段
        
        返回：
            Markdown格式的报告文本
        
        报告结构：
            1. 标题（日期）
            2. 主要指数
            3. 市场概况
            4. 板块涨跌排行（TOP10）
            5. 北向资金流向（TOP10）
            6. AI分析
            7. 市场新闻
            8. 生成时间
        
        格式特点：
            - 使用emoji图标增强可读性
            - 涨跌用不同颜色标识
            - 数据保留2位小数
        """
        report_lines = []

        # 标题
        report_lines.append(f"# 📊 {review_data.get('date', '')} 大盘复盘")
        report_lines.append("")

        # 主要指数
        indices = review_data.get('indices', {})
        if indices:
            report_lines.append("## 📈 主要指数")
            for key, data in indices.items():
                name = data.get('name', '')
                price = data.get('price', 0)
                change = data.get('change_percent', 0)
                emoji = "🟢" if change > 0 else "🔴"
                report_lines.append(f"{emoji} {name}: {price:.2f} ({change:+.2f}%)")

        # 市场概况
        market_summary = review_data.get('market_summary', {})
        if market_summary:
            report_lines.append("\n## 📊 市场概况")
            rise_count = market_summary.get('rise_count', 0)
            fall_count = market_summary.get('fall_count', 0)
            flat_count = market_summary.get('flat_count', 0)
            limit_up_count = market_summary.get('limit_up_count', 0)
            limit_down_count = market_summary.get('limit_down_count', 0)

            report_lines.append(f"上涨: {rise_count} | 下跌: {fall_count} | 平盘: {flat_count}")
            report_lines.append(f"涨停: {limit_up_count} | 跌停: {limit_down_count}")

        # 板块排行
        sector_rank = review_data.get('sector_rank', [])
        if sector_rank:
            report_lines.append("\n## 🔥 板块涨跌排行(TOP10)")
            for i, sector in enumerate(sector_rank[:10], 1):
                name = sector.get('name', '')
                change = sector.get('change_percent', 0)
                emoji = "🟢" if change > 0 else "🔴"
                report_lines.append(f"{i}. {emoji} {name}: {change:+.2f}%")

        # 北向资金
        fund_flow = review_data.get('fund_flow', [])
        if fund_flow:
            report_lines.append("\n## 💰 北向资金流向(TOP10)")
            for i, flow in enumerate(fund_flow[:10], 1):
                name = flow.get('name', '')
                net_inflow = flow.get('main_net_inflow', 0)
                emoji = "🟢" if net_inflow > 0 else "🔴"
                report_lines.append(f"{i}. {emoji} {name}: {net_inflow:+.2f}亿")

        # AI分析
        ai_analysis = review_data.get('ai_analysis', {})
        if ai_analysis:
            report_lines.append("\n## 🤖 AI分析")
            summary = ai_analysis.get('analysis_summary', '')
            trend = ai_analysis.get('trend_prediction', '')
            advice = ai_analysis.get('operation_advice', '')

            report_lines.append(f"趋势: {trend}")
            report_lines.append(f"建议: {advice}")
            if summary:
                report_lines.append(f"摘要: {summary}")

        # 新闻
        news = review_data.get('news', [])
        if news:
            report_lines.append("\n## 📰 市场新闻")
            for item in news[:5]:
                title = item.get('title', '')
                report_lines.append(f"- {title}")

        report_lines.append("\n---")
        report_lines.append(f"*生成时间: {datetime.now().strftime('%H:%M:%S')}")

        return "\n".join(report_lines)
