# -*- coding:utf-8 -*-
"""
CogniPathDB FastAPI 使用示例
演示如何使用API进行知识图谱和星火知识库操作
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"

class CogniPathDBClient:
    """CogniPathDB API客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()
    
    def create_knowledge_node(self, name: str, node_type: str = "concept", 
                            description: str = "", source: str = "manual", 
                            weight: float = 1.0) -> Dict[str, Any]:
        """创建知识节点"""
        data = {
            "name": name,
            "type": node_type,
            "description": description,
            "source": source,
            "weight": weight
        }
        response = self.session.post(f"{self.base_url}/api/nodes", json=data)
        return response.json()
    
    def search_nodes(self, name_pattern: str = "", limit: int = 50) -> Dict[str, Any]:
        """搜索知识节点"""
        params = {"limit": limit}
        if name_pattern:
            params["name"] = name_pattern
        response = self.session.get(f"{self.base_url}/api/nodes", params=params)
        return response.json()
    
    def create_relationship(self, from_node_id: str, to_node_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建关系"""
        data = {
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "relationship_type": relationship_type
        }
        if properties:
            data["properties"] = properties
        response = self.session.post(f"{self.base_url}/api/relationships", json=data)
        return response.json()
    
    def batch_create_nodes(self, nodes: list) -> Dict[str, Any]:
        """批量创建节点"""
        data = {"nodes": nodes}
        response = self.session.post(f"{self.base_url}/api/nodes/batch", json=data)
        return response.json()
    
    def create_knowledge_base(self, repo_name: str, repo_desc: str = "", 
                            repo_tags: str = "") -> Dict[str, Any]:
        """创建星火知识库"""
        data = {
            "repo_name": repo_name,
            "repo_desc": repo_desc,
            "repo_tags": repo_tags
        }
        response = self.session.post(f"{self.base_url}/api/spark/knowledge-bases", json=data)
        return response.json()
    
    def get_knowledge_bases(self, repo_name: str = "", current_page: int = 1, 
                          page_size: int = 10) -> Dict[str, Any]:
        """获取知识库列表"""
        params = {
            "repo_name": repo_name,
            "current_page": current_page,
            "page_size": page_size
        }
        response = self.session.get(f"{self.base_url}/api/spark/knowledge-bases", params=params)
        return response.json()
    
    def intelligent_qa(self, question: str, enable_reasoning: bool = True, 
                      enable_spark_query: bool = True) -> Dict[str, Any]:
        """智能问答"""
        data = {
            "question": question,
            "enable_reasoning": enable_reasoning,
            "enable_spark_query": enable_spark_query
        }
        response = self.session.post(f"{self.base_url}/api/intelligent/qa", json=data)
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        response = self.session.get(f"{self.base_url}/api/statistics")
        return response.json()


def demo_knowledge_graph():
    """演示知识图谱操作"""
    print("=" * 60)
    print("知识图谱操作演示")
    print("=" * 60)
    
    client = CogniPathDBClient()
    
    # 1. 健康检查
    print("1. 健康检查")
    health = client.health_check()
    print(f"   状态: {health.get('status', 'unknown')}")
    print(f"   Neo4j连接: {health.get('neo4j_connected', False)}")
    print(f"   星火API: {health.get('spark_api_available', False)}")
    print()
    
    # 2. 创建知识节点
    print("2. 创建知识节点")
    nodes_data = [
        {
            "name": "人工智能",
            "type": "concept",
            "description": "人工智能是计算机科学的一个分支",
            "weight": 0.9
        },
        {
            "name": "机器学习",
            "type": "concept", 
            "description": "机器学习是AI的一个子领域",
            "weight": 0.8
        },
        {
            "name": "深度学习",
            "type": "concept",
            "description": "深度学习是机器学习的一个分支",
            "weight": 0.7
        }
    ]
    
    created_nodes = []
    for node_data in nodes_data:
        result = client.create_knowledge_node(**node_data)
        if result.get('success'):
            node_id = result['data']['node_id']
            created_nodes.append((node_id, node_data['name']))
            print(f"   创建节点成功: {node_data['name']} (ID: {node_id})")
        else:
            print(f"   创建节点失败: {node_data['name']} - {result.get('message', '未知错误')}")
    print()
    
    # 3. 搜索节点
    print("3. 搜索节点")
    search_result = client.search_nodes("人工智能", limit=10)
    if search_result.get('success'):
        nodes = search_result['data']['nodes']
        print(f"   找到 {len(nodes)} 个节点:")
        for node in nodes:
            print(f"     - {node.get('name', 'Unknown')}: {node.get('description', 'No description')}")
    else:
        print(f"   搜索失败: {search_result.get('message', '未知错误')}")
    print()
    
    # 4. 创建关系
    print("4. 创建关系")
    if len(created_nodes) >= 2:
        # 创建"人工智能包含机器学习"的关系
        result = client.create_relationship(
            from_node_id=created_nodes[0][0],  # 人工智能
            to_node_id=created_nodes[1][0],    # 机器学习
            relationship_type="CONTAINS",
            properties={"weight": 0.8}
        )
        if result.get('success'):
            print(f"   创建关系成功: {created_nodes[0][1]} -> {created_nodes[1][1]}")
        else:
            print(f"   创建关系失败: {result.get('message', '未知错误')}")
    print()
    
    # 5. 获取统计信息
    print("5. 统计信息")
    stats = client.get_statistics()
    if stats.get('success'):
        data = stats['data']
        print(f"   总节点数: {data.get('total_nodes', 0)}")
        print(f"   总关系数: {data.get('total_relationships', 0)}")
        print(f"   节点类型统计: {data.get('node_types', {})}")
    else:
        print(f"   获取统计信息失败: {stats.get('message', '未知错误')}")


def demo_spark_api():
    """演示星火API操作"""
    print("\n" + "=" * 60)
    print("星火API操作演示")
    print("=" * 60)
    
    client = CogniPathDBClient()
    
    # 1. 创建知识库
    print("1. 创建知识库")
    kb_result = client.create_knowledge_base(
        repo_name="示例知识库",
        repo_desc="这是一个示例知识库，用于演示API功能",
        repo_tags="示例,演示,API"
    )
    if kb_result.get('success'):
        print(f"   创建知识库成功: {kb_result['data']}")
    else:
        print(f"   创建知识库失败: {kb_result.get('message', '未知错误')}")
    print()
    
    # 2. 获取知识库列表
    print("2. 获取知识库列表")
    kb_list = client.get_knowledge_bases()
    if kb_list.get('success'):
        data = kb_list['data']
        print(f"   找到 {data.get('total', 0)} 个知识库:")
        for kb in data.get('list', []):
            print(f"     - {kb.get('repoName', 'Unknown')}: {kb.get('repoDesc', 'No description')}")
    else:
        print(f"   获取知识库列表失败: {kb_list.get('message', '未知错误')}")


def demo_intelligent_qa():
    """演示智能问答"""
    print("\n" + "=" * 60)
    print("智能问答演示")
    print("=" * 60)
    
    client = CogniPathDBClient()
    
    # 智能问答
    questions = [
        "什么是人工智能？",
        "机器学习和深度学习有什么关系？",
        "如何学习Python编程？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. 问题: {question}")
        result = client.intelligent_qa(question)
        if result.get('success'):
            answer = result['data']
            print(f"   回答: {answer.get('answer', 'No answer')}")
            print(f"   推理启用: {answer.get('reasoning_enabled', False)}")
            print(f"   星火查询启用: {answer.get('spark_query_enabled', False)}")
        else:
            print(f"   问答失败: {result.get('message', '未知错误')}")
        print()


def main():
    """主函数"""
    print("CogniPathDB FastAPI 使用示例")
    print("请确保服务已启动: python start.py")
    print()
    
    try:
        # 演示知识图谱操作
        demo_knowledge_graph()
        
        # 演示星火API操作
        demo_spark_api()
        
        # 演示智能问答
        demo_intelligent_qa()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到API服务")
        print("请确保服务已启动: python start.py")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main() 