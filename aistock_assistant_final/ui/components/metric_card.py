# -*- coding: utf-8 -*-
"""
===================================
指标卡片组件
===================================

职责：
1. 显示关键指标（如总资产、今日盈亏等）
2. 支持自定义颜色和图标
3. 提供hover效果增强交互反馈
4. 支持动态更新数值
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MetricCard(QWidget):
    """
    指标卡片组件 - 显示关键指标
    
    功能：
    - 显示标题和数值
    - 支持自定义颜色和图标
    - 提供hover效果
    - 支持动态更新数值
    """
    
    def __init__(self, title, value, color="#3498db", icon=""):
        """
        初始化指标卡片
        
        参数：
            title: 卡片标题（如"总资产"、"今日盈亏"）
            value: 指标数值（如"¥1,234,567"）
            color: 指标颜色（十六进制颜色代码）
            icon: 图标（可选，如"💰"、"📊"）
        """
        super().__init__()
        self.title = title
        self.value = value
        self.color = color
        self.icon = icon
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI界面
        
        布局结构：
        - QVBoxLayout: 垂直布局
        - QFrame: 卡片容器，设置圆角和边框
        - QLabel: 标题标签和数值标签
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 创建卡片容器
        self.card = QFrame()
        self.card.setObjectName("metricCard")
        self.card.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }}
            QFrame#metricCard:hover {{
                border: 2px solid {self.color};
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(5)
        
        # 创建标题行
        title_row = QLabel()
        if self.icon:
            # 如果有图标，显示图标+标题
            title_row.setText(f"{self.icon} {self.title}")
        else:
            # 如果没有图标，只显示标题
            title_row.setText(self.title)
        title_row.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                font-weight: 500;
            }
        """)
        card_layout.addWidget(title_row)
        
        # 创建数值行
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.color};
            }}
        """)
        card_layout.addWidget(self.value_label)
        
        self.card.setLayout(card_layout)
        layout.addWidget(self.card)
        self.setLayout(layout)
    
    def update_value(self, new_value, subtitle: str = None):
        """
        更新指标值
        
        参数：
            new_value: 新的指标值
            subtitle: 可选的副标题/百分比显示
        
        功能：
        - 更新数值显示
        - 保持颜色和图标不变
        """
        self.value = new_value
        if subtitle:
            self.value_label.setText(f"{new_value}\n{subtitle}")
        else:
            self.value_label.setText(new_value)
    
    def set_color(self, new_color):
        """
        设置指标颜色
        
        参数：
            new_color: 新的颜色（十六进制颜色代码）
        
        功能：
        - 更新数值颜色
        - 保持标题和图标不变
        """
        self.color = new_color
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {new_color};
            }}
        """)