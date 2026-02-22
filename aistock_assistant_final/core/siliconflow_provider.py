# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 硅基流动API提供者
===================================

职责:
1. 封装硅基流动API调用
2. 支持流式响应
3. 实现错误重试和超时控制
4. 兼容OpenAI接口格式
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Generator
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SiliconFlowProvider(ABC):
    """硅基流动API提供者基类"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """发送聊天请求"""
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """发送流式聊天请求"""
        pass

    @abstractmethod
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析股票"""
        pass


class SiliconFlowAPI(SiliconFlowProvider):
    """硅基流动API实现"""

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        """
        初始化硅基流动API

        Args:
            api_key: 硅基流动API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model = "deepseek-ai/DeepSeek-V3"
        self._timeout = 60
        self._max_retries = 3

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            AI响应文本
        """
        try:
            url = f"{self.base_url}/chat/completions"
            data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }

            response = self._request_with_retry(url, data)
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API响应格式错误: {result}")
                return "AI服务暂时不可用"

        except Exception as e:
            logger.error(f"硅基流动聊天请求失败: {e}")
            return f"请求失败: {str(e)}"

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        发送流式聊天请求

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Yields:
            流式响应文本片段
        """
        try:
            url = f"{self.base_url}/chat/completions"
            data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": True
            }

            response = self._request_with_retry(url, data, stream=True)

            for line in response.iter_lines():
                if line.startswith('data: '):
                    line = line[6:]
                    if line == '[DONE]':
                        break
                    try:
                        chunk = json.loads(line)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            logger.error(f"硅基流动流式请求失败: {e}")
            yield f"流式请求失败: {str(e)}"

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析股票

        Args:
            stock_data: 股票数据

        Returns:
            分析结果字典
        """
        try:
            prompt = self._build_stock_analysis_prompt(stock_data)
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
            logger.error(f"硅基流动股票分析失败: {e}")
            return {"error": str(e)}

    def _build_stock_analysis_prompt(self, stock_data: Dict[str, Any]) -> str:
        """
        构建股票分析提示词

        Args:
            stock_data: 股票数据

        Returns:
            提示词文本
        """
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
        return prompt

    def _request_with_retry(self, url: str, data: Dict, stream: bool = False) -> requests.Response:
        """
        带重试机制的请求

        Args:
            url: 请求URL
            data: 请求数据
            stream: 是否流式请求

        Returns:
            响应对象
        """
        for attempt in range(self._max_retries):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self._timeout,
                    stream=stream
                )
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，重试 {attempt + 1}/{self._max_retries}")
                if attempt < self._max_retries - 1:
                    continue
                raise
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败，重试 {attempt + 1}/{self._max_retries}: {e}")
                if attempt < self._max_retries - 1:
                    continue
                raise

        raise Exception(f"请求失败，已重试{self._max_retries}次")

    def set_model(self, model: str):
        """
        设置模型

        Args:
            model: 模型名称
        """
        self.model = model
        logger.info(f"模型已更新: {model}")

    def set_timeout(self, timeout: int):
        """
        设置超时时间

        Args:
            timeout: 超时时间(秒)
        """
        self._timeout = timeout
        logger.info(f"超时时间已更新: {timeout}秒")

    def set_max_retries(self, max_retries: int):
        """
        设置最大重试次数

        Args:
            max_retries: 最大重试次数
        """
        self._max_retries = max_retries
        logger.info(f"最大重试次数已更新: {max_retries}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self._timeout,
            "max_retries": self._max_retries
        }
