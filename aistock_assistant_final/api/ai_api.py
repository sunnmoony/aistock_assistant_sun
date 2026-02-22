import requests
import json
from typing import Dict, Any, Optional, List
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """AI提供者基类"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析股票"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI API提供者"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model = "gpt-3.5-turbo"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            url = f"{self.base_url}/chat/completions"
            data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }

            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI聊天请求失败: {e}")
            return f"AI服务暂时不可用: {str(e)}"

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析股票"""
        try:
            prompt = f"""
            请分析以下股票数据，提供专业的投资建议：

            股票代码: {stock_data.get('code', '')}
            股票名称: {stock_data.get('name', '')}
            最新价: {stock_data.get('price', 0)}
            涨跌幅: {stock_data.get('change_percent', 0)}%
            成交量: {stock_data.get('volume', 0)}
            成交额: {stock_data.get('turnover', 0)}

            技术指标:
            - MA5: {stock_data.get('ma5', 'N/A')}
            - MA10: {stock_data.get('ma10', 'N/A')}
            - MA20: {stock_data.get('ma20', 'N/A')}
            - MACD: {stock_data.get('macd', 'N/A')}
            - RSI: {stock_data.get('rsi', 'N/A')}

            请从以下几个方面进行分析：
            1. 趋势分析
            2. 技术面分析
            3. 风险评估
            4. 操作建议（买入/持有/卖出/观望）
            5. 支撑位和阻力位

            请以JSON格式返回分析结果，包含以下字段：
            {{
                "trend": "趋势描述",
                "technical_analysis": "技术面分析",
                "risk_level": "风险等级（低/中/高）",
                "recommendation": "操作建议",
                "support": "支撑位",
                "resistance": "阻力位",
                "reasoning": "分析理由"
            }}
            """

            messages = [{"role": "user", "content": prompt}]
            response = self.chat(messages)

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "trend": "无法解析",
                    "technical_analysis": response,
                    "risk_level": "中",
                    "recommendation": "观望",
                    "support": 0,
                    "resistance": 0,
                    "reasoning": "AI分析结果格式错误"
                }
        except Exception as e:
            logger.error(f"OpenAI股票分析失败: {e}")
            return {"error": str(e)}


