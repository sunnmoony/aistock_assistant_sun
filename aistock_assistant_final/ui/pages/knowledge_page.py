from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QTextBrowser, QPushButton,
                             QSplitter, QFrame, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


class KnowledgePage(QWidget):
    """知识库页面 - 用户文档管理"""

    def __init__(self):
        super().__init__()
        self.knowledge_base = None
        self.event_bus = None
        self.notification_manager = None
        self.current_document = None
        self.init_ui()
    
    def set_knowledge_base(self, knowledge_base):
        """设置知识库"""
        self.knowledge_base = knowledge_base
    
    def set_event_bus(self, event_bus):
        """设置事件总线"""
        self.event_bus = event_bus
    
    def set_notification_manager(self, notification_manager):
        """设置通知管理器"""
        self.notification_manager = notification_manager

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 页面标题
        title_label = QLabel("📚 知识库")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        main_layout.addWidget(title_label)

        # 副标题
        subtitle = QLabel("管理您的投资文档和知识资料")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(subtitle)

        # 按钮栏
        button_layout = QHBoxLayout()

        # 上传文档按钮
        upload_btn = QPushButton("📤 上传文档")
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        upload_btn.clicked.connect(self.upload_document)
        button_layout.addWidget(upload_btn)

        button_layout.addStretch()

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        refresh_btn.clicked.connect(self.load_documents)
        button_layout.addWidget(refresh_btn)

        # 删除按钮
        delete_btn = QPushButton("🗑️ 删除")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        delete_btn.clicked.connect(self.delete_document)
        button_layout.addWidget(delete_btn)

        main_layout.addLayout(button_layout)

        # 分割器：左侧文档列表 + 右侧预览区
        splitter = QSplitter(Qt.Horizontal)

        # 左侧文档列表
        left_panel = self.create_document_list_panel()
        splitter.addWidget(left_panel)

        # 右侧预览区
        right_panel = self.create_preview_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([350, 650])
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

    def create_document_list_panel(self):
        """创建左侧文档列表面板"""
        panel = QFrame()
        panel.setObjectName("documentListPanel")
        panel.setStyleSheet("""
            QFrame#documentListPanel {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题
        title = QLabel("📄 文档列表")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(title)

        # 文档列表
        self.doc_list = QListWidget()
        self.doc_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 5px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected:hover {
                background-color: #2980b9;
            }
        """)
        self.doc_list.itemClicked.connect(self.on_document_selected)
        layout.addWidget(self.doc_list)

        panel.setLayout(layout)
        return panel

    def create_preview_panel(self):
        """创建右侧预览面板"""
        panel = QFrame()
        panel.setObjectName("previewPanel")
        panel.setStyleSheet("""
            QFrame#previewPanel {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        self.preview_title = QLabel("📖 文档预览")
        self.preview_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        layout.addWidget(self.preview_title)

        # 预览区
        self.preview_browser = QTextBrowser()
        self.preview_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
                padding: 15px;
                font-size: 14px;
                line-height: 1.8;
                color: #34495e;
            }
        """)
        self.preview_browser.setOpenExternalLinks(True)
        layout.addWidget(self.preview_browser)

        panel.setLayout(layout)
        return panel

    def load_documents(self):
        """加载文档列表"""
        self.doc_list.clear()
        
        # 检查知识库是否已设置
        if not self.knowledge_base:
            item = QListWidgetItem("📚 知识库功能正在完善中...")
            self.doc_list.addItem(item)
            return
        
        try:
            documents = self.knowledge_base.list_documents()

            for doc in documents:
                # 创建列表项
                item = QListWidgetItem()

                # 格式化显示文本
                filename = doc['filename']
                created_time = self.format_datetime(doc['created_time'])
                display_text = f"📄 {filename}\n📅 {created_time}"

                item.setText(display_text)
                item.setData(Qt.UserRole, doc)

                # 设置字体样式
                font = QFont()
                font.setPointSize(11)
                item.setFont(font)
                self.doc_list.addItem(item)

            if not documents:
                empty_item = QListWidgetItem("📭 暂无文档\n请点击上方按钮上传文档")
                empty_item.setFlags(Qt.NoItemFlags)
                empty_item.setTextAlignment(Qt.AlignCenter)
                self.doc_list.addItem(empty_item)
        except Exception as e:
            logger.error(f"加载文档列表失败: {e}")
            error_item = QListWidgetItem("❌ 加载文档失败，请检查知识库配置")
            self.doc_list.addItem(error_item)

    def format_datetime(self, datetime_str):
        """格式化日期时间"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(datetime_str)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return datetime_str

    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} B"

    def on_document_selected(self, item):
        """文档选择处理"""
        doc = item.data(Qt.UserRole)
        if not doc:
            return

        self.current_document = doc
        self.preview_document(doc)

    def preview_document(self, doc):
        """预览文档"""
        filename = doc['filename']
        file_type = doc['file_type'].lower()
        file_size = self.format_file_size(doc['size'])
        created_time = self.format_datetime(doc['created_time'])

        self.preview_title.setText(f"📖 {filename}")

        # 文本文件显示内容
        if file_type in ['.txt', '.md']:
            content = self.knowledge_base.get_document_content(doc['id'])
            if content:
                # 对于Markdown文件,简单格式化
                if file_type == '.md':
                    html_content = self.markdown_to_html(content)
                    self.preview_browser.setHtml(html_content)
                else:
                    self.preview_browser.setPlainText(content)
            else:
                self.preview_browser.setPlainText("无法读取文档内容")
        else:
            # 非文本文件显示文件信息
            info_html = f"""
            <h2>📄 文件信息</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; font-weight: bold; width: 120px;">文件名:</td>
                    <td style="padding: 10px;">{filename}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; font-weight: bold;">文件类型:</td>
                    <td style="padding: 10px;">{file_type.upper()}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; font-weight: bold;">文件大小:</td>
                    <td style="padding: 10px;">{file_size}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; font-weight: bold;">上传时间:</td>
                    <td style="padding: 10px;">{created_time}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 10px; font-weight: bold;">文件路径:</td>
                    <td style="padding: 10px; font-family: monospace; font-size: 12px;">{doc['path']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold;">分类:</td>
                    <td style="padding: 10px;">{doc['category']}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #7f8c8d;">
                ℹ️ 此文件类型不支持直接预览,请下载后使用相应软件打开。
            </p>
            """
            self.preview_browser.setHtml(info_html)

    def markdown_to_html(self, markdown_text):
        """简单的Markdown转HTML"""
        html = markdown_text
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        html = f"<p>{html}</p>"
        html = html.replace('<h1>', '<h1>').replace('</h1>', '</h1>')
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        html = html.replace('*', '<em>').replace('*', '</em>')
        return html

    def upload_document(self):
        """上传文档"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter(
            "所有文件 (*.*);;文本文件 (*.txt);;Markdown (*.md);;PDF文件 (*.pdf);;Word文档 (*.doc *.docx);;Excel表格 (*.xls *.xlsx)"
        )

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                if os.path.exists(file_path):
                    result = self.knowledge_base.add_document(file_path, category="未分类")
                    if result:
                        QMessageBox.information(
                            self,
                            "上传成功",
                            f"文档 '{os.path.basename(file_path)}' 上传成功!"
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "上传失败",
                            f"文档 '{os.path.basename(file_path)}' 上传失败!"
                        )
                else:
                    QMessageBox.warning(
                        self,
                        "文件不存在",
                        f"文件 '{file_path}' 不存在!"
                    )

            self.load_documents()

    def delete_document(self):
        """删除选中的文档"""
        current_item = self.doc_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要删除的文档")
            return

        doc = current_item.data(Qt.UserRole)
        if not doc:
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除文档 '{doc['filename']}' 吗?\n此操作不可撤销!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.knowledge_base.delete_document(doc['id'])
            if success:
                QMessageBox.information(self, "删除成功", "文档已删除")
                self.load_documents()
                self.preview_browser.clear()
                self.preview_title.setText("📖 文档预览")
            else:
                QMessageBox.warning(self, "删除失败", "文档删除失败")
