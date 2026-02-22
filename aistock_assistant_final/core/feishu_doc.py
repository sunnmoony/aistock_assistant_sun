# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 飞书云文档模块
===================================

职责:
1. 飞书开放平台API认证
2. 云文档创建和管理
3. 文档内容编辑和更新
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DocInfo:
    """文档信息"""
    doc_token: str
    title: str
    url: str
    create_time: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_token": self.doc_token,
            "title": self.title,
            "url": self.url,
            "create_time": self.create_time
        }


class FeishuDocManager:
    """
    飞书云文档管理器
    
    功能:
    1. 获取访问凭证（tenant_access_token）
    2. 创建云文档
    3. 编辑文档内容
    4. 管理文档权限
    """

    def __init__(
        self,
        app_id: str = "",
        app_secret: str = "",
        folder_token: str = ""
    ):
        """
        初始化飞书文档管理器
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            folder_token: 默认文件夹token
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.folder_token = folder_token
        self._access_token = None
        self._token_expire_time = 0
        self._base_url = "https://open.feishu.cn/open-apis"
        
        if app_id and app_secret:
            self._refresh_token()

    def _refresh_token(self) -> bool:
        """刷新访问令牌"""
        if not self.app_id or not self.app_secret:
            logger.warning("未配置飞书应用凭证")
            return False
        
        try:
            url = f"{self._base_url}/auth/v3/tenant_access_token/internal"
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self._access_token = result.get("tenant_access_token")
                self._token_expire_time = time.time() + result.get("expire", 7200) - 300
                logger.info("飞书访问令牌获取成功")
                return True
            else:
                logger.error(f"获取飞书访问令牌失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            logger.error(f"刷新飞书令牌异常: {e}")
            return False

    def _get_token(self) -> Optional[str]:
        """获取有效的访问令牌"""
        if not self._access_token or time.time() >= self._token_expire_time:
            if not self._refresh_token():
                return None
        return self._access_token

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_doc(
        self,
        title: str,
        content: str = "",
        folder_token: str = None
    ) -> Optional[DocInfo]:
        """
        创建云文档
        
        Args:
            title: 文档标题
            content: 文档内容（Markdown格式）
            folder_token: 目标文件夹token
            
        Returns:
            DocInfo 文档信息
        """
        token = self._get_token()
        if not token:
            logger.error("无法获取访问令牌")
            return None
        
        target_folder = folder_token or self.folder_token
        
        try:
            url = f"{self._base_url}/docx/v1/documents"
            data = {
                "title": title,
                "folder_token": target_folder
            }
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            result = response.json()
            
            if result.get("code") == 0:
                doc = result.get("data", {}).get("document", {})
                doc_token = doc.get("document_id", "")
                
                if content:
                    self.append_content(doc_token, content)
                
                return DocInfo(
                    doc_token=doc_token,
                    title=title,
                    url=f"https://feishu.cn/docx/{doc_token}",
                    create_time=datetime.now().isoformat()
                )
            else:
                logger.error(f"创建文档失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            logger.error(f"创建文档异常: {e}")
            return None

    def append_content(
        self,
        doc_token: str,
        content: str,
        index: int = None
    ) -> bool:
        """
        追加文档内容
        
        Args:
            doc_token: 文档token
            content: 内容（Markdown格式）
            index: 插入位置索引
            
        Returns:
            是否成功
        """
        token = self._get_token()
        if not token:
            return False
        
        try:
            url = f"{self._base_url}/docx/v1/documents/{doc_token}/blocks/{doc_token}/children/batch_insert"
            
            blocks = self._parse_markdown_to_blocks(content)
            
            data = {
                "children": blocks,
                "index": index
            }
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"文档内容追加成功: {doc_token}")
                return True
            else:
                logger.error(f"追加内容失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            logger.error(f"追加内容异常: {e}")
            return False

    def _parse_markdown_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """将Markdown内容解析为飞书文档块"""
        blocks = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("# "):
                blocks.append({
                    "block_type": 3,
                    "heading1": {
                        "elements": [{"text_run": {"content": line[2:]}}]
                    }
                })
            elif line.startswith("## "):
                blocks.append({
                    "block_type": 4,
                    "heading2": {
                        "elements": [{"text_run": {"content": line[3:]}}]
                    }
                })
            elif line.startswith("### "):
                blocks.append({
                    "block_type": 5,
                    "heading3": {
                        "elements": [{"text_run": {"content": line[4:]}}]
                    }
                })
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append({
                    "block_type": 12,
                    "bullet": {
                        "elements": [{"text_run": {"content": line[2:]}}]
                    }
                })
            else:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"text_run": {"content": line}}]
                    }
                })
        
        return blocks

    def get_doc_info(self, doc_token: str) -> Optional[Dict[str, Any]]:
        """
        获取文档信息
        
        Args:
            doc_token: 文档token
            
        Returns:
            文档信息字典
        """
        token = self._get_token()
        if not token:
            return None
        
        try:
            url = f"{self._base_url}/docx/v1/documents/{doc_token}"
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {}).get("document", {})
            else:
                logger.error(f"获取文档信息失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            logger.error(f"获取文档信息异常: {e}")
            return None

    def delete_doc(self, doc_token: str) -> bool:
        """
        删除文档
        
        Args:
            doc_token: 文档token
            
        Returns:
            是否成功
        """
        token = self._get_token()
        if not token:
            return False
        
        try:
            url = f"{self._base_url}/docx/v1/documents/{doc_token}/trash"
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"文档删除成功: {doc_token}")
                return True
            else:
                logger.error(f"删除文档失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            logger.error(f"删除文档异常: {e}")
            return False

    def is_available(self) -> bool:
        """检查飞书服务是否可用"""
        return self._get_token() is not None

    def set_credentials(self, app_id: str, app_secret: str):
        """设置凭证"""
        self.app_id = app_id
        self.app_secret = app_secret
        self._refresh_token()
