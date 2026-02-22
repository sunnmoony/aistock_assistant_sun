# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - AI分析器模块
===================================

职责:
1. 提供统一的AI分析接口
2. 支持股票数据分析和新闻上下文处理
3. 生成投资建议和风险提示
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    analysis_summary: str = ""
    trend_prediction: str = ""
    operation_advice: str = ""
    risk_level: str = "中"
    support_level: float = 0.0
    resistance_level: float = 0.0
    confidence: float = 0.5
    key_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "analysis_summary": self.analysis_summary,
            "trend_prediction": self.trend_prediction,
            "operation_advice": self.operation_advice,
            "risk_level": self.risk_level,
            "support_level": self.support_level,
            "resistance_level": self.resistance_level,
            "confidence": self.confidence,
            "key_points": self.key_points
        }


class GeminiAnalyzer:
    """
    AI分析器 - 基于硅基流动API
    
    功能:
    1. 分析股票数据
    2. 结合新闻上下文生成综合分析
    3. 提供投资建议
    """

    def __init__(self, api_key: str = "", api_url: str = "", model: str = ""):
        """
        初始化AI分析器
        
        Args:
            api_key: API密钥
            api_url: API地址
            model: 模型名称
        """
        self.api_key = api_key
        self.api_url = api_url or "https://api.siliconflow.cn/v1"
        self.model = model or "deepseek-ai/DeepSeek-V3"
        self._ai_provider = None
        self._init_provider()

    def _init_provider(self):
        """初始化AI提供者"""
        if self.api_key:
            try:
                from .siliconflow_provider import SiliconFlowAPI
                self._ai_provider = SiliconFlowAPI(
                    api_key=self.api_key,
                    base_url=self.api_url
                )
                self._ai_provider.set_model(self.model)
                logger.info("AI分析器初始化成功")
            except Exception as e:
                logger.warning(f"AI分析器初始化失败: {e}")
                self._ai_provider = None
        else:
            logger.warning("未配置API密钥，AI分析功能将受限")

    def analyze(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any],
        news_context: str = ""
    ) -> AnalysisResult:
        """
        分析股票
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            stock_data: 股票数据
            news_context: 新闻上下文
            
        Returns:
            AnalysisResult 分析结果对象
        """
        try:
            if self._ai_provider:
                return self._analyze_with_ai(stock_code, stock_name, stock_data, news_context)
            else:
                return self._analyze_fallback(stock_code, stock_name, stock_data, news_context)
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return AnalysisResult(
                analysis_summary=f"分析失败: {str(e)}",
                trend_prediction="无法预测",
                operation_advice="建议观望"
            )

    def _analyze_with_ai(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any],
        news_context: str
    ) -> AnalysisResult:
        """使用AI进行分析"""
        prompt = self._build_analysis_prompt(stock_code, stock_name, stock_data, news_context)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self._ai_provider.chat(messages)
            
            import json
            try:
                result = json.loads(response)
                return AnalysisResult(
                    analysis_summary=result.get("analysis_summary", ""),
                    trend_prediction=result.get("trend_prediction", ""),
                    operation_advice=result.get("operation_advice", ""),
                    risk_level=result.get("risk_level", "中"),
                    support_level=float(result.get("support_level", 0)),
                    resistance_level=float(result.get("resistance_level", 0)),
                    confidence=float(result.get("confidence", 0.5)),
                    key_points=result.get("key_points", [])
                )
            except json.JSONDecodeError:
                return AnalysisResult(
                    analysis_summary=response[:500] if response else "分析完成",
                    trend_prediction="请参考详细分析",
                    operation_advice="建议结合其他指标判断"
                )
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            return self._analyze_fallback(stock_code, stock_name, stock_data, news_context)

    def _analyze_fallback(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any],
        news_context: str
    ) -> AnalysisResult:
        """降级分析（无AI时使用）"""
        indices = stock_data.get("indices", {})
        market_summary = stock_data.get("market_summary", {})
        sector_rank = stock_data.get("sector_rank", [])
        
        rise_count = market_summary.get("rise_count", 0)
        fall_count = market_summary.get("fall_count", 0)
        
        if rise_count > fall_count * 1.5:
            trend = "上涨趋势"
            advice = "市场偏强，可适当参与"
            risk = "中"
        elif fall_count > rise_count * 1.5:
            trend = "下跌趋势"
            advice = "市场偏弱，建议谨慎"
            risk = "高"
        else:
            trend = "震荡整理"
            advice = "市场震荡，观望为主"
            risk = "中"
        
        summary_parts = [f"今日市场{trend}"]
        if indices:
            for key, data in list(indices.items())[:3]:
                name = data.get("name", key)
                change = data.get("change_percent", 0)
                summary_parts.append(f"{name}{'上涨' if change > 0 else '下跌'}{abs(change):.2f}%")
        
        return AnalysisResult(
            analysis_summary="，".join(summary_parts),
            trend_prediction=trend,
            operation_advice=advice,
            risk_level=risk,
            confidence=0.6,
            key_points=["基于市场数据分析", "AI服务未启用"]
        )

    def _build_analysis_prompt(
        self,
        stock_code: str,
        stock_name: str,
        stock_data: Dict[str, Any],
        news_context: str
    ) -> str:
        """构建分析提示词"""
        prompt = f"""
请分析以下市场数据，提供专业的投资建议：

分析对象: {stock_name} ({stock_code})

市场数据:
"""
        
        indices = stock_data.get("indices", {})
        if indices:
            prompt += "\n主要指数:\n"
            for key, data in indices.items():
                name = data.get("name", key)
                price = data.get("price", 0)
                change = data.get("change_percent", 0)
                prompt += f"- {name}: {price:.2f} ({change:+.2f}%)\n"
        
        market_summary = stock_data.get("market_summary", {})
        if market_summary:
            prompt += f"\n市场概况:\n"
            prompt += f"- 上涨: {market_summary.get('rise_count', 0)}家\n"
            prompt += f"- 下跌: {market_summary.get('fall_count', 0)}家\n"
            prompt += f"- 涨停: {market_summary.get('limit_up_count', 0)}家\n"
            prompt += f"- 跌停: {market_summary.get('limit_down_count', 0)}家\n"
        
        sector_rank = stock_data.get("sector_rank", [])
        if sector_rank:
            prompt += "\n板块涨跌排行(TOP5):\n"
            for i, sector in enumerate(sector_rank[:5], 1):
                name = sector.get("name", "")
                change = sector.get("change_percent", 0)
                prompt += f"{i}. {name}: {change:+.2f}%\n"
        
        if news_context:
            prompt += f"\n相关新闻:\n{news_context}\n"
        
        prompt += """
请从以下几个方面进行分析，并以JSON格式返回结果：
{
    "analysis_summary": "市场整体分析摘要",
    "trend_prediction": "趋势预测（上涨/下跌/震荡）",
    "operation_advice": "操作建议",
    "risk_level": "风险等级（低/中/高）",
    "support_level": 支撑位数值,
    "resistance_level": 阻力位数值,
    "confidence": 信心度(0-1),
    "key_points": ["关键点1", "关键点2"]
}
"""
        return prompt

    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        self._init_provider()

    def set_model(self, model: str):
        """设置模型"""
        self.model = model
        if self._ai_provider:
            self._ai_provider.set_model(model)

    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self._ai_provider is not None
