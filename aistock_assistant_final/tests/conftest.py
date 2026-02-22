# -*- coding: utf-8 -*-
"""
===================================
单元测试框架
===================================

功能：
1. 测试数据提供者
2. 测试数据管理器
3. 测试数据库管理器
4. 测试AI引擎
5. 测试UI组件

使用方法：
    python -m pytest tests/
    python -m pytest tests/ -v
    python -m pytest tests/ -k test_pytdx
"""

import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 配置pytest
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(scope="session")
def setup_test_environment():
    """
    设置测试环境
    
    在所有测试开始前执行一次
    """
    # 创建测试数据目录
    os.makedirs("data/test", exist_ok=True)
    
    # 创建测试数据库
    os.makedirs("data/test/db", exist_ok=True)
    
    yield
    
    # 清理测试环境
    import shutil
    if os.path.exists("data/test"):
        shutil.rmtree("data/test")


@pytest.fixture
def mock_logger():
    """
    模拟日志记录器
    
    用于测试中的日志输出
    """
    import logging
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    
    # 添加控制台处理器
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


@pytest.fixture
def sample_stock_data():
    """
    示例股票数据
    
    用于测试的模拟股票数据
    """
    return {
        "code": "600519",
        "name": "贵州茅台",
        "price": 1800.00,
        "change": 20.00,
        "change_percent": 1.12,
        "open": 1790.00,
        "high": 1810.00,
        "low": 1785.00,
        "pre_close": 1780.00,
        "volume": 100000,
        "turnover": 180000000.00,
        "amplitude": 1.40,
        "pe": 35.5,
        "market_cap": 2250000000000.00
    }


@pytest.fixture
def sample_history_data():
    """
    示例历史数据
    
    用于测试的模拟历史K线数据
    """
    import pandas as pd
    
    dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
    data = {
        'date': dates,
        'open': [100 + i for i in range(10)],
        'close': [100 + i + 2 for i in range(10)],
        'high': [100 + i + 3 for i in range(10)],
        'low': [100 + i - 1 for i in range(10)],
        'volume': [1000000 + i * 100000 for i in range(10)],
        'amount': [100000000 + i * 10000000 for i in range(10)]
    }
    
    return pd.DataFrame(data)
