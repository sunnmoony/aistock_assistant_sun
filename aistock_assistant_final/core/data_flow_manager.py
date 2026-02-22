from typing import Dict, List, Callable, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataFlowManager(QObject):
    """数据流管理器 - 实现发布/订阅模式，支持数据缓存和更新"""
    
    data_updated = pyqtSignal(str, object)
    data_published = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._data_cache: Dict[str, Dict[str, Any]] = {}
        self._data_sources: Dict[str, Callable] = {}
        self._update_intervals: Dict[str, int] = {}
        self._timers: Dict[str, QTimer] = {}
        self._default_cache_ttl = 300
    
    def register_data_source(self, data_type: str, source_func: Callable, 
                           update_interval: int = 0):
        """
        注册数据源
        
        Args:
            data_type: 数据类型
            source_func: 数据获取函数
            update_interval: 更新间隔（秒），0表示不自动更新
        """
        self._data_sources[data_type] = source_func
        self._update_intervals[data_type] = update_interval
        
        if update_interval > 0:
            self._start_auto_update(data_type, update_interval)
        
        logger.info(f"注册数据源: {data_type}, 更新间隔: {update_interval}秒")
    
    def _start_auto_update(self, data_type: str, interval: int):
        """
        启动自动更新
        
        Args:
            data_type: 数据类型
            interval: 更新间隔
        """
        if data_type in self._timers:
            self._timers[data_type].stop()
        
        timer = QTimer()
        timer.timeout.connect(lambda: self._update_data(data_type))
        timer.start(interval * 1000)
        self._timers[data_type] = timer
    
    def _update_data(self, data_type: str):
        """
        更新数据
        
        Args:
            data_type: 数据类型
        """
        if data_type not in self._data_sources:
            return
        
        try:
            data = self._data_sources[data_type]()
            self.publish(data_type, data, force_update=True)
        except Exception as e:
            logger.error(f"更新数据失败 {data_type}: {e}")
    
    def subscribe(self, data_type: str, handler: Callable) -> bool:
        """
        订阅数据更新
        
        Args:
            data_type: 数据类型
            handler: 数据处理函数
            
        Returns:
            是否订阅成功
        """
        if data_type not in self._subscribers:
            self._subscribers[data_type] = []
        
        if handler not in self._subscribers[data_type]:
            self._subscribers[data_type].append(handler)
            logger.info(f"订阅数据: {data_type}")
            
            if data_type in self._data_cache:
                handler(self._data_cache[data_type]["data"])
            
            return True
        return False
    
    def unsubscribe(self, data_type: str, handler: Callable) -> bool:
        """
        取消订阅数据更新
        
        Args:
            data_type: 数据类型
            handler: 数据处理函数
            
        Returns:
            是否取消成功
        """
        if data_type in self._subscribers and handler in self._subscribers[data_type]:
            self._subscribers[data_type].remove(handler)
            logger.info(f"取消订阅数据: {data_type}")
            return True
        return False
    
    def publish(self, data_type: str, data: Any, force_update: bool = False) -> bool:
        """
        发布数据
        
        Args:
            data_type: 数据类型
            data: 数据内容
            force_update: 是否强制更新
            
        Returns:
            是否发布成功
        """
        try:
            self._cache_data(data_type, data)
            
            if data_type in self._subscribers:
                for handler in self._subscribers[data_type]:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"数据处理器执行失败 {data_type}: {e}")
            
            self.data_published.emit(data_type, data)
            self.data_updated.emit(data_type, data)
            
            logger.info(f"发布数据: {data_type}")
            return True
        except Exception as e:
            logger.error(f"发布数据失败 {data_type}: {e}")
            return False
    
    def _cache_data(self, data_type: str, data: Any):
        """
        缓存数据
        
        Args:
            data_type: 数据类型
            data: 数据内容
        """
        self._data_cache[data_type] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def get_cached_data(self, data_type: str, max_age: int = None) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            data_type: 数据类型
            max_age: 最大缓存时间（秒），None表示不限制
            
        Returns:
            缓存的数据
        """
        if data_type not in self._data_cache:
            return None
        
        cache_entry = self._data_cache[data_type]
        
        if max_age is not None:
            age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
            if age > max_age:
                return None
        
        return cache_entry["data"]
    
    def request_data(self, data_type: str, use_cache: bool = True, 
                    max_age: int = None) -> Optional[Any]:
        """
        请求数据
        
        Args:
            data_type: 数据类型
            use_cache: 是否使用缓存
            max_age: 最大缓存时间
            
        Returns:
            数据内容
        """
        if use_cache:
            cached_data = self.get_cached_data(data_type, max_age)
            if cached_data is not None:
                return cached_data
        
        if data_type in self._data_sources:
            try:
                data = self._data_sources[data_type]()
                self.publish(data_type, data)
                return data
            except Exception as e:
                logger.error(f"请求数据失败 {data_type}: {e}")
        
        return None
    
    def clear_cache(self, data_type: str = None):
        """
        清空缓存
        
        Args:
            data_type: 数据类型，None表示清空所有
        """
        if data_type:
            if data_type in self._data_cache:
                del self._data_cache[data_type]
                logger.info(f"清空缓存: {data_type}")
        else:
            self._data_cache.clear()
            logger.info("清空所有缓存")
    
    def get_cache_info(self) -> Dict[str, Dict[str, Any]]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        cache_info = {}
        for data_type, cache_entry in self._data_cache.items():
            age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
            cache_info[data_type] = {
                "timestamp": cache_entry["timestamp"].isoformat(),
                "age_seconds": age,
                "age_formatted": self._format_age(age)
            }
        return cache_info
    
    def _format_age(self, seconds: float) -> str:
        """
        格式化时间差
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            return f"{seconds/60:.1f}分钟"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}小时"
        else:
            return f"{seconds/86400:.1f}天"
    
    def stop_auto_updates(self):
        """停止所有自动更新"""
        for timer in self._timers.values():
            timer.stop()
        self._timers.clear()
        logger.info("停止所有自动更新")
    
    def get_subscribers(self, data_type: str = None) -> Dict[str, int]:
        """
        获取订阅者数量
        
        Args:
            data_type: 数据类型（可选）
            
        Returns:
            订阅者数量字典
        """
        if data_type:
            return {data_type: len(self._subscribers.get(data_type, []))}
        return {k: len(v) for k, v in self._subscribers.items()}
    
    def get_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        获取数据源信息
        
        Returns:
            数据源信息字典
        """
        sources_info = {}
        for data_type, source_func in self._data_sources.items():
            sources_info[data_type] = {
                "update_interval": self._update_intervals.get(data_type, 0),
                "auto_update": data_type in self._timers,
                "cached": data_type in self._data_cache
            }
        return sources_info
