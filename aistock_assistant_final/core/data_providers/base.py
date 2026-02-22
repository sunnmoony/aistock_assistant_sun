# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 数据源管理器
===================================

职责:
1. 管理多个数据源(AkShare/Tushare/Efinance/Pytdx/Baostock/YFinance)
2. 按优先级自动切换数据源
3. 实现数据源健康检查和自动降级
4. 请求限流控制和熔断器机制
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import time

logger = logging.getLogger(__name__)


class BaseDataFetcher(ABC):
    """数据获取器基类"""

    @abstractmethod
    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时行情"""
        pass

    @abstractmethod
    def get_stock_history(self, stock_code: str, period: str = "daily",
                        start_date: str = None, end_date: str = None) -> Any:
        """获取股票历史K线数据"""
        pass

    @abstractmethod
    def get_index_data(self, index_code: str) -> Optional[Dict[str, Any]]:
        """获取指数数据"""
        pass

    @abstractmethod
    def get_all_indices(self) -> List[Dict[str, Any]]:
        """获取主要指数数据"""
        pass

    @abstractmethod
    def get_sector_data(self) -> List[Dict[str, Any]]:
        """获取板块数据"""
        pass

    @abstractmethod
    def get_sector_stocks(self, sector_name: str) -> List[Dict[str, Any]]:
        """获取板块内股票列表"""
        pass

    @abstractmethod
    def get_sector_rank(self) -> List[Dict[str, Any]]:
        """获取板块涨跌幅排行"""
        pass

    @abstractmethod
    def get_fund_flow(self, stock_code: str = None) -> List[Dict[str, Any]]:
        """获取资金流向数据"""
        pass

    @abstractmethod
    def get_stock_list(self, market: str = "SH") -> List[Dict[str, Any]]:
        """获取股票列表"""
        pass

    @abstractmethod
    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票"""
        pass

    @abstractmethod
    def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        pass

    @abstractmethod
    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """获取财务数据"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取数据源名称"""
        pass


