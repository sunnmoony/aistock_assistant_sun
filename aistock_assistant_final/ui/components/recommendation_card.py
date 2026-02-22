from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class RecommendationCard(QWidget):
    """推荐卡片组件 - 显示智能推荐"""
    
    def __init__(self, title, description, action_text="查看分析", tag_color=None):
        super().__init__()
        self.title = title
        self.description = description
        self.action_text = action_text
        self.tag_color = tag_color
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self.card = QFrame()
        self.card.setObjectName("recommendationCard")
        self.card.setStyleSheet("""
            QFrame#recommendationCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QFrame#recommendationCard:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)
        
        # 标题和标签行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title_label, 1)
        
        self.tag_label = QLabel("推荐")
        self.tag_label.setStyleSheet("""
            font-size: 11px;
            color: white;
            background-color: #3498db;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.tag_label)
        
        card_layout.addLayout(header_layout)
        
        # 描述
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #7f8c8d;
            line-height: 1.6;
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        # 操作按钮
        action_btn = QPushButton(self.action_text)
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        card_layout.addWidget(action_btn)
        
        self.card.setLayout(card_layout)
        layout.addWidget(self.card)
        self.setLayout(layout)
        
    def set_tag_color(self, color):
        """设置标签颜色"""
        if color:
            self.tag_label.setStyleSheet(f"""
                font-size: 11px;
                color: white;
                background-color: {color};
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: bold;
            """)
