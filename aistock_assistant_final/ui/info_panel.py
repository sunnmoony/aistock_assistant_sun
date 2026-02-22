from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QScrollArea)
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime


class InfoPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setProperty("info_panel_header", True)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("市场概览")
        title_label.setProperty("panel_title", True)
        header_layout.addWidget(title_label)
        header.setLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)

        self.time_label = QLabel()
        self.time_label.setProperty("time_label", True)
        self.time_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.time_label)

        content_layout.addSpacing(10)

        rise_fall_header = QLabel("快速涨跌榜")
        rise_fall_header.setProperty("section_title", True)
        content_layout.addWidget(rise_fall_header)

        rise_fall_table = QTableWidget()
        rise_fall_table.setColumnCount(3)
        rise_fall_table.setHorizontalHeaderLabels(["名称", "现价", "涨跌"])
        rise_fall_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        rise_fall_table.verticalHeader().setVisible(False)
        rise_fall_table.setFixedHeight(120)
        rise_fall_table.setProperty("info_table", True)

        rise_fall_data = [
            ("贵州茅台", "1850.00", "+2.35%"),
            ("宁德时代", "210.50", "+1.88%"),
            ("比亚迪", "280.30", "-1.20%"),
            ("中国平安", "45.20", "-0.85%")
        ]

        for i, (name, price, change) in enumerate(rise_fall_data):
            rise_fall_table.insertRow(i)
            rise_fall_table.setItem(i, 0, QTableWidgetItem(name))
            rise_fall_table.setItem(i, 1, QTableWidgetItem(price))
            change_item = QTableWidgetItem(change)
            if "+" in change:
                change_item.setForeground(Qt.red)
            else:
                change_item.setForeground(Qt.darkGreen)
            rise_fall_table.setItem(i, 2, change_item)

        content_layout.addWidget(rise_fall_table)

        news_header = QLabel("最新资讯")
        news_header.setProperty("section_title", True)
        content_layout.addWidget(news_header)

        news_content = QLabel()
        news_content.setProperty("news_content", True)
        news_content.setWordWrap(True)
        news_content.setText(
            "• 央行宣布降准0.5个百分点\n"
            "• A股三大指数集体收涨\n"
            "• 新能源板块表现强势\n"
            "• 科技股持续活跃\n"
            "• 北向资金净流入50亿"
        )
        content_layout.addWidget(news_content)

        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)

        layout.addWidget(header)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
