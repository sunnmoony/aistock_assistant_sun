from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal
import logging
import json
import os

logger = logging.getLogger(__name__)


class KnowledgeBase(QObject):
    """知识库系统 - 管理文档和知识"""
    
    document_added = pyqtSignal(str, dict)
    document_removed = pyqtSignal(str)
    document_updated = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._tags: Dict[str, List[str]] = {}
        self._knowledge_path = "data/knowledge"
        self._index_file = "data/knowledge/index.json"
        
        self._load_index()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录存在"""
        try:
            os.makedirs(self._knowledge_path, exist_ok=True)
            os.makedirs(f"{self._knowledge_path}/documents", exist_ok=True)
            os.makedirs(f"{self._knowledge_path}/categories", exist_ok=True)
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
    
    def _load_index(self):
        """加载索引"""
        try:
            if os.path.exists(self._index_file):
                with open(self._index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    self._documents = index_data.get("documents", {})
                    self._categories = index_data.get("categories", {})
                    self._tags = index_data.get("tags", {})
                logger.info(f"加载知识库索引: {len(self._documents)}个文档")
        except Exception as e:
            logger.error(f"加载索引失败: {e}")
            self._documents = {}
            self._categories = {}
            self._tags = {}
    
    def _save_index(self):
        """保存索引"""
        try:
            os.makedirs(os.path.dirname(self._index_file), exist_ok=True)
            index_data = {
                "documents": self._documents,
                "categories": self._categories,
                "tags": self._tags
            }
            with open(self._index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            logger.info("保存知识库索引")
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
    
    def add_document(self, doc_id: str, title: str, content: str, 
                    category: str = "未分类", tags: List[str] = None,
                    metadata: Dict[str, Any] = None) -> bool:
        """
        添加文档
        
        Args:
            doc_id: 文档ID
            title: 文档标题
            content: 文档内容
            category: 分类
            tags: 标签列表
            metadata: 元数据
            
        Returns:
            是否添加成功
        """
        try:
            if doc_id in self._documents:
                logger.warning(f"文档已存在: {doc_id}")
                return False
            
            document = {
                "id": doc_id,
                "title": title,
                "content": content,
                "category": category,
                "tags": tags or [],
                "metadata": metadata or {},
                "created_at": self._get_timestamp(),
                "updated_at": self._get_timestamp()
            }
            
            self._documents[doc_id] = document
            self._add_to_category(category, doc_id)
            self._add_to_tags(tags or [], doc_id)
            
            self._save_document_file(doc_id, content)
            self._save_index()
            
            self.document_added.emit(doc_id, document)
            logger.info(f"添加文档: {doc_id} - {title}")
            return True
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _add_to_category(self, category: str, doc_id: str):
        """
        添加到分类
        
        Args:
            category: 分类名称
            doc_id: 文档ID
        """
        if category not in self._categories:
            self._categories[category] = []
        if doc_id not in self._categories[category]:
            self._categories[category].append(doc_id)
    
    def _add_to_tags(self, tags: List[str], doc_id: str):
        """
        添加到标签
        
        Args:
            tags: 标签列表
            doc_id: 文档ID
        """
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = []
            if doc_id not in self._tags[tag]:
                self._tags[tag].append(doc_id)
    
    def _save_document_file(self, doc_id: str, content: str):
        """
        保存文档文件
        
        Args:
            doc_id: 文档ID
            content: 内容
        """
        try:
            file_path = f"{self._knowledge_path}/documents/{doc_id}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"保存文档文件失败: {e}")
    
    def update_document(self, doc_id: str, title: str = None, 
                       content: str = None, category: str = None,
                       tags: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        更新文档
        
        Args:
            doc_id: 文档ID
            title: 标题
            content: 内容
            category: 分类
            tags: 标签
            metadata: 元数据
            
        Returns:
            是否更新成功
        """
        try:
            if doc_id not in self._documents:
                logger.warning(f"文档不存在: {doc_id}")
                return False
            
            document = self._documents[doc_id]
            
            old_category = document["category"]
            old_tags = document["tags"].copy()
            
            if title is not None:
                document["title"] = title
            if content is not None:
                document["content"] = content
                self._save_document_file(doc_id, content)
            if category is not None and category != old_category:
                self._remove_from_category(old_category, doc_id)
                self._add_to_category(category, doc_id)
                document["category"] = category
            if tags is not None:
                self._remove_from_tags(old_tags, doc_id)
                self._add_to_tags(tags, doc_id)
                document["tags"] = tags
            if metadata is not None:
                document["metadata"].update(metadata)
            
            document["updated_at"] = self._get_timestamp()
            
            self._save_index()
            self.document_updated.emit(doc_id, document)
            
            logger.info(f"更新文档: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"更新文档失败: {e}")
            return False
    
    def _remove_from_category(self, category: str, doc_id: str):
        """
        从分类移除
        
        Args:
            category: 分类名称
            doc_id: 文档ID
        """
        if category in self._categories and doc_id in self._categories[category]:
            self._categories[category].remove(doc_id)
    
    def _remove_from_tags(self, tags: List[str], doc_id: str):
        """
        从标签移除
        
        Args:
            tags: 标签列表
            doc_id: 文档ID
        """
        for tag in tags:
            if tag in self._tags and doc_id in self._tags[tag]:
                self._tags[tag].remove(doc_id)
    
    def remove_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            if doc_id not in self._documents:
                logger.warning(f"文档不存在: {doc_id}")
                return False
            
            document = self._documents[doc_id]
            
            self._remove_from_category(document["category"], doc_id)
            self._remove_from_tags(document["tags"], doc_id)
            
            del self._documents[doc_id]
            
            self._delete_document_file(doc_id)
            self._save_index()
            
            self.document_removed.emit(doc_id)
            logger.info(f"删除文档: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    def _delete_document_file(self, doc_id: str):
        """
        删除文档文件
        
        Args:
            doc_id: 文档ID
        """
        try:
            file_path = f"{self._knowledge_path}/documents/{doc_id}.txt"
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"删除文档文件失败: {e}")
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档数据
        """
        return self._documents.get(doc_id)
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        获取所有文档
        
        Returns:
            文档列表
        """
        return list(self._documents.values())
    
    def search_documents(self, keyword: str, category: str = None, 
                       tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        搜索文档
        
        Args:
            keyword: 关键词
            category: 分类
            tags: 标签列表
            
        Returns:
            文档列表
        """
        try:
            results = []
            
            for doc_id, document in self._documents.items():
                if category and document["category"] != category:
                    continue
                
                if tags:
                    if not any(tag in document["tags"] for tag in tags):
                        continue
                
                if keyword:
                    keyword_lower = keyword.lower()
                    if (keyword_lower in document["title"].lower() or 
                        keyword_lower in document["content"].lower()):
                        results.append(document)
                else:
                    results.append(document)
            
            logger.info(f"搜索文档: {keyword}, 结果: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        return list(self._categories.keys())
    
    def get_category_documents(self, category: str) -> List[Dict[str, Any]]:
        """
        获取分类下的文档
        
        Args:
            category: 分类名称
            
        Returns:
            文档列表
        """
        if category not in self._categories:
            return []
        
        doc_ids = self._categories[category]
        return [self._documents[doc_id] for doc_id in doc_ids if doc_id in self._documents]
    
    def get_tags(self) -> List[str]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        return list(self._tags.keys())
    
    def get_tag_documents(self, tag: str) -> List[Dict[str, Any]]:
        """
        获取标签下的文档
        
        Args:
            tag: 标签名称
            
        Returns:
            文档列表
        """
        if tag not in self._tags:
            return []
        
        doc_ids = self._tags[tag]
        return [self._documents[doc_id] for doc_id in doc_ids if doc_id in self._documents]
    
    def import_document(self, file_path: str, title: str = None, 
                       category: str = "导入文档", tags: List[str] = None) -> bool:
        """
        导入文档
        
        Args:
            file_path: 文件路径
            title: 标题
            category: 分类
            tags: 标签
            
        Returns:
            是否导入成功
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not title:
                title = os.path.basename(file_path)
            
            doc_id = f"doc_{self._get_timestamp()}_{hash(file_path)}"
            
            return self.add_document(doc_id, title, content, category, tags)
        except Exception as e:
            logger.error(f"导入文档失败: {e}")
            return False
    
    def export_document(self, doc_id: str, export_path: str) -> bool:
        """
        导出文档
        
        Args:
            doc_id: 文档ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            document = self.get_document(doc_id)
            if not document:
                logger.error(f"文档不存在: {doc_id}")
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(document["content"])
            
            logger.info(f"导出文档: {doc_id} -> {export_path}")
            return True
        except Exception as e:
            logger.error(f"导出文档失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "total_documents": len(self._documents),
            "total_categories": len(self._categories),
            "total_tags": len(self._tags),
            "documents_by_category": {
                cat: len(docs) for cat, docs in self._categories.items()
            },
            "documents_by_tag": {
                tag: len(docs) for tag, docs in self._tags.items()
            }
        }
    
    def clear_all(self) -> bool:
        """
        清空所有数据
        
        Returns:
            是否清空成功
        """
        try:
            self._documents.clear()
            self._categories.clear()
            self._tags.clear()
            
            self._save_index()
            
            logger.info("清空知识库")
            return True
        except Exception as e:
            logger.error(f"清空知识库失败: {e}")
            return False
