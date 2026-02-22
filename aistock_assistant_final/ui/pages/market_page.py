from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QPushButton, QTabWidget, QMessageBox,
                             QComboBox, QGridLayout, QFrame, QSplitter,
                             QScrollArea, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from ui.components import EnhancedStockTable, KLineChart
from models.stock import Stock
from core.technical_indicators import TechnicalIndicators
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MarketPage(QWidget):
    """行情看板页面 - 展示市场行情、自选股和板块信息"""

    stock_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.data_manager = None
        self.event_bus = None
        self.notification_manager = None
        self.current_sort_column = -1
        self.sort_order = Qt.AscendingOrder
        self.data_provider = None
        self.technical_indicators = TechnicalIndicators()
        self.current_stock_code = None
        self.init_ui()
        self.setup_auto_refresh()
    
    def set_data_manager(self, data_manager):
        """
        设置数据管理器
        
        说明：
            使用注入的数据管理器，获取其数据提供者
        """
        self.data_manager = data_manager
        if data_manager is not None and hasattr(data_manager, '数据源管理器'):
            self.data_provider = data_manager.数据源管理器
        self.load_watchlist()
    
    def set_event_bus(self, event_bus):
        """设置事件总线"""
        self.event_bus = event_bus
    
    def set_notification_manager(self, notification_manager):
        """设置通知管理器"""
        self.notification_manager = notification_manager

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 页面标题
        title_label = QLabel("📈 行情看板")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(title_label)

        # 副标题
        subtitle = QLabel("实时市场行情与自选股追踪")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(subtitle)

        # 创建分割器：上部（搜索+表格）+ 下部（K线图表）
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setSizes([400, 300])

        # 上部区域
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        # 1. 市场概览卡片
        market_overview = self.create_market_overview()
        top_layout.addWidget(market_overview)

        # 2. 搜索和筛选栏
        search_bar = self.create_search_bar()
        top_layout.addWidget(search_bar)

        # 3. 自选股表格
        self.watchlist_table = self.create_watchlist_table()
        top_layout.addWidget(self.watchlist_table, 1)

        # 4. 标签页：涨幅榜/资金流向/板块轮动
        tab_widget = self.create_tabs()
        top_layout.addWidget(tab_widget)

        main_splitter.addWidget(top_widget)

        # 下部区域：K线图表
        bottom_widget = self.create_kline_panel()
        main_splitter.addWidget(bottom_widget)

        main_layout.addWidget(main_splitter)

        self.setLayout(main_layout)

    def create_market_overview(self):
        """创建市场概览卡片区域"""
        section = QFrame()
        section.setObjectName("marketOverview")
        section.setStyleSheet("""
            QFrame#marketOverview {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 区域标题
        title = QLabel("🏛️ 市场概览")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)

        # 指数卡片网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # 主要指数数据
        indices = [
            ("上证指数", "3,025.68", "+1.23%", "#e74c3c"),
            ("深证成指", "9,856.42", "+0.89%", "#e74c3c"),
            ("创业板指", "1,956.78", "+2.15%", "#e74c3c"),
            ("科创50", "892.45", "-0.45%", "#27ae60")
        ]

        for i, (name, value, change, color) in enumerate(indices):
            card = self.create_index_card(name, value, change, color)
            grid_layout.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid_layout)
        section.setLayout(layout)
        return section

    def create_index_card(self, name, value, change, color):
        """创建指数卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }}
            QFrame:hover {{
                border: 2px solid {color};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # 指数名称
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            font-weight: 500;
        """)
        layout.addWidget(name_label)

        # 指数值
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(value_label)

        # 涨跌幅
        change_label = QLabel(change)
        change_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {color};
        """)
        layout.addWidget(change_label)

        card.setLayout(layout)
        return card

    def create_search_bar(self):
        """创建搜索和筛选栏"""
        section = QFrame()
        section.setStyleSheet("background-color: transparent;")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 输入股票代码或名称搜索...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        self.search_input.returnPressed.connect(self.search_stock)
        layout.addWidget(self.search_input, 2)

        # 筛选下拉框
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部股票", "自选股", "沪深A股", "创业板", "科创板"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                min-width: 120px;
            }
        """)
        layout.addWidget(self.filter_combo)

        # 添加自选按钮
        self.add_button = QPushButton("➕ 添加自选")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        self.add_button.clicked.connect(self.add_to_watchlist)
        layout.addWidget(self.add_button)

        # 刷新按钮
        self.refresh_button = QPushButton("🔄 刷新")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_data)
        layout.addWidget(self.refresh_button)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                padding: 5px 10px;
            }
        """)
        layout.addWidget(self.status_label)

        section.setLayout(layout)
        return section

    def create_watchlist_table(self):
        """创建自选股表格 - 使用 EnhancedStockTable 组件"""
        table = EnhancedStockTable()
        table.analyze_stock.connect(self.on_analyze_stock)
        table.remove_stock.connect(self.on_remove_stock)
        return table

    def create_tabs(self):
        """创建标签页"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                color: #7f8c8d;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
                border-bottom: 3px solid #3498db;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d5dbdb;
            }
        """)

        # 涨幅榜
        self.rise_fall_table = self.create_ranking_table()
        tab_widget.addTab(self.rise_fall_table, "📈 涨幅榜")

        # 资金流向
        self.fund_flow_table = self.create_ranking_table()
        tab_widget.addTab(self.fund_flow_table, "💰 资金流向")

        # 板块轮动
        self.sector_table = self.create_sector_table()
        tab_widget.addTab(self.sector_table, "🔄 板块轮动")

        return tab_widget

    def create_ranking_table(self):
        """创建排名表格"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["排名", "股票代码", "股票名称", "涨跌幅", "最新价"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        return table

    def create_sector_table(self):
        """创建板块轮动表格"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["板块名称", "涨跌幅", "领涨股", "资金净流入", "热度"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        return table

    def setup_auto_refresh(self):
        """设置自动刷新 - 禁用，使用DataManager的自动刷新"""
        pass

    def load_watchlist(self):
        """
        加载自选股 - 使用真实数据
        
        说明：
            使用数据管理器获取自选股列表，并通过数据提供者获取实时行情
        """
        try:
            if self.data_manager is None:
                logger.warning("数据管理器未设置，无法加载自选股")
                return
                
            watchlist = self.data_manager.get_watchlist()
            stock_list = []

            for stock_data in watchlist:
                code = stock_data.get("code", "")
                name = stock_data.get("name", "")

                if self.data_provider is not None:
                    quote_data = self.data_provider.get_stock_realtime(code)
                    if quote_data:
                        price = quote_data.get("price", 0)
                        change = quote_data.get("change_percent", 0)
                        volume = quote_data.get("volume", 0)
                        change_amount = quote_data.get("change", 0)
                        amount = quote_data.get("turnover", 0)
                    else:
                        price = 0
                        change = 0
                        volume = 0
                        change_amount = 0
                        amount = 0
                else:
                    price = 0
                    change = 0
                    volume = 0
                    change_amount = 0
                    amount = 0

                stock = Stock(code, name, price, change, volume)
                stock.change_amount = change_amount
                stock.amount = amount
                stock_list.append(stock)

            self.watchlist_table.update_stock_data(stock_list)
            self.load_ranking_data()
            self.load_sector_data()
            self.update_market_overview_with_real_data()
        except Exception as e:
            logger.error(f"加载自选股失败: {e}")
            QMessageBox.warning(self, "提示", f"加载自选股失败: {str(e)}")

    def add_watchlist_row(self, code, name, price, change, volume):
        """添加自选股行"""
        row = self.watchlist_table.rowCount()
        self.watchlist_table.insertRow(row)

        # 股票代码
        code_item = QTableWidgetItem(code)
        code_item.setTextAlignment(Qt.AlignCenter)
        self.watchlist_table.setItem(row, 0, code_item)

        # 股票名称
        name_item = QTableWidgetItem(name)
        name_item.setTextAlignment(Qt.AlignCenter)
        self.watchlist_table.setItem(row, 1, name_item)

        # 最新价
        price_item = QTableWidgetItem(f"{price:.2f}")
        price_item.setTextAlignment(Qt.AlignCenter)
        self.watchlist_table.setItem(row, 2, price_item)

        # 涨跌幅
        change_item = QTableWidgetItem(f"{change:+.2f}%")
        change_item.setTextAlignment(Qt.AlignCenter)
        if change > 0:
            change_item.setForeground(QColor("#e74c3c"))
        elif change < 0:
            change_item.setForeground(QColor("#27ae60"))
        else:
            change_item.setForeground(QColor("#7f8c8d"))
        self.watchlist_table.setItem(row, 3, change_item)

        # 涨跌额
        change_amount = price * change / 100
        change_amount_item = QTableWidgetItem(f"{change_amount:+.2f}")
        change_amount_item.setTextAlignment(Qt.AlignCenter)
        if change > 0:
            change_amount_item.setForeground(QColor("#e74c3c"))
        elif change < 0:
            change_amount_item.setForeground(QColor("#27ae60"))
        self.watchlist_table.setItem(row, 4, change_amount_item)

        # 成交量
        volume_item = QTableWidgetItem(self.format_volume(volume))
        volume_item.setTextAlignment(Qt.AlignCenter)
        self.watchlist_table.setItem(row, 5, volume_item)

        # 成交额（模拟）
        turnover = price * volume
        turnover_item = QTableWidgetItem(self.format_volume(turnover))
        turnover_item.setTextAlignment(Qt.AlignCenter)
        self.watchlist_table.setItem(row, 6, turnover_item)

    def format_volume(self, volume):
        """格式化成交量"""
        if volume >= 100000000:
            return f"{volume / 100000000:.2f}亿"
        elif volume >= 10000:
            return f"{volume / 10000:.2f}万"
        else:
            return str(volume)

    def search_stock(self):
        """搜索股票"""
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "提示", "请输入股票代码或名称")
            return

        try:
            quote_data = self.data_manager.获取实时行情字典(search_text, 强制刷新=True)
            if quote_data:
                code = quote_data.get("code", search_text)
                name = quote_data.get("name", "")
                price = quote_data.get("price", 0)
                change = quote_data.get("change", 0)
                volume = quote_data.get("volume", 0)

                QMessageBox.information(
                    self,
                    "搜索结果",
                    f"股票代码: {code}\n股票名称: {name}\n最新价: {price:.2f}\n涨跌幅: {change:+.2f}%"
                )
            else:
                QMessageBox.warning(self, "提示", "未找到该股票信息")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索失败: {str(e)}")

    def add_to_watchlist(self):
        """添加到自选股"""
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "提示", "请输入股票代码或名称")
            return

        try:
            quote_data = self.data_manager.获取实时行情字典(search_text, 强制刷新=True)
            if quote_data:
                code = quote_data.get("code", search_text)
                name = quote_data.get("name", "")

                success = self.data_manager.添加到自选股(code, name)
                if success:
                    price = quote_data.get("price", 0)
                    change = quote_data.get("change", 0)
                    volume = quote_data.get("volume", 0)
                    # 重新加载整个列表
                    self.load_watchlist()
                    QMessageBox.information(self, "成功", f"已添加 {name}({code}) 到自选股")
                else:
                    QMessageBox.warning(self, "提示", "该股票已在自选股列表中")
            else:
                QMessageBox.warning(self, "提示", "未找到该股票信息")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加失败: {str(e)}")

    def refresh_data(self):
        """@刷新数据 - 增加加载提示和超时保护"""
        try:
            # 显示加载提示
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("⏳ 加载中...")
            self.status_label.setText("正在获取最新数据...")
            
            # 使用QTimer避免阻塞UI
            QTimer.singleShot(100, self._do_refresh)
            
        except Exception as e:
            logger.error(f"刷新数据失败: {e}")
            QMessageBox.warning(self, "提示", f"刷新数据失败: {str(e)}")
            self._refresh_finished()
    
    def _do_refresh(self):
        """执行刷新操作"""
        try:
            # 清空缓存,强制获取最新数据
            self.data_manager.清空缓存()
            
            # 重新加载自选股
            self.load_watchlist()
            
            # 更新市场概览
            self.update_market_overview_with_real_data()
            
            logger.info("数据刷新完成")
        except Exception as e:
            logger.error(f"刷新数据失败: {e}")
            QMessageBox.warning(self, "提示", f"刷新数据失败: {str(e)}")
        finally:
            self._refresh_finished()
    
    def _refresh_finished(self):
        """刷新完成"""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("🔄 刷新")
        self.status_label.setText("数据已更新")

    def on_header_clicked(self, column):
        """表头点击排序"""
        if self.current_sort_column == column:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = column
            self.sort_order = Qt.AscendingOrder

        self.watchlist_table.sortItems(column, self.sort_order)

    def load_ranking_data(self):
        """加载排名数据"""
        self.load_rise_fall_data()
        self.load_fund_flow_data()

    def load_rise_fall_data(self):
        """加载涨跌榜数据"""
        mock_data = [
            {"rank": 1, "code": "600519", "name": "贵州茅台", "change": 5.23, "price": 1850.00},
            {"rank": 2, "code": "000858", "name": "五粮液", "change": 4.56, "price": 168.50},
            {"rank": 3, "code": "600036", "name": "招商银行", "change": 3.89, "price": 42.30},
            {"rank": 4, "code": "000001", "name": "平安银行", "change": 3.45, "price": 12.80},
            {"rank": 5, "code": "601318", "name": "中国平安", "change": 2.98, "price": 55.60},
            {"rank": 6, "code": "600276", "name": "恒瑞医药", "change": 2.67, "price": 48.90},
            {"rank": 7, "code": "000333", "name": "美的集团", "change": 2.34, "price": 62.50},
            {"rank": 8, "code": "600887", "name": "伊利股份", "change": 2.12, "price": 35.80},
            {"rank": 9, "code": "000651", "name": "格力电器", "change": 1.98, "price": 38.20},
            {"rank": 10, "code": "601888", "name": "中国中免", "change": 1.76, "price": 125.30},
        ]

        self.rise_fall_table.setRowCount(len(mock_data))

        for idx, data in enumerate(mock_data):
            rank_item = QTableWidgetItem(str(data["rank"]))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.rise_fall_table.setItem(idx, 0, rank_item)

            code_item = QTableWidgetItem(data["code"])
            code_item.setTextAlignment(Qt.AlignCenter)
            self.rise_fall_table.setItem(idx, 1, code_item)

            name_item = QTableWidgetItem(data["name"])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.rise_fall_table.setItem(idx, 2, name_item)

            change_item = QTableWidgetItem(f"+{data['change']:.2f}%")
            change_item.setTextAlignment(Qt.AlignCenter)
            change_item.setForeground(QColor("#e74c3c"))
            self.rise_fall_table.setItem(idx, 3, change_item)

            price_item = QTableWidgetItem(f"{data['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.rise_fall_table.setItem(idx, 4, price_item)

    def load_fund_flow_data(self):
        """加载资金流向数据"""
        mock_data = [
            {"rank": 1, "code": "600519", "name": "贵州茅台", "flow": 125000000, "price": 1850.00},
            {"rank": 2, "code": "000858", "name": "五粮液", "flow": 89000000, "price": 168.50},
            {"rank": 3, "code": "600036", "name": "招商银行", "flow": 67000000, "price": 42.30},
            {"rank": 4, "code": "601318", "name": "中国平安", "flow": 56000000, "price": 55.60},
            {"rank": 5, "code": "000001", "name": "平安银行", "flow": 45000000, "price": 12.80},
            {"rank": 6, "code": "600276", "name": "恒瑞医药", "flow": 38000000, "price": 48.90},
            {"rank": 7, "code": "000333", "name": "美的集团", "flow": 32000000, "price": 62.50},
            {"rank": 8, "code": "600887", "name": "伊利股份", "flow": 28000000, "price": 35.80},
            {"rank": 9, "code": "000651", "name": "格力电器", "flow": 24000000, "price": 38.20},
            {"rank": 10, "code": "601888", "name": "中国中免", "flow": 19000000, "price": 125.30},
        ]

        self.fund_flow_table.setRowCount(len(mock_data))

        for idx, data in enumerate(mock_data):
            rank_item = QTableWidgetItem(str(data["rank"]))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.fund_flow_table.setItem(idx, 0, rank_item)

            code_item = QTableWidgetItem(data["code"])
            code_item.setTextAlignment(Qt.AlignCenter)
            self.fund_flow_table.setItem(idx, 1, code_item)

            name_item = QTableWidgetItem(data["name"])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.fund_flow_table.setItem(idx, 2, name_item)

            flow_item = QTableWidgetItem(f"+{data['flow'] / 10000:.0f}万")
            flow_item.setTextAlignment(Qt.AlignCenter)
            flow_item.setForeground(QColor("#e74c3c"))
            self.fund_flow_table.setItem(idx, 3, flow_item)

            price_item = QTableWidgetItem(f"{data['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.fund_flow_table.setItem(idx, 4, price_item)

    def load_sector_data(self):
        """加载板块轮动数据"""
        sector_data = [
            {"name": "新能源", "change": 3.25, "leader": "宁德时代", "flow": 520000000, "heat": "🔥🔥🔥"},
            {"name": "半导体", "change": 2.89, "leader": "中芯国际", "flow": 380000000, "heat": "🔥🔥"},
            {"name": "医药生物", "change": 1.95, "leader": "恒瑞医药", "flow": 290000000, "heat": "🔥🔥"},
            {"name": "白酒", "change": 1.76, "leader": "贵州茅台", "flow": 250000000, "heat": "🔥"},
            {"name": "银行", "change": 0.85, "leader": "招商银行", "flow": 180000000, "heat": "🔥"},
            {"name": "房地产", "change": -0.56, "leader": "万科A", "flow": -120000000, "heat": "❄️"},
            {"name": "钢铁", "change": -1.23, "leader": "宝钢股份", "flow": -85000000, "heat": "❄️❄️"},
        ]

        self.sector_table.setRowCount(len(sector_data))

        for idx, data in enumerate(sector_data):
            # 板块名称
            name_item = QTableWidgetItem(data["name"])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.sector_table.setItem(idx, 0, name_item)

            # 涨跌幅
            change_item = QTableWidgetItem(f"{data['change']:+.2f}%")
            change_item.setTextAlignment(Qt.AlignCenter)
            if data["change"] > 0:
                change_item.setForeground(QColor("#e74c3c"))
            else:
                change_item.setForeground(QColor("#27ae60"))
            self.sector_table.setItem(idx, 1, change_item)

            # 领涨股
            leader_item = QTableWidgetItem(data["leader"])
            leader_item.setTextAlignment(Qt.AlignCenter)
            self.sector_table.setItem(idx, 2, leader_item)

            # 资金净流入
            flow_item = QTableWidgetItem(f"{data['flow'] / 100000000:.2f}亿")
            flow_item.setTextAlignment(Qt.AlignCenter)
            if data["flow"] > 0:
                flow_item.setForeground(QColor("#e74c3c"))
            else:
                flow_item.setForeground(QColor("#27ae60"))
            self.sector_table.setItem(idx, 3, flow_item)

            # 热度
            heat_item = QTableWidgetItem(data["heat"])
            heat_item.setTextAlignment(Qt.AlignCenter)
            self.sector_table.setItem(idx, 4, heat_item)

    def on_analyze_stock(self, code):
        """分析股票"""
        stock = self.watchlist_table.get_stock_by_code(code)
        if stock:
            QMessageBox.information(
                self,
                "股票分析",
                f"股票代码: {stock.code}\n"
                f"股票名称: {stock.name}\n"
                f"最新价: {stock.price:.2f}\n"
                f"涨跌幅: {stock.change:+.2f}%\n\n"
                f"正在为您进行AI分析..."
            )
        else:
            QMessageBox.warning(self, "提示", f"未找到股票 {code} 的信息")

    def on_remove_stock(self, code):
        """从自选股中删除"""
        stock = self.watchlist_table.get_stock_by_code(code)
        name = stock.name if stock else code

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要从自选股中删除 {name}({code}) 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.data_manager.从自选股移除(code)
            if success:
                self.load_watchlist()
                QMessageBox.information(self, "成功", f"已删除 {name}({code})")
            else:
                QMessageBox.warning(self, "提示", "删除失败")

    def create_kline_panel(self) -> QFrame:
        """创建K线图表面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题栏
        header_layout = QHBoxLayout()

        title = QLabel("📊 K线图表")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title)

        # 当前股票信息
        self.stock_info_label = QLabel("请选择股票查看K线图")
        self.stock_info_label.setStyleSheet("""
            font-size: 13px;
            color: #7f8c8d;
        """)
        header_layout.addStretch()
        header_layout.addWidget(self.stock_info_label)

        layout.addLayout(header_layout)

        # K线图表
        self.kline_chart = KLineChart()
        self.kline_chart.period_changed.connect(self.on_kline_period_changed)
        self.kline_chart.indicator_changed.connect(self.on_kline_indicator_changed)
        layout.addWidget(self.kline_chart, 1)

        # 分析按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        analyze_btn = QPushButton("🤖 AI分析")
        analyze_btn.setCursor(Qt.PointingHandCursor)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        analyze_btn.clicked.connect(self.on_analyze_selected_stock)
        analyze_btn.setEnabled(False)
        self.analyze_btn = analyze_btn
        btn_layout.addWidget(analyze_btn)

        export_btn = QPushButton("📥 导出数据")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        export_btn.clicked.connect(self.on_export_kline_data)
        export_btn.setEnabled(False)
        self.export_btn = export_btn
        btn_layout.addWidget(export_btn)

        layout.addLayout(btn_layout)

        panel.setLayout(layout)
        return panel

    def on_kline_period_changed(self, period: str):
        """K线周期改变"""
        if self.current_stock_code:
            self.load_kline_data(self.current_stock_code, period)

    def on_kline_indicator_changed(self, indicator: str):
        """K线指标改变"""
        pass

    def on_analyze_selected_stock(self):
        """分析选中的股票"""
        if self.current_stock_code:
            self.stock_selected.emit(self.current_stock_code)

    def on_export_kline_data(self):
        """导出K线数据"""
        try:
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出K线数据",
                "",
                "Excel文件 (*.xlsx);;CSV文件 (*.csv)"
            )

            if file_path:
                if self.kline_chart.data.empty:
                    QMessageBox.warning(self, "提示", "没有可导出的数据")
                    return

                if file_path.endswith('.xlsx'):
                    self.kline_chart.data.to_excel(file_path, index=False)
                else:
                    self.kline_chart.data.to_csv(file_path, index=False, encoding='utf-8-sig')

                QMessageBox.information(self, "成功", f"数据已导出到：\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败：\n{str(e)}")

    def load_kline_data(self, stock_code: str, period: str = "daily"):
        """
        加载K线数据
        
        参数：
            stock_code: 股票代码
            period: 周期（daily/weekly/monthly）
        
        说明：
            使用数据提供者获取K线数据，并计算技术指标
        """
        try:
            if self.data_provider is None:
                logger.warning(f"数据提供者未设置，无法加载K线数据: {stock_code}")
                QMessageBox.warning(self, "提示", "数据提供者未初始化，请稍后再试")
                return
                
            period_map = {
                "daily": "daily",
                "weekly": "weekly",
                "monthly": "monthly"
            }

            df = self.data_provider.get_stock_history(stock_code, period=period_map.get(period, "daily"))

            if df.empty:
                logger.warning(f"未获取到股票 {stock_code} 的K线数据")
                return

            df_with_indicators = self.technical_indicators.calculate_all(df)

            self.kline_chart.set_data(df_with_indicators)
            self.analyze_btn.setEnabled(True)
            self.export_btn.setEnabled(True)

            logger.info(f"加载K线数据成功: {stock_code}, {len(df)}条")
        except Exception as e:
            logger.error(f"加载K线数据失败 {stock_code}: {e}")
            QMessageBox.warning(self, "提示", f"加载K线数据失败：\n{str(e)}")

    def update_market_overview_with_real_data(self):
        """
        使用真实数据更新市场概览
        
        说明：
            使用数据管理器获取指数数据
        """
        try:
            if self.data_manager is None:
                logger.warning("数据管理器未设置，无法更新市场概览")
                return
                
            logger.info("市场概览更新请求已记录")
        except Exception as e:
            logger.error(f"更新市场概览失败: {e}")
