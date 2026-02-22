# -*- coding: utf-8 -*-
"""
===================================
A股智能助手 - 主窗口模块
===================================

功能：
1. 创建主窗口和UI布局
2. 管理各个功能页面（仪表盘、行情、AI助手、知识库、设置）
3. 处理页面导航和切换
4. 集成核心管理器（数据管理、AI引擎、知识库等）
5. 处理事件总线和通知
6. 提供菜单栏、工具栏、状态栏
7. 支持数据刷新和视图更新

依赖：
- PyQt5: GUI框架
- core模块: 核心管理器
- ui模块: UI组件和页面
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QToolBar, QStatusBar, QStackedWidget,
                             QPushButton, QAction, QMessageBox, QLabel, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from ui.pages.dashboard_page import DashboardPage
from ui.pages.market_page import MarketPage
from ui.pages.ai_assistant_page import AIAssistantPage
from ui.pages.knowledge_page import KnowledgePage
from ui.pages.settings_page import SettingsPage
from ui.navigation_sidebar import NavigationSidebar
from ui.info_panel import InfoPanel
from ui.styles import get_stylesheet
from datetime import datetime
import logging

日志记录器 = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    主窗口 - A股智能助手应用主界面
    
    功能：
    1. 创建主窗口和UI布局
    2. 管理各个功能页面（仪表盘、行情、AI助手、知识库、设置）
    3. 处理页面导航和切换
    4. 集成核心管理器（数据管理、AI引擎、知识库等）
    5. 处理事件总线和通知
    6. 提供菜单栏、工具栏、状态栏
    7. 支持数据刷新和视图更新
    
    UI布局：
    - 左侧：导航侧边栏（240px）
    - 中间：内容区域（弹性）
    - 右侧：信息面板（300px，可折叠）
    
    页面：
    - 仪表盘：市场概况和大盘复盘
    - 行情：实时行情和股票搜索
    - AI助手：智能分析和投资建议
    - 知识库：投资知识和文档管理
    - 设置：系统配置和偏好设置
    """
    
    def __init__(self, 数据管理器=None, AI引擎=None, 知识库=None, 
                 事件总线=None, 通知管理器=None, 调度器=None, 轻量模式=False):
        """
        初始化主窗口
        
        参数：
            数据管理器: 数据管理器（可选）
            AI引擎: AI引擎（可选）
            知识库: 知识库（可选）
            事件总线: 事件总线（可选）
            通知管理器: 通知管理器（可选）
            调度器: 自动化调度器（可选）
            轻量模式: 轻量模式（默认False）
        """
        super().__init__()
        
        self.轻量模式 = 轻量模式
        self.已初始化 = False
        self.组件已加载 = False
        
        self.配置管理器 = None
        self.事件总线 = 事件总线
        self.通知管理器 = 通知管理器
        self.数据管理器 = 数据管理器
        self.AI引擎 = AI引擎
        self.知识库 = 知识库
        self.数据流管理器 = None
        self.搜索服务 = None
        self.导航管理器 = None
        self.事件处理器 = None
        self.调度器 = 调度器
        
        # 先创建启动容器，再初始化UI
        self.show_startup_status()
        self.init_ui()
        
        self.setup_timer()
        
        QTimer.singleShot(100, self.delayed_show_window)
        QTimer.singleShot(3500, self.delayed_initialization)
    
    def delayed_show_window(self):
        """
        延迟显示窗口，确保UI组件快速呈现
        """
        self.show()
        self.raise_()
        self.activateWindow()
    
    def show_startup_status(self):
        """
        显示启动状态指示器
        """
        self.startup_label = QLabel("正在启动 A股智能助手...")
        self.startup_label.setAlignment(Qt.AlignCenter)
        self.startup_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.startup_label.setStyleSheet("color: #3498db;")
        
        self.startup_progress = QProgressBar()
        self.startup_progress.setRange(0, 0)
        self.startup_progress.setTextVisible(False)
        self.startup_progress.setFixedWidth(300)
        
        self.startup_hint_label = QLabel("请稍候，正在加载必要组件...")
        self.startup_hint_label.setAlignment(Qt.AlignCenter)
        self.startup_hint_label.setStyleSheet("color: #7f8c8d;")
        
        启动布局 = QVBoxLayout()
        启动布局.addStretch()
        启动布局.addWidget(self.startup_label)
        启动布局.addSpacing(20)
        启动布局.addWidget(self.startup_progress, 0, Qt.AlignCenter)
        启动布局.addSpacing(10)
        启动布局.addWidget(self.startup_hint_label)
        启动布局.addStretch()
        
        self.startup_container = QWidget()
        self.startup_container.setLayout(启动布局)
        self.startup_container.setStyleSheet("background-color: #ecf0f1;")
    
    def hide_startup_status(self):
        """
        隐藏启动状态指示器
        """
        if hasattr(self, 'startup_container'):
            self.startup_container.hide()
            self.status_bar.showMessage("系统已就绪", 3000)
    
    def delayed_initialization(self):
        """
        延迟初始化 - 在UI完全加载后执行
        
        说明：
            延迟初始化重量级组件，避免阻塞UI
            延迟时间设置为3.5秒，确保窗口完全显示后再加载
        """
        try:
            self.status_bar.showMessage("正在初始化核心组件...")
            
            from core import (NavigationManager as 导航管理器类, 
                               DataFlowManager as 数据流管理器类, 
                               EventBus as 事件总线类, 
                               ConfigManager as 配置管理器类, 
                               NotificationManager as 通知管理器类, 
                               DataManager as 数据管理器类,
                               AIEngine as AI引擎类, 
                               KnowledgeBase as 知识库类, 
                               EventHandler as 事件处理器类)
            
            if not self.配置管理器:
                self.配置管理器 = 配置管理器类()
            
            if not self.事件总线:
                self.事件总线 = 事件总线类()
            
            if not self.通知管理器:
                self.通知管理器 = 通知管理器类()
            
            if not self.数据管理器:
                self.数据管理器 = 数据管理器类(轻量模式=self.轻量模式)
            
            if not self.数据流管理器:
                self.数据流管理器 = 数据流管理器类()
            
            self.事件处理器 = 事件处理器类(
                event_bus=self.事件总线,
                data_manager=self.数据管理器,
                ai_engine=self.AI引擎,
                knowledge_base=self.知识库,
                notification_manager=self.通知管理器
            )
            
            self.事件总线.event_emitted.connect(self.on_event_emitted)
            
            self.init_navigation_manager()
            
            self.inject_managers_to_pages()
            
            if not self.轻量模式:
                try:
                    from core.search_service import SearchService
                    搜索配置 = self.配置管理器.get_section("search")
                    bocha_keys = 搜索配置.get("bocha_api_keys", [])
                    tavily_keys = 搜索配置.get("tavily_api_keys", [])
                    serpapi_keys = 搜索配置.get("serpapi_keys", [])
                    brave_keys = 搜索配置.get("brave_api_keys", [])
                    self.搜索服务 = SearchService(
                        tavily_keys=tavily_keys,
                        serpapi_keys=serpapi_keys,
                        bocha_keys=bocha_keys,
                        brave_keys=brave_keys
                    )
                    日志记录器.info("搜索服务延迟初始化完成")
                    self.inject_search_service_to_pages()
                except Exception as e:
                    日志记录器.warning(f"搜索服务初始化失败: {e}")
            
            self.setup_data_source()
            
            if hasattr(self.dashboard_page, 'schedule_data_load'):
                self.dashboard_page.schedule_data_load(延迟毫秒=500)
            
            self.组件已加载 = True
            self.已初始化 = True
            self.hide_startup_status()
            
            日志记录器.info("延迟初始化完成")
        except Exception as e:
            日志记录器.error(f"延迟初始化失败: {e}")
            self.status_bar.showMessage(f"初始化失败: {str(e)}", 5000)
    
    def init_navigation_manager(self):
        """
        初始化导航管理器
        """
        from core import NavigationManager
        self.导航管理器 = NavigationManager(self.content_stack)
        self.事件处理器.set_navigation_manager(self.导航管理器)
    
    def inject_search_service_to_pages(self):
        """
        向页面注入搜索服务
        """
        页面列表 = [
            self.dashboard_page,
            self.market_page,
            self.ai_assistant_page,
            self.knowledge_page,
            self.settings_page
        ]
        
        for 页面 in 页面列表:
            if hasattr(页面, 'set_search_service'):
                页面.set_search_service(self.搜索服务)
    
    def on_event_emitted(self, 事件类型: str, 数据):
        """
        事件发射处理
        
        参数：
            事件类型: 事件类型
            数据: 事件数据
        
        说明：
            当事件总线发射事件时，调用事件处理器处理事件
        """
        if self.事件处理器:
            self.事件处理器.handle_event(事件类型, 数据)
    
    def init_ui(self):
        """
        初始化UI
        
        流程：
            1. 应用全局样式
            2. 设置窗口基本属性
            3. 创建菜单栏
            4. 创建工具栏
            5. 创建状态栏
            6. 创建主内容区域
        """
        self.setStyleSheet(get_stylesheet())
        
        self.setWindowTitle("A股智能助手 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_main_content()
    
    def create_menu_bar(self):
        """
        创建菜单栏
        
        菜单结构：
            - 文件：退出
            - 视图：刷新、切换右侧面板
            - 工具：设置
            - 帮助：关于
        """
        菜单栏 = self.menuBar()
        
        文件菜单 = 菜单栏.addMenu("文件")
        
        退出动作 = QAction("退出", self)
        退出动作.setShortcut("Ctrl+Q")
        退出动作.triggered.connect(self.close)
        文件菜单.addAction(退出动作)
        
        视图菜单 = 菜单栏.addMenu("视图")
        
        刷新动作 = QAction("刷新", self)
        刷新动作.setShortcut("F5")
        刷新动作.triggered.connect(self.refresh_view)
        视图菜单.addAction(刷新动作)
        
        视图菜单.addSeparator()
        
        切换面板动作 = QAction("切换右侧面板", self)
        切换面板动作.setShortcut("Ctrl+R")
        切换面板动作.triggered.connect(self.toggle_right_panel)
        视图菜单.addAction(切换面板动作)
        
        工具菜单 = 菜单栏.addMenu("工具")
        
        设置动作 = QAction("设置", self)
        设置动作.setShortcut("Ctrl+,")
        设置动作.triggered.connect(lambda: self.navigate_to_page("settings"))
        工具菜单.addAction(设置动作)
        
        帮助菜单 = 菜单栏.addMenu("帮助")
        
        关于动作 = QAction("关于", self)
        关于动作.triggered.connect(self.show_about)
        帮助菜单.addAction(关于动作)
    
    def create_tool_bar(self):
        """
        创建工具栏
        
        工具栏按钮：
            - 刷新
            - 仪表盘
            - 行情
            - AI助手
            - 设置
        """
        工具栏 = QToolBar("主工具栏")
        工具栏.setMovable(False)
        self.addToolBar(工具栏)
        
        刷新动作 = 工具栏.addAction("🔄 刷新")
        刷新动作.triggered.connect(self.refresh_view)
        
        工具栏.addSeparator()
        
        仪表盘动作 = 工具栏.addAction("📊 仪表盘")
        仪表盘动作.triggered.connect(lambda: self.navigate_to_page("dashboard"))
        
        行情动作 = 工具栏.addAction("📈 行情")
        行情动作.triggered.connect(lambda: self.navigate_to_page("market"))
        
        AI动作 = 工具栏.addAction("🤖 AI助手")
        AI动作.triggered.connect(lambda: self.navigate_to_page("ai_assistant"))
        
        工具栏.addSeparator()
        
        设置动作 = 工具栏.addAction("⚙️ 设置")
        设置动作.triggered.connect(lambda: self.navigate_to_page("settings"))
    
    def create_status_bar(self):
        """
        创建状态栏
        
        功能：
            - 显示当前状态信息
            - 显示永久信息（占位）
        """
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        self.status_bar.addPermanentWidget(QWidget())
    
    def create_main_content(self):
        """
        创建主内容区域
        
        布局结构：
            - 左侧导航栏 (240px)
            - 中间内容区 (弹性)
            - 右侧信息栏 (300px，可折叠)
            - 折叠按钮 (20px)
        
        说明：
            使用QStackedWidget管理多个页面
            通过NavigationSidebar进行页面切换
        """
        中央部件 = QWidget()
        中央部件.setObjectName("centralWidget")
        主布局 = QVBoxLayout(中央部件)
        主布局.setContentsMargins(0, 0, 0, 0)
        主布局.setSpacing(0)
        
        主布局.addWidget(self.startup_container)
        
        内容容器 = QWidget()
        内容布局 = QHBoxLayout(内容容器)
        内容布局.setContentsMargins(0, 0, 0, 0)
        内容布局.setSpacing(0)
        
        self.left_sidebar = NavigationSidebar()
        内容布局.addWidget(self.left_sidebar)
        
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        内容布局.addWidget(self.content_stack, 3)
        
        self.right_panel = InfoPanel()
        self.right_panel.setFixedWidth(300)
        self.right_panel.setHidden(False)
        内容布局.addWidget(self.right_panel)
        
        self.collapse_button = QPushButton("◀")
        self.collapse_button.setObjectName("collapseBtn")
        self.collapse_button.setFixedWidth(20)
        self.collapse_button.setStyleSheet("""
            QPushButton#collapseBtn {
                background-color: #ecf0f1;
                color: #7f8c8d;
                border: none;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton#collapseBtn:hover {
                background-color: #bdc3c7;
                color: #2c3e50;
            }
        """)
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.clicked.connect(self.toggle_right_panel)
        内容布局.addWidget(self.collapse_button)
        
        主布局.addWidget(内容容器)
        
        self.setCentralWidget(中央部件)
        
        self.setup_pages()
        
        self.left_sidebar.page_changed.connect(self.on_page_changed)
    
    def setup_pages(self):
        """
        设置各个功能页面
        
        页面列表：
            1. DashboardPage: 仪表盘
            2. MarketPage: 行情
            3. AIAssistantPage: AI助手
            4. KnowledgePage: 知识库
            5. SettingsPage: 设置
        
        流程：
            1. 创建各个页面实例
            2. 将管理器注入到页面
            3. 将页面添加到内容堆栈
        """
        self.dashboard_page = DashboardPage()
        self.market_page = MarketPage()
        self.ai_assistant_page = AIAssistantPage()
        self.knowledge_page = KnowledgePage()
        self.settings_page = SettingsPage()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.market_page)
        self.content_stack.addWidget(self.ai_assistant_page)
        self.content_stack.addWidget(self.knowledge_page)
        self.content_stack.addWidget(self.settings_page)
    
    def inject_managers_to_pages(self):
        """
        将管理器注入到页面
        
        说明：
            遍历所有页面，将管理器注入到支持该管理器的页面
            支持的管理器：
            - data_manager
            - ai_engine
            - knowledge_base
            - event_bus
            - notification_manager
            - search_service
        """
        页面列表 = [
            self.dashboard_page,
            self.market_page,
            self.ai_assistant_page,
            self.knowledge_page,
            self.settings_page
        ]
        
        for 页面 in 页面列表:
            if hasattr(页面, 'set_data_manager'):
                页面.set_data_manager(self.数据管理器)
            if hasattr(页面, 'set_ai_engine'):
                页面.set_ai_engine(self.AI引擎)
            if hasattr(页面, 'set_knowledge_base'):
                页面.set_knowledge_base(self.知识库)
            if hasattr(页面, 'set_event_bus'):
                页面.set_event_bus(self.事件总线)
            if hasattr(页面, 'set_notification_manager'):
                页面.set_notification_manager(self.通知管理器)
        
        if hasattr(self.dashboard_page, 'init_market_review'):
            self.dashboard_page.init_market_review()
    
    def setup_data_source(self):
        """
        设置数据源
        
        说明：
            注册数据源到数据流管理器
            包括市场数据和自选股数据
            刷新间隔为60秒（优化后）
        """
        if self.数据流管理器 and self.数据管理器:
            self.数据流管理器.register_data_source(
                "market_data",
                self.数据管理器.get_market_data,
                60
            )
            
            self.数据流管理器.register_data_source(
                "watchlist_data",
                self.数据管理器.get_watchlist_data,
                60
            )
    
    def navigate_to_page(self, 页面名称):
        """
        导航到指定页面
        
        参数：
            页面名称: 页面名称（dashboard/market/ai_assistant/knowledge/settings）
        
        说明：
            通过导航管理器切换到指定页面
        """
        if self.导航管理器:
            self.导航管理器.navigate_to(页面名称)
    
    def on_page_changed(self, 索引):
        """
        页面切换处理
        
        参数：
            索引: 页面索引
        
        流程：
            1. 直接切换到指定页面
            2. 更新状态栏
        """
        self.content_stack.setCurrentIndex(索引)
        
        页面标题列表 = ["仪表盘", "行情看板", "AI助手", "知识库", "系统设置"]
        self.status_bar.showMessage(f"当前页面: {页面标题列表[索引]}", 2000)
        日志记录器.info(f"切换到页面: {页面标题列表[索引]}")
    
    def refresh_view(self):
        """
        刷新视图
        
        流程：
            1. 显示刷新状态
            2. 根据当前页面刷新数据
            3. 显示刷新完成状态
        """
        self.status_bar.showMessage("正在刷新...")
        
        当前索引 = self.content_stack.currentIndex()
        if 当前索引 == 0:
            if hasattr(self.dashboard_page, 'update_metrics'):
                self.dashboard_page.update_metrics()
        elif 当前索引 == 1:
            if hasattr(self.market_page, 'refresh_data'):
                self.market_page.refresh_data()
            
        self.status_bar.showMessage("刷新完成", 2000)
    
    def show_about(self):
        """
        显示关于对话框
        
        说明：
            显示应用版本、主要功能等信息
        """
        QMessageBox.about(
            self,
            "关于 A股智能助手",
            """
            <h2>A股智能助手 v1.0</h2>
            <p>一款基于AI的智能股票投资辅助工具</p>
            <p><b>主要功能：</b></p>
            <ul>
                <li>实时行情监控</li>
                <li>AI智能分析</li>
                <li>投资策略推荐</li>
                <li>知识库查询</li>
            </ul>
            <p>© 2024 All Rights Reserved</p>
            """
        )
    
    def toggle_right_panel(self):
        """
        切换右侧面板显示/隐藏
        
        说明：
            切换右侧信息面板的可见性
            更新折叠按钮的文本和状态栏提示
        """
        if self.right_panel.isHidden():
            self.right_panel.setHidden(False)
            self.collapse_button.setText("◀")
            self.status_bar.showMessage("右侧面板已显示", 1500)
        else:
            self.right_panel.setHidden(True)
            self.collapse_button.setText("▶")
            self.status_bar.showMessage("右侧面板已隐藏", 1500)
            
    def setup_timer(self):
        """
        设置定时器
        
        功能：
            - 每秒更新时间显示
            - 检查市场状态
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time_display)
        self.timer.start(1000)
        
    def _update_time_display(self):
        """
        更新时间显示
        
        说明：
            更新侧边栏的时间显示
            检查市场状态（简化版，实际应该根据交易时间判断）
        """
        当前时间 = datetime.now().strftime("%H:%M:%S")
        self.left_sidebar.update_time(当前时间)
        
        小时 = datetime.now().hour
        是否开市 = (9 <= 小时 < 11) or (13 <= 小时 < 15)
        self.left_sidebar.update_market_status(是否开市)
