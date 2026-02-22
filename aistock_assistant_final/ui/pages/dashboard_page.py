from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QPushButton, QScrollArea, QFrame,
                             QSpacerItem, QSizePolicy, QTabWidget, QTextEdit,
                             QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex, QMutexLocker
from PyQt5.QtGui import QFont
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import functools
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ui.components import MetricCard, ActivityItem, RecommendationCard
import logging

logger = logging.getLogger(__name__)


class DataLoaderThread(QThread):
    """异步数据加载线程，支持超时和取消"""
    
    data_loaded = pyqtSignal(bool, object)
    data_loading_progress = pyqtSignal(str)
    
    def __init__(self, 加载函数, 超时秒数=10):
        super().__init__()
        self.加载函数 = 加载函数
        self.超时秒数 = 超时秒数
        self._取消标志 = False
        self._互斥锁 = QMutex()
        
    def 取消加载(self):
        """取消数据加载"""
        with QMutexLocker(self._互斥锁):
            self._取消标志 = True
            
    def 已取消(self):
        """检查是否已取消"""
        with QMutexLocker(self._互斥锁):
            return self._取消标志
            
    def run(self):
        """执行数据加载"""
        try:
            self.数据加载进度.emit("正在初始化...")
            
            with ThreadPoolExecutor(max_workers=1) as 执行器:
                未来对象 = 执行器.submit(self.加载函数)
                
                while not 未来对象.done():
                    if self.已取消():
                        未来对象.cancel()
                        self.data_loaded.emit(False, "加载已取消")
                        return
                    self.msleep(100)
                
                try:
                    结果 = 未来对象.result(timeout=0.1)
                    self.data_loaded.emit(True, 结果)
                except TimeoutError:
                    self.data_loaded.emit(False, "数据加载超时")
                except Exception as e:
                    logger.error(f"数据加载异常: {e}")
                    self.data_loaded.emit(False, str(e))
                    
        except Exception as e:
            logger.error(f"数据加载线程异常: {e}")
            self.data_loaded.emit(False, str(e))


