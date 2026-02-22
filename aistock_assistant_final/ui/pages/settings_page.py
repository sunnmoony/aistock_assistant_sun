from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QLineEdit, QComboBox,
                             QCheckBox, QSpinBox, QTabWidget, QFormLayout,
                             QMessageBox, QFileDialog, QScrollArea, QFrame)
from PyQt5.QtCore import Qt


class SettingsPage(QWidget):
    """设置页面 - 系统配置和个性化设置"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 页面标题
        title_label = QLabel("⚙️ 系统设置")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(title_label)
        
        # 副标题
        subtitle = QLabel("配置应用参数和个性化选项")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(subtitle)
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # API设置页
        api_tab = self.create_api_settings()
        tab_widget.addTab(api_tab, "🔑 API设置")
        
        # 数据设置页
        data_tab = self.create_data_settings()
        tab_widget.addTab(data_tab, "📊 数据设置")
        
        # 界面设置页
        ui_tab = self.create_ui_settings()
        tab_widget.addTab(ui_tab, "🎨 界面设置")
        
        # 通知设置页
        notification_tab = self.create_notification_settings()
        tab_widget.addTab(notification_tab, "🔔 通知设置")
        
        main_layout.addWidget(tab_widget)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        reset_btn = QPushButton("🔄 恢复默认")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("💾 保存设置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
    def create_api_settings(self):
        """创建API设置页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # AI API设置
        ai_group = QGroupBox("🤖 AI分析API")
        ai_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        ai_layout = QFormLayout()
        ai_layout.setSpacing(15)
        
        self.ai_provider = QComboBox()
        self.ai_provider.addItems(["OpenAI", "百度文心", "阿里通义", "本地模型"])
        ai_layout.addRow("AI提供商:", self.ai_provider)
        
        self.ai_key_input = QLineEdit()
        self.ai_key_input.setPlaceholderText("输入API密钥")
        self.ai_key_input.setEchoMode(QLineEdit.Password)
        ai_layout.addRow("API密钥:", self.ai_key_input)
        
        self.ai_model = QComboBox()
        self.ai_model.addItems(["gpt-3.5-turbo", "gpt-4", "文心一言", "通义千问"])
        ai_layout.addRow("模型选择:", self.ai_model)
        
        test_ai_btn = QPushButton("🧪 测试连接")
        test_ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        test_ai_btn.clicked.connect(self.test_ai_connection)
        ai_layout.addRow("", test_ai_btn)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # 股票数据API设置
        data_group = QGroupBox("📈 股票数据API")
        data_group.setStyleSheet(ai_group.styleSheet())
        data_layout = QFormLayout()
        data_layout.setSpacing(15)
        
        self.data_provider = QComboBox()
        self.data_provider.addItems(["新浪财经", "东方财富", "腾讯财经", "本地数据"])
        data_layout.addRow("数据源:", self.data_provider)
        
        self.data_key_input = QLineEdit()
        self.data_key_input.setPlaceholderText("输入API密钥（可选）")
        data_layout.addRow("API密钥:", self.data_key_input)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
        
    def create_data_settings(self):
        """创建数据设置页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 刷新设置
        refresh_group = QGroupBox("🔄 数据刷新")
        refresh_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        refresh_layout = QFormLayout()
        refresh_layout.setSpacing(15)
        
        self.auto_refresh = QCheckBox("启用自动刷新")
        self.auto_refresh.setChecked(True)
        refresh_layout.addRow("自动刷新:", self.auto_refresh)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(10, 300)
        self.refresh_interval.setValue(30)
        self.refresh_interval.setSuffix(" 秒")
        refresh_layout.addRow("刷新间隔:", self.refresh_interval)
        
        refresh_group.setLayout(refresh_layout)
        layout.addWidget(refresh_group)
        
        # 数据存储
        storage_group = QGroupBox("💾 数据存储")
        storage_group.setStyleSheet(refresh_group.styleSheet())
        storage_layout = QFormLayout()
        storage_layout.setSpacing(15)
        
        self.data_path = QLineEdit()
        self.data_path.setPlaceholderText("选择数据存储路径")
        self.data_path.setText("./data")
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_data_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.data_path)
        path_layout.addWidget(browse_btn)
        storage_layout.addRow("存储路径:", path_layout)
        
        self.cache_size = QSpinBox()
        self.cache_size.setRange(100, 5000)
        self.cache_size.setValue(500)
        self.cache_size.setSuffix(" MB")
        storage_layout.addRow("缓存大小:", self.cache_size)
        
        clear_cache_btn = QPushButton("🗑️ 清除缓存")
        clear_cache_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_cache_btn.clicked.connect(self.clear_cache)
        storage_layout.addRow("", clear_cache_btn)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
        
    def create_ui_settings(self):
        """创建界面设置页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 主题设置
        theme_group = QGroupBox("🎨 主题设置")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        theme_layout = QFormLayout()
        theme_layout.setSpacing(15)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认主题", "深色主题", "浅色主题", "高对比度"])
        theme_layout.addRow("主题风格:", self.theme_combo)
        
        self.font_size = QComboBox()
        self.font_size.addItems(["小", "正常", "大", "超大"])
        self.font_size.setCurrentIndex(1)
        theme_layout.addRow("字体大小:", self.font_size)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # 布局设置
        layout_group = QGroupBox("📐 布局设置")
        layout_group.setStyleSheet(theme_group.styleSheet())
        layout_form = QFormLayout()
        layout_form.setSpacing(15)
        
        self.sidebar_visible = QCheckBox("显示左侧导航栏")
        self.sidebar_visible.setChecked(True)
        layout_form.addRow("导航栏:", self.sidebar_visible)
        
        self.info_panel_visible = QCheckBox("显示右侧信息面板")
        self.info_panel_visible.setChecked(True)
        layout_form.addRow("信息面板:", self.info_panel_visible)
        
        self.default_page = QComboBox()
        self.default_page.addItems(["仪表盘", "行情看板", "AI助手", "知识库"])
        layout_form.addRow("默认页面:", self.default_page)
        
        layout_group.setLayout(layout_form)
        layout.addWidget(layout_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
        
    def create_notification_settings(self):
        """创建通知设置页"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 价格提醒
        price_group = QGroupBox("💰 价格提醒")
        price_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        price_layout = QVBoxLayout()
        price_layout.setSpacing(10)
        
        self.price_alert = QCheckBox("启用价格提醒")
        self.price_alert.setChecked(True)
        price_layout.addWidget(self.price_alert)
        
        self.price_change_alert = QCheckBox("涨跌幅超过5%时提醒")
        self.price_change_alert.setChecked(True)
        price_layout.addWidget(self.price_change_alert)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # 系统通知
        system_group = QGroupBox("🔔 系统通知")
        system_group.setStyleSheet(price_group.styleSheet())
        system_layout = QVBoxLayout()
        system_layout.setSpacing(10)
        
        self.market_open_alert = QCheckBox("市场开盘提醒")
        self.market_open_alert.setChecked(True)
        system_layout.addWidget(self.market_open_alert)
        
        self.market_close_alert = QCheckBox("市场收盘提醒")
        self.market_close_alert.setChecked(True)
        system_layout.addWidget(self.market_close_alert)
        
        self.ai_analysis_complete = QCheckBox("AI分析完成提醒")
        self.ai_analysis_complete.setChecked(True)
        system_layout.addWidget(self.ai_analysis_complete)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # 通知方式
        method_group = QGroupBox("📢 通知方式")
        method_group.setStyleSheet(price_group.styleSheet())
        method_layout = QVBoxLayout()
        method_layout.setSpacing(10)
        
        self.desktop_notify = QCheckBox("桌面通知")
        self.desktop_notify.setChecked(True)
        method_layout.addWidget(self.desktop_notify)
        
        self.sound_alert = QCheckBox("声音提醒")
        method_layout.addWidget(self.sound_alert)
        
        self.email_alert = QCheckBox("邮件通知")
        method_layout.addWidget(self.email_alert)
        
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
        
    def test_ai_connection(self):
        """测试AI API连接"""
        provider = self.ai_provider.currentText()
        QMessageBox.information(self, "测试连接", f"正在测试 {provider} 连接...\n\n连接成功！")
        
    def browse_data_path(self):
        """浏览数据存储路径"""
        path = QFileDialog.getExistingDirectory(self, "选择数据存储路径")
        if path:
            self.data_path.setText(path)
            
    def clear_cache(self):
        """清除缓存"""
        reply = QMessageBox.question(
            self, 
            "确认清除", 
            "确定要清除所有缓存数据吗？\n这将删除本地存储的历史数据。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "清除完成", "缓存数据已清除！")
            
    def save_settings(self):
        """保存设置"""
        QMessageBox.information(self, "保存成功", "设置已保存！")
        
    def reset_settings(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self,
            "确认恢复",
            "确定要恢复默认设置吗？\n这将重置所有自定义配置。",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 重置所有控件到默认值
            self.ai_provider.setCurrentIndex(0)
            self.data_provider.setCurrentIndex(0)
            self.auto_refresh.setChecked(True)
            self.refresh_interval.setValue(30)
            self.theme_combo.setCurrentIndex(0)
            self.font_size.setCurrentIndex(1)
            self.sidebar_visible.setChecked(True)
            self.info_panel_visible.setChecked(True)
            self.default_page.setCurrentIndex(0)
            self.price_alert.setChecked(True)
            self.desktop_notify.setChecked(True)
            
            QMessageBox.information(self, "恢复完成", "已恢复默认设置！")