class BaiduProvider(BaseAIProvider):
    """百度文心一言API提供者"""

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.base_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key
            }

            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()

            result = response.json()
            self.access_token = result["access_token"]
            return self.access_token
        except Exception as e:
            logger.error(f"获取百度访问令牌失败: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            if not self.access_token:
                self._get_access_token()

            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.8)
            }

            url = f"{self.base_url}?access_token={self.access_token}"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["result"]
        except Exception as e:
            logger.error(f"百度聊天请求失败: {e}")
            return f"AI服务暂时不可用: {str(e)}"

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析股票"""
        try:
            prompt = f"""
            请分析以下股票数据，提供专业的投资建议：

            股票代码: {stock_data.get('code', '')}
            股票名称: {stock_data.get('name', '')}
            最新价: {stock_data.get('price', 0)}
            涨跌幅: {stock_data.get('change_percent', 0)}%

            请从趋势、技术面、风险等方面进行分析，给出操作建议。
            """

            messages = [{"role": "user", "content": prompt}]
            response = self.chat(messages)

            return {
                "trend": "待分析",
                "technical_analysis": response,
                "risk_level": "中",
                "recommendation": "观望",
                "support": 0,
                "resistance": 0,
                "reasoning": "AI分析完成"
            }
        except Exception as e:
            logger.error(f"百度股票分析失败: {e}")
            return {"error": str(e)}


class AliProvider(BaseAIProvider):
    """阿里通义千问API提供者"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "qwen-turbo",
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.8),
                    "max_tokens": kwargs.get("max_tokens", 2000)
                }
            }

            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["output"]["text"]
        except Exception as e:
            logger.error(f"阿里聊天请求失败: {e}")
            return f"AI服务暂时不可用: {str(e)}"

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析股票"""
        try:
            prompt = f"""
            请分析以下股票数据，提供专业的投资建议：

            股票代码: {stock_data.get('code', '')}
            股票名称: {stock_data.get('name', '')}
            最新价: {stock_data.get('price', 0)}
            涨跌幅: {stock_data.get('change_percent', 0)}%

            请从趋势、技术面、风险等方面进行分析，给出操作建议。
            """

            messages = [{"role": "user", "content": prompt}]
            response = self.chat(messages)

            return {
                "trend": "待分析",
                "technical_analysis": response,
                "risk_level": "中",
                "recommendation": "观望",
                "support": 0,
                "resistance": 0,
                "reasoning": "AI分析完成"
            }
        except Exception as e:
            logger.error(f"阿里股票分析失败: {e}")
            return {"error": str(e)}


class AIApi:
    """AI API封装类 - 统一接口"""

    def __init__(self, provider_type: str = "openai", **kwargs):
        """
        初始化AI API

        Args:
            provider_type: 提供者类型（openai/baidu/ali）
            **kwargs: API密钥等参数
        """
        self.provider_type = provider_type
        self.provider = self._create_provider(provider_type, **kwargs)

    def _create_provider(self, provider_type: str, **kwargs) -> BaseAIProvider:
        """创建AI提供者"""
        try:
            if provider_type == "openai":
                return OpenAIProvider(
                    api_key=kwargs.get("api_key", ""),
                    base_url=kwargs.get("base_url", "https://api.openai.com/v1")
                )
            elif provider_type == "baidu":
                return BaiduProvider(
                    api_key=kwargs.get("api_key", ""),
                    secret_key=kwargs.get("secret_key", "")
                )
            elif provider_type == "ali":
                return AliProvider(
                    api_key=kwargs.get("api_key", "")
                )
            else:
                logger.warning(f"未知的AI提供者类型: {provider_type}")
                return OpenAIProvider(api_key="")
        except Exception as e:
            logger.error(f"创建AI提供者失败: {e}")
            return OpenAIProvider(api_key="")

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            AI响应
        """
        try:
            return self.provider.chat(messages, **kwargs)
        except Exception as e:
            logger.error(f"聊天请求失败: {e}")
            return f"请求失败: {str(e)}"

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析股票

        Args:
            stock_data: 股票数据

        Returns:
            分析结果
        """
        try:
            return self.provider.analyze_stock(stock_data)
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return {"error": str(e)}

    def generate_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        生成报告

        Args:
            analysis_data: 分析数据

        Returns:
            报告内容
        """
        try:
            stock_code = analysis_data.get("stock_code", "")
            trend = analysis_data.get("trend", "")
            technical_analysis = analysis_data.get("technical_analysis", "")
            risk_level = analysis_data.get("risk_level", "")
            recommendation = analysis_data.get("recommendation", "")
            support = analysis_data.get("support", 0)
            resistance = analysis_data.get("resistance", 0)
            reasoning = analysis_data.get("reasoning", "")

            report = f"""
# 股票分析报告

**股票代码**: {stock_code}

## 基本分析
- **趋势**: {trend}
- **支撑位**: {support}
- **阻力位**: {resistance}
- **风险等级**: {risk_level}

## 技术面分析
{technical_analysis}

## 投资建议
- **操作建议**: {recommendation}

## 分析理由
{reasoning}

---
*本报告由AI生成，仅供参考，不构成投资建议*
"""
            return report
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return "生成报告失败"

    def answer_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        回答问题

        Args:
            question: 问题
            context: 上下文

        Returns:
            答案
        """
        try:
            messages = [{"role": "user", "content": question}]

            if context:
                context_str = json.dumps(context, ensure_ascii=False)
                messages.insert(0, {
                    "role": "system",
                    "content": f"以下是一些上下文信息：\n{context_str}\n请基于这些信息回答用户的问题。"
                })

            return self.chat(messages)
        except Exception as e:
            logger.error(f"回答问题失败: {e}")
            return f"回答失败: {str(e)}"

    def detect_pattern(self, price_data: List[float]) -> Dict[str, Any]:
        """
        检测价格形态

        Args:
            price_data: 价格数据

        Returns:
            形态分析结果
        """
        try:
            prompt = f"""
            请分析以下价格序列，识别K线形态：

            价格数据: {price_data}

            请识别以下形态（如果存在）：
            - 头肩顶/底
            - 双顶/底
            - 三重顶/底
            - 上升/下降三角形
            - 矩形整理
            - 上升/下降楔形

            请以JSON格式返回分析结果，包含以下字段：
            {{
                "pattern": "形态名称",
                "confidence": "置信度（0-1）",
                "description": "形态描述",
                "signal": "交易信号（买入/卖出/中性）"
            }}
            """

            messages = [{"role": "user", "content": prompt}]
            response = self.chat(messages)

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "pattern": "未知",
                    "confidence": 0.5,
                    "description": response,
                    "signal": "中性"
                }
        except Exception as e:
            logger.error(f"形态检测失败: {e}")
            return {"error": str(e)}