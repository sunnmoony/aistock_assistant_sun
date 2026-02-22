from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject
import logging

logger = logging.getLogger(__name__)


class NavigationManager(QObject):
    """导航管理器 - 管理页面导航和历史记录"""
    
    page_changed = pyqtSignal(str, object)
    navigation_back = pyqtSignal()
    navigation_forward = pyqtSignal()
    
    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.page_map: Dict[str, int] = {}
        self.history: List[Dict[str, Any]] = []
        self.current_index = -1
        self.max_history = 50
        self.page_contexts: Dict[str, Any] = {}
        
        self._initialize_page_map()
    
    def _initialize_page_map(self):
        """初始化页面映射"""
        default_pages = [
            "dashboard",
            "market",
            "ai_assistant",
            "knowledge",
            "settings"
        ]
        
        for i, page_name in enumerate(default_pages):
            if i < self.stacked_widget.count():
                self.page_map[page_name] = i
    
    def register_page(self, page_name: str, index: int):
        """
        注册页面
        
        Args:
            page_name: 页面名称
            index: 页面索引
        """
        self.page_map[page_name] = index
        logger.info(f"注册页面: {page_name} -> {index}")
    
    def navigate_to(self, page_name: str, context: Any = None) -> bool:
        """
        导航到指定页面
        
        Args:
            page_name: 页面名称
            context: 页面上下文数据
            
        Returns:
            是否导航成功
        """
        if page_name not in self.page_map:
            logger.error(f"页面不存在: {page_name}")
            return False
        
        try:
            index = self.page_map[page_name]
            
            if self.stacked_widget.currentIndex() != index:
                self._add_to_history(page_name, context)
            
            self.stacked_widget.setCurrentIndex(index)
            
            if context is not None:
                self.page_contexts[page_name] = context
            
            self.page_changed.emit(page_name, context)
            logger.info(f"导航到页面: {page_name}")
            return True
        except Exception as e:
            logger.error(f"导航失败 {page_name}: {e}")
            return False
    
    def _add_to_history(self, page_name: str, context: Any = None):
        """
        添加到历史记录
        
        Args:
            page_name: 页面名称
            context: 上下文数据
        """
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        self.history.append({
            "page": page_name,
            "context": context
        })
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1
    
    def back(self) -> bool:
        """
        返回上一页
        
        Returns:
            是否返回成功
        """
        if self.current_index > 0:
            self.current_index -= 1
            history_item = self.history[self.current_index]
            self.stacked_widget.setCurrentIndex(self.page_map[history_item["page"]])
            self.page_changed.emit(history_item["page"], history_item["context"])
            self.navigation_back.emit()
            logger.info(f"返回上一页: {history_item['page']}")
            return True
        return False
    
    def forward(self) -> bool:
        """
        前进到下一页
        
        Returns:
            是否前进成功
        """
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            history_item = self.history[self.current_index]
            self.stacked_widget.setCurrentIndex(self.page_map[history_item["page"]])
            self.page_changed.emit(history_item["page"], history_item["context"])
            self.navigation_forward.emit()
            logger.info(f"前进到下一页: {history_item['page']}")
            return True
        return False
    
    def get_current_page(self) -> Optional[str]:
        """
        获取当前页面名称
        
        Returns:
            当前页面名称
        """
        current_index = self.stacked_widget.currentIndex()
        for page_name, index in self.page_map.items():
            if index == current_index:
                return page_name
        return None
    
    def get_page_context(self, page_name: str) -> Any:
        """
        获取页面上下文
        
        Args:
            page_name: 页面名称
            
        Returns:
            页面上下文数据
        """
        return self.page_contexts.get(page_name)
    
    def set_page_context(self, page_name: str, context: Any):
        """
        设置页面上下文
        
        Args:
            page_name: 页面名称
            context: 上下文数据
        """
        self.page_contexts[page_name] = context
    
    def can_go_back(self) -> bool:
        """
        是否可以返回
        
        Returns:
            是否可以返回
        """
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """
        是否可以前进
        
        Returns:
            是否可以前进
        """
        return self.current_index < len(self.history) - 1
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        获取导航历史
        
        Returns:
            导航历史列表
        """
        return self.history.copy()
    
    def clear_history(self):
        """清空导航历史"""
        self.history.clear()
        self.current_index = -1
        logger.info("导航历史已清空")
    
    def get_page_name_by_index(self, index: int) -> Optional[str]:
        """
        根据索引获取页面名称
        
        Args:
            index: 页面索引
            
        Returns:
            页面名称
        """
        for page_name, page_index in self.page_map.items():
            if page_index == index:
                return page_name
        return None
