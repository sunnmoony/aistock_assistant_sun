from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ActivityItem(QWidget):
    """活动项组件 - 显示最近活动"""
    
    def __init__(self, time, title, description):
        super().__init__()
        self.time = time
        self.title = title
        self.description = description
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # 时间标签
        time_label = QLabel(self.time)
        time_label.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            font-weight: 500;
            min-width: 60px;
        """)
        layout.addWidget(time_label)
        
        # 活动内容
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px;
            color: #2c3e50;
            font-weight: bold;
        """)
        content_layout.addWidget(title_label)
        
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
        """)
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        layout.addWidget(content_widget, 1)
        self.setLayout(layout)
