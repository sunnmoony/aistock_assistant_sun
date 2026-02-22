# -*- coding: utf-8 -*-
"""
A股智能助手 - 主程序入口
"""
import sys
import os
import logging
import argparse
import gc
from threading import Thread

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

轻量模式标志 = os.environ.get('AISTOCK_LITE_MODE', '0') == '1'

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ui.main_window import MainWindow
from core import DataManager, AIEngine, KnowledgeBase, ConfigManager, EventBus, NotificationManager

logging.basicConfig(
    level=logging.WARNING if 轻量模式标志 else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
日志记录器 = logging.getLogger(__name__)


class StartupSignals(QObject):
    """
    启动过程中使用的信号类
    用于在后台线程和主线程之间传递初始化进度和状态
    """
    progress_updated = pyqtSignal(str, int)
    completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)


class StartupSplashScreen(QSplashScreen):
    """
    启动进度显示窗口
    显示应用程序启动过程中的进度信息
    """
    
    def __init__(self):
        """初始化启动进度窗口"""
        super().__init__()
        self.设置界面()
        self.设置样式()
    
    def 设置界面(self):
        """设置界面布局"""
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        
        主布局 = QVBoxLayout()
        
        self.标题标签 = QLabel("A股智能助手")
        self.标题标签.setAlignment(Qt.AlignCenter)
        self.标题标签.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px 0;")
        主布局.addWidget(self.标题标签)
        
        self.状态标签 = QLabel("正在初始化...")
        self.状态标签.setAlignment(Qt.AlignCenter)
        主布局.addWidget(self.状态标签)
        
        self.进度标签 = QLabel("")
        self.进度标签.setAlignment(Qt.AlignCenter)
        主布局.addWidget(self.进度标签)
        
        容器 = QWidget()
        容器.setLayout(主布局)
        
        self.setLayout(主布局)
    
    def 设置样式(self):
        """设置窗口样式"""
        self.setStyleSheet("""
            QSplashScreen {
                background-color: #f8f9fa;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
        """)
    
    def 更新进度(self, 状态信息, 百分比):
        """
        更新进度显示
        
        Args:
            状态信息: 当前状态描述
            百分比: 完成百分比 (0-100)
        """
        self.状态标签.setText(状态信息)
        if 百分比 > 0:
            self.进度标签.setText(f"进度: {百分比}%")
        self.showMessage("", Qt.AlignBottom | Qt.AlignHCenter)


class AutoTaskScheduler:
    """
    自动化任务调度器
    负责定时刷新市场数据和自选股数据
    """
    
    def __init__(self, 数据管理器, 轻量模式=False):
        """
        初始化调度器
        
        Args:
            数据管理器: 数据管理器实例
            轻量模式: 是否启用轻量模式
        """
        self.调度器 = BackgroundScheduler()
        self.数据管理器 = 数据管理器
        self.轻量模式 = 轻量模式
        self._设置任务()
    
    def _设置任务(self):
        """设置定时任务"""
        try:
            时间间隔 = 5 if self.轻量模式 else 1
            self.调度器.add_job(
                self.刷新市场数据,
                trigger=IntervalTrigger(minutes=时间间隔),
                id='refresh_market_data',
                name='刷新市场数据',
                replace_existing=True
            )
            自选股间隔 = 10 if self.轻量模式 else 5
            self.调度器.add_job(
                self.刷新自选股,
                trigger=IntervalTrigger(minutes=自选股间隔),
                id='refresh_watchlist',
                name='刷新自选股',
                replace_existing=True
            )
            日志记录器.info(f"定时任务已设置 (模式: {'轻量' if self.轻量模式 else '标准'})")
        except Exception as 异常:
            日志记录器.error(f"设置定时任务失败: {异常}")
    
    def 刷新市场数据(self):
        """刷新市场数据"""
        try:
            self.数据管理器.refresh_market_data()
        except Exception as 异常:
            日志记录器.error(f"刷新市场数据失败: {异常}")
    
    def 刷新自选股(self):
        """刷新自选股数据"""
        try:
            self.数据管理器.refresh_watchlist()
        except Exception as 异常:
            日志记录器.error(f"刷新自选股失败: {异常}")
    
    def 启动(self):
        """启动调度器"""
        try:
            self.调度器.start()
            日志记录器.info("自动化调度器已启动")
        except Exception as 异常:
            日志记录器.error(f"启动调度器失败: {异常}")
    
    def 关闭(self):
        """关闭调度器"""
        try:
            self.调度器.shutdown()
            日志记录器.info("自动化调度器已关闭")
        except Exception as 异常:
            日志记录器.error(f"关闭调度器失败: {异常}")


