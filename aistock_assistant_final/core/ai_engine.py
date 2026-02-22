# -*- coding: utf-8 -*-
"""
===================================
AI引擎模块 - 股票智能分析核心
===================================

功能：
1. 集成硅基流动API进行AI分析
2. 计算技术指标（MA、MACD、RSI、KDJ、BOLL等）
3. 识别K线形态
4. 生成投资建议和风险提示
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import logging
import json
import os
import numpy as np
import pandas as pd
from .technical_indicators import TechnicalIndicators
from .siliconflow_provider import SiliconFlowAPI

logger = logging.getLogger(__name__)


class AIAnalysisThread(QThread):
    """AI分析线程"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, query: str, context: Dict[str, Any] = None, ai_provider: SiliconFlowAPI = None):
        super().__init__()
        self.query = query
        self.context = context or {}
        self.ai_provider = ai_provider

    def run(self):
        try:
            if self.ai_provider:
                response = self.ai_provider.chat([{"role": "user", "content": self.query}])
                self.finished.emit(response)
            else:
                self.finished.emit("AI服务未配置，请先在config.yaml中设置API密钥")
        except Exception as e:
            logger.error(f"AI分析失败: {e}")
            self.error.emit(str(e))


class AIEngine(QObject):
    """AI引擎 - 股票智能分析核心"""

    analysis_started = pyqtSignal(str)
    analysis_finished = pyqtSignal(str, str)
    analysis_error = pyqtSignal(str, str)

    def __init__(self, api_key: str = "", api_url: str = "", provider_type: str = "siliconflow"):
        super().__init__()
        self.api_key = api_key
        self.api_url = api_url
        self.provider_type = provider_type
        self._conversation_history: List[Dict[str, str]] = []
        self._max_history = 50
        self._model = "deepseek-ai/DeepSeek-V3"
        self._timeout = 60
        self._max_retries = 3
        self.technical_indicators = TechnicalIndicators()
        self.ai_provider = None
        self._load_settings()

    def _load_settings(self):
        """加载AI设置"""
        try:
            settings_file = "data/ai_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.api_key = settings.get("api_key", self.api_key)
                self.api_url = settings.get("api_url", self.api_url)
                self._model = settings.get("model", self._model)
        except Exception as e:
            logger.warning(f"加载AI设置失败: {e}")

        if self.api_key and self.api_key.strip():
            try:
                self.ai_provider = SiliconFlowAPI(
                    api_key=self.api_key,
                    base_url=self.api_url if self.api_url else "https://api.siliconflow.cn/v1"
                )
                logger.info("AI提供者已初始化")
            except Exception as e:
                logger.error(f"初始化AI提供者失败: {e}")

    def analyze_stock(self, stock_code: str, stock_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析股票"""
        try:
            if not stock_data:
                return {"success": False, "error": "缺少股票数据"}

            df = stock_data.get('history', pd.DataFrame())
            signals = {}
            if not df.empty:
                df_with_indicators = self.technical_indicators.calculate_all(df)
                signals = self.technical_indicators.get_latest_signals(df_with_indicators)

            price = stock_data.get("price", 0)
            pre_close = stock_data.get("pre_close", 0)
            change_percent = stock_data.get("change_percent", 0)

            deviation_rate = abs((price - pre_close) / pre_close * 100) if pre_close > 0 else 0
            ma5 = signals.get("ma5", 0)
            ma10 = signals.get("ma10", 0)
            ma20 = signals.get("ma20", 0)
            is_bullish = ma5 > ma10 > ma20

            buy_price = round(price * 0.98, 2) if deviation_rate < 2 else price
            stop_loss = round(buy_price * 0.97, 2)
            target_price = round(price * 1.05, 2) if change_percent > 0 else round(price * 1.03, 2)

            checklist = {
                "多头排列": "满足" if is_bullish else "不满足",
                "乖离安全": "满足" if deviation_rate <= 5 else "不满足",
                "量能配合": "满足" if signals.get("volume_signal", "") == "放量" else "不满足",
                "趋势向上": "满足" if signals.get("ma_trend", "") == "多头向上" else "不满足"
            }

            trend = self._analyze_trend(change_percent)
            recommendation = self._get_recommendation(change_percent)
            risk_level = self._assess_risk(change_percent)

            analysis = {
                "stock_code": stock_code,
                "trend": trend,
                "support": round(stock_data.get("low", 0) * 0.98, 2),
                "resistance": round(stock_data.get("high", 0) * 1.02, 2),
                "recommendation": recommendation,
                "reasoning": f"股票当前处于{trend}状态，涨跌幅{change_percent:.2f}%。建议根据市场情况决策。",
                "risk_level": risk_level,
                "target_price": target_price,
                "deviation_rate": deviation_rate,
                "is_bullish": is_bullish,
                "buy_price": buy_price,
                "stop_loss": stop_loss,
                "checklist": checklist,
                "ma_trend": signals.get("ma_trend", "无法判断"),
                "macd_signal": signals.get("macd_signal", "无明显信号"),
                "rsi_signal": signals.get("rsi_signal", "无法判断"),
                "kdj_signal": signals.get("kdj_signal", "无法判断"),
                "boll_signal": signals.get("boll_signal", "无法判断"),
                "technical_indicators": {
                    "ma5": signals.get("ma5", 0),
                    "ma10": signals.get("ma10", 0),
                    "ma20": signals.get("ma20", 0),
                    "ma60": signals.get("ma60", 0),
                    "macd": signals.get("macd", 0),
                    "rsi": signals.get("rsi", 50),
                    "k": signals.get("k", 50),
                    "d": signals.get("kdj_d", 50),
                    "j": signals.get("j", 50),
                },
                "pattern": self._detect_pattern(df)
            }

            return {"success": True, "data": analysis}
        except Exception as e:
            logger.error(f"股票分析失败 {stock_code}: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_trend(self, change_percent: float) -> str:
        """分析趋势"""
        if change_percent > 5:
            return "强势上涨"
        elif change_percent > 2:
            return "温和上涨"
        elif change_percent > -2:
            return "震荡整理"
        elif change_percent > -5:
            return "温和下跌"
        else:
            return "强势下跌"

    def _get_recommendation(self, change_percent: float) -> str:
        """获取推荐"""
        if change_percent > 5:
            return "持有"
        elif change_percent > 2:
            return "买入"
        elif change_percent > -2:
            return "观望"
        elif change_percent > -5:
            return "减仓"
        else:
            return "卖出"

    def _assess_risk(self, change_percent: float) -> str:
        """评估风险"""
        if abs(change_percent) > 7:
            return "高风险"
        elif abs(change_percent) > 4:
            return "中高风险"
        elif abs(change_percent) > 2:
            return "中等风险"
        else:
            return "低风险"

    def _detect_pattern(self, df) -> Dict[str, Any]:
        """检测K线形态"""
        if df.empty or len(df) < 10:
            return {"pattern": "数据不足", "confidence": 0, "signal": "中性"}

        try:
            closes = df['close'].values
            first = closes[0]
            last = closes[-1]

            if last > first * 1.05:
                return {"pattern": "上升趋势", "confidence": 0.7, "signal": "买入", "description": "价格持续上涨"}
            elif last < first * 0.95:
                return {"pattern": "下降趋势", "confidence": 0.7, "signal": "卖出", "description": "价格持续下跌"}
            else:
                return {"pattern": "震荡整理", "confidence": 0.6, "signal": "观望", "description": "价格波动较小"}
        except Exception:
            return {"pattern": "无法判断", "confidence": 0, "signal": "中性"}

    def analyze_with_context(self, query: str, context: Dict[str, Any] = None) -> str:
        """带上下文的分析"""
        try:
            self.analysis_started.emit(query)
            thread = AIAnalysisThread(query, context, self.ai_provider)
            thread.finished.connect(lambda r: self._on_analysis_finished(query, r))
            thread.error.connect(lambda e: self._on_analysis_error(query, e))
            thread.start()
            return "AI正在分析中..."
        except Exception as e:
            return f"分析失败: {str(e)}"

    def _on_analysis_finished(self, query: str, response: str):
        self.analysis_finished.emit(query, response)
        self._add_to_history("user", query)
        self._add_to_history("assistant", response)

    def _on_analysis_error(self, query: str, error: str):
        self.analysis_error.emit(query, error)

    def _add_to_history(self, role: str, content: str):
        self._conversation_history.append({"role": role, "content": content})
        if len(self._conversation_history) > self._max_history:
            self._conversation_history.pop(0)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self._conversation_history.copy()

    def clear_conversation_history(self):
        self._conversation_history.clear()

    def answer_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """回答问题"""
        try:
            if self.ai_provider:
                messages = [{"role": "user", "content": question}]
                if context:
                    context_str = json.dumps(context, ensure_ascii=False)
                    messages.insert(0, {
                        "role": "system",
                        "content": f"上下文信息：\n{context_str}"
                    })
                return self.ai_provider.chat(messages)
            else:
                return "AI服务未配置，请先在config.yaml中设置API密钥"
        except Exception as e:
            return f"回答失败: {str(e)}"

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        if self.ai_provider:
            self.ai_provider.api_key = api_key
        self._save_settings()

    def _save_settings(self):
        try:
            os.makedirs("data", exist_ok=True)
            settings = {
                "api_key": self.api_key,
                "api_url": self.api_url,
                "model": self._model,
                "timeout": self._timeout,
                "max_retries": self._max_retries
            }
            with open("data/ai_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存AI设置失败: {e}")