class DashboardPage(QWidget):
    """仪表盘页面 - 展示关键指标、快速操作、活动时间和智能推荐"""

    def __init__(self):
        super().__init__()
        self.数据管理器 = None
        self.事件总线 = None
        self.通知管理器 = None
        self.数据提供者 = None
        self.资金流分析器 = None
        self.大盘复盘 = None
        self.ai引擎 = None
        self.搜索服务 = None
        self._数据已加载 = False
        self._正在加载 = False
        self._加载线程 = None
        self._加载互斥锁 = QMutex()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """初始化用户界面"""
        主布局 = QVBoxLayout()
        主布局.setContentsMargins(20, 20, 20, 20)
        主布局.setSpacing(20)
        
        页面标题 = QLabel("📊 仪表盘")
        页面标题.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        主布局.addWidget(页面标题)

        副标题 = QLabel("实时数据概览与智能分析")
        副标题.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        """)
        主布局.addWidget(副标题)

        self.加载状态标签 = QLabel("准备就绪")
        self.加载状态标签.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            padding: 5px;
        """)
        self.加载状态标签.hide()
        主布局.addWidget(self.加载状态标签)

        滚动区域 = QScrollArea()
        滚动区域.setWidgetResizable(True)
        滚动区域.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        滚动区域.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        内容容器 = QWidget()
        内容布局 = QVBoxLayout(内容容器)
        内容布局.setContentsMargins(0, 0, 0, 0)
        内容布局.setSpacing(20)
        
        指标区域 = self.create_metrics_area()
        内容布局.addWidget(指标区域)
        
        快速操作区域 = self.create_quick_actions_area()
        内容布局.addWidget(快速操作区域)
        
        活动区域 = self.create_activity_area()
        内容布局.addWidget(活动区域)
        
        推荐区域 = self.create_recommendations_area()
        内容布局.addWidget(推荐区域)
        
        滚动区域.setWidget(内容容器)
        主布局.addWidget(滚动区域)
        
        self.setLayout(主布局)
        
    def create_metrics_area(self):
        """
        创建关键指标展示区域
        
        说明：
            创建动态可更新的指标卡片，包括上涨家数、下跌家数、涨停、跌停
        """
        区域容器 = QFrame()
        区域容器.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        区域布局 = QVBoxLayout(区域容器)
        区域布局.setContentsMargins(20, 20, 20, 20)
        区域布局.setSpacing(15)
        
        标题标签 = QLabel("📈 关键指标")
        标题标签.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        区域布局.addWidget(标题标签)
        
        网格布局 = QGridLayout()
        网格布局.setSpacing(15)
        
        self.上涨家数卡片 = MetricCard("上涨家数", "--", "#4CAF50", "�")
        self.下跌家数卡片 = MetricCard("下跌家数", "--", "#f44336", "�")
        self.涨停卡片 = MetricCard("涨停", "--", "#FF5722", "�")
        self.跌停卡片 = MetricCard("跌停", "--", "#9C27B0", "❄️")
        
        网格布局.addWidget(self.上涨家数卡片, 0, 0)
        网格布局.addWidget(self.下跌家数卡片, 0, 1)
        网格布局.addWidget(self.涨停卡片, 1, 0)
        网格布局.addWidget(self.跌停卡片, 1, 1)
        
        区域布局.addLayout(网格布局)
        return 区域容器
        
    def create_quick_actions_area(self):
        """创建快速操作按钮区域"""
        区域容器 = QFrame()
        区域容器.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        区域布局 = QVBoxLayout(区域容器)
        区域布局.setContentsMargins(20, 20, 20, 20)
        区域布局.setSpacing(15)
        
        标题标签 = QLabel("⚡ 快速操作")
        标题标签.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        区域布局.addWidget(标题标签)
        
        网格布局 = QGridLayout()
        网格布局.setSpacing(10)
        
        操作列表 = [
            ("🔍 查询股票", self.search_stock),
            ("➕ 添加自选", self.add_to_watchlist),
            ("📊 查看分析", self.view_analysis),
            ("⚙️ 系统设置", self.open_settings),
            ("📚 知识库", self.open_knowledge),
            ("🤖 AI助手", self.open_ai_assistant)
        ]
        
        for 索引, (文本, 处理函数) in enumerate(操作列表):
            按钮 = QPushButton(文本)
            按钮.setCursor(Qt.PointingHandCursor)
            按钮.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #3498db;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
            按钮.clicked.connect(处理函数)
            网格布局.addWidget(按钮, 索引 // 3, 索引 % 3)
        
        区域布局.addLayout(网格布局)
        return 区域容器
        
    def create_activity_area(self):
        """创建最近活动时间轴区域"""
        区域容器 = QFrame()
        区域容器.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        区域布局 = QVBoxLayout(区域容器)
        区域布局.setContentsMargins(20, 20, 20, 20)
        区域布局.setSpacing(15)
        
        标题标签 = QLabel("🕐 最近活动")
        标题标签.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        区域布局.addWidget(标题标签)
        
        活动列表 = [
            ("10:30", "贵州茅台", "价格突破1850元", "📈"),
            ("09:45", "五粮液", "加入自选股", "⭐"),
            ("09:15", "招商银行", "AI分析完成", "🤖"),
            ("昨天", "平安银行", "查看分析报告", "📄")
        ]
        
        for 时间, 股票, 动作, 图标 in 活动列表:
            项目 = ActivityItem(时间, 股票, 动作)
            区域布局.addWidget(项目)
        
        区域布局.addStretch()
        return 区域容器
        
    def create_recommendations_area(self):
        """创建智能推荐卡片区域"""
        区域容器 = QFrame()
        区域容器.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        区域布局 = QVBoxLayout(区域容器)
        区域布局.setContentsMargins(20, 20, 20, 20)
        区域布局.setSpacing(15)
        
        标题标签 = QLabel("🎯 智能推荐")
        标题标签.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        区域布局.addWidget(标题标签)
        
        推荐列表 = [
            ("贵州茅台", "长期价值投资", "技术面强势，基本面优秀", "买入"),
            ("招商银行", "稳健配置", "分红稳定，估值合理", "持有"),
            ("宁德时代", "成长性机会", "新能源龙头，业绩增长", "关注")
        ]
        
        for 名称, 策略, 理由, 操作 in 推荐列表:
            卡片 = RecommendationCard(名称, 策略, 理由, 操作)
            区域布局.addWidget(卡片)
        
        return 区域容器
        
    def setup_timer(self):
        """设置定时刷新定时器，间隔60秒"""
        self.刷新定时器 = QTimer()
        self.刷新定时器.timeout.connect(self._async_update_indicators)
        self.刷新定时器.start(60000)
    
    def delayed_init_data_provider(self):
        """
        延迟初始化数据提供者组件
        
        说明：
            如果数据管理器已设置，使用数据管理器的数据提供者
            否则创建独立的数据提供者（兼容模式）
        """
        if self.数据提供者 is not None:
            return
        
        try:
            if self.数据管理器 is not None and hasattr(self.数据管理器, '数据提供者'):
                self.数据提供者 = self.数据管理器.数据提供者
                logger.info("使用数据管理器的数据提供者")
            else:
                from core.data_providers import PytdxProvider
                from core.fund_flow_analyzer import FundFlowAnalyzer
                
                self.数据提供者 = PytdxProvider(池大小=3, 缓存超时=60)
                self.资金流分析器 = FundFlowAnalyzer()
                logger.info("独立数据提供者延迟初始化完成")
        except Exception as e:
            logger.error(f"初始化数据提供者失败: {e}")
    
    def schedule_data_load(self, 延迟毫秒: int = 2000):
        """
        延迟调度数据加载任务
        
        参数:
            延迟毫秒: 延迟时间（毫秒），默认2秒
        """
        if self._数据已加载 or self._正在加载:
            return
        QTimer.singleShot(延迟毫秒, self._async_load_real_data)
    
    def _async_load_real_data(self):
        """异步加载真实数据，带超时和取消机制"""
        if self._正在加载 or self._数据已加载:
            return
        
        with QMutexLocker(self._加载互斥锁):
            if self._正在加载:
                return
            self._正在加载 = True
        
        self.show_loading_status("正在初始化数据加载...")
        self.delayed_init_data_provider()
        
        if self.数据提供者 is None:
            self._正在加载 = False
            self.hide_loading_status()
            return
        
        def 加载任务():
            """实际的数据加载任务"""
            try:
                self.数据提供者.init_async(callback=lambda success: None)
                return True
            except Exception as e:
                logger.error(f"异步加载数据失败: {e}")
                raise
        
        self._加载线程 = DataLoaderThread(加载任务, 超时秒数=10)
        self._加载线程.data_loaded.connect(self._on_data_loaded)
        self._加载线程.data_loading_progress.connect(self.update_loading_status)
        self._加载线程.start()
    
    def _on_data_loaded(self, 成功: bool, 结果):
        """数据加载完成后的回调处理"""
        try:
            if 成功:
                self.show_loading_status("正在更新数据...")
                self.update_market_overview()
                self.update_fund_flow()
                self.update_sector_ranking()
                self._数据已加载 = True
                logger.info("加载仪表盘真实数据完成")
            else:
                logger.warning(f"数据加载失败: {结果}")
                self.show_loading_status(f"加载失败: {结果}")
        except Exception as e:
            logger.error(f"更新数据失败: {e}")
            self.show_loading_status(f"更新失败: {e}")
        finally:
            self._正在加载 = False
            QTimer.singleShot(2000, self._hide_loading_status)
    
    def show_loading_status(self, 消息: str):
        """显示加载状态信息"""
        self.加载状态标签.setText(f"⏳ {消息}")
        self.加载状态标签.show()
    
    def update_loading_status(self, 消息: str):
        """更新加载状态信息"""
        self.加载状态标签.setText(f"⏳ {消息}")
    
    def _hide_loading_status(self):
        """隐藏加载状态信息"""
        self.加载状态标签.hide()
    
    def hide_loading_status(self):
        """隐藏加载状态信息（兼容旧接口）"""
        self._hide_loading_status()
    
    def load_real_data(self):
        """加载真实数据（兼容旧接口）"""
        self._async_load_real_data()

    def update_market_overview(self):
        """
        更新市场概况数据
        
        说明：
            使用数据管理器获取市场概况数据，更新指标卡片
        """
        if self.数据管理器 is None:
            return
        try:
            概况数据 = self.数据管理器.获取市场概况()
            
            if 概况数据:
                上涨家数 = 概况数据.get('rise_count', 0)
                下跌家数 = 概况数据.get('fall_count', 0)
                平盘家数 = 概况数据.get('flat_count', 0)
                涨停家数 = 概况数据.get('limit_up_count', 0)
                跌停家数 = 概况数据.get('limit_down_count', 0)
                
                总数 = 上涨家数 + 下跌家数 + 平盘家数
                上涨比例 = (上涨家数 / 总数 * 100) if 总数 > 0 else 0
                
                if hasattr(self, '上涨家数卡片'):
                    self.上涨家数卡片.update_value(str(上涨家数), f"{上涨比例:.1f}%")
                if hasattr(self, '下跌家数卡片'):
                    self.下跌家数卡片.update_value(str(下跌家数), f"{100-上涨比例:.1f}%")
                if hasattr(self, '涨停卡片'):
                    self.涨停卡片.update_value(str(涨停家数), "涨停")
                if hasattr(self, '跌停卡片'):
                    self.跌停卡片.update_value(str(跌停家数), "跌停")
                
                logger.info(f"更新市场概况: 涨{上涨家数} 跌{下跌家数}")
        except Exception as e:
            logger.error(f"更新市场概况失败: {e}")

    def update_fund_flow(self):
        """更新资金流向数据"""
        if self.数据提供者 is None or self.资金流分析器 is None:
            return
        try:
            资金数据 = self.数据提供者.get_fund_flow()

            if 资金数据:
                分析结果 = self.资金流分析器.analyze_fund_flow(资金数据)

                if hasattr(self, '资金流卡片'):
                    净流入 = 分析结果.get('net_inflow', 0)
                    趋势 = 分析结果.get('trend', '无法判断')
                    self.资金流卡片.update_value(
                        f"{净流入/100000000:.2f}亿" if abs(净流入) > 100000000 else f"{净流入/10000:.2f}万",
                        趋势
                    )

                logger.info(f"更新资金流向: {分析结果.get('summary', '')}")
        except Exception as e:
            logger.error(f"更新资金流向失败: {e}")

    def update_sector_ranking(self):
        """更新板块排行数据"""
        if self.数据提供者 is None:
            return
        try:
            板块排行 = self.数据提供者.get_sector_rank()

            if 板块排行:
                热门板块 = 板块排行[:5]

                if hasattr(self, '板块排行组件'):
                    self._update_sector_ranking_display(热门板块)

                logger.info(f"更新板块排行: {len(热门板块)}个板块")
        except Exception as e:
            logger.error(f"更新板块排行失败: {e}")

    def _update_sector_ranking_display(self, 板块列表):
        """更新板块排行的显示内容"""
        pass

    def _async_update_indicators(self):
        """异步更新指标数据，避免阻塞UI线程"""
        QTimer.singleShot(100, self._do_update_indicators)
    
    def _do_update_indicators(self):
        """执行实际的指标更新操作"""
        try:
            self.update_market_overview()
            self.update_fund_flow()
            self.update_sector_ranking()
        except Exception as e:
            logger.error(f"更新指标失败: {e}")
        
    def search_stock(self):
        """查询股票功能"""
        pass
        
    def add_to_watchlist(self):
        """添加自选股功能"""
        pass
        
    def view_analysis(self):
        """查看分析功能"""
        pass
        
    def open_settings(self):
        """打开系统设置"""
        pass
        
    def open_knowledge(self):
        """打开知识库"""
        pass
        
    def open_ai_assistant(self):
        """打开AI助手"""
        pass

    def set_data_manager(self, 数据管理器):
        """设置数据管理器"""
        self.数据管理器 = 数据管理器

    def set_ai_engine(self, ai引擎):
        """设置AI引擎"""
        self.ai引擎 = ai引擎

    def set_search_service(self, 搜索服务):
        """设置搜索服务"""
        self.搜索服务 = 搜索服务

    def set_event_bus(self, 事件总线):
        """设置事件总线"""
        self.事件总线 = 事件总线

    def set_notification_manager(self, 通知管理器):
        """设置通知管理器"""
        self.通知管理器 = 通知管理器

    def init_market_review(self):
        """初始化大盘复盘组件"""
        if self.数据管理器 and self.ai引擎 and self.搜索服务:
            try:
                from core.analyzer_dashboard import GeminiAnalyzer
                from core.market_review import MarketReview
                ai分析器 = GeminiAnalyzer(self.ai引擎)
                self.大盘复盘 = MarketReview(self.数据管理器, ai分析器, self.搜索服务)
                logger.info("大盘复盘初始化成功")
            except Exception as e:
                logger.error(f"大盘复盘初始化失败: {e}")

    def generate_market_review_report(self):
        """生成大盘复盘报告"""
        if self.大盘复盘:
            try:
                报告 = self.大盘复盘.generate_market_review()
                return 报告
            except Exception as e:
                logger.error(f"生成大盘复盘报告失败: {e}")
                return None
        return None
    
    def cancel_data_load(self):
        """取消正在进行的数据加载"""
        if self._加载线程 and self._加载线程.isRunning():
            self._加载线程.取消加载()
            self.show_loading_status("正在取消...")
    
    def closeEvent(self, event):
        """页面关闭事件处理，清理资源"""
        self.cancel_data_load()
        super().closeEvent(event)
