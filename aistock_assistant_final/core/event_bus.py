from typing import Dict, List, Callable, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QDateTime, Qt
from concurrent.futures import ThreadPoolExecutor, Future
import logging
import threading

logger = logging.getLogger(__name__)


class EventBus(QObject):
    """事件总线 - 实现发布/订阅模式，支持页面间通信和异步事件处理"""

    event_emitted = pyqtSignal(str, object)

    def __init__(self, max_workers: int = 10):
        """
        初始化事件总线

        Args:
            max_workers: 线程池最大工作线程数
        """
        super().__init__()
        self._订阅者: Dict[str, List[Callable]] = {}
        self._事件历史: List[Dict[str, Any]] = []
        self._最大历史长度 = 100
        self._线程池: Optional[ThreadPoolExecutor] = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="EventBusThread"
        )
        self._锁 = threading.Lock()
        self._运行中 = True

    def 订阅(self, 事件类型: str, 处理函数: Callable) -> bool:
        """
        订阅事件

        Args:
            事件类型: 事件类型
            处理函数: 事件处理函数

        Returns:
            是否订阅成功
        """
        with self._锁:
            if 事件类型 not in self._订阅者:
                self._订阅者[事件类型] = []

            if 处理函数 not in self._订阅者[事件类型]:
                self._订阅者[事件类型].append(处理函数)
                logger.info(f"订阅事件: {事件类型}")
                return True
            return False

    def 取消订阅(self, 事件类型: str, 处理函数: Callable) -> bool:
        """
        取消订阅事件

        Args:
            事件类型: 事件类型
            处理函数: 事件处理函数

        Returns:
            是否取消成功
        """
        with self._锁:
            if 事件类型 in self._订阅者 and 处理函数 in self._订阅者[事件类型]:
                self._订阅者[事件类型].remove(处理函数)
                logger.info(f"取消订阅事件: {事件类型}")
                return True
            return False

    def 发布(self, 事件类型: str, 数据: Any = None, 异步: bool = True) -> bool:
        """
        发布事件

        Args:
            事件类型: 事件类型
            数据: 事件数据
            异步: 是否异步处理事件，默认为True

        Returns:
            是否发布成功
        """
        try:
            # 复制订阅者列表，避免在处理过程中修改
            处理函数列表 = []
            with self._锁:
                if 事件类型 in self._订阅者:
                    处理函数列表 = self._订阅者[事件类型].copy()

            if 异步 and self._线程池:
                # 异步处理
                for 处理函数 in 处理函数列表:
                    self._线程池.submit(
                        self._安全执行处理函数,
                        处理函数,
                        数据,
                        事件类型
                    )
            else:
                # 同步处理
                for 处理函数 in 处理函数列表:
                    self._安全执行处理函数(处理函数, 数据, 事件类型)

            self._安全发射信号(self.event_emitted, 事件类型, 数据)

            self._记录事件(事件类型, 数据)
            return True
        except Exception as e:
            logger.error(f"发布事件失败 {事件类型}: {e}")
            return False

    def _安全执行处理函数(self, 处理函数: Callable, 数据: Any, 事件类型: str):
        """
        安全执行处理函数，捕获异常

        Args:
            处理函数: 事件处理函数
            数据: 事件数据
            事件类型: 事件类型
        """
        try:
            处理函数(数据)
        except Exception as e:
            logger.error(f"事件处理器执行失败 {事件类型}: {e}")

    def _记录事件(self, 事件类型: str, 数据: Any):
        """
        记录事件历史

        Args:
            事件类型: 事件类型
            数据: 事件数据
        """
        with self._锁:
            事件记录 = {
                "type": 事件类型,
                "data": 数据,
                "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
            }

            self._事件历史.append(事件记录)

            if len(self._事件历史) > self._最大历史长度:
                self._事件历史.pop(0)

    def 获取事件历史(self, 事件类型: str = None) -> List[Dict[str, Any]]:
        """
        获取事件历史

        Args:
            事件类型: 事件类型（可选）

        Returns:
            事件历史列表
        """
        with self._锁:
            if 事件类型:
                return [e for e in self._事件历史 if e["type"] == 事件类型]
            return self._事件历史.copy()

    def 清空历史(self):
        """清空事件历史"""
        with self._锁:
            self._事件历史.clear()
            logger.info("事件历史已清空")

    def 获取订阅者数量(self, 事件类型: str = None) -> Dict[str, int]:
        """
        获取订阅者数量

        Args:
            事件类型: 事件类型（可选）

        Returns:
            订阅者数量字典
        """
        with self._锁:
            if 事件类型:
                return {事件类型: len(self._订阅者.get(事件类型, []))}
            return {k: len(v) for k, v in self._订阅者.items()}

    def 关闭(self):
        """关闭事件总线，释放线程池资源"""
        self._运行中 = False
        if self._线程池:
            self._线程池.shutdown(wait=True)
            self._线程池 = None
            logger.info("事件总线已关闭，线程池资源已释放")

    def _安全发射信号(self, 信号, *参数):
        """
        安全地发射信号

        Args:
            信号: 信号对象
            *参数: 信号参数
        """
        try:
            信号.emit(*参数)
        except Exception as e:
            logger.error(f"发射信号失败: {e}")

    # 保留英文方法名以保持向后兼容
    subscribe = 订阅
    unsubscribe = 取消订阅
    publish = 发布
    get_event_history = 获取事件历史
    clear_history = 清空历史
    get_subscribers = 获取订阅者数量
