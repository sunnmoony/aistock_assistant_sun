# -*- coding: utf-8 -*-
"""
===================================
数据提供者模块
===================================

提供多种数据源，支持自动降级和熔断器机制
"""

from .base import BaseDataFetcher, DataFetcherManager
from .pytdx_provider import PytdxProvider
from .akshare_provider import AkShareProvider
from .mock_provider import MockProvider

__all__ = [
    'BaseDataFetcher',
    'DataFetcherManager',
    'PytdxProvider',
    'AkShareProvider',
    'MockProvider'
]
