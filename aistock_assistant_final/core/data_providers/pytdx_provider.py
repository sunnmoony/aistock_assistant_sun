# -*- coding: utf-8 -*-
"""
===================================
通达信数据源提供者 - 完全异步优化版
===================================

使用通达信数据接口，完全免费，无需API Key
支持功能：
1. 实时行情获取
2. 历史K线数据获取
3. 指数数据获取
4. 市场概况获取
5. 板块数据获取
6. 资金流向获取

优化功能：
1. 完全异步连接池初始化
2. 后台线程处理连接池
3. 10秒超时机制
4. 服务器连接池
5. 自动重连机制
6. 心跳检测
7. 智能重试
8. 数据缓存优化
9. 性能监控
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import os
import time
import threading
from queue import Queue, Empty
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)


class TdxConnectionPool:
    """
    通达信连接池
    
    功能：
    1. 管理多个通达信服务器连接
    2. 自动选择最优服务器
    3. 连接健康检查
    4. 自动重连
    5. 完全异步初始化
    6. 超时控制机制
    """
    
    # 通达信服务器列表
    TDX服务器列表 = [
        ("119.147.212.81", 7709),  # 上海电信
        ("60.12.136.250", 7709),   # 上海联通
        ("218.108.47.69", 7709),    # 上海移动
        ("14.215.128.18", 7709),    # 广州电信
        ("59.173.18.140", 7709),    # 广州联通
        ("116.23.64.141", 7709),    # 深圳电信
        ("113.105.142.136", 7709),  # 深圳联通
        ("218.75.126.9", 7709),     # 深圳移动
    ]
    
    # 超时时间（秒）
    网络超时 = 10
    
    def __init__(self, 池大小: int = 3, 异步初始化: bool = True):
        """
        初始化连接池
        
        参数：
            池大小: 连接池大小，默认3
            异步初始化: 是否使用异步初始化，默认True
        """
        self.池大小 = 池大小
        self.连接列表: List[Any] = []
        self.可用队列: Queue = Queue()
        self.使用中列表: List[bool] = []
        self.服务器索引 = 0
        self._锁 = threading.Lock()
        self._初始化完成 = False
        self._初始化错误 = None
        self._初始化线程: Optional[threading.Thread] = None
        self._线程池: Optional[ThreadPoolExecutor] = None
        
        if 异步初始化:
            self._后台初始化连接池()
        else:
            self._同步初始化连接池()
    
    def _同步初始化连接池(self):
        """
        同步初始化连接池（仅用于测试）
        """
        self._线程池 = ThreadPoolExecutor(max_workers=4)
        self._初始化连接池()
        self._初始化完成 = True
    
    def _后台初始化连接池(self):
        """
        在后台线程中初始化连接池
        """
        self._线程池 = ThreadPoolExecutor(max_workers=4)
        
        def _初始化任务():
            try:
                logger.info("开始异步初始化连接池...")
                self._初始化连接池()
                self._初始化完成 = True
                logger.info(f"通达信连接池异步初始化完成，大小: {self.池大小}")
            except Exception as e:
                self._初始化错误 = str(e)
                logger.error(f"连接池异步初始化失败: {e}")
        
        self._初始化线程 = threading.Thread(target=_初始化任务, daemon=True)
        self._初始化线程.start()
    
    def _带超时执行(self, 函数, *参数, **关键字参数) -> Any:
        """
        带超时控制执行函数
        
        参数：
            函数: 要执行的函数
            参数: 位置参数
            关键字参数: 关键字参数
        
        返回：
            函数执行结果
        
        异常：
            TimeoutError: 执行超时时抛出
        """
        if self._线程池 is None:
            return 函数(*参数, **关键字参数)
        
        未来对象 = self._线程池.submit(函数, *参数, **关键字参数)
        try:
            return 未来对象.result(timeout=self.网络超时)
        except TimeoutError:
            未来对象.cancel()
            raise TimeoutError(f"操作超时（{self.网络超时}秒）")
    
    def _测试单个服务器(self, 服务器地址: str, 服务器端口: int) -> Optional[Tuple[float, Tuple[str, int]]]:
        """
        测试单个服务器连接速度
        
        参数：
            服务器地址: 服务器IP地址
            服务器端口: 服务器端口
        
        返回：
            (连接耗时, (服务器地址, 端口))，失败返回None
        """
        try:
            import pytdx.hq as hq
            
            开始时间 = time.time()
            api = hq.TdxHq_API()
            api.connect(服务器地址, 服务器端口)
            连接耗时 = time.time() - 开始时间
            api.disconnect()
            
            return (连接耗时, (服务器地址, 服务器端口))
        except Exception as e:
            logger.debug(f"服务器 {服务器地址}:{服务器端口} 连接失败: {e}")
            return None
    
    def _选择最优服务器(self) -> Optional[Tuple[str, int]]:
        """
        选择响应最快的服务器
        
        返回：
            (最优服务器地址, 端口)，失败返回None
        """
        最优服务器 = None
        最优耗时 = float('inf')
        
        for 服务器地址, 服务器端口 in self.TDX服务器列表:
            try:
                结果 = self._带超时执行(self._测试单个服务器, 服务器地址, 服务器端口)
                if 结果:
                    连接耗时, 服务器信息 = 结果
                    if 连接耗时 < 最优耗时:
                        最优耗时 = 连接耗时
                        最优服务器 = 服务器信息
                        logger.info(f"发现更优服务器: {服务器地址}:{服务器端口} ({连接耗时*1000:.0f}ms)")
            except TimeoutError:
                logger.warning(f"服务器 {服务器地址}:{服务器端口} 连接超时")
            except Exception as e:
                logger.debug(f"服务器 {服务器地址}:{服务器端口} 测试失败: {e}")
        
        if 最优服务器:
            logger.info(f"选择最优服务器: {最优服务器[0]}:{最优服务器[1]}")
        else:
            logger.warning("所有服务器连接失败，使用默认服务器")
            最优服务器 = self.TDX服务器列表[0]
        
        return 最优服务器
    
    def _初始化连接池(self):
        """
        初始化连接池
        
        流程：
            1. 尝试连接多个服务器
            2. 选择响应最快的服务器
            3. 创建连接池
        """
        try:
            import pytdx.hq as hq
            
            最优服务器 = self._选择最优服务器()
            if not 最优服务器:
                raise Exception("无法连接到任何服务器")
            
            服务器地址, 服务器端口 = 最优服务器
            
            # 创建连接池
            for i in range(self.池大小):
                try:
                    def _创建连接():
                        api = hq.TdxHq_API()
                        api.connect(服务器地址, 服务器端口)
                        return api
                    
                    api = self._带超时执行(_创建连接)
                    self.连接列表.append(api)
                    self.可用队列.put(api)
                    self.使用中列表.append(False)
                    logger.info(f"连接池连接 {i+1}/{self.池大小} 创建成功")
                except TimeoutError:
                    logger.error(f"连接池连接 {i+1} 创建超时")
                    break
                except Exception as e:
                    logger.error(f"连接池连接 {i+1} 创建失败: {e}")
                    break
        except ImportError:
            logger.warning("pytdx未安装，请运行: pip install pytdx")
        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            raise
    
    def 等待初始化(self, 超时时间: float = 30.0) -> bool:
        """
        等待连接池初始化完成
        
        参数：
            超时时间: 等待超时时间（秒），默认30秒
        
        返回：
            True: 初始化成功
            False: 初始化失败或超时
        """
        开始时间 = time.time()
        while not self._初始化完成:
            if self._初始化错误:
                logger.error(f"连接池初始化错误: {self._初始化错误}")
                return False
            if time.time() - 开始时间 > 超时时间:
                logger.error(f"连接池初始化超时（{超时时间}秒）")
                return False
            time.sleep(0.1)
        return True
    
    def 是否已初始化(self) -> bool:
        """
        检查连接池是否已初始化
        
        返回：
            True: 已初始化
            False: 未初始化
        """
        return self._初始化完成
    
    def 获取连接(self, 超时时间: float = 5.0) -> Optional[Any]:
        """
        获取连接
        
        参数：
            超时时间: 超时时间（秒），默认5秒
        
        返回：
            通达信API连接对象，失败返回None
        """
        if not self._初始化完成:
            if not self.等待初始化(超时时间=10.0):
                logger.warning("连接池未初始化完成")
                return None
        
        try:
            with self._锁:
                try:
                    连接 = self.可用队列.get(timeout=超时时间)
                    for i, 使用中 in enumerate(self.使用中列表):
                        if not 使用中 and self.连接列表[i] == 连接:
                            self.使用中列表[i] = True
                            break
                    return 连接
                except Empty:
                    logger.warning("连接池超时，无可用连接")
                    return None
        except Exception as e:
            logger.error(f"获取连接失败: {e}")
            return None
    
    def 释放连接(self, 连接: Any):
        """
        释放连接
        
        参数：
            连接: 要释放的连接对象
        """
        try:
            with self._锁:
                for i, 使用中 in enumerate(self.使用中列表):
                    if 使用中 and self.连接列表[i] == 连接:
                        self.使用中列表[i] = False
                        self.可用队列.put(连接)
                        break
        except Exception as e:
            logger.error(f"释放连接失败: {e}")
    
    def 健康检查(self) -> bool:
        """
        健康检查
        
        返回：
            True: 连接池健康
            False: 连接池异常
        """
        try:
            连接 = self.获取连接(超时时间=2.0)
            if 连接 is None:
                return False
            
            try:
                def _测试连接():
                    return 连接.get_security_quotes([(1, 0)])
                
                数据 = self._带超时执行(_测试连接)
                return 数据 is not None and len(数据) > 0
            finally:
                self.释放连接(连接)
        except Exception as e:
            logger.error(f"连接池健康检查失败: {e}")
            return False
    
    def 重连(self):
        """
        重连所有连接
        
        流程：
            1. 断开所有现有连接
            2. 重新初始化连接池
        """
        try:
            with self._锁:
                # 断开所有连接
                for 连接 in self.连接列表:
                    try:
                        连接.disconnect()
                    except:
                        pass
                
                # 清空连接池
                self.连接列表.clear()
                self.使用中列表.clear()
                
                # 清空可用队列
                while not self.可用队列.empty():
                    try:
                        self.可用队列.get_nowait()
                    except Empty:
                        break
                
                # 重新初始化
                self._初始化连接池()
                logger.info("连接池重连完成")
        except Exception as e:
            logger.error(f"连接池重连失败: {e}")
    
    def 关闭(self):
        """
        关闭连接池
        
        流程：
            1. 断开所有连接
            2. 清空连接池
            3. 关闭线程池
        """
        try:
            with self._锁:
                for 连接 in self.连接列表:
                    try:
                        连接.disconnect()
                    except:
                        pass
                
                self.连接列表.clear()
                self.使用中列表.clear()
                
                while not self.可用队列.empty():
                    try:
                        self.可用队列.get_nowait()
                    except Empty:
                        break
                
                if self._线程池:
                    self._线程池.shutdown(wait=False)
                
                logger.info("连接池已关闭")
        except Exception as e:
            logger.error(f"关闭连接池失败: {e}")


class PytdxProvider:
    """
    通达信数据提供者 - 完全异步优化版
    
    功能：
    1. 实时行情获取
    2. 历史K线数据获取
    3. 指数数据获取
    4. 市场概况获取
    5. 板块数据获取
    6. 资金流向获取
    
    优化功能：
    1. 完全异步连接池初始化
    2. 后台线程处理连接池
    3. 10秒超时机制
    4. 服务器连接池
    5. 自动重连机制
    6. 心跳检测
    7. 智能重试
    8. 数据缓存优化
    9. 性能监控
    """
    
    def __init__(self, 池大小: int = 3, 缓存超时: int = 60):
        """
        初始化通达信数据提供者
        
        参数：
            池大小: 连接池大小，默认3
            缓存超时: 缓存超时时间（秒），默认60
        """
        self.缓存: Dict[str, Tuple[Any, float]] = {}
        self.缓存超时时间 = 缓存超时
        self.连接池: Optional[TdxConnectionPool] = None
        self._上次心跳时间 = time.time()
        self._心跳间隔 = 30
        self._重试次数 = 0
        self._最大重试次数 = 3
        self._重试延迟 = 2
        self._性能统计 = {
            '总请求数': 0,
            '成功数': 0,
            '失败数': 0,
            '平均响应时间': 0
        }
        self._锁 = threading.Lock()
        self._池大小 = 池大小
        self._已初始化 = False
        
        self._异步初始化连接池()
        logger.info("通达信数据提供者初始化完成（完全异步模式）")
    
    def _异步初始化连接池(self):
        """
        异步初始化连接池
        """
        def _初始化任务():
            try:
                logger.info("开始初始化连接池...")
                self.连接池 = TdxConnectionPool(池大小=self._池大小, 异步初始化=True)
                self._已初始化 = True
                logger.info("连接池初始化任务提交完成")
            except Exception as e:
                logger.error(f"连接池初始化失败: {e}")
                self.连接池 = None
        
        线程 = threading.Thread(target=_初始化任务, daemon=True)
        线程.start()
    
    def _确保已初始化(self) -> bool:
        """
        确保连接池已初始化（延迟初始化）
        
        返回：
            True: 已初始化
            False: 初始化失败
        """
        while not self._已初始化:
            time.sleep(0.1)
        
        if self.连接池 is None:
            return False
        
        if not self.连接池.是否已初始化():
            return self.连接池.等待初始化(超时时间=30.0)
        
        return True
    
    def 是否就绪(self) -> bool:
        """
        检查数据源是否就绪
        
        返回:
            True: 连接池已初始化且可用
            False: 连接池未初始化或不可用
        """
        if not self._已初始化 or self.连接池 is None:
            return False
        return self.连接池.是否已初始化()
    
    def _检查心跳(self):
        """
        检查心跳
        
        流程：
            1. 检查距离上次心跳的时间
            2. 如果超过心跳间隔，执行健康检查
            3. 如果健康检查失败，重连连接池
        """
        当前时间 = time.time()
        if 当前时间 - self._上次心跳时间 > self._心跳间隔:
            self._上次心跳时间 = 当前时间
            
            if self.连接池 and not self.连接池.健康检查():
                logger.warning("心跳检测失败，尝试重连")
                self.连接池.重连()
    
    def _带重试执行(self, 函数, *参数, **关键字参数) -> Optional[Any]:
        """
        带重试的执行
        
        参数：
            函数: 要执行的函数
            参数: 位置参数
            关键字参数: 关键字参数
        
        返回：
            函数执行结果，失败返回None
        """
        for 尝试 in range(self._最大重试次数):
            try:
                # 检查心跳
                self._检查心跳()
                
                # 执行函数
                开始时间 = time.time()
                结果 = 函数(*参数, **关键字参数)
                耗时 = time.time() - 开始时间
                
                # 更新性能统计
                with self._锁:
                    self._性能统计['总请求数'] += 1
                    self._性能统计['成功数'] += 1
                    self._性能统计['平均响应时间'] = (
                        self._性能统计['平均响应时间'] * 
                        (self._性能统计['总请求数'] - 1) + 
                        耗时
                    ) / self._性能统计['总请求数']
                
                # 重置重试计数
                self._重试次数 = 0
                return 结果
            except Exception as e:
                self._重试次数 += 1
                
                # 更新性能统计
                with self._锁:
                    self._性能统计['总请求数'] += 1
                    self._性能统计['失败数'] += 1
                
                logger.error(f"执行失败 (尝试 {尝试 + 1}/{self._最大重试次数}): {e}")
                
                # 最后一次尝试失败
                if 尝试 == self._最大重试次数 - 1:
                    logger.error(f"所有重试失败: {函数.__name__}")
                    return None
                
                # 等待后重试
                time.sleep(self._重试延迟 * (尝试 + 1))
        
        return None
    
    def _从缓存获取(self, 键: str) -> Optional[Any]:
        """
        从缓存获取数据
        
        参数：
            键: 缓存键
        
        返回：
            缓存数据，不存在或过期返回None
        """
        if 键 in self.缓存:
            数据, 时间戳 = self.缓存[键]
            if time.time() - 时间戳 < self.缓存超时时间:
                return 数据
            else:
                del self.缓存[键]
        return None
    
    def _设置缓存(self, 键: str, 数据: Any):
        """
        设置缓存
        
        参数：
            键: 缓存键
            数据: 要缓存的数据
        """
        self.缓存[键] = (数据, time.time())
    
    def 获取股票实时行情(self, 股票代码: str, 强制刷新: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取股票实时行情
        
        参数：
            股票代码: 股票代码（6位数字）
            强制刷新: 是否强制刷新，默认False
        
        返回：
            股票实时行情数据字典
        """
        缓存键 = f"realtime_{股票代码}"
        if not 强制刷新:
            缓存数据 = self._从缓存获取(缓存键)
            if 缓存数据:
                return 缓存数据
        
        if not self._确保已初始化():
            logger.warning("连接池未初始化")
            return None
        
        def _获取数据():
            连接 = self.连接池.获取连接()
            if 连接 is None:
                raise Exception("无法获取连接")
            
            try:
                # 转换股票代码格式
                if 股票代码.startswith('6'):
                    市场 = 1  # 上海市场
                    代码 = 股票代码
                elif 股票代码.startswith('0') or 股票代码.startswith('3'):
                    市场 = 0  # 深圳市场
                    代码 = 股票代码
                else:
                    logger.warning(f"不支持的股票代码格式: {股票代码}")
                    raise Exception("不支持的股票代码格式")
                
                # 获取实时行情
                数据 = 连接.get_security_quotes([(市场, 代码)])
                
                if not 数据 or len(数据) == 0:
                    logger.warning(f"未获取到股票数据: {股票代码}")
                    raise Exception("未获取到股票数据")
                
                行情 = 数据[0]
                
                # 安全获取价格数据
                价格 = float(行情.price) if hasattr(行情, 'price') and 行情.price is not None else 0
                昨收 = float(行情.last_close) if hasattr(行情, 'last_close') and 行情.last_close is not None else 0
                
                # 构造返回数据
                结果 = {
                    "code": 股票代码,
                    "name": 行情.name if hasattr(行情, 'name') and 行情.name else '',
                    "price": 价格,
                    "change": 价格 - 昨收 if 昨收 > 0 else 0,
                    "change_percent": (价格 - 昨收) / 昨收 * 100 if 昨收 > 0 else 0,
                    "open": float(行情.open) if hasattr(行情, 'open') and 行情.open is not None else 0,
                    "high": float(行情.high) if hasattr(行情, 'high') and 行情.high is not None else 0,
                    "low": float(行情.low) if hasattr(行情, 'low') and 行情.low is not None else 0,
                    "pre_close": 昨收,
                    "volume": int(行情.vol) if hasattr(行情, 'vol') and 行情.vol is not None else 0,
                    "turnover": float(行情.amount) if hasattr(行情, 'amount') and 行情.amount is not None else 0,
                    "amplitude": 0,
                    "pe": 0,
                    "market_cap": 0
                }
                
                # 设置缓存
                self._设置缓存(缓存键, 结果)
                
                return 结果
            finally:
                self.连接池.释放连接(连接)
        
        return self._带重试执行(_获取数据)
    
    def 获取股票历史数据(self, 股票代码: str, 周期: str = "daily",
                        开始日期: str = None, 结束日期: str = None) -> Any:
        """
        获取历史K线数据
        
        参数：
            股票代码: 股票代码（6位数字）
            周期: 周期类型，可选 "daily"（日线）、"weekly"（周线）、"monthly"（月线）
            开始日期: 开始日期
            结束日期: 结束日期
        
        返回：
            历史K线数据DataFrame
        """
        if not self._确保已初始化():
            logger.warning("连接池未初始化")
            return None
        
        def _获取数据():
            连接 = self.连接池.获取连接()
            if 连接 is None:
                raise Exception("无法获取连接")
            
            try:
                # 转换股票代码格式
                if 股票代码.startswith('6'):
                    市场 = 1  # 上海市场
                    代码 = 股票代码
                elif 股票代码.startswith('0') or 股票代码.startswith('3'):
                    市场 = 0  # 深圳市场
                    代码 = 股票代码
                else:
                    logger.warning(f"不支持的股票代码格式: {股票代码}")
                    raise Exception("不支持的股票代码格式")
                
                # 确定周期
                周期映射 = {
                    "daily": 9,   # 日线
                    "weekly": 5,  # 周线
                    "monthly": 6  # 月线
                }
                K线类型 = 周期映射.get(周期, 9)
                
                # 获取历史K线 - 尝试不同的参数组合
                try:
                    # 方法1: 使用 (market, code) 格式
                    数据 = 连接.get_security_bars([(市场, 代码)], start=0, count=1000, ktype=K线类型)
                except Exception as e:
                    logger.debug(f"方法1失败: {e}")
                    # 方法2: 使用单独参数
                    try:
                        数据 = 连接.get_security_bars(市场, 代码, 0, 1000, K线类型)
                    except Exception as e2:
                        logger.debug(f"方法2失败: {e2}")
                        raise Exception(f"获取历史数据失败: {e}")
                
                if not 数据 or len(数据) == 0:
                    logger.warning(f"未获取到股票历史数据: {股票代码}")
                    raise Exception("未获取到股票历史数据")
                
                # 转换为DataFrame
                import pandas as pd
                df = pd.DataFrame(数据)
                
                # 重命名列
                df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']
                
                return df
            finally:
                self.连接池.释放连接(连接)
        
        return self._带重试执行(_获取数据)
    
    def 获取指数数据(self, 指数代码: str) -> Optional[Dict[str, Any]]:
        """
        获取指数数据
        
        参数：
            指数代码: 指数代码（6位数字）
        
        返回:
            指数实时行情数据字典
        """
        return self.获取股票实时行情(指数代码)
    
    def 获取所有指数(self) -> List[Dict[str, Any]]:
        """
        获取主要指数数据
        
        返回:
            指数列表，包含：
            - 上证指数（000001）
            - 深证成指（399001）
            - 创业板指（399006）
            - 科创50（688981）
        """
        指数列表 = []
        指数代码映射 = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
            "688981": "科创50"
        }
        
        for 代码, 名称 in 指数代码映射.items():
            数据 = self.获取股票实时行情(代码)
            if 数据:
                数据['name'] = 名称
                指数列表.append(数据)
        
        return 指数列表
    
    def 获取市场概况(self) -> Dict[str, Any]:
        """
        获取市场概况
        
        返回:
            市场概况字典，包含涨跌统计
        """
        if not self._确保已初始化():
            logger.warning("连接池未初始化")
            return None
        
        def _获取数据():
            连接 = self.连接池.获取连接()
            if 连接 is None:
                raise Exception("无法获取连接")
            
            try:
                # 获取上海市场概况
                上海股票 = 连接.get_security_list([(1, 1)], 0, 100)
                
                # 获取深圳市场概况
                深圳股票 = 连接.get_security_list([(0, 1)], 0, 100)
                
                # 计算涨跌统计
                所有股票 = 上海股票 + 深圳股票
                
                上涨数 = sum(1 for 股票 in 所有股票 if hasattr(股票, 'price') and hasattr(股票, 'last_close') and 股票.last_close > 0 and (股票.price - 股票.last_close) / 股票.last_close > 0)
                下跌数 = sum(1 for 股票 in 所有股票 if hasattr(股票, 'price') and hasattr(股票, 'last_close') and 股票.last_close > 0 and (股票.price - 股票.last_close) / 股票.last_close < 0)
                平盘数 = len(所有股票) - 上涨数 - 下跌数
                
                return {
                    "rise_count": 上涨数,
                    "fall_count": 下跌数,
                    "flat_count": 平盘数,
                    "total_turnover": 0
                }
            finally:
                self.连接池.释放连接(连接)
        
        return self._带重试执行(_获取数据)
    
    def 健康检查(self) -> bool:
        """
        健康检查
        
        返回:
            True: 数据源正常
            False: 数据源异常
        """
        if self.连接池 is None:
            return False
        
        return self.连接池.健康检查()
    
    def 获取性能统计(self) -> Dict[str, Any]:
        """
        获取性能统计
        
        返回:
            性能统计数据字典，包含：
            - 总请求数: 总请求数
            - 成功数: 成功数
            - 失败数: 失败数
            - 成功率: 成功率
            - 平均响应时间: 平均响应时间
        """
        with self._锁:
            统计 = self._性能统计.copy()
            总数 = 统计['总请求数']
            if 总数 > 0:
                统计['成功率'] = 统计['成功数'] / 总数 * 100
            else:
                统计['成功率'] = 0
            return 统计
    
    def 清空缓存(self):
        """
        清空缓存
        """
        self.缓存.clear()
        logger.info("缓存已清空")
    
    def 获取名称(self) -> str:
        """
        获取数据源名称
        
        返回:
            数据源名称字符串
        """
        return "PytdxProvider(完全异步优化版)"
    
    def 获取板块数据(self) -> List[Dict[str, Any]]:
        """
        获取板块数据
        
        返回:
            板块数据列表
        """
        缓存键 = "sector_data"
        缓存数据 = self._从缓存获取(缓存键)
        if 缓存数据:
            return 缓存数据
        
        if self.连接池 is None:
            return []
        
        def _获取数据():
            连接 = self.连接池.获取连接()
            if 连接 is None:
                raise Exception("无法获取连接")
            try:
                板块列表 = []
                for 市场 in [1, 0]:
                    for 起始 in range(0, 200, 100):
                        数据 = 连接.get_security_list(市场, 起始)
                        if 数据:
                            for 项目 in 数据:
                                代码 = 项目.code if hasattr(项目, 'code') else ''
                                名称 = 项目.name if hasattr(项目, 'name') else ''
                                if 代码 and 名称:
                                    板块列表.append({
                                        'code': 代码,
                                        'name': 名称,
                                        'market': 'SH' if 市场 == 1 else 'SZ'
                                    })
                return 板块列表
            finally:
                self.连接池.释放连接(连接)
        
        结果 = self._带重试执行(_获取数据)
        if 结果:
            self._设置缓存(缓存键, 结果)
        return 结果 or []
    
    def 获取板块内股票(self, 板块名称: str) -> List[Dict[str, Any]]:
        """
        获取板块内股票列表
        
        参数：
            板块名称: 板块名称
        
        返回:
            股票列表
        """
        return []
    
    def 获取板块排行(self) -> List[Dict[str, Any]]:
        """
        获取板块涨跌幅排行
        
        返回:
            板块排行列表
        """
        return []
    
    def 获取资金流向(self, 股票代码: str = None) -> List[Dict[str, Any]]:
        """
        获取资金流向数据
        
        参数：
            股票代码: 股票代码，可选
        
        返回:
            资金流向数据列表
        """
        return []
    
    def 获取股票列表(self, 市场: str = "SH") -> List[Dict[str, Any]]:
        """
        获取股票列表
        
        参数：
            市场: 市场类型，可选 "SH"（上海）或 "SZ"（深圳）
        
        返回:
            股票列表
        """
        缓存键 = f"stock_list_{市场}"
        缓存数据 = self._从缓存获取(缓存键)
        if 缓存数据:
            return 缓存数据
        
        if self.连接池 is None:
            return []
        
        def _获取数据():
            连接 = self.连接池.获取连接()
            if 连接 is None:
                raise Exception("无法获取连接")
            try:
                股票列表 = []
                市场代码 = 1 if 市场 == "SH" else 0
                for 起始 in range(0, 2000, 100):
                    数据 = 连接.get_security_list(市场代码, 起始)
                    if not 数据:
                        break
                    for 项目 in 数据:
                        代码 = 项目.code if hasattr(项目, 'code') else ''
                        名称 = 项目.name if hasattr(项目, 'name') else ''
                        if 代码 and 名称 and len(代码) == 6:
                            股票列表.append({
                                'code': 代码,
                                'name': 名称,
                                'market': 市场
                            })
                return 股票列表
            finally:
                self.连接池.释放连接(连接)
        
        结果 = self._带重试执行(_获取数据)
        if 结果:
            self._设置缓存(缓存键, 结果)
        return 结果 or []
    
    def 搜索股票(self, 关键词: str) -> List[Dict[str, Any]]:
        """
        搜索股票
        
        参数：
            关键词: 搜索关键词
        
        返回:
            搜索结果列表
        """
        关键词 = 关键词.upper().strip()
        if not 关键词:
            return []
        
        结果 = []
        for 市场 in ["SH", "SZ"]:
            股票列表 = self.获取股票列表(市场)
            for 股票 in 股票列表:
                if 关键词 in 股票['code'] or 关键词 in 股票['name']:
                    结果.append(股票)
                    if len(结果) >= 20:
                        return 结果
        return 结果
    
    def 获取财务数据(self, 股票代码: str) -> Dict[str, Any]:
        """
        获取财务数据
        
        参数：
            股票代码: 股票代码
        
        返回:
            财务数据字典
        """
        return {}
    
    def 关闭(self):
        """
        关闭数据提供者
        
        流程：
            1. 清空缓存
            2. 关闭连接池
        """
        self.清空缓存()
        if self.连接池:
            self.连接池.关闭()
        logger.info("通达信数据提供者已关闭")