class DataFetcherManager:
    """
    数据源管理器 - 多数据源策略

    职责:
    1. 管理多个数据源,按优先级自动切换
    2. 实现数据源健康检查和自动降级
    3. 请求限流控制和熔断器机制
    4. 智能代理配置(国内数据源自动走直连)
    """

    def __init__(self, fetchers: List[BaseDataFetcher] = None):
        """
        初始化数据源管理器

        Args:
            fetchers: 数据获取器列表(按优先级排序)
        """
        self.fetchers = fetchers or []
        self._current_fetcher_index = 0
        self._failure_counts = [0] * len(self.fetchers)
        self._circuit_breaker_enabled = True
        self._circuit_breaker_threshold = 5  # 连续失败5次触发熔断
        self._circuit_breaker_cooldown = 300  # 熔断冷却时间(秒)
        self._last_failure_time = [None] * len(self.fetchers)
        self._in_circuit_breaker = [False] * len(self.fetchers)

        logger.info(f"数据源管理器初始化完成,共 {len(self.fetchers)} 个数据源")

    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时行情 - 自动降级

        Args:
            stock_code: 股票代码

        Returns:
            股票数据字典
        """
        return self._fetch_with_fallback(
            lambda f: f.get_stock_realtime(stock_code),
            stock_code
        )

    def get_stock_history(self, stock_code: str, period: str = "daily",
                    start_date: str = None, end_date: str = None) -> Any:
        """
        获取股票历史K线数据 - 自动降级

        Args:
            stock_code: 股票代码
            period: 周期(daily=日线, weekly=周线, monthly=月线)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            K线数据
        """
        return self._fetch_with_fallback(
            lambda f: f.get_stock_history(stock_code, period, start_date, end_date),
            stock_code
        )

    def get_index_data(self, index_code: str) -> Optional[Dict[str, Any]]:
        """获取指数数据"""
        return self._fetch_with_fallback(
            lambda f: f.get_index_data(index_code),
            index_code
        )

    def get_all_indices(self) -> List[Dict[str, Any]]:
        """获取主要指数数据"""
        for i, fetcher in enumerate(self.fetchers):
            try:
                result = fetcher.get_all_indices()
                if result:
                    logger.info(f"使用数据源 {i} ({fetcher.get_name()}) 获取指数数据成功")
                    return result
            except Exception as e:
                logger.warning(f"数据源 {i} ({fetcher.get_name()}) 获取指数数据失败: {e}")
                self._record_failure(i)
                continue

        return []

    def get_sector_data(self) -> List[Dict[str, Any]]:
        """获取板块数据"""
        return self._fetch_with_fallback(
            lambda f: f.get_sector_data(),
            "sector"
        )

    def get_sector_stocks(self, sector_name: str) -> List[Dict[str, Any]]:
        """获取板块内股票列表"""
        return self._fetch_with_fallback(
            lambda f: f.get_sector_stocks(sector_name),
            f"sector_{sector_name}"
        )

    def get_sector_rank(self) -> List[Dict[str, Any]]:
        """获取板块涨跌幅排行"""
        return self._fetch_with_fallback(
            lambda f: f.get_sector_rank(),
            "sector_rank"
        )

    def get_fund_flow(self, stock_code: str = None) -> List[Dict[str, Any]]:
        """获取资金流向数据"""
        return self._fetch_with_fallback(
            lambda f: f.get_fund_flow(stock_code),
            stock_code if stock_code else "market"
        )

    def get_stock_list(self, market: str = "SH") -> List[Dict[str, Any]]:
        """获取股票列表"""
        return self._fetch_with_fallback(
            lambda f: f.get_stock_list(market),
            f"market_{market}"
        )

    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票"""
        return self._fetch_with_fallback(
            lambda f: f.search_stock(keyword),
            f"search_{keyword}"
        )

    def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        return self._fetch_with_fallback(
            lambda f: f.get_market_summary(),
            "market_summary"
        )

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """获取财务数据"""
        return self._fetch_with_fallback(
            lambda f: f.get_financial_data(stock_code),
            stock_code
        )

    def _fetch_with_fallback(self, fetch_func, resource_key: str) -> Any:
        """
        使用自动降级策略获取数据 - 增强网络检测和重试

        Args:
            fetch_func: 获取函数(接受fetcher作为参数)
            resource_key: 资源标识(用于日志)

        Returns:
            获取结果
        """
        if not self.fetchers:
            logger.error("没有可用的数据源")
            return None

        # 检查熔断器
        if self._circuit_breaker_enabled and self._is_all_in_circuit_breaker():
            logger.warning("所有数据源都处于熔断状态,等待冷却")
            return None

        # 尝试按优先级获取数据 - 增加重试机制
        max_retries = 3
        retry_delay = 2

        for retry in range(max_retries):
            for i, fetcher in enumerate(self.fetchers):
                if self._in_circuit_breaker[i]:
                    logger.warning(f"数据源 {i} ({fetcher.get_name()}) 处于熔断状态,跳过")
                    continue

                try:
                    result = fetch_func(fetcher)
                    
                    # 判断结果是否有效 - 支持DataFrame和字典
                    is_valid = False
                    if result is not None:
                        # 检查是否是DataFrame
                        try:
                            import pandas as pd
                            if isinstance(result, pd.DataFrame):
                                is_valid = not result.empty
                            else:
                                # 字典或列表类型
                                is_valid = bool(result)
                        except ImportError:
                            # pandas未安装，按普通类型判断
                            is_valid = bool(result)
                    
                    if is_valid:
                        self._on_success(i)
                        logger.info(f"使用数据源 {i} ({fetcher.get_name()}) 成功获取 {resource_key}")
                        return result
                except Exception as e:
                    self._on_failure(i, e)
                    logger.warning(f"数据源 {i} ({fetcher.get_name()}) 获取 {resource_key} 失败: {e}")

                    # 检查是否是网络连接错误
                    error_str = str(e).lower()
                    is_network_error = any(keyword in error_str for keyword in [
                        'connection', 'timeout', 'network', 'remote', 'aborted', 'unreachable'
                    ])

                    if is_network_error and retry < max_retries - 1:
                        logger.info(f"检测到网络错误,将在 {retry_delay}秒后重试...")
                        import time
                        time.sleep(retry_delay)
                        break
                    elif retry == max_retries - 1:
                        # 最后一次重试失败,触发熔断器
                        if self._circuit_breaker_enabled:
                            logger.warning(f"数据源 {i} ({fetcher.get_name()}) 连续失败,触发熔断")
                            self._in_circuit_breaker[i] = True

        # 所有数据源都失败
        logger.error(f"所有数据源都失败获取 {resource_key}")
        return None

    def _on_success(self, fetcher_index: int):
        """成功获取数据"""
        self._failure_counts[fetcher_index] = 0
        self._current_fetcher_index = fetcher_index
        self._last_failure_time[fetcher_index] = None

        # 检查是否需要重置熔断器
        if self._circuit_breaker_enabled:
            if not any(self._in_circuit_breaker):
                logger.info("所有数据源都恢复正常,重置熔断器")
                self._in_circuit_breaker = [False] * len(self.fetchers)

    def _on_failure(self, fetcher_index: int, error: Exception):
        """失败处理"""
        self._failure_counts[fetcher_index] += 1
        self._last_failure_time[fetcher_index] = time.time()

        # 检查是否需要触发熔断器
        if self._circuit_breaker_enabled:
            if self._failure_counts[fetcher_index] >= self._circuit_breaker_threshold:
                logger.warning(f"数据源 {fetcher_index} 连续失败 {self._failure_counts[fetcher_index]} 次,触发熔断")
                self._in_circuit_breaker[fetcher_index] = True

                # 检查是否所有数据源都熔断
                if self._is_all_in_circuit_breaker():
                    logger.error("所有数据源都触发熔断,停止请求")

    def _is_all_in_circuit_breaker(self) -> bool:
        """检查是否所有数据源都熔断"""
        return all(self._in_circuit_breaker)

    def get_current_fetcher(self) -> Optional[BaseDataFetcher]:
        """获取当前使用的数据源"""
        if self._current_fetcher_index < len(self.fetchers):
            return self.fetchers[self._current_fetcher_index]
        return None

    def get_fetcher_status(self) -> Dict[str, Any]:
        """获取所有数据源状态"""
        status = {}
        for i, fetcher in enumerate(self.fetchers):
            status[f"fetcher_{i}"] = {
                "name": fetcher.get_name(),
                "failure_count": self._failure_counts[i],
                "is_broken": self._in_circuit_breaker[i],
                "last_failure_time": self._last_failure_time[i],
                "is_current": i == self._current_fetcher_index
            }
        return status

    def reset_circuit_breaker(self, fetcher_index: Optional[int] = None):
        """
        重置熔断器

        Args:
            fetcher_index: 数据源索引,None表示重置所有
        """
        if fetcher_index is None:
            self._in_circuit_breaker = [False] * len(self.fetchers)
            logger.info("重置所有数据源的熔断器")
        else:
            self._in_circuit_breaker[fetcher_index] = False
            logger.info(f"重置数据源 {fetcher_index} 的熔断器")

    def set_circuit_breaker_enabled(self, enabled: bool):
        """启用/禁用熔断器"""
        self._circuit_breaker_enabled = enabled
        logger.info(f"熔断器已{'启用' if enabled else '禁用'}")

    def health_check(self) -> Dict[str, bool]:
        """
        健康检查所有数据源

        Returns:
            健康状态字典
        """
        health_status = {}
        for i, fetcher in enumerate(self.fetchers):
            try:
                is_healthy = fetcher.health_check()
                health_status[fetcher.get_name()] = is_healthy
                logger.info(f"数据源 {i} ({fetcher.get_name()}) 健康检查: {'健康' if is_healthy else '不健康'}")
            except Exception as e:
                logger.error(f"数据源 {i} ({fetcher.get_name()}) 健康检查失败: {e}")
                health_status[fetcher.get_name()] = False

        return health_status

    def get_priority_order(self) -> List[str]:
        """获取优先级顺序"""
        return [fetcher.get_name() for fetcher in self.fetchers]
