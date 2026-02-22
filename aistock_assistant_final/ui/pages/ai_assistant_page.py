from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTextEdit, QPushButton, QScrollArea, QFrame,
                             QSplitter, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QTextCursor
from models.stock import Stock


class AIAssistantPage(QWidget):
    """AI助手页面 - 智能投资分析和对话"""

    def __init__(self):
        super().__init__()
        self.data_manager = None
        self.ai_engine = None
        self.event_bus = None
        self.notification_manager = None
        self.current_stock = None
        self.chat_history = []
        self.is_streaming = False
        self.current_analysis = None
        self.init_ui()
    
    def set_data_manager(self, data_manager):
        """设置数据管理器"""
        self.data_manager = data_manager
    
    def set_ai_engine(self, ai_engine):
        """设置AI引擎"""
        self.ai_engine = ai_engine
    
    def set_event_bus(self, event_bus):
        """设置事件总线"""
        self.event_bus = event_bus
    
    def set_notification_manager(self, notification_manager):
        """设置通知管理器"""
        self.notification_manager = notification_manager

    def init_ui(self):
        """初始化UI - 使用垂直分割布局"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 页面标题
        title_label = QLabel("🤖 AI助手")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(title_label)

        # 副标题
        subtitle = QLabel("智能投资分析助手，为您提供专业的股票分析建议")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(subtitle)

        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)

        # 上部：对话历史区域
        chat_area = self.create_chat_area()
        splitter.addWidget(chat_area)

        # 下部：输入和快捷指令区域
        bottom_panel = self.create_bottom_panel()
        splitter.addWidget(bottom_panel)

        # 设置分割比例
        splitter.setSizes([500, 200])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def create_chat_area(self):
        """创建对话显示区域"""
        chat_frame = QFrame()
        chat_frame.setObjectName("chatArea")
        chat_frame.setStyleSheet("""
            QFrame#chatArea {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 对话标题
        chat_header = QLabel("💬 对话历史")
        chat_header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        """)
        layout.addWidget(chat_header)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # 聊天容器
        chat_container = QWidget()
        chat_container.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(chat_container)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()

        # 聊天显示区域
        self.chat_browser = QTextEdit()
        self.chat_browser.setReadOnly(True)
        self.chat_browser.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.chat_layout.addWidget(self.chat_browser)

        scroll_area.setWidget(chat_container)
        layout.addWidget(scroll_area)

        chat_frame.setLayout(layout)

        # 添加欢迎消息
        self.add_welcome_message()

        return chat_frame

    def create_bottom_panel(self):
        """创建底部输入和快捷指令面板"""
        panel = QFrame()
        panel.setObjectName("bottomPanel")
        panel.setStyleSheet("""
            QFrame#bottomPanel {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 快捷指令区域
        quick_commands_widget = self.create_quick_commands()
        layout.addWidget(quick_commands_widget)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e0e0;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # 输入区域
        input_area = self.create_input_area()
        layout.addLayout(input_area)

        panel.setLayout(layout)
        return panel

    def create_quick_commands(self):
        """创建快捷指令栏"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 标题
        title = QLabel("⚡ 快捷指令")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)

        # 按钮网格
        btn_layout = QGridLayout()
        btn_layout.setSpacing(10)

        commands = [
            ("📊 技术分析", "请对该股票进行技术分析，包括趋势、支撑位、阻力位等", 0, 0),
            ("📋 基本面分析", "请分析该股票的基本面情况，包括财务状况、估值水平等", 0, 1),
            ("⚠️ 风险评估", "请评估该股票的投资风险和潜在风险因素", 0, 2),
            ("💡 操作建议", "请给出该股票的投资建议和操作策略", 1, 0),
            ("📈 图表解读", "请解读该股票的K线图表形态和技术指标信号", 1, 1),
            ("🔍 深度分析", "请对该股票进行全面深入的分析", 1, 2),
            ("📊 决策仪表盘", "请生成决策仪表盘，包含买卖点位和检查清单", 0, 3)
        ]

        for text, prompt, row, col in commands:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #3498db;
                    color: white;
                    border-color: #3498db;
                }
                QPushButton:pressed {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, p=prompt: self.handle_quick_command(p))
            btn_layout.addWidget(btn, row, col)

        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        return widget

    def create_input_area(self):
        """创建输入区域"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # 输入框
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText("输入您的问题，AI助手将为您提供专业分析...")
        self.input_field.setStyleSheet("""
            QTextEdit {
                padding: 12px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """)
        layout.addWidget(self.input_field, 1)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(100)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # 连接信号
        self.input_field.textChanged.connect(self.on_input_changed)

        return layout

    def add_welcome_message(self):
        """添加欢迎消息"""
        welcome_html = """
        <div style="background-color: #e3f2fd; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px; border-left: 4px solid #2196F3;">
            <div style="font-weight: bold; color: #1976d2; margin-bottom: 8px; font-size: 16px;">🤖 AI助手</div>
            <div style="color: #424242; line-height: 1.6;">
                您好！我是您的A股投资助手。我可以为您提供：<br>
                • <b>技术分析</b> - K线形态、技术指标解读<br>
                • <b>基本面分析</b> - 财务状况、估值分析<br>
                • <b>风险评估</b> - 投资风险识别与提示<br>
                • <b>操作建议</b> - 买卖时机和策略建议<br><br>
                您可以直接输入问题，或点击上方的快捷按钮获取快速分析。
            </div>
        </div>
        """
        self.chat_browser.setHtml(welcome_html)

    def on_input_changed(self):
        """输入变化处理"""
        text = self.input_field.toPlainText().strip()
        self.send_button.setEnabled(bool(text) and not self.is_streaming)

    def get_current_stock(self):
        """@获取当前股票"""
        try:
            watchlist_data = self.data_manager.get_watchlist_data()
            if watchlist_data:
                stock_data = watchlist_data[0]
                code = stock_data.get("code", "")
                name = stock_data.get("name", "")

                quote_data = self.data_manager.get_realtime_quote(code)
                if quote_data:
                    price = quote_data.get("price", 0)
                    change = quote_data.get("change", 0)
                    volume = quote_data.get("volume", 0)
                    return Stock(code, name, price, change, volume)
        except Exception as e:
            print(f"获取当前股票失败: {e}")
        return None

    def display_user_message(self, message):
        """显示用户消息"""
        html = f"""
        <div style="text-align: right; margin: 10px 0;">
            <div style="display: inline-block; max-width: 75%; background-color: #3498db; color: white;
                        padding: 12px 18px; border-radius: 18px 18px 4px 18px; text-align: left;">
                <div style="font-size: 14px; line-height: 1.5;">{message}</div>
            </div>
            <div style="font-size: 11px; color: #95a5a6; margin-top: 5px;">您</div>
        </div>
        """
        self.chat_browser.append(html)
        self.scroll_to_bottom()

    def display_ai_message(self, message):
        """显示AI消息"""
        html = f"""
        <div style="text-align: left; margin: 10px 0;">
            <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">🤖 AI助手</div>
            <div style="display: inline-block; max-width: 75%; background-color: #f5f5f5; color: #333;
                        padding: 12px 18px; border-radius: 18px 18px 18px 4px; text-align: left;">
                <div style="font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{message}</div>
            </div>
        </div>
        """
        self.chat_browser.append(html)
        self.scroll_to_bottom()

    def stream_ai_response(self, response):
        """@流式显示AI响应 - 支持分析结果可视化"""
        self.is_streaming = True
        self.send_button.setEnabled(False)

        cursor = self.chat_browser.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 检查是否是分析结果（JSON格式）
        try:
            import json
            if response.strip().startswith('{'):
                try:
                    analysis = json.loads(response)
                    # 检查是否包含决策仪表盘所需字段
                    if "buy_price" in analysis and "checklist" in analysis:
                        self.display_decision_dashboard(analysis)
                    else:
                        self.display_analysis_result(analysis)
                    self.is_streaming = False
                    self.on_input_changed()
                    return
                except json.JSONDecodeError:
                    pass
        except:
            pass

        html_start = """
        <div style="text-align: left; margin: 10px 0;">
            <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">🤖 AI助手</div>
            <div style="display: inline-block; max-width: 75%; background-color: #f5f5f5; color: #333;
                        padding: 12px 18px; border-radius: 18px 18px 18px 4px; text-align: left;">
                <div style="font-size: 14px; line-height: 1.6; white-space: pre-wrap;">
        """

        self.chat_browser.insertHtml(html_start)

        displayed_text = ""
        for i, char in enumerate(response):
            displayed_text += char
            cursor.insertHtml(char)
            self.chat_browser.setTextCursor(cursor)
            self.chat_browser.ensureCursorVisible()

            if i % 3 == 0:
                QTimer.singleShot(10, lambda: None)

        html_end = """
                </div>
            </div>
        </div>
        """
        self.chat_browser.insertHtml(html_end)

        self.is_streaming = False
        self.on_input_changed()

    def display_analysis_result(self, analysis: dict):
        """@显示分析结果 - 可视化展示"""
        try:
            trend = analysis.get("trend", "")
            recommendation = analysis.get("recommendation", "")
            risk_level = analysis.get("risk_level", "")
            support = analysis.get("support", 0)
            resistance = analysis.get("resistance", 0)
            reasoning = analysis.get("reasoning", "")
            technical_indicators = analysis.get("technical_indicators", {})
            pattern = analysis.get("pattern", {})
            
            # 获取数据来源时间
            import time
            data_source_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # 判断数据来源类型
            stock_code = analysis.get("stock_code", "")
            if self.data_manager._use_mock_data:
                source_type = "模拟数据"
                source_color = "#e67a00"
            elif stock_code in self.data_manager._cache_timestamps:
                cache_time = self.data_manager._cache_timestamps[stock_code]
                if time.time() - cache_time < 300:  # 5分钟内
                    source_type = "缓存数据"
                    source_color = "#666"
                else:
                    source_type = "缓存数据"
                    source_color = "#999"
            else:
                source_type = "实时数据"
                source_color = "#27ae60"
            
            html = f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">🤖 AI分析结果</div>
                
                <div style="background-color: #f0f8ff; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">📊 基本面分析</div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">趋势:</td>
                            <td style="padding: 8px;">{trend}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">操作建议:</td>
                            <td style="padding: 8px; font-weight: bold; color: #e74c3c;">{recommendation}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">风险等级:</td>
                            <td style="padding: 8px;">{risk_level}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">支撑位:</td>
                            <td style="padding: 8px;">{support}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">阻力位:</td>
                            <td style="padding: 8px;">{resistance}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #fff3cd; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">📈 技术指标信号</div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 8px;">
                            <div style="font-size: 12px; margin-bottom: 5px;">均线趋势</div>
                            <div style="font-size: 14px; font-weight: bold;">{technical_indicators.get('ma_trend', 'N/A')}</div>
                        </div>
                        <div style="background-color: #ffeaa7; padding: 10px; border-radius: 8px;">
                            <div style="font-size: 12px; margin-bottom: 5px;">MACD信号</div>
                            <div style="font-size: 14px; font-weight: bold;">{technical_indicators.get('macd_signal', 'N/A')}</div>
                        </div>
                        <div style="background-color: #a8e6cf; padding: 10px; border-radius: 8px;">
                            <div style="font-size: 12px; margin-bottom: 5px;">RSI信号</div>
                            <div style="font-size: 14px; font-weight: bold;">{technical_indicators.get('rsi_signal', 'N/A')}</div>
                        </div>
                        <div style="background-color: #ffd966; padding: 10px; border-radius: 8px;">
                            <div style="font-size: 12px; margin-bottom: 5px;">KDJ信号</div>
                            <div style="font-size: 14px; font-weight: bold;">{technical_indicators.get('kdj_signal', 'N/A')}</div>
                        </div>
                    </div>
                </div>
            """

            if pattern and pattern.get("pattern") != "数据不足":
                pattern_name = pattern.get("pattern", "")
                pattern_confidence = pattern.get("confidence", 0)
                pattern_signal = pattern.get("signal", "中性")
                pattern_description = pattern.get("description", "")

                html += f"""
                <div style="background-color: #d4edda; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">📊 K线形态识别</div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">形态:</td>
                            <td style="padding: 8px;">{pattern_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">置信度:</td>
                            <td style="padding: 8px;">{pattern_confidence:.0%}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">交易信号:</td>
                            <td style="padding: 8px; font-weight: bold;">{pattern_signal}</td>
                        </tr>
                    </table>
                    <div style="margin-top: 10px; font-size: 13px; line-height: 1.6;">{pattern_description}</div>
                </div>
                """

            html += f"""
                <div style="background-color: #f8f9fa; color: #1a365d; padding: 15px; border-radius: 10px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">💡 分析理由</div>
                    <div style="font-size: 14px; line-height: 1.6;">{reasoning}</div>
                </div>

                <div style="text-align: left; margin: 10px 0;">
                    <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">📊 数据来源时间</div>
                    
                    <div style="background-color: #e3f2fd; color: #1a365d; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="font-size: 13px; font-weight: bold;">⏰ 数据时间: {data_source_time}</div>
                        <div style="font-size: 12px; color: #666;">
                            数据来源: {source_type}
                        </div>
                    </div>
                </div>
            </div>
            """

            self.chat_browser.append(html)
            self.scroll_to_bottom()

        except Exception as e:
            error_html = f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="display: inline-block; max-width: 75%; background-color: #ffebee; color: #c62828;
                                    padding: 12px 18px; border-radius: 18px 18px 18px 4px;">
                    <div style="font-size: 14px;">⚠️ 显示分析结果失败: {str(e)}</div>
                </div>
            </div>
            """
            self.chat_browser.append(error_html)
            self.scroll_to_bottom()

    def display_decision_dashboard(self, analysis: dict):
        """@显示决策仪表盘"""
        try:
            stock_code = analysis.get("stock_code", "")
            trend = analysis.get("trend", "")
            recommendation = analysis.get("recommendation", "")
            risk_level = analysis.get("risk_level", "")
            deviation_rate = analysis.get("deviation_rate", 0)
            is_bullish = analysis.get("is_bullish", False)
            buy_price = analysis.get("buy_price", 0)
            stop_loss = analysis.get("stop_loss", 0)
            target_price = analysis.get("target_price", 0)
            checklist = analysis.get("checklist", {})
            
            # 获取数据来源时间
            import time
            data_source_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # 判断数据来源类型
            if self.data_manager._use_mock_data:
                source_type = "模拟数据"
                source_color = "#e67a00"
            elif stock_code in self.data_manager._cache_timestamps:
                cache_time = self.data_manager._cache_timestamps[stock_code]
                if time.time() - cache_time < 300:  # 5分钟内
                    source_type = "缓存数据"
                    source_color = "#666"
                else:
                    source_type = "缓存数据"
                    source_color = "#999"
            else:
                source_type = "实时数据"
                source_color = "#27ae60"
            
            # 判断操作类型
            if recommendation in ["买入", "持有"]:
                operation_type = "🟢 买入"
                operation_color = "#27ae60"
            elif recommendation in ["观望", "减仓"]:
                operation_type = "🟡 观望"
                operation_color = "#f39c12"
            else:
                operation_type = "🔴 卖出"
                operation_color = "#e74c3c"

            # 判断乖离率风险
            if deviation_rate > 5:
                deviation_warning = "⚠️ 乖离率{deviation_rate:.2f}%超过5%警戒线,严禁追高"
                deviation_color = "#e74c3c"
            elif deviation_rate > 2:
                deviation_warning = "✅ 乖离率{deviation_rate:.2f}%处于最佳买点"
                deviation_color = "#27ae60"
            else:
                deviation_warning = f"✅ 乖离率{deviation_rate:.2f}%处于安全范围"
                deviation_color = "#27ae60"

            html = f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">📊 决策仪表盘</div>
                
                <div style="background-color: #f8f9fa; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">{operation_type}</div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">股票代码:</td>
                            <td style="padding: 8px;">{stock_code}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">趋势:</td>
                            <td style="padding: 8px;">{trend}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">操作建议:</td>
                            <td style="padding: 8px; font-weight: bold; color: {operation_color};">{recommendation}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">风险等级:</td>
                            <td style="padding: 8px;">{risk_level}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #fff3cd; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">💰 精确点位</div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">买入价:</td>
                            <td style="padding: 8px; font-weight: bold; color: #27ae60;">{buy_price:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">止损价:</td>
                            <td style="padding: 8px; font-weight: bold; color: #e74c3c;">{stop_loss:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">目标价:</td>
                            <td style="padding: 8px; font-weight: bold; color: #27ae60;">{target_price:.2f}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #d4edda; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">✅ 检查清单</div>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">多头排列:</td>
                            <td style="padding: 8px; font-weight: bold; color: {'#27ae60' if checklist.get('多头排列') == '满足' else '#e74c3c'};">{checklist.get('多头排列', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">乖离安全:</td>
                            <td style="padding: 8px; font-weight: bold; color: {deviation_color};">{checklist.get('乖离安全', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">量能配合:</td>
                            <td style="padding: 8px; font-weight: bold; color: {'#27ae60' if checklist.get('量能配合') == '满足' else '#e74c3c'};">{checklist.get('量能配合', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">趋势向上:</td>
                            <td style="padding: 8px; font-weight: bold; color: {'#27ae60' if checklist.get('趋势向上') == '满足' else '#e74c3c'};">{checklist.get('趋势向上', 'N/A')}</td>
                        </tr>
                    </table>
                </div>

                <div style="background-color: #f8f9fa; color: #1a365d; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">⚠️ 风险提示</div>
                    <div style="font-size: 14px; line-height: 1.6;">{deviation_warning}</div>
                </div>

                <div style="text-align: left; margin: 10px 0;">
                    <div style="font-size: 11px; color: #95a5a6; margin-bottom: 5px;">📊 数据来源时间</div>
                    
                    <div style="background-color: #f0f8ff; color: #1a365d; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="font-size: 13px; font-weight: bold;">⏰ 数据时间: {data_source_time}</div>
                        <div style="font-size: 12px; color: #666;">
                            数据来源: {source_type}
                        </div>
                    </div>
                </div>
            """

            self.chat_browser.append(html)
            self.scroll_to_bottom()
        except Exception as e:
            error_html = f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="display: inline-block; max-width: 75%; background-color: #ffebee; color: #c62828;
                                    padding: 12px 18px; border-radius: 18px 18px 18px 4px;">
                    <div style="font-size: 14px;">⚠️ 显示决策仪表盘失败: {str(e)}</div>
                </div>
            </div>
            """
            self.chat_browser.append(error_html)
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def handle_quick_command(self, prompt):
        """处理快捷指令"""
        if self.is_streaming:
            return

        self.input_field.setPlainText(prompt)
        self.send_message()

    def send_message(self):
        """发送消息"""
        if self.is_streaming:
            return

        user_message = self.input_field.toPlainText().strip()
        if not user_message:
            return

        self.display_user_message(user_message)
        self.input_field.clear()

        self.chat_history.append(user_message)

        self.chat_browser.append('<div style="text-align: center; color: #95a5a6; margin: 15px 0; font-size: 12px;">● ● ● 正在思考...</div>')
        self.scroll_to_bottom()

        QTimer.singleShot(100, self.process_ai_response)

    def process_ai_response(self):
        """处理AI响应 - 使用真实AI API"""
        try:
            cursor = self.chat_browser.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
            if cursor.selectedText().strip() == "● ● ● 正在思考...":
                cursor.removeSelectedText()

            user_message = self.chat_history[-1] if self.chat_history else ""

            # 准备上下文
            context = None
            if self.current_stock:
                context = {
                    "stock_code": self.current_stock.code,
                    "stock_name": self.current_stock.name,
                    "price": self.current_stock.price,
                    "change": self.current_stock.change
                }

            # 调用AI API
            if self.ai_engine:
                response = self.ai_engine.answer_question(user_message, context)

                if response:
                    self.stream_ai_response(response)
                else:
                    error_html = """
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="display: inline-block; max-width: 75%; background-color: #ffebee; color: #c62828;
                                    padding: 12px 18px; border-radius: 18px 18px 18px 4px;">
                            <div style="font-size: 14px;">⚠️ AI服务暂时不可用，请检查API配置。</div>
                        </div>
                    </div>
                    """
                    self.chat_browser.append(error_html)
                    self.scroll_to_bottom()
                    self.is_streaming = False
                    self.on_input_changed()
            else:
                error_html = """
                <div style="text-align: left; margin: 10px 0;">
                    <div style="display: inline-block; max-width: 75%; background-color: #ffebee; color: #c62828;
                                    padding: 12px 18px; border-radius: 18px 18px 18px 4px;">
                        <div style="font-size: 14px;">⚠️ AI引擎未初始化。</div>
                    </div>
                </div>
                """
                self.chat_browser.append(error_html)
                self.scroll_to_bottom()
                self.is_streaming = False
                self.on_input_changed()

        except Exception as e:
            error_html = f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="display: inline-block; max-width: 75%; background-color: #ffebee; color: #c62828;
                                    padding: 12px 18px; border-radius: 18px 18px 18px 4px;">
                    <div style="font-size: 14px;">⚠️ 发生错误: {str(e)}</div>
                </div>
            </div>
            """
            self.chat_browser.append(error_html)
            self.scroll_to_bottom()
            self.is_streaming = False
            self.on_input_changed()
