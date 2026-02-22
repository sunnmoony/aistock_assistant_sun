# -*- coding: utf-8 -*-
"""
===================================
数据提供者单元测试
===================================

测试内容：
1. PytdxProvider测试
2. ChinaDataProvider测试
3. MockProvider测试
4. 数据源管理器测试
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from core.data_providers.pytdx_provider import PytdxProvider, TdxConnectionPool
from core.data_providers.china_data_provider import ChinaDataProvider
from core.data_providers.mock_provider import MockProvider
from core.data_providers.base import DataFetcherManager


class TestPytdxProvider:
    """通达信数据提供者测试"""
    
    @pytest.fixture
    def provider(self):
        """创建PytdxProvider实例"""
        return PytdxProvider(pool_size=2, cache_timeout=30)
    
    def test_init(self, provider):
        """测试初始化"""
        assert provider is not None
        assert provider.cache_timeout == 30
        assert provider._max_retries == 3
        assert provider._retry_delay == 2
    
    @pytest.mark.skip(reason="需要实际pytdx连接")
    def test_get_stock_realtime(self, provider):
        """测试获取实时行情"""
        data = provider.get_stock_realtime("600519")
        
        if data:
            assert "code" in data
            assert "name" in data
            assert "price" in data
            assert "change_percent" in data
            assert data["code"] == "600519"
    
    @pytest.mark.skip(reason="需要实际pytdx连接")
    def test_get_stock_history(self, provider):
        """测试获取历史数据"""
        df = provider.get_stock_history("600519", period="daily")
        
        if df is not None and not df.empty:
            assert "date" in df.columns
            assert "open" in df.columns
            assert "close" in df.columns
            assert "high" in df.columns
            assert "low" in df.columns
            assert "volume" in df.columns
    
    @pytest.mark.skip(reason="需要实际pytdx连接")
    def test_get_all_indices(self, provider):
        """测试获取主要指数"""
        indices = provider.get_all_indices()
        
        if indices:
            assert len(indices) > 0
            for index in indices:
                assert "code" in index
                assert "name" in index
                assert "price" in index
    
    def test_cache_mechanism(self, provider):
        """测试缓存机制"""
        # 第一次获取，应该从API获取
        data1 = provider.get_stock_realtime("600519")
        
        # 第二次获取，应该从缓存获取
        data2 = provider.get_stock_realtime("600519")
        
        # 强制刷新
        data3 = provider.get_stock_realtime("600519", force_refresh=True)
        
        # 验证缓存键存在
        cache_key = f"realtime_600519"
        assert cache_key in provider.cache
    
    def test_performance_stats(self, provider):
        """测试性能统计"""
        stats = provider.get_performance_stats()
        
        assert "total_requests" in stats
        assert "success_count" in stats
        assert "failure_count" in stats
        assert "avg_response_time" in stats
        assert "success_rate" in stats
    
    def test_clear_cache(self, provider):
        """测试清空缓存"""
        # 添加一些缓存数据
        provider._set_cache("test_key", {"data": "test"})
        assert "test_key" in provider.cache
        
        # 清空缓存
        provider.clear_cache()
        assert len(provider.cache) == 0


class TestChinaDataProvider:
    """中国数据提供者测试"""
    
    @pytest.fixture
    def provider(self):
        """创建ChinaDataProvider实例"""
        return ChinaDataProvider()
    
    def test_init(self, provider):
        """测试初始化"""
        assert provider is not None
    
    def test_get_stock_realtime(self, provider):
        """测试获取实时行情"""
        data = provider.get_stock_realtime("600519")
        
        # 由于网络问题，可能返回None
        if data:
            assert "code" in data
            assert "price" in data
            assert "change_percent" in data
    
    def test_get_stock_history(self, provider):
        """测试获取历史数据"""
        df = provider.get_stock_history("600519", period="daily")
        
        # 由于网络问题，可能返回None
        if df is not None and not df.empty:
            assert "date" in df.columns
            assert "close" in df.columns
    
    def test_get_market_summary(self, provider):
        """测试获取市场概况"""
        summary = provider.get_market_summary()
        
        # 由于网络问题，可能返回None
        if summary:
            assert "rise_count" in summary
            assert "fall_count" in summary
            assert "flat_count" in summary
    
    def test_health_check(self, provider):
        """测试健康检查"""
        is_healthy = provider.health_check()
        
        # 健康检查应该返回布尔值
        assert isinstance(is_healthy, bool)


class TestMockProvider:
    """模拟数据提供者测试"""
    
    @pytest.fixture
    def provider(self):
        """创建MockProvider实例"""
        return MockProvider()
    
    def test_init(self, provider):
        """测试初始化"""
        assert provider is not None
        assert provider.cache is not None
    
    def test_get_stock_realtime(self, provider):
        """测试获取实时行情"""
        data = provider.get_stock_realtime("600519")
        
        assert data is not None
        assert "code" in data
        assert data["code"] == "600519"
        assert "price" in data
        assert "change_percent" in data
    
    def test_get_stock_history(self, provider):
        """测试获取历史数据"""
        df = provider.get_stock_history("600519", period="daily")
        
        assert df is not None
        assert not df.empty
        assert "date" in df.columns
        assert "close" in df.columns
    
    def test_get_all_indices(self, provider):
        """测试获取主要指数"""
        indices = provider.get_all_indices()
        
        assert indices is not None
        assert len(indices) > 0
        
        for index in indices:
            assert "code" in index
            assert "name" in index
            assert "price" in index
    
    def test_get_market_summary(self, provider):
        """测试获取市场概况"""
        summary = provider.get_market_summary()
        
        assert summary is not None
        assert "rise_count" in summary
        assert "fall_count" in summary
        assert "flat_count" in summary
    
    def test_health_check(self, provider):
        """测试健康检查"""
        is_healthy = provider.health_check()
        
        assert is_healthy is True
    
    def test_get_name(self, provider):
        """测试获取数据源名称"""
        name = provider.get_name()
        
        assert name == "Mock(模拟数据)"


class TestDataFetcherManager:
    """数据源管理器测试"""
    
    @pytest.fixture
    def manager(self):
        """创建DataFetcherManager实例"""
        mock_provider = MockProvider()
        return DataFetcherManager([mock_provider])
    
    def test_init(self, manager):
        """测试初始化"""
        assert manager is not None
        assert len(manager.fetchers) > 0
    
    def test_get_stock_realtime(self, manager):
        """测试获取实时行情"""
        data = manager.get_stock_realtime("600519")
        
        assert data is not None
        assert "code" in data
        assert data["code"] == "600519"
    
    def test_get_stock_history(self, manager):
        """测试获取历史数据"""
        df = manager.get_stock_history("600519", period="daily")
        
        assert df is not None
        assert not df.empty
    
    def test_get_all_indices(self, manager):
        """测试获取主要指数"""
        indices = manager.get_all_indices()
        
        assert indices is not None
        assert len(indices) > 0
    
    def test_get_market_summary(self, manager):
        """测试获取市场概况"""
        summary = manager.get_market_summary()
        
        assert summary is not None
        assert "rise_count" in summary
        assert "fall_count" in summary
        assert "flat_count" in summary
    
    def test_get_fetcher_status(self, manager):
        """测试获取数据源状态"""
        status = manager.get_fetcher_status()
        
        assert status is not None
        assert "fetcher_0" in status
        
        fetcher_status = status["fetcher_0"]
        assert "name" in fetcher_status
        assert "failure_count" in fetcher_status
        assert "is_broken" in fetcher_status
    
    def test_health_check(self, manager):
        """测试健康检查"""
        health_status = manager.health_check()
        
        assert health_status is not None
        assert len(health_status) > 0
    
    def test_reset_circuit_breaker(self, manager):
        """测试重置熔断器"""
        # 触发熔断器
        manager._in_circuit_breaker[0] = True
        
        # 重置熔断器
        manager.reset_circuit_breaker()
        
        # 验证熔断器已重置
        assert not any(manager._in_circuit_breaker)
    
    def test_set_circuit_breaker_enabled(self, manager):
        """测试启用/禁用熔断器"""
        # 禁用熔断器
        manager.set_circuit_breaker_enabled(False)
        assert not manager._circuit_breaker_enabled
        
        # 启用熔断器
        manager.set_circuit_breaker_enabled(True)
        assert manager._circuit_breaker_enabled
    
    def test_get_priority_order(self, manager):
        """测试获取优先级顺序"""
        order = manager.get_priority_order()
        
        assert order is not None
        assert len(order) == len(manager.fetchers)


@pytest.mark.integration
class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def manager(self):
        """创建完整的数据源管理器"""
        mock_provider = MockProvider()
        return DataFetcherManager([mock_provider])
    
    def test_full_data_flow(self, manager):
        """测试完整数据流"""
        # 1. 获取实时行情
        realtime_data = manager.get_stock_realtime("600519")
        assert realtime_data is not None
        
        # 2. 获取历史数据
        history_data = manager.get_stock_history("600519", period="daily")
        assert history_data is not None
        
        # 3. 获取指数数据
        indices_data = manager.get_all_indices()
        assert indices_data is not None
        
        # 4. 获取市场概况
        summary_data = manager.get_market_summary()
        assert summary_data is not None
        
        # 5. 检查数据源状态
        status = manager.get_fetcher_status()
        assert status is not None
        
        # 6. 健康检查
        health = manager.health_check()
        assert health is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
