from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, QMetaObject, Qt
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging
import threading
import functools

logger = logging.getLogger(__name__)


def 超时装饰器(超时时间: float = 10.0):
    """
    超时装饰器，用于限制函数执行时间

    Args:
        超时时间: 最大执行时间（秒），默认10秒

    Returns:
        装饰后的函数
    """
    def 装饰器(函数):
        @functools.wraps(函数)
        def 包装函数(*args, **kwargs):
            线程池 = ThreadPoolExecutor(max_workers=1)
            try:
                未来对象 = 线程池.submit(函数, *args, **kwargs)
                return 未来对象.result(timeout=超时时间)
            except TimeoutError:
                raise TimeoutError(f"函数执行超时（{超时时间}秒）")
            finally:
                线程池.shutdown(wait=False)
        return 包装函数
    return 装饰器


class EventHandler(QObject):
    """统一事件处理器 - 处理所有应用事件，支持超时控制"""

    event_processed = pyqtSignal(str, dict)
    event_failed = pyqtSignal(str, str)

    def __init__(self, event_bus=None, data_manager=None, ai_engine=None,
                 knowledge_base=None, navigation_manager=None,
                 notification_manager=None, 超时时间: float = 10.0):
        """
        初始化事件处理器

        Args:
            event_bus: 事件总线实例
            data_manager: 数据管理器实例
            ai_engine: AI引擎实例
            knowledge_base: 知识库实例
            navigation_manager: 导航管理器实例
            notification_manager: 通知管理器实例
            超时时间: 事件处理最大超时时间（秒），默认10秒
        """
        super().__init__()
        self.event_bus = event_bus
        self.data_manager = data_manager
        self.ai_engine = ai_engine
        self.knowledge_base = knowledge_base
        self.navigation_manager = navigation_manager
        self.notification_manager = notification_manager
        self.超时时间 = 超时时间

        self.处理器映射: Dict[str, callable] = {}
        self.注册处理器()

    def 注册处理器(self):
        """注册事件处理器"""
        self.处理器映射["stock.select"] = self.处理股票选择
        self.处理器映射["stock.add_to_watchlist"] = self.处理添加自选股
        self.处理器映射["stock.remove"] = self.处理移除股票
        self.处理器映射["stock.analyze"] = self.处理股票分析
        self.处理器映射["stock.search"] = self.处理股票搜索

        self.处理器映射["ai.query"] = self.处理AI查询
        self.处理器映射["ai.analyze_chart"] = self.处理图表分析
        self.处理器映射["ai.save_strategy"] = self.处理保存策略

        self.处理器映射["knowledge.upload"] = self.处理知识库上传
        self.处理器映射["knowledge.search"] = self.处理知识库搜索
        self.处理器映射["knowledge.apply"] = self.处理知识库应用

        self.处理器映射["system.update"] = self.处理系统更新
        self.处理器映射["system.export"] = self.处理系统导出
        self.处理器映射["system.backup"] = self.处理系统备份

        logger.info("事件处理器注册完成")

    @超时装饰器(10.0)
    def 处理事件(self, 事件类型: str, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理事件（带超时控制）

        Args:
            事件类型: 事件类型
            数据: 事件数据

        Returns:
            处理结果
        """
        try:
            if 事件类型 in self.处理器映射:
                结果 = self.处理器映射[事件类型](数据)
                self.event_processed.emit(事件类型, 结果)
                return {"success": True, "data": 结果}
            else:
                错误信息 = f"未知事件类型: {事件类型}"
                logger.error(错误信息)
                self.event_failed.emit(事件类型, 错误信息)
                return {"success": False, "error": 错误信息}
        except TimeoutError as e:
            错误信息 = f"处理事件超时 {事件类型}: {str(e)}"
            logger.error(错误信息)
            self.event_failed.emit(事件类型, 错误信息)
            return {"success": False, "error": 错误信息}
        except Exception as e:
            错误信息 = f"处理事件失败 {事件类型}: {str(e)}"
            logger.error(错误信息)
            self.event_failed.emit(事件类型, 错误信息)
            return {"success": False, "error": 错误信息}

    def 处理股票选择(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理股票选择事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        股票代码 = 数据.get("code")

        if not 股票代码:
            return {"success": False, "error": "缺少股票代码"}

        股票数据 = self.data_manager.get_realtime_quote(股票代码) if self.data_manager else None

        if self.event_bus:
            self.event_bus.publish("stock.selected", {
                "code": 股票代码,
                "data": 股票数据
            })

        if 数据.get("analyze", False) and self.navigation_manager:
            self.navigation_manager.navigate_to("ai_assistant", {
                "context": f"分析股票 {股票代码}",
                "stock_data": 股票数据
            })

        return {"success": True, "data": 股票数据}

    def 处理添加自选股(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理添加自选股事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        股票代码 = 数据.get("code")

        if not 股票代码:
            return {"success": False, "error": "缺少股票代码"}

        if self.data_manager:
            成功 = self.data_manager.add_to_watchlist(股票代码)

            if 成功 and self.notification_manager:
                self.notification_manager.notify(
                    "添加自选股",
                    f"已将 {股票代码} 添加到自选股",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("watchlist.added", {"code": 股票代码})

            return {"success": 成功}

        return {"success": False, "error": "数据管理器未初始化"}

    def 处理移除股票(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理移除股票事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        股票代码 = 数据.get("code")

        if not 股票代码:
            return {"success": False, "error": "缺少股票代码"}

        if self.data_manager:
            成功 = self.data_manager.remove_from_watchlist(股票代码)

            if 成功 and self.notification_manager:
                self.notification_manager.notify(
                    "移除自选股",
                    f"已从自选股移除 {股票代码}",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("watchlist.removed", {"code": 股票代码})

            return {"success": 成功}

        return {"success": False, "error": "数据管理器未初始化"}

    def 处理股票分析(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理股票分析事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        股票代码 = 数据.get("code")
        股票数据 = 数据.get("stock_data")

        if not 股票代码:
            return {"success": False, "error": "缺少股票代码"}

        if not 股票数据 and self.data_manager:
            股票数据 = self.data_manager.get_realtime_quote(股票代码)

        if self.ai_engine:
            分析结果 = self.ai_engine.analyze_stock(股票代码, 股票数据)

            if 分析结果.get("success"):
                if self.event_bus:
                    self.event_bus.publish("stock.analyzed", {
                        "code": 股票代码,
                        "analysis": 分析结果.get("data")
                    })

            return 分析结果

        return {"success": False, "error": "AI引擎未初始化"}

    def 处理股票搜索(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理股票搜索事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        关键词 = 数据.get("keyword", "")

        if self.data_manager:
            结果 = self.data_manager.search_stocks(关键词)
            return {"success": True, "data": 结果}

        return {"success": False, "error": "数据管理器未初始化"}

    def 处理AI查询(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI查询事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        查询内容 = 数据.get("query")
        上下文 = 数据.get("context")

        if not 查询内容:
            return {"success": False, "error": "缺少查询内容"}

        if self.ai_engine:
            响应 = self.ai_engine.analyze_with_context(查询内容, 上下文)

            if self.event_bus:
                self.event_bus.publish("ai.response", {
                    "query": 查询内容,
                    "response": 响应
                })

            return {"success": True, "data": 响应}

        return {"success": False, "error": "AI引擎未初始化"}

    def 处理图表分析(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理图表分析事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        价格数据 = 数据.get("price_data", [])

        if not 价格数据:
            return {"success": False, "error": "缺少价格数据"}

        if self.ai_engine:
            模式结果 = self.ai_engine.detect_pattern(价格数据)

            if 模式结果.get("success"):
                if self.event_bus:
                    self.event_bus.publish("chart.analyzed", {
                        "pattern": 模式结果.get("data")
                    })

            return 模式结果

        return {"success": False, "error": "AI引擎未初始化"}

    def 处理保存策略(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理保存策略事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        策略名称 = 数据.get("name")
        策略内容 = 数据.get("content")

        if not 策略名称 or not 策略内容:
            return {"success": False, "error": "缺少策略名称或内容"}

        if self.knowledge_base:
            文档ID = f"strategy_{策略名称}"
            成功 = self.knowledge_base.add_document(
                doc_id=文档ID,
                title=策略名称,
                content=策略内容,
                category="投资策略",
                tags=["策略", "投资"]
            )

            if 成功 and self.notification_manager:
                self.notification_manager.notify(
                    "策略保存",
                    f"投资策略 {策略名称} 已保存",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("strategy.saved", {
                    "name": 策略名称,
                    "doc_id": 文档ID
                })

            return {"success": 成功}

        return {"success": False, "error": "知识库未初始化"}

    def 处理知识库上传(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识库上传事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        文件路径 = 数据.get("file_path")
        标题 = 数据.get("title")
        分类 = 数据.get("category", "上传文档")
        标签 = 数据.get("tags", [])

        if not 文件路径:
            return {"success": False, "error": "缺少文件路径"}

        if self.knowledge_base:
            成功 = self.knowledge_base.import_document(
                file_path=文件路径,
                title=标题,
                category=分类,
                tags=标签
            )

            if 成功 and self.notification_manager:
                self.notification_manager.notify(
                    "文档上传",
                    f"文档 {标题 or 文件路径} 已上传到知识库",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("knowledge.uploaded", {
                    "file_path": 文件路径,
                    "title": 标题
                })

            return {"success": 成功}

        return {"success": False, "error": "知识库未初始化"}

    def 处理知识库搜索(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识库搜索事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        关键词 = 数据.get("keyword", "")
        分类 = 数据.get("category")
        标签 = 数据.get("tags")

        if self.knowledge_base:
            结果 = self.knowledge_base.search_documents(
                keyword=关键词,
                category=分类,
                tags=标签
            )

            if self.event_bus:
                self.event_bus.publish("knowledge.searched", {
                    "keyword": 关键词,
                    "results": 结果
                })

            return {"success": True, "data": 结果}

        return {"success": False, "error": "知识库未初始化"}

    def 处理知识库应用(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理知识库应用事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        文档ID = 数据.get("doc_id")

        if not 文档ID:
            return {"success": False, "error": "缺少文档ID"}

        if self.knowledge_base:
            文档 = self.knowledge_base.get_document(文档ID)

            if 文档:
                if self.event_bus:
                    self.event_bus.publish("knowledge.applied", {
                        "doc_id": 文档ID,
                        "document": 文档
                    })

                return {"success": True, "data": 文档}

            return {"success": False, "error": "文档不存在"}

        return {"success": False, "error": "知识库未初始化"}

    def 处理系统更新(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理系统更新事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        更新类型 = 数据.get("type", "all")

        if self.data_manager:
            if 更新类型 in ["all", "market"]:
                self.data_manager.update_market_data()
            if 更新类型 in ["all", "watchlist"]:
                self.data_manager.update_watchlist_data()

        if self.event_bus:
            self.event_bus.publish("system.updated", {"type": 更新类型})

        if self.notification_manager:
            self.notification_manager.notify(
                "系统更新",
                f"数据已更新: {更新类型}",
                "info"
            )

        return {"success": True}

    def 处理系统导出(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理系统导出事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        导出类型 = 数据.get("type", "config")
        导出路径 = 数据.get("path")

        if not 导出路径:
            return {"success": False, "error": "缺少导出路径"}

        try:
            if 导出类型 == "config":
                if self.event_bus and hasattr(self.event_bus, 'config_manager'):
                    成功 = self.event_bus.config_manager.export_config(导出路径)
                else:
                    return {"success": False, "error": "配置管理器未初始化"}
            else:
                return {"success": False, "error": "不支持的导出类型"}

            if 成功 and self.notification_manager:
                self.notification_manager.notify(
                    "导出成功",
                    f"数据已导出到 {导出路径}",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("system.exported", {
                    "type": 导出类型,
                    "path": 导出路径
                })

            return {"success": 成功}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def 处理系统备份(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理系统备份事件

        Args:
            数据: 事件数据

        Returns:
            处理结果
        """
        备份路径 = 数据.get("path", "backup")

        try:
            import shutil
            import os
            from datetime import datetime

            时间戳 = datetime.now().strftime("%Y%m%d_%H%M%S")
            备份目录 = f"{备份路径}/backup_{时间戳}"

            os.makedirs(备份目录, exist_ok=True)

            数据目录列表 = ["data", "config.yaml"]
            for 项目 in 数据目录列表:
                if os.path.exists(项目):
                    目标路径 = os.path.join(备份目录, 项目)
                    if os.path.isdir(项目):
                        shutil.copytree(项目, 目标路径, dirs_exist_ok=True)
                    else:
                        shutil.copy2(项目, 目标路径)

            if self.notification_manager:
                self.notification_manager.notify(
                    "备份成功",
                    f"系统已备份到 {备份目录}",
                    "info"
                )

            if self.event_bus:
                self.event_bus.publish("system.backed_up", {
                    "path": 备份目录
                })

            return {"success": True, "data": {"path": 备份目录}}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def 设置事件总线(self, event_bus):
        """
        设置事件总线

        Args:
            event_bus: 事件总线实例
        """
        self.event_bus = event_bus

    def 设置数据管理器(self, data_manager):
        """
        设置数据管理器

        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager

    def 设置AI引擎(self, ai_engine):
        """
        设置AI引擎

        Args:
            ai_engine: AI引擎实例
        """
        self.ai_engine = ai_engine

    def 设置知识库(self, knowledge_base):
        """
        设置知识库

        Args:
            knowledge_base: 知识库实例
        """
        self.knowledge_base = knowledge_base

    def 设置导航管理器(self, navigation_manager):
        """
        设置导航管理器

        Args:
            navigation_manager: 导航管理器实例
        """
        self.navigation_manager = navigation_manager

    def 设置通知管理器(self, notification_manager):
        """
        设置通知管理器

        Args:
            notification_manager: 通知管理器实例
        """
        self.notification_manager = notification_manager

    # 保留英文方法名以保持向后兼容
    register_handlers = 注册处理器
    handle_event = 处理事件
    handle_stock_select = 处理股票选择
    handle_add_to_watchlist = 处理添加自选股
    handle_stock_remove = 处理移除股票
    handle_stock_analyze = 处理股票分析
    handle_stock_search = 处理股票搜索
    handle_ai_query = 处理AI查询
    handle_analyze_chart = 处理图表分析
    handle_save_strategy = 处理保存策略
    handle_knowledge_upload = 处理知识库上传
    handle_knowledge_search = 处理知识库搜索
    handle_knowledge_apply = 处理知识库应用
    handle_system_update = 处理系统更新
    handle_system_export = 处理系统导出
    handle_system_backup = 处理系统备份
    set_event_bus = 设置事件总线
    set_data_manager = 设置数据管理器
    set_ai_engine = 设置AI引擎
    set_knowledge_base = 设置知识库
    set_navigation_manager = 设置导航管理器
    set_notification_manager = 设置通知管理器
