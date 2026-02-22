from PyQt5.QtWidgets import QApplication
import os


def get_stylesheet():
    """获取样式表"""
    style_file = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(style_file):
        with open(style_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""
