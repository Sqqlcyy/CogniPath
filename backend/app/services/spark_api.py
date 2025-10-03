# -*- coding:utf-8 -*-
"""
星火知识库API服务
基于官方API文档的正确实现
"""

import hashlib
import base64
import hmac
import time
import json
import requests
from typing import Dict, List, Optional, Any
from requests_toolbelt.multipart.encoder import MultipartEncoder
from ..core.config import SPARK_API_CONFIG

class SparkAPIService:
    """星火知识库API服务"""
    
    def __init__(self, app_id: str = None, api_secret: str = None, base_url: str = None):
        """
        初始化星火API服务
        
        Args:
            app_id: 应用ID
            api_secret: API密钥
            base_url: API基础URL
        """
        self.app_id = app_id or SPARK_API_CONFIG['app_id']
        self.api_secret = api_secret or SPARK_API_CONFIG['api_secret']
        self.base_url = base_url or SPARK_API_CONFIG['base_url']
    
    def _get_origin_signature(self, timestamp: str) -> str:
        """获取原始签名"""
        m2 = hashlib.md5()
        data = bytes(self.app_id + timestamp, encoding="utf-8")
        m2.update(data)
        checkSum = m2.hexdigest()
        return checkSum
    
    def _get_signature(self, timestamp: str) -> str:
        """生成API签名"""
        # 获取原始签名
        signature_origin = self._get_origin_signature(timestamp)
        # 使用加密键加密文本
        signature = hmac.new(
            self.api_secret.encode('utf-8'), 
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest()
        # base64密文编码
        signature = base64.b64encode(signature).decode(encoding='utf-8')
        return signature
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        timestamp = str(int(time.time()))
        signature = self._get_signature(timestamp)
        
        return {
            "appId": self.app_id,
            "timestamp": timestamp,
            "signature": signature,
        }
    
    def create_knowledge_base(self, repo_name: str, repo_desc: str = "", repo_tags: str = "") -> Dict[str, Any]:
        """
        创建知识库
        
        Args:
            repo_name: 知识库名称
            repo_desc: 知识库描述
            repo_tags: 知识库标签
            
        Returns:
            创建结果
        """
        try:
            url = f"{self.base_url}/repo/create"
            headers = self._get_headers()
            
            body = {
                "repoName": repo_name,
                "repoDesc": repo_desc,
                "repoTags": repo_tags
            }
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_knowledge_bases(self, repo_name: str = "", current_page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        获取知识库列表
        
        Args:
            repo_name: 知识库名称过滤
            current_page: 当前页码
            page_size: 每页大小
            
        Returns:
            知识库列表
        """
        try:
            url = f"{self.base_url}/repo/list"
            headers = self._get_headers()
            
            body = {
                "repoName": repo_name,
                "currentPage": current_page,
                "pageSize": page_size
            }
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_knowledge_base_info(self, repo_id: str) -> Dict[str, Any]:
        """
        获取知识库详情
        
        Args:
            repo_id: 知识库ID
            
        Returns:
            知识库详情
        """
        try:
            url = f"{self.base_url}/repo/info"
            headers = self._get_headers()
            
            body = {"repoId": repo_id}
            
            response = requests.post(url, data=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def upload_file(self, file_path: str, file_type: str = "wiki", need_summary: bool = True, 
                   step_by_step: bool = False) -> Dict[str, Any]:
        """
        上传文件到星火知识库
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 (wiki, qa, doc)
            need_summary: 是否需要摘要
            step_by_step: 是否分步骤处理
            
        Returns:
            上传结果
        """
        try:
            url = f"{self.base_url}/file/upload"
            headers = self._get_headers()
            headers.pop("Content-Type", None)  # 移除Content-Type，让requests自动设置
            
            with open(file_path, 'rb') as f:
                encoder = MultipartEncoder(
                    fields={
                        'file': (file_path.split('/')[-1], f, 'application/octet-stream'),
                        'fileType': file_type,
                        'needSummary': str(need_summary).lower(),
                        'stepByStep': str(step_by_step).lower()
                    }
                )
                headers['Content-Type'] = encoder.content_type
                
                response = requests.post(url, data=encoder, headers=headers)
                response.raise_for_status()
                
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def add_files_to_repo(self, repo_id: str, file_ids: List[str]) -> Dict[str, Any]:
        """
        将文件添加到知识库
        
        Args:
            repo_id: 知识库ID
            file_ids: 文件ID列表
            
        Returns:
            添加结果
        """
        try:
            url = f"{self.base_url}/repo/file/add"
            headers = self._get_headers()
            
            body = {
                "repoId": repo_id,
                "fileIds": file_ids
            }
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_repo_files(self, repo_id: str, file_name: str = "", ext_name: str = "", 
                      current_page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        获取知识库文件列表
        
        Args:
            repo_id: 知识库ID
            file_name: 文件名过滤
            ext_name: 扩展名过滤
            current_page: 当前页码
            page_size: 每页大小
            
        Returns:
            文件列表
        """
        try:
            url = f"{self.base_url}/repo/file/list"
            headers = self._get_headers()
            
            body = {
                "repoId": repo_id,
                "fileName": file_name,
                "extName": ext_name,
                "currentPage": current_page,
                "pageSize": page_size
            }
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def remove_files_from_repo(self, repo_id: str, file_ids: List[str]) -> Dict[str, Any]:
        """
        从知识库移除文件
        
        Args:
            repo_id: 知识库ID
            file_ids: 文件ID列表
            
        Returns:
            移除结果
        """
        try:
            url = f"{self.base_url}/repo/file/remove"
            headers = self._get_headers()
            
            body = {
                "repoId": repo_id,
                "fileIds": file_ids
            }
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delete_knowledge_base(self, repo_id: str) -> Dict[str, Any]:
        """
        删除知识库
        
        Args:
            repo_id: 知识库ID
            
        Returns:
            删除结果
        """
        try:
            url = f"{self.base_url}/repo/del"
            headers = self._get_headers()
            
            body = {"repoId": repo_id}
            
            response = requests.post(url, data=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat_with_knowledge_base(self, question: str, repo_id: str, file_ids: List[str] = None,
                                temperature: float = 0.7, wiki_filter_score: float = 0.8) -> Dict[str, Any]:
        """
        与知识库对话
        
        Args:
            question: 问题
            repo_id: 知识库ID
            file_ids: 文件ID列表
            temperature: 温度参数
            wiki_filter_score: 过滤分数
            
        Returns:
            对话结果
        """
        try:
            url = f"{self.base_url}/chat"
            headers = self._get_headers()
            
            body = {
                "question": question,
                "repoId": repo_id,
                "temperature": temperature,
                "wikiFilterScore": wiki_filter_score
            }
            
            if file_ids:
                body["fileIds"] = file_ids
            
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}


# 全局星火API服务实例
def get_spark_api_service() -> SparkAPIService:
    """获取星火API服务实例"""
    return SparkAPIService() 