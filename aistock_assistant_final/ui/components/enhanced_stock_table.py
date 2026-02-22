from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                             QWidget, QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class EnhancedStockTable(QTableWidget):
    """增强股票表格组件 - 支持操作按钮和颜色显示"""
    
    analyze_stock = pyqtSignal(str)
    remove_stock = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        self.stock_data = {}
        
    def setup_table(self):
        """初始化表格设置"""
        headers = ["代码", "名称", "最新价", "涨跌幅", "涨跌额", "成交量", "成交额", "操作"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # 设置列宽
        self.setColumnWidth(0, 80)   # 代码
        self.setColumnWidth(1, 100)  # 名称
        self.setColumnWidth(2, 80)   # 最新价
        self.setColumnWidth(3, 80)   # 涨跌幅
        self.setColumnWidth(4, 80)   # 涨跌额
        self.setColumnWidth(5, 100)  # 成交量
        self.setColumnWidth(6, 100)  # 成交额
        self.setColumnWidth(7, 150)  # 操作
        
        # 美化样式
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                gridline-color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 10px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: bold;
                color: #2c3e50;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        
    def update_stock_data(self, stock_list):
        """更新股票数据
        
        Args:
            stock_list: 股票对象列表，每个对象需包含 code, name, price, change, change_amount, volume, amount 属性
        """
        self.setRowCount(len(stock_list))
        self.stock_data = {}
        
        for i, stock in enumerate(stock_list):
            self.stock_data[stock.code] = stock
            
            # 代码
            code_item = QTableWidgetItem(stock.code)
            code_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 0, code_item)
            
            # 名称
            name_item = QTableWidgetItem(stock.name)
            name_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 1, name_item)
            
            # 最新价
            price_item = QTableWidgetItem(f"{stock.price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(i, 2, price_item)
            
            # 涨跌幅（带颜色）
            change_item = QTableWidgetItem(f"{stock.change:+.2f}%")
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if stock.change > 0:
                change_item.setForeground(QColor("#e74c3c"))  # 红色涨
            elif stock.change < 0:
                change_item.setForeground(QColor("#27ae60"))  # 绿色跌
            else:
                change_item.setForeground(QColor("#7f8c8d"))  # 灰色平
            self.setItem(i, 3, change_item)
            
            # 涨跌额
            change_amount_item = QTableWidgetItem(f"{stock.change_amount:+.2f}")
            change_amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if stock.change_amount > 0:
                change_amount_item.setForeground(QColor("#e74c3c"))
            elif stock.change_amount < 0:
                change_amount_item.setForeground(QColor("#27ae60"))
            else:
                change_amount_item.setForeground(QColor("#7f8c8d"))
            self.setItem(i, 4, change_amount_item)
            
            # 成交量
            volume_item = QTableWidgetItem(self.format_volume(stock.volume))
            volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(i, 5, volume_item)
            
            # 成交额
            amount_item = QTableWidgetItem(self.format_amount(stock.amount))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.setItem(i, 6, amount_item)
            
            # 操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(5, 2, 5, 2)
            button_layout.setSpacing(8)
            
            analyze_btn = QPushButton("分析")
            analyze_btn.setCursor(Qt.PointingHandCursor)
            analyze_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            analyze_btn.clicked.connect(lambda checked, code=stock.code: self.on_analyze_clicked(code))
            button_layout.addWidget(analyze_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, code=stock.code: self.on_remove_clicked(code))
            button_layout.addWidget(delete_btn)
            
            self.setCellWidget(i, 7, button_widget)
            
    def on_analyze_clicked(self, code):
        """分析按钮点击处理"""
        self.analyze_stock.emit(code)
        
    def on_remove_clicked(self, code):
        """删除按钮点击处理"""
        self.remove_stock.emit(code)
        
    def format_volume(self, volume):
        """格式化成交量"""
        if volume >= 100000000:
            return f"{volume/100000000:.2f}亿"
        elif volume >= 10000:
            return f"{volume/10000:.2f}万"
        else:
            return str(volume)
            
    def format_amount(self, amount):
        """格式化成交额"""
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        else:
            return str(amount)
            
    def get_stock_by_code(self, code):
        """根据代码获取股票对象"""
        return self.stock_data.get(code)
        
    def clear_data(self):
        """清空表格数据"""
        self.setRowCount(0)
        self.stock_data.clear()