def 验证配置(配置管理器, 轻量模式=False):
    """
    验证配置完整性
    
    Args:
        配置管理器: 配置管理器实例
        轻量模式: 是否启用轻量模式
    
    Returns:
        问题列表: 配置问题列表
    """
    问题列表 = []
    
    if not 轻量模式:
        AI配置 = 配置管理器.config.get('ai', {})
        if not AI配置.get('api_key'):
            问题列表.append("AI功能需要配置API密钥（可选）")
    
    数据目录 = 配置管理器.config.get('advanced', {}).get('data_path', './data')
    if not os.path.exists(数据目录):
        try:
            os.makedirs(数据目录, exist_ok=True)
            日志记录器.info(f"创建数据目录: {数据目录}")
        except Exception as 异常:
            问题列表.append(f"无法创建数据目录: {异常}")
    
    return 问题列表


def 后台初始化核心管理器(信号对象, 轻量模式=False):
    """
    在后台线程中初始化核心管理器
    
    Args:
        信号对象: 用于传递进度和状态的信号对象
        轻量模式: 是否启用轻量模式
    """
    try:
        模式描述 = "轻量模式" if 轻量模式 else "标准模式"
        日志记录器.info(f"正在初始化核心管理器 ({模式描述})...")
        
        信号对象.progress_updated.emit("加载配置管理器...", 10)
        配置管理器 = ConfigManager()
        
        信号对象.progress_updated.emit("初始化事件总线...", 20)
        事件总线 = EventBus()
        
        信号对象.progress_updated.emit("初始化通知管理器...", 30)
        通知管理器 = NotificationManager()
        
        信号对象.progress_updated.emit("初始化数据管理器...", 40)
        数据管理器 = DataManager(lite_mode=轻量模式)
        
        信号对象.progress_updated.emit("初始化AI引擎...", 60)
        AI引擎 = None
        if not 轻量模式:
            AI配置 = 配置管理器.config.get('ai', {})
            if AI配置.get('api_key'):
                AI引擎 = AIEngine(
                    api_key=AI配置.get('api_key', ''),
                    api_url=AI配置.get('api_url', ''),
                    provider_type='siliconflow'
                )
        
        信号对象.progress_updated.emit("初始化知识库...", 80)
        知识库 = KnowledgeBase() if not 轻量模式 else None
        
        信号对象.progress_updated.emit("初始化完成!", 100)
        日志记录器.info(f"核心管理器初始化完成 ({模式描述})")
        
        核心管理器集合 = {
            'config_manager': 配置管理器,
            'event_bus': 事件总线,
            'notification_manager': 通知管理器,
            'data_manager': 数据管理器,
            'ai_engine': AI引擎,
            'knowledge_base': 知识库
        }
        
        信号对象.completed.emit(核心管理器集合)
        
    except Exception as 异常:
        日志记录器.error(f"初始化核心管理器失败: {异常}", exc_info=True)
        信号对象.error_occurred.emit(str(异常))


def 优化内存():
    """内存优化 - 执行垃圾回收并调整GC阈值"""
    gc.collect()
    if hasattr(gc, 'set_threshold'):
        gc.set_threshold(700, 10, 10)


