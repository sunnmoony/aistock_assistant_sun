from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QCheckBox, QPushButton, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from mplfinance import plot
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class KLineChart(QWidget):
    """K线图表组件"""

    period_changed = pyqtSignal(str)
    indicator_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = pd.DataFrame()
        self.current_period = "daily"
        self.current_indicator = "none"
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 图表区域
        self.chart_canvas = self.create_chart()
        main_layout.addWidget(self.chart_canvas)

        self.setLayout(main_layout)

    def create_control_panel(self) -> QFrame:
        """创建控制面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # 周期选择
        period_label = QLabel("周期:")
        period_label.setStyleSheet("font-size: 13px; color: #2c3e50; font-weight: 500;")
        layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        layout.addWidget(self.period_combo)

        # 技术指标选择
        indicator_label = QLabel("指标:")
        indicator_label.setStyleSheet("font-size: 13px; color: #2c3e50; font-weight: 500;")
        layout.addWidget(indicator_label)

        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems(["无指标", "MA均线", "MACD", "RSI", "KDJ", "BOLL", "成交量"])
        self.indicator_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        self.indicator_combo.currentTextChanged.connect(self.on_indicator_changed)
        layout.addWidget(self.indicator_combo)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_chart)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        panel.setLayout(layout)
        return panel

    def create_chart(self) -> FigureCanvas:
        """创建图表画布"""
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.figure.patch.set_facecolor('white')

        canvas = FigureCanvas(self.figure)
        canvas.setStyleSheet("background-color: white;")

        return canvas

    def set_data(self, data: pd.DataFrame):
        """
        设置K线数据

        Args:
            data: K线数据DataFrame
        """
        try:
            if data.empty:
                logger.warning("K线数据为空")
                return

            self.data = data.copy()

            if 'date' not in self.data.columns:
                logger.error("K线数据缺少date列")
                return

            self.data['date'] = pd.to_datetime(self.data['date'])

            self.update_chart()
            logger.info(f"K线数据已更新: {len(self.data)}条")
        except Exception as e:
            logger.error(f"设置K线数据失败: {e}")

    def on_period_changed(self, text: str):
        """周期改变处理"""
        period_map = {
            "日线": "daily",
            "周线": "weekly",
            "月线": "monthly"
        }
        self.current_period = period_map.get(text, "daily")
        self.period_changed.emit(self.current_period)

    def on_indicator_changed(self, text: str):
        """指标改变处理"""
        indicator_map = {
            "无指标": "none",
            "MA均线": "ma",
            "MACD": "macd",
            "RSI": "rsi",
            "KDJ": "kdj",
            "BOLL": "boll",
            "成交量": "volume"
        }
        self.current_indicator = indicator_map.get(text, "none")
        self.indicator_changed.emit(self.current_indicator)
        self.update_chart()

    def refresh_chart(self):
        """刷新图表"""
        self.update_chart()

    def update_chart(self):
        """更新图表"""
        try:
            self.figure.clear()

            if self.data.empty:
                self._draw_empty_chart()
                return

            if self.current_indicator == "macd":
                self._draw_macd_chart()
            elif self.current_indicator == "rsi":
                self._draw_rsi_chart()
            elif self.current_indicator == "kdj":
                self._draw_kdj_chart()
            elif self.current_indicator == "volume":
                self._draw_volume_chart()
            else:
                self._draw_kline_chart()

            self.chart_canvas.draw()
        except Exception as e:
            logger.error(f"更新图表失败: {e}")

    def _draw_empty_chart(self):
        """绘制空图表"""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, '暂无数据', 
                ha='center', va='center', fontsize=16, color='#7f8c8d')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def _draw_kline_chart(self):
        """绘制K线图"""
        try:
            # 准备数据 - 使用mplfinance要求的格式
            if self.data.empty:
                self._draw_empty_chart()
                return
            
            # 确保数据有正确的列名
            plot_data = self.data.copy()
            
            # 重命名列以符合mplfinance要求
            column_mapping = {
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in plot_data.columns:
                    plot_data[new_col] = plot_data[old_col]
            
            # 设置日期索引
            if 'Date' in plot_data.columns:
                plot_data['Date'] = pd.to_datetime(plot_data['Date'])
                plot_data.set_index('Date', inplace=True)
            
            # 创建子图
            gs = self.figure.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
            ax1 = self.figure.add_subplot(gs[0])
            ax2 = self.figure.add_subplot(gs[1], sharex=ax1)
            
            # 使用mplfinance绘制K线图
            if all(col in plot_data.columns for col in ['Open', 'High', 'Low', 'Close']):
                # 创建样式
                mc = plot.make_marketcolors(
                    up='#e74c3c',
                    down='#27ae60',
                    edge='inherit',
                    wick='inherit',
                    volume='inherit'
                )
                
                style = plot.make_mpf_style(
                    marketcolors=mc,
                    gridstyle='--',
                    gridcolor='#d5d5d5',
                    gridalpha=0.3,
                    facecolor='white'
                )
                
                # 绘制K线图
                plot.plot(
                    plot_data,
                    type='candle',
                    style=style,
                    ax=ax1,
                    volume=ax2,
                    show_nontrading=False,
                    datetime_format='%Y-%m-%d',
                    xrotation=45
                )
                
                # 添加技术指标
                if self.current_indicator == "ma":
                    self._draw_ma_lines(ax1)
                elif self.current_indicator == "boll":
                    self._draw_boll_bands(ax1)
                
                # 设置标题
                ax1.set_title('K线图', fontsize=14, fontweight='bold', pad=10)
                
        except Exception as e:
            logger.error(f"绘制K线图失败: {e}")
            self._draw_empty_chart()

    def _draw_ma_lines(self, ax):
        """绘制均线"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                return
            
            if 'MA5' in self.data.columns:
                ax.plot(dates, self.data['MA5'], 
                       label='MA5', linewidth=1.5, color='#f39c12', alpha=0.8)
            if 'MA10' in self.data.columns:
                ax.plot(dates, self.data['MA10'], 
                       label='MA10', linewidth=1.5, color='#e67e22', alpha=0.8)
            if 'MA20' in self.data.columns:
                ax.plot(dates, self.data['MA20'], 
                       label='MA20', linewidth=1.5, color='#3498db', alpha=0.8)
            if 'MA60' in self.data.columns:
                ax.plot(dates, self.data['MA60'], 
                       label='MA60', linewidth=1.5, color='#9b59b6', alpha=0.8)

            ax.legend(loc='upper left', fontsize=9, framealpha=0.8)
        except Exception as e:
            logger.error(f"绘制均线失败: {e}")

    def _draw_boll_bands(self, ax):
        """绘制布林带"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                return
            
            if all(col in self.data.columns for col in ['BOLL_UP', 'BOLL_MID', 'BOLL_LOW']):
                ax.plot(dates, self.data['BOLL_UP'], 
                       label='上轨', linewidth=1, color='#e74c3c', linestyle='--', alpha=0.6)
                ax.plot(dates, self.data['BOLL_MID'], 
                       label='中轨', linewidth=1.5, color='#3498db', alpha=0.8)
                ax.plot(dates, self.data['BOLL_LOW'], 
                       label='下轨', linewidth=1, color='#27ae60', linestyle='--', alpha=0.6)

                ax.fill_between(dates, self.data['BOLL_UP'], self.data['BOLL_LOW'],
                               alpha=0.1, color='#3498db')

                ax.legend(loc='upper left', fontsize=9, framealpha=0.8)
        except Exception as e:
            logger.error(f"绘制布林带失败: {e}")

    def _draw_macd_chart(self):
        """绘制MACD图"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                self._draw_empty_chart()
                return
            
            gs = self.figure.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.15)

            ax1 = self.figure.add_subplot(gs[0])
            ax2 = self.figure.add_subplot(gs[1], sharex=ax1)

            # 主图：DIF和DEA
            if all(col in self.data.columns for col in ['DIF', 'DEA']):
                ax1.plot(dates, self.data['DIF'], 
                       label='DIF', linewidth=1.5, color='#3498db', alpha=0.8)
                ax1.plot(dates, self.data['DEA'], 
                       label='DEA', linewidth=1.5, color='#e67e22', alpha=0.8)

            ax1.set_title('MACD', fontsize=14, fontweight='bold', pad=10)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.legend(loc='upper left', fontsize=9, framealpha=0.8)

            # 副图：MACD柱状图
            if 'MACD' in self.data.columns:
                colors = ['#e74c3c' if macd > 0 else '#27ae60' for macd in self.data['MACD']]
                ax2.bar(dates, self.data['MACD'], color=colors, alpha=0.6, width=0.8)

                ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)

            ax2.set_ylabel('MACD', fontsize=11)
            ax2.grid(True, alpha=0.3, linestyle='--')
        except Exception as e:
            logger.error(f"绘制MACD图失败: {e}")
            self._draw_empty_chart()

    def _draw_rsi_chart(self):
        """绘制RSI图"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                self._draw_empty_chart()
                return
            
            ax = self.figure.add_subplot(111)

            if 'RSI' in self.data.columns:
                ax.plot(dates, self.data['RSI'], 
                       linewidth=2, color='#9b59b6', alpha=0.8)

                ax.axhline(y=70, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5, label='超买线')
                ax.axhline(y=30, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5, label='超卖线')
                ax.axhline(y=50, color='#7f8c8d', linestyle='-', linewidth=0.5, alpha=0.3)

            ax.set_title('RSI (相对强弱指标)', fontsize=14, fontweight='bold', pad=10)
            ax.set_ylabel('RSI', fontsize=11)
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper right', fontsize=9, framealpha=0.8)
        except Exception as e:
            logger.error(f"绘制RSI图失败: {e}")
            self._draw_empty_chart()

    def _draw_kdj_chart(self):
        """绘制KDJ图"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                self._draw_empty_chart()
                return
            
            ax = self.figure.add_subplot(111)

            if all(col in self.data.columns for col in ['K', 'D', 'J']):
                ax.plot(dates, self.data['K'], 
                       label='K', linewidth=1.5, color='#3498db', alpha=0.8)
                ax.plot(dates, self.data['D'], 
                       label='D', linewidth=1.5, color='#e67e22', alpha=0.8)
                ax.plot(dates, self.data['J'], 
                       label='J', linewidth=1.5, color='#9b59b6', alpha=0.8)

                ax.axhline(y=80, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5, label='超买区')
                ax.axhline(y=20, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5, label='超卖区')

            ax.set_title('KDJ (随机指标)', fontsize=14, fontweight='bold', pad=10)
            ax.set_ylabel('KDJ', fontsize=11)
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper left', fontsize=9, framealpha=0.8)
        except Exception as e:
            logger.error(f"绘制KDJ图失败: {e}")
            self._draw_empty_chart()

    def _draw_volume_chart(self):
        """绘制成交量图"""
        try:
            # 获取日期数据
            if 'date' in self.data.columns:
                dates = self.data['date']
            elif 'Date' in self.data.columns:
                dates = self.data['Date']
            else:
                self._draw_empty_chart()
                return
            
            gs = self.figure.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)

            ax1 = self.figure.add_subplot(gs[0])
            ax2 = self.figure.add_subplot(gs[1], sharex=ax1)

            # 使用mplfinance绘制K线图
            if all(col in self.data.columns for col in ['open', 'high', 'low', 'close']):
                # 准备数据
                plot_data = self.data.copy()
                
                # 重命名列
                column_mapping = {
                    'date': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in plot_data.columns:
                        plot_data[new_col] = plot_data[old_col]
                
                if 'Date' in plot_data.columns:
                    plot_data['Date'] = pd.to_datetime(plot_data['Date'])
                    plot_data.set_index('Date', inplace=True)
                
                # 创建样式
                mc = plot.make_marketcolors(
                    up='#e74c3c',
                    down='#27ae60',
                    edge='inherit',
                    wick='inherit',
                    volume='inherit'
                )
                
                style = plot.make_mpf_style(
                    marketcolors=mc,
                    gridstyle='--',
                    gridcolor='#d5d5d5',
                    gridalpha=0.3,
                    facecolor='white'
                )
                
                # 绘制K线图
                plot.plot(
                    plot_data,
                    type='candle',
                    style=style,
                    ax=ax1,
                    volume=ax2,
                    show_nontrading=False,
                    datetime_format='%Y-%m-%d',
                    xrotation=45
                )
                
                ax1.set_title('K线图 + 成交量', fontsize=14, fontweight='bold', pad=10)
                
                # 绘制OBV
                if 'OBV' in self.data.columns:
                    ax2_twin = ax2.twinx()
                    ax2_twin.plot(dates, self.data['OBV'], 
                                  label='OBV', linewidth=1.5, color='#f39c12', alpha=0.8)
                    ax2_twin.set_ylabel('OBV', fontsize=11)
                    ax2_twin.legend(loc='upper left', fontsize=9, framealpha=0.8)
        except Exception as e:
            logger.error(f"绘制成交量图失败: {e}")
            self._draw_empty_chart()

    def clear_chart(self):
        """清空图表"""
        self.data = pd.DataFrame()
        self.figure.clear()
        self.chart_canvas.draw()