# -*- coding:utf-8 -*-
"""
混合知识查询服务
协调Neo4j图数据库和星火知识库的查询
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.database import KnowledgeGraphManager
from ..services.spark_api import SparkAPIService
from ..models.schemas import HybridSearchQuery, HybridSearchResponse, KnowledgePath

class HybridKnowledgeService:
    """混合知识查询服务"""
    
    def __init__(self, db_manager: KnowledgeGraphManager, spark_service: SparkAPIService):
        self.db_manager = db_manager
        self.spark_service = spark_service
        self.logger = logging.getLogger(__name__)
    
    def hybrid_search(self, query: HybridSearchQuery) -> HybridSearchResponse:
        """
        混合搜索：结合图数据库推理和星火知识库查询
        
        Args:
            query: 混合搜索查询
            
        Returns:
            混合搜索响应
        """
        try:
            reasoning_paths = []
            spark_results = None
            combined_answer = None
            
            # 1. 图数据库推理搜索
            if query.enable_graph_search:
                reasoning_paths = self._search_knowledge_paths(query)
            
            # 2. 星火知识库查询
            if query.enable_spark_search and reasoning_paths:
                spark_results = self._query_spark_knowledge_bases(query, reasoning_paths)
            
            # 3. 生成综合答案
            if reasoning_paths and spark_results:
                combined_answer = self._generate_combined_answer(query.question, reasoning_paths, spark_results)
            
            return HybridSearchResponse(
                question=query.question,
                reasoning_paths=reasoning_paths,
                spark_results=spark_results,
                combined_answer=combined_answer
            )
            
        except Exception as e:
            self.logger.error(f"混合搜索失败: {e}")
            return HybridSearchResponse(
                question=query.question,
                reasoning_paths=[],
                spark_results=None,
                combined_answer=f"搜索失败: {str(e)}"
            )
    
    def _search_knowledge_paths(self, query: HybridSearchQuery) -> List[KnowledgePath]:
        """搜索知识推理路径"""
        try:
            # 使用数据库管理器搜索路径
            paths_data = self.db_manager.search_knowledge_paths(
                question=query.question,
                max_depth=query.max_path_depth,
                limit=query.limit
            )
            
            # 转换为KnowledgePath模型
            knowledge_paths = []
            for path_data in paths_data:
                knowledge_path = KnowledgePath(
                    path_id=path_data['path_id'],
                    nodes=path_data['nodes'],
                    relationships=path_data['relationships'],
                    confidence=path_data['confidence'],
                    spark_repos=path_data['spark_repos']
                )
                knowledge_paths.append(knowledge_path)
            
            return knowledge_paths
            
        except Exception as e:
            self.logger.error(f"搜索知识路径失败: {e}")
            return []
    
    def _query_spark_knowledge_bases(self, query: HybridSearchQuery, reasoning_paths: List[KnowledgePath]) -> Dict[str, Any]:
        """查询星火知识库"""
        try:
            # 收集所有相关的知识库ID
            all_repo_ids = set()
            for path in reasoning_paths:
                all_repo_ids.update(path.spark_repos)
            
            if not all_repo_ids:
                return {"message": "未找到相关的星火知识库"}
            
            # 对每个知识库进行查询
            spark_results = {
                "repo_queries": [],
                "total_repos": len(all_repo_ids)
            }
            
            for repo_id in list(all_repo_ids)[:3]:  # 限制最多查询3个知识库
                try:
                    result = self.spark_service.chat_with_knowledge_base(
                        question=query.question,
                        repo_id=repo_id,
                        temperature=0.7,
                        wiki_filter_score=0.8
                    )
                    
                    if "error" not in result:
                        spark_results["repo_queries"].append({
                            "repo_id": repo_id,
                            "result": result
                        })
                    else:
                        self.logger.warning(f"知识库 {repo_id} 查询失败: {result['error']}")
                        
                except Exception as e:
                    self.logger.error(f"查询知识库 {repo_id} 时出错: {e}")
            
            return spark_results
            
        except Exception as e:
            self.logger.error(f"查询星火知识库失败: {e}")
            return {"error": str(e)}
    
    def _generate_combined_answer(self, question: str, reasoning_paths: List[KnowledgePath], spark_results: Dict[str, Any]) -> str:
        """生成综合答案"""
        try:
            # 构建推理路径说明
            reasoning_text = "基于知识图谱推理：\n"
            for i, path in enumerate(reasoning_paths[:3], 1):  # 最多显示3个路径
                reasoning_text += f"{i}. 路径: {' -> '.join([node.get('name', '') for node in path.nodes])}\n"
                reasoning_text += f"   置信度: {path.confidence:.2f}\n"
                reasoning_text += f"   相关知识库: {', '.join(path.spark_repos[:3])}\n\n"
            
            # 构建星火查询结果
            spark_text = "星火知识库回答：\n"
            if "repo_queries" in spark_results:
                for i, repo_query in enumerate(spark_results["repo_queries"][:2], 1):  # 最多显示2个知识库的回答
                    result = repo_query["result"]
                    if "data" in result and "answer" in result["data"]:
                        spark_text += f"{i}. 知识库 {repo_query['repo_id']}: {result['data']['answer'][:200]}...\n\n"
            
            # 综合答案
            combined = f"问题：{question}\n\n{reasoning_text}{spark_text}"
            return combined
            
        except Exception as e:
            self.logger.error(f"生成综合答案失败: {e}")
            return f"生成答案时出错: {str(e)}"
    
    def create_knowledge_base_node(self, repo_id: str, repo_name: str, repo_desc: str = "") -> Optional[str]:
        """创建知识库节点"""
        try:
            node_data = {
                "name": repo_name,
                "type": "knowledge_base",
                "description": repo_desc,
                "source": "spark_api",
                "weight": 1.0,
                "spark_repo_ids": [repo_id],
                "spark_file_ids": []
            }
            
            node_id = self.db_manager.create_knowledge_node(node_data)
            if node_id:
                self.logger.info(f"知识库节点创建成功: {node_id}")
                return node_id
            return None
            
        except Exception as e:
            self.logger.error(f"创建知识库节点失败: {e}")
            return None
    
    def link_concept_to_knowledge_base(self, concept_name: str, repo_id: str, file_ids: List[str] = None) -> bool:
        """将概念关联到知识库"""
        try:
            # 搜索概念节点
            nodes = self.db_manager.search_nodes_by_name(concept_name, limit=1)
            if not nodes:
                # 如果概念不存在，创建一个
                node_data = {
                    "name": concept_name,
                    "type": "concept",
                    "description": f"与知识库 {repo_id} 相关的概念",
                    "source": "spark_integration",
                    "weight": 0.8,
                    "spark_repo_ids": [repo_id],
                    "spark_file_ids": file_ids or []
                }
                node_id = self.db_manager.create_knowledge_node(node_data)
            else:
                # 如果概念存在，关联到知识库
                node_id = nodes[0].get('id')
                if node_id:
                    success = self.db_manager.link_node_to_spark_repo(node_id, repo_id, file_ids)
                    if not success:
                        return False
            
            return node_id is not None
            
        except Exception as e:
            self.logger.error(f"关联概念到知识库失败: {e}")
            return False
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """获取知识系统摘要"""
        try:
            # 获取Neo4j统计
            total_nodes_query = "MATCH (n:KnowledgeNode) RETURN count(n) as count"
            total_nodes_result = self.db_manager.execute_custom_query(total_nodes_query)
            total_nodes = total_nodes_result[0]['count'] if total_nodes_result else 0
            
            # 获取关联知识库的节点数
            linked_nodes_query = "MATCH (n:KnowledgeNode) WHERE n.spark_repo_ids IS NOT NULL AND size(n.spark_repo_ids) > 0 RETURN count(n) as count"
            linked_nodes_result = self.db_manager.execute_custom_query(linked_nodes_query)
            linked_nodes = linked_nodes_result[0]['count'] if linked_nodes_result else 0
            
            # 获取知识库节点数
            kb_nodes_query = "MATCH (n:KnowledgeNode {type: 'knowledge_base'}) RETURN count(n) as count"
            kb_nodes_result = self.db_manager.execute_custom_query(kb_nodes_query)
            kb_nodes = kb_nodes_result[0]['count'] if kb_nodes_result else 0
            
            return {
                "total_nodes": total_nodes,
                "linked_nodes": linked_nodes,
                "knowledge_base_nodes": kb_nodes,
                "integration_ratio": linked_nodes / total_nodes if total_nodes > 0 else 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取知识摘要失败: {e}")
            return {"error": str(e)}


def get_hybrid_service(db_manager: KnowledgeGraphManager, spark_service: SparkAPIService) -> HybridKnowledgeService:
    """获取混合知识服务实例"""
    return HybridKnowledgeService(db_manager, spark_service) 