def 主函数():
    """
    主函数 - 应用程序入口
    负责初始化所有组件并启动应用程序
    采用完全异步初始化，避免主线程阻塞
    """
    参数解析器 = argparse.ArgumentParser(description='A股智能助手')
    参数解析器.add_argument('--lite', action='store_true', help='轻量模式启动（适合低配置电脑）')
    参数 = 参数解析器.parse_args()
    
    轻量模式 = 参数.lite or 轻量模式标志
    
    if 轻量模式:
        优化内存()
        日志记录器.info("已启用内存优化")
    
    try:
        日志记录器.info("=" * 50)
        日志记录器.info(f"A股智能助手 v2.0 启动中... ({'轻量模式' if 轻量模式 else '标准模式'})")
        日志记录器.info("=" * 50)
        
        应用程序 = QApplication(sys.argv)
        应用程序.setApplicationName("A股智能助手")
        应用程序.setOrganizationName("AIStockAssistant")
        
        启动窗口 = StartupSplashScreen()
        启动窗口.show()
        应用程序.processEvents()
        
        try:
            if os.path.exists("ui/styles/style.qss") and not 轻量模式:
                with open("ui/styles/style.qss", "r", encoding="utf-8") as f:
                    应用程序.setStyleSheet(f.read())
                日志记录器.info("样式表已加载")
        except Exception as 异常:
            日志记录器.warning(f"加载样式表失败: {异常}")
        
        启动信号 = StartupSignals()
        调度器引用 = [None]  # 用于存储调度器引用
        
        def on_progress_updated(状态信息, 百分比):
            """处理进度更新信号"""
            启动窗口.更新进度(状态信息, 百分比)
            应用程序.processEvents()
        
        def on_initialization_complete(管理器集合):
            """处理初始化完成信号 - 在主线程中创建主窗口"""
            try:
                配置管理器 = 管理器集合['config_manager']
                问题列表 = 验证配置(配置管理器, 轻量模式)
                if 问题列表 and not 轻量模式:
                    错误消息 = "提示：\n\n" + "\n".join(f"• {问题}" for 问题 in 问题列表)
                    QMessageBox.information(None, "配置提示", 错误消息)
                
                数据管理器 = 管理器集合['data_manager']
                
                # 在主线程中启动数据管理器的延迟初始化
                QTimer.singleShot(100, 数据管理器._delayed_init_data_source)
                
                调度器 = AutoTaskScheduler(数据管理器, 轻量模式=轻量模式)
                调度器.启动()
                调度器引用[0] = 调度器
                
                日志记录器.info("正在创建主窗口...")
                主窗口 = MainWindow(
                    数据管理器=数据管理器,
                    调度器=调度器,
                    轻量模式=轻量模式
                )
                
                启动窗口.更新进度("显示主窗口...", 100)
                应用程序.processEvents()
                
                # 关闭启动窗口并显示主窗口
                QTimer.singleShot(100, 启动窗口.close)
                QTimer.singleShot(150, 主窗口.show)
                
                日志记录器.info("应用程序已启动")
                日志记录器.info("=" * 50)
                
            except Exception as 异常:
                日志记录器.error(f"创建主窗口失败: {异常}", exc_info=True)
                QMessageBox.critical(None, "启动错误", f"创建主窗口失败:\n\n{str(异常)}")
                sys.exit(1)
        
        def on_initialization_error(错误信息):
            """处理初始化错误信号"""
            日志记录器.error(f"后台初始化失败: {错误信息}")
            QMessageBox.critical(None, "初始化错误", f"后台初始化失败:\n\n{错误信息}")
            sys.exit(1)
        
        启动信号.progress_updated.connect(on_progress_updated)
        启动信号.completed.connect(on_initialization_complete)
        启动信号.error_occurred.connect(on_initialization_error)
        
        # 启动后台线程（不再 join，采用完全异步）
        初始化线程 = Thread(
            target=后台初始化核心管理器,
            args=(启动信号, 轻量模式),
            daemon=True
        )
        初始化线程.start()
        
        # 直接进入事件循环
        退出码 = 应用程序.exec_()
        
        # 清理
        if 调度器引用[0]:
            调度器引用[0].关闭()
        
        日志记录器.info(f"应用程序退出，退出码: {退出码}")
        优化内存()
        
        return 退出码
        
    except KeyboardInterrupt:
        日志记录器.info("用户中断，正在关闭应用程序...")
        return 0
    except Exception as 异常:
        日志记录器.error(f"应用程序启动失败: {异常}", exc_info=True)
        
        try:
            应用程序 = QApplication.instance()
            if 应用程序:
                QMessageBox.critical(
                    None,
                    "启动错误",
                    f"应用程序启动失败:\n\n{str(异常)}\n\n请检查日志文件获取详细信息。"
                )
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(主函数())
