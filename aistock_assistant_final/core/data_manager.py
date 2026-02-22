# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 数据管理器(优化版)
===================================

职责:
1. 管理股票数据和自选股
2. 使用多源数据策略(Pytdx/AkShare/Mock)
3. 实现自动降级和熔断器机制
4. 支持大盘复盘数据获取
5. 优化性能，减少卡顿
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import logging
import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from models.stock import Stock
from core.config_manager import ConfigManager
from core.data_providers.base import DataFetcherManager
from core.data_providers.pytdx_provider import PytdxProvider
from core.data_providers.mock_provider import MockProvider
from core.data_providers.akshare_provider import AkShareProvider

logger = logging.getLogger(__name__)


class DataManager(QObject):
    """数据管理器 - 管理股票数据和自选股(优化版)"""

    data_updated = pyqtSignal(str, object)
    watchlist_changed = pyqtSignal(list)

    def __init__(self, lite_mode=False):
        """
        初始化数据管理器
        
        Args:
            lite_mode: 精简模式标志
        """
        super().__init__()
        self._精简模式 = lite_mode
        self._股票缓存: Dict[str, Dict[str, Any]] = {}
        self._缓存时间戳: Dict[str, float] = {}
        self._自选股列表: List[str] = []
        self._市场数据: Dict[str, Any] = {}
        self._缓存生存时间 = 180 if lite_mode else 120
        self._自动刷新启用 = not lite_mode
        self._刷新间隔 = 180 if lite_mode else 60
        self._刷新定时器: Optional[QTimer] = None
        self._使用模拟数据 = False
        self._最大缓存数量 = 50 if lite_mode else 200
        self._数据源已初始化 = False
        self._数据源超时时间 = 30
        self._线程池 = ThreadPoolExecutor(max_workers=3)
        self._正在刷新 = False
        
        self.配置管理器 = ConfigManager()
        self._数据源配置 = self.配置管理器.config.get('data_sources', {})
        self.数据源管理器: Optional[DataFetcherManager] = None
        
        self._加载自选股()
        
        self._初始化数据源管理器()
        self._数据源已初始化 = True
        if not self._精简模式:
            self._setup_auto_refresh()
    
    def _delayed_init_data_source(self):
        """延迟初始化数据源管理器"""
        if self._数据源已初始化:
            return
        self._初始化数据源管理器()
        self._数据源已初始化 = True
        if not self._精简模式:
            self._setup_auto_refresh()
    
    def _初始化数据源管理器(self):
        """初始化数据源管理器 - 只使用免费数据源，延迟加载"""
        try:
            获取器列表 = []
            线程池大小 = 1 if self._精简模式 else 2
            
            try:
                akshare启用 = self._数据源配置.get('akshare', {}).get('enabled', True)
                if akshare启用:
                    获取器列表.append(AkShareProvider())
                    logger.info("AkShare数据源已启用")
            except Exception as e:
                logger.warning(f"AkShare数据源初始化失败: {e}")
            
            try:
                pytdx启用 = self._数据源配置.get('pytdx', {}).get('enabled', False)
                if pytdx启用:
                    获取器列表.append(PytdxProvider(
                        pool_size=线程池大小, 
                        cache_timeout=self._缓存生存时间, 
                        lazy_init=True
                    ))
                    logger.info(f"Pytdx数据源已启用 (延迟加载模式)")
            except Exception as e:
                logger.warning(f"Pytdx数据源初始化失败: {e}")
            
            try:
                mock启用 = self._数据源配置.get('mock', {}).get('enabled', True)
                if mock启用:
                    获取器列表.append(MockProvider())
                    logger.info("Mock数据源已启用 (后备)")
            except Exception as e:
                logger.warning(f"Mock数据源初始化失败: {e}")
            
            if not 获取器列表:
                获取器列表.append(MockProvider())
                logger.warning("没有可用数据源，使用Mock数据源")
            
            self.数据源管理器 = DataFetcherManager(获取器列表)
            
            logger.info(f"数据源管理器初始化完成,共 {len(获取器列表)} 个数据源")
            
        except Exception as e:
            logger.error(f"初始化数据源管理器失败: {e}")
            self.数据源管理器 = DataFetcherManager([MockProvider()])
    
    def 是否已就绪(self) -> bool:
        """检查数据管理器是否就绪"""
        return self._数据源已初始化 and self.数据源管理器 is not None

    def 获取实时行情(self, 股票代码: str, 强制刷新: bool = False) -> Optional[Stock]:
        """
        获取实时行情
        
        Args:
            股票代码: 股票代码
            强制刷新: 是否强制刷新缓存
            
        Returns:
            股票对象
        """
        if not self.是否已就绪():
            return None
        try:
            if 强制刷新 or 股票代码 not in self._股票缓存:
                return self._从数据源获取实时行情(股票代码)
            
            缓存时间 = self._缓存时间戳.get(股票代码, 0)
            if time.time() - 缓存时间 > self._缓存生存时间:
                return self._从数据源获取实时行情(股票代码)
            
            缓存数据 = self._股票缓存[股票代码]
            return Stock(
                code=缓存数据.get('code', ''),
                name=缓存数据.get('name', ''),
                price=缓存数据.get('price', 0),
                change=缓存数据.get('change', 0),
                volume=缓存数据.get('volume', 0)
            )
        except Exception as e:
            logger.error(f"获取实时行情失败 {股票代码}: {e}")
            return None

    def _从数据源获取实时行情(self, 股票代码: str) -> Optional[Stock]:
        """
        从数据源管理器获取实时行情（带超时保护）
        
        Args:
            股票代码: 股票代码
            
        Returns:
            股票对象
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_stock_realtime, 
                股票代码
            )
            数据 = 未来对象.result(timeout=self._数据源超时时间)
            
            if not 数据:
                logger.warning(f"所有数据源都失败获取股票 {股票代码}")
                return None
            
            股票 = Stock(
                code=数据.get('code', 股票代码),
                name=数据.get('name', f"股票{股票代码}"),
                price=数据.get('price', 0),
                change=数据.get('change', 0),
                volume=数据.get('volume', 0)
            )
            
            self._更新缓存(股票代码, 数据)
            
            当前获取器 = self.数据源管理器.get_current_fetcher()
            if 当前获取器:
                logger.info(f"获取实时行情成功({当前获取器.get_name()}): {股票代码} {股票.name} 价格:{股票.price}")
            
            return 股票
        except TimeoutError:
            logger.error(f"获取实时行情超时 {股票代码} (超过{self._数据源超时时间}秒)")
            return None
        except Exception as e:
            logger.error(f"获取实时行情失败 {股票代码}: {e}")
            return None

    def _更新缓存(self, 股票代码: str, 数据: Dict[str, Any]):
        """
        更新缓存（带LRU策略）
        
        Args:
            股票代码: 股票代码
            数据: 股票数据
        """
        self._股票缓存[股票代码] = 数据
        self._缓存时间戳[股票代码] = time.time()
        
        if len(self._股票缓存) > self._最大缓存数量:
            self._清理过期缓存()

    def _清理过期缓存(self):
        """清理过期缓存，保留最新的数据"""
        try:
            排序股票 = sorted(
                self._缓存时间戳.items(), 
                key=lambda x: x[1]
            )
            需要删除的数量 = len(self._股票缓存) - self._最大缓存数量
            for 股票代码, _ in 排序股票[:需要删除的数量]:
                if 股票代码 in self._股票缓存:
                    del self._股票缓存[股票代码]
                if 股票代码 in self._缓存时间戳:
                    del self._缓存时间戳[股票代码]
            logger.debug(f"缓存清理完成，当前缓存数量: {len(self._股票缓存)}")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")

    def 获取实时行情字典(self, 股票代码: str, 强制刷新: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取实时行情(字典格式)
        
        Args:
            股票代码: 股票代码
            强制刷新: 是否强制刷新缓存
            
        Returns:
            股票数据字典
        """
        股票 = self.获取实时行情(股票代码, 强制刷新)
        return 股票.to_dict() if 股票 else None

    def 设置使用模拟数据(self, 使用模拟: bool):
        """
        设置是否使用模拟数据
        
        Args:
            使用模拟: 是否使用模拟数据
        """
        self._使用模拟数据 = 使用模拟
        logger.info(f"{'使用' if 使用模拟 else '不使用'}模拟数据模式")
        if 使用模拟:
            self._股票缓存.clear()
            self._缓存时间戳.clear()

    def 获取股票历史数据(self, 股票代码: str, 周期: str = "daily",
                        开始日期: str = None, 结束日期: str = None) -> Any:
        """
        获取股票历史K线数据（带超时保护）
        
        Args:
            股票代码: 股票代码
            周期: K线周期
            开始日期: 开始日期
            结束日期: 结束日期
            
        Returns:
            K线数据
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_stock_history,
                股票代码, 周期, 开始日期, 结束日期
            )
            数据框 = 未来对象.result(timeout=self._数据源超时时间 * 2)
            
            if 数据框 is not None and not 数据框.empty:
                logger.debug(f"获取历史数据成功: {股票代码} {len(数据框)}条记录")
            return 数据框
        except TimeoutError:
            logger.error(f"获取历史数据超时 {股票代码}")
            return None
        except Exception as e:
            logger.error(f"获取历史数据失败 {股票代码}: {e}")
            return None

    def 获取指数数据(self, 指数代码: str) -> Optional[Dict[str, Any]]:
        """
        获取指数数据（带超时保护）
        
        Args:
            指数代码: 指数代码
            
        Returns:
            指数数据字典
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_index_data,
                指数代码
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error(f"获取指数数据超时 {指数代码}")
            return None
        except Exception as e:
            logger.error(f"获取指数数据失败 {指数代码}: {e}")
            return None

    def 获取所有指数(self) -> List[Dict[str, Any]]:
        """
        获取主要指数数据（带超时保护）
        
        Returns:
            指数数据列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_all_indices
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("获取所有指数数据超时")
            return []
        except Exception as e:
            logger.error(f"获取主要指数数据失败: {e}")
            return []

    def 获取板块数据(self) -> List[Dict[str, Any]]:
        """
        获取板块数据（带超时保护）
        
        Returns:
            板块数据列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_sector_data
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("获取板块数据超时")
            return []
        except Exception as e:
            logger.error(f"获取板块数据失败: {e}")
            return []

    def 获取板块排行(self) -> List[Dict[str, Any]]:
        """
        获取板块涨跌幅排行（带超时保护）
        
        Returns:
            板块排行数据列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_sector_rank
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("获取板块排行超时")
            return []
        except Exception as e:
            logger.error(f"获取板块排行失败: {e}")
            return []

    def 获取资金流向(self, 股票代码: str = None) -> List[Dict[str, Any]]:
        """
        获取资金流向数据（带超时保护）
        
        Args:
            股票代码: 股票代码，None表示市场整体
            
        Returns:
            资金流向数据列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_fund_flow,
                股票代码
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("获取资金流向数据超时")
            return []
        except Exception as e:
            logger.error(f"获取资金流向数据失败: {e}")
            return []

    def 获取股票列表(self, 市场: str = "SH") -> List[Dict[str, Any]]:
        """
        获取股票列表（带超时保护）
        
        Args:
            市场: 市场代码，SH或SZ
            
        Returns:
            股票列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_stock_list,
                市场
            )
            return 未来对象.result(timeout=self._数据源超时时间 * 2)
        except TimeoutError:
            logger.error("获取股票列表超时")
            return []
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    def 搜索股票(self, 关键词: str) -> List[Dict[str, Any]]:
        """
        搜索股票（带超时保护）
        
        Args:
            关键词: 搜索关键词
            
        Returns:
            搜索结果列表
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.search_stock,
                关键词
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error(f"搜索股票超时 {关键词}")
            return []
        except Exception as e:
            logger.error(f"搜索股票失败 {关键词}: {e}")
            return []

    def 获取市场概况(self) -> Dict[str, Any]:
        """
        获取市场概况（带超时保护）
        
        Returns:
            市场概况字典
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_market_summary
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("获取市场概况超时")
            return {}
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}

    def 获取财务数据(self, 股票代码: str) -> Dict[str, Any]:
        """
        获取财务数据（带超时保护）
        
        Args:
            股票代码: 股票代码
            
        Returns:
            财务数据字典
        """
        try:
            未来对象 = self._线程池.submit(
                self.数据源管理器.get_financial_data,
                股票代码
            )
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error(f"获取财务数据超时 {股票代码}")
            return {}
        except Exception as e:
            logger.error(f"获取财务数据失败 {股票代码}: {e}")
            return {}

    def 添加到自选股(self, 股票代码: str, 股票名称: str = None) -> bool:
        """
        添加到自选股
        
        Args:
            股票代码: 股票代码
            股票名称: 股票名称
            
        Returns:
            是否添加成功
        """
        if 股票代码 in self._自选股列表:
            logger.warning(f"股票已在自选股中: {股票代码}")
            return False
        try:
            self._自选股列表.append(股票代码)
            self._保存自选股()
            self.watchlist_changed.emit(self._自选股列表)
            logger.info(f"添加到自选股: {股票代码}")
            return True
        except Exception as e:
            logger.error(f"添加自选股失败 {股票代码}: {e}")
            return False

    def 从自选股移除(self, 股票代码: str) -> bool:
        """
        从自选股移除
        
        Args:
            股票代码: 股票代码
            
        Returns:
            是否移除成功
        """
        if 股票代码 not in self._自选股列表:
            logger.warning(f"股票不在自选股中: {股票代码}")
            return False
        try:
            self._自选股列表.remove(股票代码)
            self._保存自选股()
            self.watchlist_changed.emit(self._自选股列表)
            logger.info(f"从自选股移除: {股票代码}")
            return True
        except Exception as e:
            logger.error(f"移除自选股失败 {股票代码}: {e}")
            return False

    def 获取自选股列表(self) -> List[str]:
        """
        获取自选股列表
        
        Returns:
            自选股代码列表
        """
        return self._自选股列表.copy()

    def 获取自选股数据(self) -> List[Dict[str, Any]]:
        """
        获取自选股数据
        
        Returns:
            自选股数据列表
        """
        try:
            自选股数据 = []
            for 股票代码 in self._自选股列表:
                股票 = self.获取实时行情(股票代码)
                if 股票:
                    自选股数据.append(股票.to_dict())
            return 自选股数据
        except Exception as e:
            logger.error(f"获取自选股详细信息失败: {e}")
            return []

    def 设置自动刷新(self, 启用: bool):
        """
        设置自动刷新
        
        Args:
            启用: 是否启用自动刷新
        """
        self._自动刷新启用 = 启用
        logger.info(f"自动刷新已{'启用' if 启用 else '禁用'}")

    def 设置刷新间隔(self, 间隔: int):
        """
        设置刷新间隔（最小60秒）
        
        Args:
            间隔: 刷新间隔（秒）
        """
        最小间隔 = 60
        if 间隔 < 最小间隔:
            logger.warning(f"刷新间隔不能小于{最小间隔}秒，已自动设置为{最小间隔}秒")
            间隔 = 最小间隔
        self._刷新间隔 = 间隔
        if self._刷新定时器:
            self._刷新定时器.setInterval(间隔 * 1000)
        logger.info(f"刷新间隔已更新: {间隔}秒")

    def 清空缓存(self):
        """清空缓存"""
        self._股票缓存.clear()
        self._缓存时间戳.clear()
        logger.info("股票缓存已清空")

    def 获取缓存信息(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        获取器状态 = self.数据源管理器.get_fetcher_status()
        return {
            "stock_count": len(self._股票缓存),
            "watchlist_count": len(self._自选股列表),
            "auto_refresh": self._自动刷新启用,
            "refresh_interval": self._刷新间隔,
            "data_sources": 获取器状态
        }

    def _加载自选股(self):
        """加载自选股列表"""
        try:
            自选股文件 = "data/watchlist.json"
            if os.path.exists(自选股文件):
                with open(自选股文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                    self._自选股列表 = 数据.get("watchlist", [])
                logger.info(f"加载自选股列表: {len(self._自选股列表)}只")
        except Exception as e:
            logger.error(f"加载自选股列表失败: {e}")
            self._自选股列表 = []

    def _保存自选股(self):
        """保存自选股列表"""
        try:
            os.makedirs("data", exist_ok=True)
            自选股文件 = "data/watchlist.json"
            with open(自选股文件, 'w', encoding='utf-8') as f:
                json.dump({"watchlist": self._自选股列表}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存自选股列表失败: {e}")

    def _setup_auto_refresh(self):
        """设置自动刷新"""
        if self._刷新定时器:
            self._刷新定时器.stop()

        from PyQt5.QtWidgets import QApplication
        if QApplication.instance() is None:
            logger.info("非 GUI 环境，跳过自动刷新定时器设置")
            return

        self._刷新定时器 = QTimer()
        self._刷新定时器.timeout.connect(self._refresh_all_data)
        self._刷新定时器.start(self._刷新间隔 * 1000)
        logger.info(f"自动刷新已启动,间隔: {self._刷新间隔}秒")

    def _refresh_all_data(self):
        """刷新所有数据"""
        if not self._自动刷新启用:
            return
        if self._正在刷新:
            logger.debug("上次刷新尚未完成，跳过本次刷新")
            return
        QTimer.singleShot(100, self._do_refresh_all_data)
    
    def _do_refresh_all_data(self):
        """执行刷新操作"""
        if self._正在刷新:
            return
        self._正在刷新 = True
        try:
            self.更新自选股数据()
            self.更新市场数据()
        except Exception as e:
            logger.error(f"刷新数据失败: {e}")
        finally:
            self._正在刷新 = False

    def 更新自选股数据(self):
        """更新自选股数据"""
        try:
            自选股数据 = []
            for 股票代码 in self._自选股列表:
                股票 = self.获取实时行情(股票代码)
                if 股票:
                    自选股数据.append(股票.to_dict())
            self.data_updated.emit("watchlist", 自选股数据)
            logger.info(f"自选股数据更新完成: {len(自选股数据)}只")
        except Exception as e:
            logger.error(f"更新自选股数据失败: {e}")

    def 更新市场数据(self):
        """更新市场数据"""
        try:
            指数列表 = self.获取所有指数()
            if 指数列表:
                self._市场数据["indices"] = 指数列表
            self.data_updated.emit("market", self._市场数据)
            logger.info("市场数据更新完成")
        except Exception as e:
            logger.error(f"更新市场数据失败: {e}")

    def 获取市场数据(self) -> Dict[str, Any]:
        """
        获取市场数据
        
        Returns:
            市场数据字典
        """
        return self._市场数据

    def 刷新市场数据(self):
        """刷新市场数据"""
        self.更新市场数据()

    def 刷新自选股(self):
        """刷新自选股数据"""
        self.更新自选股数据()

    def 获取数据源状态(self) -> Dict[str, Any]:
        """
        获取数据源状态
        
        Returns:
            数据源状态字典
        """
        return self.数据源管理器.get_fetcher_status()

    def 健康检查数据源(self) -> Dict[str, bool]:
        """
        健康检查所有数据源（带超时保护）
        
        Returns:
            健康状态字典
        """
        def 执行健康检查():
            return self.数据源管理器.health_check()
        
        try:
            未来对象 = self._线程池.submit(执行健康检查)
            return 未来对象.result(timeout=self._数据源超时时间)
        except TimeoutError:
            logger.error("数据源健康检查超时")
            return {}
        except Exception as e:
            logger.error(f"健康检查数据源失败: {e}")
            return {}

    def 重置数据源熔断器(self, 获取器索引: Optional[int] = None):
        """
        重置数据源熔断器
        
        Args:
            获取器索引: 数据源索引，None表示重置所有
        """
        self.数据源管理器.reset_circuit_breaker(获取器索引)
    
    def 关闭(self):
        """关闭数据管理器，释放资源"""
        try:
            if self._刷新定时器:
                self._刷新定时器.stop()
            self._线程池.shutdown(wait=False)
            logger.info("数据管理器已关闭")
        except Exception as e:
            logger.error(f"关闭数据管理器失败: {e}")

    # ========== 英文方法别名（供外部调用）==========
    is_ready = 是否已就绪
    get_realtime_quote = 获取实时行情
    get_realtime_quote_dict = 获取实时行情字典
    set_use_mock_data = 设置使用模拟数据
    get_stock_history = 获取股票历史数据
    get_index_data = 获取指数数据
    get_all_indices = 获取所有指数
    get_sector_data = 获取板块数据
    get_sector_ranking = 获取板块排行
    get_fund_flow = 获取资金流向
    get_stock_list = 获取股票列表
    search_stock = 搜索股票
    get_market_summary = 获取市场概况
    get_financial_data = 获取财务数据
    add_to_watchlist = 添加到自选股
    remove_from_watchlist = 从自选股移除
    get_watchlist = 获取自选股列表
    get_watchlist_data = 获取自选股数据
    set_auto_refresh = 设置自动刷新
    set_refresh_interval = 设置刷新间隔
    clear_cache = 清空缓存
    get_cache_info = 获取缓存信息
    get_market_data = 获取市场数据
    refresh_market_data = 刷新市场数据
    refresh_watchlist = 刷新自选股
    update_watchlist_data = 更新自选股数据
    update_market_data = 更新市场数据
    get_data_source_status = 获取数据源状态
    health_check_data_sources = 健康检查数据源
    reset_data_source_circuit_breaker = 重置数据源熔断器
    close = 关闭
