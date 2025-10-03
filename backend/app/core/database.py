# -*- coding:utf-8 -*-
"""
Neo4j图数据库交互模块
实现知识图谱的节点管理、关系管理、复杂查询
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from neo4j import GraphDatabase, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError, ClientError
import json
import time
from datetime import datetime
import hashlib
from .config import NEO4J_CONFIG

class Neo4jConnector:
    """Neo4j图数据库连接器"""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None, database: str = None):
        """
        初始化Neo4j连接器
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
            database: 数据库名称
        """
        self.uri = uri or NEO4J_CONFIG['uri']
        self.user = user or NEO4J_CONFIG['user']
        self.password = password or NEO4J_CONFIG['password']
        self.database = database or NEO4J_CONFIG['database']
        self.driver = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # 测试连接
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            self.logger.info("Neo4j连接成功")
            return True
        except (ServiceUnavailable, AuthError) as e:
            self.logger.error(f"Neo4j连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j连接已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


class KnowledgeGraphManager:
    """知识图谱管理器"""
    
    def __init__(self, connector: Neo4jConnector):
        self.connector = connector
        self.logger = connector.logger
    
    def create_knowledge_node(self, node_data: Dict[str, Any]) -> Optional[str]:
        """
        创建知识节点
        
        Args:
            node_data: 节点数据，包含name, type, source等属性
            
        Returns:
            节点ID，失败返回None
        """
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                # 生成唯一ID
                node_id = self._generate_node_id(node_data)
                
                # 创建节点
                query = """
                MERGE (n:KnowledgeNode {id: $node_id})
                SET n.name = $name,
                    n.type = $type,
                    n.source = $source,
                    n.weight = $weight,
                    n.description = $description,
                    n.is_tested = $is_tested,
                    n.last_accessed = $last_accessed,
                    n.created_at = $created_at,
                    n.updated_at = $updated_at,
                    n.spark_repo_ids = $spark_repo_ids,
                    n.spark_file_ids = $spark_file_ids
                RETURN n.id as node_id
                """
                
                result = session.run(query, 
                                   node_id=node_id,
                                   name=node_data.get('name'),
                                   type=node_data.get('type', 'concept'),
                                   source=node_data.get('source', 'manual'),
                                   weight=node_data.get('weight', 1.0),
                                   description=node_data.get('description', ''),
                                   is_tested=node_data.get('is_tested', False),
                                   last_accessed=datetime.now().isoformat(),
                                   created_at=datetime.now().isoformat(),
                                   updated_at=datetime.now().isoformat(),
                                   spark_repo_ids=node_data.get('spark_repo_ids', []),
                                   spark_file_ids=node_data.get('spark_file_ids', []))
                
                record = result.single()
                if record:
                    self.logger.info(f"知识节点创建成功: {node_id}")
                    return record['node_id']
                return None
                
        except Exception as e:
            self.logger.error(f"创建知识节点失败: {e}")
            return None
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取节点"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                query = "MATCH (n:KnowledgeNode {id: $node_id}) RETURN n"
                result = session.run(query, node_id=node_id)
                record = result.single()
                if record:
                    node = record['n']
                    return dict(node)
                return None
        except Exception as e:
            self.logger.error(f"获取节点失败: {e}")
            return None
    
    def search_nodes_by_name(self, name_pattern: str, limit: int = 50) -> List[Dict[str, Any]]:
        """根据名称搜索节点"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                query = """
                MATCH (n:KnowledgeNode)
                WHERE n.name CONTAINS $name_pattern
                RETURN n
                LIMIT $limit
                """
                result = session.run(query, name_pattern=name_pattern, limit=limit)
                return [dict(record['n']) for record in result]
        except Exception as e:
            self.logger.error(f"搜索节点失败: {e}")
            return []
    
    def update_node_properties(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """更新节点属性"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                # 动态构建属性设置
                props_str = ", ".join([f"n.{k} = ${k}" for k in properties.keys()])
                props_str += ", n.updated_at = $updated_at"
                
                query = f"""
                MATCH (n:KnowledgeNode {{id: $node_id}})
                SET {props_str}
                RETURN n
                """
                
                parameters = {**properties, 'node_id': node_id, 'updated_at': datetime.now().isoformat()}
                result = session.run(query, **parameters)
                record = result.single()
                if record:
                    self.logger.info(f"节点更新成功: {node_id}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"更新节点失败: {e}")
            return False
    
    def delete_node(self, node_id: str) -> bool:
        """删除节点"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                query = """
                MATCH (n:KnowledgeNode {id: $node_id})
                DETACH DELETE n
                RETURN count(n) as deleted_count
                """
                result = session.run(query, node_id=node_id)
                record = result.single()
                if record and record['deleted_count'] > 0:
                    self.logger.info(f"节点删除成功: {node_id}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"删除节点失败: {e}")
            return False
    
    def create_relationship(self, from_node_id: str, to_node_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """创建节点间关系"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                if properties:
                    props_str = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
                    query = f"""
                    MATCH (a:KnowledgeNode {{id: $from_id}}), (b:KnowledgeNode {{id: $to_id}})
                    MERGE (a)-[r:{relationship_type}]->(b)
                    SET {props_str}
                    RETURN r
                    """
                    parameters = {**properties, 'from_id': from_node_id, 'to_id': to_node_id}
                else:
                    query = f"""
                    MATCH (a:KnowledgeNode {{id: $from_id}}), (b:KnowledgeNode {{id: $to_id}})
                    MERGE (a)-[r:{relationship_type}]->(b)
                    RETURN r
                    """
                    parameters = {'from_id': from_node_id, 'to_id': to_node_id}
                
                result = session.run(query, **parameters)
                record = result.single()
                if record:
                    self.logger.info(f"关系创建成功: {from_node_id} -[{relationship_type}]-> {to_node_id}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"创建关系失败: {e}")
            return False
    
    def get_related_nodes(self, node_id: str, relationship_type: str = None, 
                         direction: str = "both", limit: int = 50) -> List[Dict[str, Any]]:
        """获取相关节点"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                if relationship_type:
                    if direction == "outgoing":
                        query = f"""
                        MATCH (n:KnowledgeNode {{id: $node_id}})-[r:{relationship_type}]->(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                    elif direction == "incoming":
                        query = f"""
                        MATCH (n:KnowledgeNode {{id: $node_id}})<-[r:{relationship_type}]-(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                    else:  # both
                        query = f"""
                        MATCH (n:KnowledgeNode {{id: $node_id}})-[r:{relationship_type}]-(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                else:
                    if direction == "outgoing":
                        query = """
                        MATCH (n:KnowledgeNode {id: $node_id})-[r]->(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                    elif direction == "incoming":
                        query = """
                        MATCH (n:KnowledgeNode {id: $node_id})<-[r]-(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                    else:  # both
                        query = """
                        MATCH (n:KnowledgeNode {id: $node_id})-[r]-(related)
                        RETURN related, r
                        LIMIT $limit
                        """
                
                result = session.run(query, node_id=node_id, limit=limit)
                return [{'node': dict(record['related']), 'relationship': dict(record['r'])} 
                       for record in result]
        except Exception as e:
            self.logger.error(f"获取相关节点失败: {e}")
            return []
    
    def execute_custom_query(self, cypher_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行自定义Cypher查询"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                result = session.run(cypher_query, **(parameters or {}))
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"执行查询失败: {e}")
            return []
    
    def _generate_node_id(self, node_data: Dict[str, Any]) -> str:
        """生成节点唯一ID"""
        content = f"{node_data.get('name', '')}{node_data.get('type', '')}{node_data.get('source', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def search_knowledge_paths(self, question: str, max_depth: int = 3, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索知识推理路径
        
        Args:
            question: 问题
            max_depth: 最大路径深度
            limit: 返回路径数量限制
            
        Returns:
            推理路径列表
        """
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                # 使用文本相似度搜索相关节点
                query = """
                MATCH (n:KnowledgeNode)
                WHERE n.name CONTAINS $question OR n.description CONTAINS $question
                WITH n, size(n.name) + size(n.description) as relevance
                ORDER BY relevance DESC
                LIMIT 5
                MATCH path = (n)-[*1..$max_depth]-(related)
                WHERE all(node in nodes(path) WHERE node:KnowledgeNode)
                WITH path, 
                     [node in nodes(path) | node.name] as node_names,
                     [rel in relationships(path) | type(rel)] as rel_types,
                     length(path) as path_length
                ORDER BY path_length ASC, size([node in nodes(path) | node.spark_repo_ids]) DESC
                LIMIT $limit
                RETURN path, node_names, rel_types, path_length
                """
                
                result = session.run(query, question=question, max_depth=max_depth, limit=limit)
                paths = []
                
                for record in result:
                    path_data = {
                        'path_id': hashlib.md5(str(record['node_names']).encode()).hexdigest(),
                        'nodes': [dict(node) for node in record['path'].nodes],
                        'relationships': [dict(rel) for rel in record['path'].relationships],
                        'node_names': record['node_names'],
                        'relationship_types': record['rel_types'],
                        'path_length': record['path_length'],
                        'confidence': 1.0 / (record['path_length'] + 1),  # 路径越短置信度越高
                        'spark_repos': self._extract_spark_repos(record['path'].nodes)
                    }
                    paths.append(path_data)
                
                return paths
                
        except Exception as e:
            self.logger.error(f"搜索知识路径失败: {e}")
            return []
    
    def _extract_spark_repos(self, nodes) -> List[str]:
        """从节点中提取星火知识库ID"""
        spark_repos = set()
        for node in nodes:
            if hasattr(node, 'spark_repo_ids') and node.spark_repo_ids:
                spark_repos.update(node.spark_repo_ids)
        return list(spark_repos)
    
    def get_nodes_by_spark_repo(self, repo_id: str) -> List[Dict[str, Any]]:
        """根据星火知识库ID获取相关节点"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                query = """
                MATCH (n:KnowledgeNode)
                WHERE $repo_id IN n.spark_repo_ids
                RETURN n
                ORDER BY n.weight DESC
                """
                result = session.run(query, repo_id=repo_id)
                return [dict(record['n']) for record in result]
        except Exception as e:
            self.logger.error(f"根据知识库ID获取节点失败: {e}")
            return []
    
    def link_node_to_spark_repo(self, node_id: str, repo_id: str, file_ids: List[str] = None) -> bool:
        """将节点关联到星火知识库"""
        try:
            with self.connector.driver.session(database=self.connector.database) as session:
                # 获取当前节点的知识库关联
                query = """
                MATCH (n:KnowledgeNode {id: $node_id})
                RETURN n.spark_repo_ids as repo_ids, n.spark_file_ids as file_ids
                """
                result = session.run(query, node_id=node_id)
                record = result.single()
                
                if record:
                    current_repo_ids = record['repo_ids'] or []
                    current_file_ids = record['file_ids'] or []
                    
                    # 添加新的关联
                    if repo_id not in current_repo_ids:
                        current_repo_ids.append(repo_id)
                    
                    if file_ids:
                        current_file_ids.extend([fid for fid in file_ids if fid not in current_file_ids])
                    
                    # 更新节点
                    update_query = """
                    MATCH (n:KnowledgeNode {id: $node_id})
                    SET n.spark_repo_ids = $repo_ids,
                        n.spark_file_ids = $file_ids,
                        n.updated_at = $updated_at
                    RETURN n
                    """
                    
                    update_result = session.run(update_query, 
                                              node_id=node_id,
                                              repo_ids=current_repo_ids,
                                              file_ids=current_file_ids,
                                              updated_at=datetime.now().isoformat())
                    
                    if update_result.single():
                        self.logger.info(f"节点 {node_id} 成功关联到知识库 {repo_id}")
                        return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"关联节点到知识库失败: {e}")
            return False


# 全局数据库管理器实例
def get_database_manager() -> KnowledgeGraphManager:
    """获取数据库管理器实例"""
    connector = Neo4jConnector()
    if connector.connect():
        return KnowledgeGraphManager(connector)
    else:
        raise Exception("无法连接到Neo4j数据库") 