"""
全局样式表 - A股智能助手
统一的视觉风格和组件样式定义
"""

# 颜色主题
COLORS = {
    # 主色调
    'primary': '#3498db',
    'primary_dark': '#2980b9',
    'primary_light': '#5dade2',
    
    # 辅助色
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#9b59b6',
    
    # 中性色
    'dark': '#2c3e50',
    'gray': '#7f8c8d',
    'light_gray': '#95a5a6',
    'lighter_gray': '#bdc3c7',
    'light': '#ecf0f1',
    'white': '#ffffff',
    
    # 背景色
    'bg_primary': '#f5f6fa',
    'bg_secondary': '#ffffff',
    'bg_dark': '#2c3e50',
    
    # 边框色
    'border': '#e0e0e0',
    'border_dark': '#bdc3c7',
    
    # 文字色
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
    'text_light': '#95a5a6',
    'text_white': '#ffffff',
}

# 全局样式表
GLOBAL_STYLE = f"""
/* 全局基础样式 */
QWidget {{
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
    font-size: 14px;
    color: {COLORS['text_primary']};
}}

/* 主窗口 */
QMainWindow {{
    background-color: {COLORS['bg_primary']};
}}

/* 菜单栏 */
QMenuBar {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_white']};
    padding: 5px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 5px 15px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['primary']};
}}

QMenu {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 25px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_white']};
}}

/* 工具栏 */
QToolBar {{
    background-color: {COLORS['white']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 5px;
    spacing: 10px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
}}

QToolBar QToolButton:hover {{
    background-color: {COLORS['light']};
}}

/* 状态栏 */
QStatusBar {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_white']};
    padding: 5px;
}}

/* 按钮基础样式 */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_white']};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary']};
}}

QPushButton:disabled {{
    background-color: {COLORS['lighter_gray']};
    color: {COLORS['text_light']};
}}

/* 次要按钮 */
QPushButton.secondary {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: 1px solid {COLORS['primary']};
}}

QPushButton.secondary:hover {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_white']};
}}

/* 成功按钮 */
QPushButton.success {{
    background-color: {COLORS['success']};
}}

QPushButton.success:hover {{
    background-color: #229954;
}}

/* 警告按钮 */
QPushButton.warning {{
    background-color: {COLORS['warning']};
}}

QPushButton.warning:hover {{
    background-color: #d68910;
}}

/* 危险按钮 */
QPushButton.danger {{
    background-color: {COLORS['danger']};
}}

QPushButton.danger:hover {{
    background-color: #c0392b;
}}

/* 输入框 */
QLineEdit {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['primary']};
    outline: none;
}}

QLineEdit:disabled {{
    background-color: {COLORS['light']};
    color: {COLORS['text_light']};
}}

/* 文本编辑框 */
QTextEdit {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
    line-height: 1.6;
}}

QTextEdit:focus {{
    border: 2px solid {COLORS['primary']};
}}

/* 下拉框 */
QComboBox {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['gray']};
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['primary']};
}}

/* 表格 */
QTableWidget {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['primary']};
    selection-color: {COLORS['text_white']};
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
}}

QTableWidget::item:alternate {{
    background-color: #f8f9fa;
}}

QHeaderView::section {{
    background-color: {COLORS['light']};
    padding: 10px;
    border: none;
    border-bottom: 2px solid {COLORS['border_dark']};
    font-weight: bold;
    color: {COLORS['text_primary']};
}}

QHeaderView::section:hover {{
    background-color: {COLORS['lighter_gray']};
}}

/* 标签页 */
QTabWidget::pane {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['light']};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
    color: {COLORS['text_secondary']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['white']};
    color: {COLORS['primary']};
    border-bottom: 2px solid {COLORS['primary']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['lighter_gray']};
}}

/* 滚动条 */
QScrollBar:vertical {{
    background-color: {COLORS['light']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['lighter_gray']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['gray']};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['light']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['lighter_gray']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['gray']};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* 分组框 */
QGroupBox {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: {COLORS['text_secondary']};
}}

/* 列表 */
QListWidget {{
    background-color: {COLORS['white']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 5px;
}}

QListWidget::item {{
    padding: 10px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_white']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['light']};
}}

QListWidget::item:selected:hover {{
    background-color: {COLORS['primary_dark']};
}}

/* 复选框 */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {COLORS['border_dark']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary']};
}}

/* 单选框 */
QRadioButton {{
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid {COLORS['border_dark']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['primary']};
}}

/* 滑块 */
QSlider::groove:horizontal {{
    height: 6px;
    background-color: {COLORS['light']};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    width: 18px;
    height: 18px;
    margin: -6px 0;
    background-color: {COLORS['primary']};
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {COLORS['primary_dark']};
}}

QSlider::sub-page:horizontal {{
    background-color: {COLORS['primary']};
    border-radius: 3px;
}}

/* 进度条 */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: {COLORS['light']};
    text-align: center;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 4px;
}}

/* 分割器 */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* 工具提示 */
QToolTip {{
    background-color: {COLORS['dark']};
    color: {COLORS['text_white']};
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
}}
"""


def get_stylesheet():
    """获取全局样式表"""
    return GLOBAL_STYLE


def get_color(name):
    """获取颜色值
    
    Args:
        name: 颜色名称
        
    Returns:
        颜色值字符串
    """
    return COLORS.get(name, COLORS['primary'])
