from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QButtonGroup,
                             QLabel, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class NavigationSidebar(QWidget):
    """导航侧边栏 - 应用主导航组件"""
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setObjectName("navigationSidebar")
        self.setFixedWidth(240)
        self.setStyleSheet("""
            QWidget#navigationSidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/标题区域
        header = self.create_header()
        layout.addWidget(header)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #34495e;")
        line.setFixedHeight(1)
        layout.addWidget(line)
        
        layout.addSpacing(20)
        
        # 导航按钮组
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        nav_items = [
            ("📊", "仪表盘", 0),
            ("📈", "行情看板", 1),
            ("🤖", "AI助手", 2),
            ("📚", "知识库", 3),
            ("⚙️", "系统设置", 4)
        ]
        
        for icon, text, index in nav_items:
            btn = self.create_nav_button(icon, text, index)
            self.button_group.addButton(btn, index)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # 底部信息
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
        
        # 默认选中第一个
        self.button_group.button(0).setChecked(True)
        self.button_group.buttonClicked.connect(self.on_button_clicked)
        
    def create_header(self):
        """创建侧边栏头部"""
        header = QWidget()
        header.setStyleSheet("background-color: transparent;")
        header.setFixedHeight(80)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 10)
        layout.setSpacing(5)
        
        # 应用名称
        app_name = QLabel("A股智能助手")
        app_name.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
        """)
        layout.addWidget(app_name)
        
        # 版本号
        version = QLabel("v1.0")
        version.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
        """)
        layout.addWidget(version)
        
        header.setLayout(layout)
        return header
        
    def create_nav_button(self, icon, text, index):
        """创建导航按钮"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                border-left: 4px solid transparent;
                padding-left: 20px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }
            QPushButton:checked {
                background-color: #34495e;
                color: #3498db;
                border-left: 4px solid #3498db;
                font-weight: bold;
            }
        """)
        return btn
        
    def create_footer(self):
        """创建侧边栏底部"""
        footer = QWidget()
        footer.setStyleSheet("background-color: transparent;")
        footer.setFixedHeight(60)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # 市场状态
        self.market_status = QLabel("🟢 交易中")
        self.market_status.setStyleSheet("""
            color: #2ecc71;
            font-size: 13px;
        """)
        layout.addWidget(self.market_status)
        
        # 时间
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
        """)
        layout.addWidget(self.time_label)
        
        footer.setLayout(layout)
        return footer
        
    def on_button_clicked(self, button):
        """导航按钮点击处理"""
        index = self.button_group.id(button)
        self.page_changed.emit(index)
        
    def set_current_page(self, index):
        """设置当前页面"""
        btn = self.button_group.button(index)
        if btn:
            btn.setChecked(True)
            
    def update_time(self, time_str):
        """更新时间显示"""
        self.time_label.setText(time_str)
        
    def update_market_status(self, is_open):
        """更新市场状态"""
        if is_open:
            self.market_status.setText("🟢 交易中")
            self.market_status.setStyleSheet("""
                color: #2ecc71;
                font-size: 13px;
            """)
        else:
            self.market_status.setText("🔴 已休市")
            self.market_status.setStyleSheet("""
                color: #e74c3c;
                font-size: 13px;
            """)
