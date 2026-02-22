from typing import Dict, List, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QDateTime
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)


class NotificationManager(QObject):
    """通知管理器 - 管理桌面通知和通知历史"""
    
    notification_sent = pyqtSignal(str, str, str)
    notification_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._history: List[Dict[str, Any]] = []
        self._max_history = 100
        self._enabled = True
        self._sound_enabled = True
        self._desktop_enabled = True
        self._notification_types = ["price_alert", "news", "system"]
        self._tray_icon: Optional[QSystemTrayIcon] = None
        
        self._setup_tray_icon()
    
    def _setup_tray_icon(self):
        """设置系统托盘图标"""
        try:
            app = QApplication.instance()
            if app and not hasattr(app, '_tray_icon'):
                icon = QIcon()
                self._tray_icon = QSystemTrayIcon(icon)
                self._tray_icon.show()
                app._tray_icon = self._tray_icon
                logger.info("系统托盘图标已设置")
        except Exception as e:
            logger.error(f"设置系统托盘图标失败: {e}")
    
    def notify(self, title: str, message: str, 
              notification_type: str = "info", 
              duration: int = 3000) -> bool:
        """
        发送通知
        
        Args:
            title: 通知标题
            message: 通知内容
            notification_type: 通知类型
            duration: 显示时长（毫秒）
            
        Returns:
            是否发送成功
        """
        if not self._enabled:
            return False
        
        if notification_type not in self._notification_types:
            logger.warning(f"未知通知类型: {notification_type}")
            return False
        
        try:
            notification_id = self._generate_id()
            
            if self._desktop_enabled and self._tray_icon:
                self._tray_icon.showMessage(title, message, 
                                         self._get_icon_type(notification_type), 
                                         duration)
            
            if self._sound_enabled:
                self._play_sound(notification_type)
            
            self._add_to_history(notification_id, title, message, notification_type)
            self.notification_sent.emit(notification_id, title, message)
            
            logger.info(f"发送通知: {title} - {message}")
            return True
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
            return False
    
    def _get_icon_type(self, notification_type: str) -> QSystemTrayIcon.MessageIcon:
        """
        获取通知图标类型
        
        Args:
            notification_type: 通知类型
            
        Returns:
            图标类型
        """
        icon_map = {
            "info": QSystemTrayIcon.Information,
            "warning": QSystemTrayIcon.Warning,
            "error": QSystemTrayIcon.Critical,
            "price_alert": QSystemTrayIcon.Information,
            "news": QSystemTrayIcon.Information,
            "system": QSystemTrayIcon.Information
        }
        return icon_map.get(notification_type, QSystemTrayIcon.Information)
    
    def _play_sound(self, notification_type: str):
        """
        播放通知声音
        
        Args:
            notification_type: 通知类型
        """
        try:
            pass
        except Exception as e:
            logger.error(f"播放声音失败: {e}")
    
    def _generate_id(self) -> str:
        """
        生成通知ID
        
        Returns:
            通知ID
        """
        return f"notif_{QDateTime.currentMSecsSinceEpoch()}"
    
    def _add_to_history(self, notification_id: str, title: str, 
                       message: str, notification_type: str):
        """
        添加到历史记录
        
        Args:
            notification_id: 通知ID
            title: 标题
            message: 内容
            notification_type: 类型
        """
        notification = {
            "id": notification_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": QDateTime.currentDateTime(),
            "read": False
        }
        
        self._history.append(notification)
        
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def get_history(self, notification_type: str = None, 
                    unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        获取通知历史
        
        Args:
            notification_type: 通知类型（可选）
            unread_only: 是否只获取未读
            
        Returns:
            通知历史列表
        """
        history = self._history.copy()
        
        if notification_type:
            history = [n for n in history if n["type"] == notification_type]
        
        if unread_only:
            history = [n for n in history if not n["read"]]
        
        return history
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        标记为已读
        
        Args:
            notification_id: 通知ID
            
        Returns:
            是否标记成功
        """
        for notification in self._history:
            if notification["id"] == notification_id:
                notification["read"] = True
                logger.info(f"标记为已读: {notification_id}")
                return True
        return False
    
    def mark_all_as_read(self):
        """标记所有通知为已读"""
        for notification in self._history:
            notification["read"] = True
        logger.info("所有通知已标记为已读")
    
    def clear_history(self, notification_type: str = None):
        """
        清空历史记录
        
        Args:
            notification_type: 通知类型（可选）
        """
        if notification_type:
            self._history = [n for n in self._history if n["type"] != notification_type]
            logger.info(f"清空通知历史: {notification_type}")
        else:
            self._history.clear()
            logger.info("清空所有通知历史")
    
    def delete_notification(self, notification_id: str) -> bool:
        """
        删除通知
        
        Args:
            notification_id: 通知ID
            
        Returns:
            是否删除成功
        """
        for i, notification in enumerate(self._history):
            if notification["id"] == notification_id:
                self._history.pop(i)
                logger.info(f"删除通知: {notification_id}")
                return True
        return False
    
    def get_unread_count(self, notification_type: str = None) -> int:
        """
        获取未读通知数量
        
        Args:
            notification_type: 通知类型（可选）
            
        Returns:
            未读数量
        """
        history = self._history
        
        if notification_type:
            history = [n for n in history if n["type"] == notification_type]
        
        return sum(1 for n in history if not n["read"])
    
    def set_enabled(self, enabled: bool):
        """
        设置是否启用通知
        
        Args:
            enabled: 是否启用
        """
        self._enabled = enabled
        logger.info(f"通知已{'启用' if enabled else '禁用'}")
    
    def set_sound_enabled(self, enabled: bool):
        """
        设置是否启用声音
        
        Args:
            enabled: 是否启用
        """
        self._sound_enabled = enabled
        logger.info(f"通知声音已{'启用' if enabled else '禁用'}")
    
    def set_desktop_enabled(self, enabled: bool):
        """
        设置是否启用桌面通知
        
        Args:
            enabled: 是否启用
        """
        self._desktop_enabled = enabled
        logger.info(f"桌面通知已{'启用' if enabled else '禁用'}")
    
    def set_notification_types(self, types: List[str]):
        """
        设置通知类型
        
        Args:
            types: 通知类型列表
        """
        self._notification_types = types
        logger.info(f"通知类型已更新: {types}")
    
    def is_enabled(self) -> bool:
        """
        是否启用通知
        
        Returns:
            是否启用
        """
        return self._enabled
    
    def get_settings(self) -> Dict[str, Any]:
        """
        获取通知设置
        
        Returns:
            设置字典
        """
        return {
            "enabled": self._enabled,
            "sound_enabled": self._sound_enabled,
            "desktop_enabled": self._desktop_enabled,
            "notification_types": self._notification_types.copy(),
            "unread_count": self.get_unread_count(),
            "total_count": len(self._history)
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """
        更新通知设置
        
        Args:
            settings: 设置字典
        """
        if "enabled" in settings:
            self.set_enabled(settings["enabled"])
        
        if "sound_enabled" in settings:
            self.set_sound_enabled(settings["sound_enabled"])
        
        if "desktop_enabled" in settings:
            self.set_desktop_enabled(settings["desktop_enabled"])
        
        if "notification_types" in settings:
            self.set_notification_types(settings["notification_types"])
        
        logger.info("通知设置已更新")
