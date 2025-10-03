# -*- coding:utf-8 -*-
"""
FastAPI路由定义
提供Neo4j数据库和星火知识库的API接口
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os
import tempfile

from ..models.schemas import (
    KnowledgeNodeCreate, KnowledgeNodeUpdate, KnowledgeNodeResponse,
    RelationshipCreate, RelationshipResponse,
    BatchNodeCreate, BatchRelationshipCreate,
    NodeSearchQuery, CustomQuery, RelatedNodesQuery,
    KnowledgeBaseCreate, KnowledgeBaseQuery, SparkQAModel,
    IntelligentQAModel, AnalysisModel, VisualizationModel,
    HybridSearchQuery, HybridSearchResponse,
    StandardResponse, HealthResponse, StatisticsResponse
)
from ..core.database import get_database_manager, KnowledgeGraphManager
from ..services.spark_api import get_spark_api_service, SparkAPIService
from ..services.hybrid_service import get_hybrid_service, HybridKnowledgeService
from ..core.config import settings

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 依赖注入
def get_db_manager() -> KnowledgeGraphManager:
    """获取数据库管理器"""
    try:
        return get_database_manager()
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise HTTPException(status_code=500, detail="数据库连接失败")

def get_spark_service() -> SparkAPIService:
    """获取星火API服务"""
    return get_spark_api_service()

def get_hybrid_service_instance() -> HybridKnowledgeService:
    """获取混合知识服务"""
    db_manager = get_database_manager()
    spark_service = get_spark_api_service()
    return get_hybrid_service(db_manager, spark_service)

# 健康检查
@router.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check(
    db_manager: KnowledgeGraphManager = Depends(get_db_manager),
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """健康检查接口"""
    try:
        # 检查Neo4j连接
        neo4j_connected = db_manager.connector.connect()
        
        # 检查星火API
        spark_api_available = True
        try:
            # 尝试获取知识库列表来测试API
            result = spark_service.get_knowledge_bases()
            spark_api_available = "error" not in result
        except:
            spark_api_available = False
        
        return HealthResponse(
            status="healthy" if neo4j_connected and spark_api_available else "unhealthy",
            neo4j_connected=neo4j_connected,
            spark_api_available=spark_api_available,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="健康检查失败")

# 统计信息
@router.get("/statistics", response_model=StatisticsResponse, tags=["系统"])
async def get_statistics(db_manager: KnowledgeGraphManager = Depends(get_db_manager)):
    """获取系统统计信息"""
    try:
        # 获取总节点数
        total_nodes_query = "MATCH (n:KnowledgeNode) RETURN count(n) as count"
        total_nodes_result = db_manager.execute_custom_query(total_nodes_query)
        total_nodes = total_nodes_result[0]['count'] if total_nodes_result else 0
        
        # 获取总关系数
        total_relationships_query = "MATCH ()-[r]->() RETURN count(r) as count"
        total_relationships_result = db_manager.execute_custom_query(total_relationships_query)
        total_relationships = total_relationships_result[0]['count'] if total_relationships_result else 0
        
        # 获取节点类型统计
        node_types_query = """
        MATCH (n:KnowledgeNode)
        RETURN n.type as type, count(n) as count
        """
        node_types_result = db_manager.execute_custom_query(node_types_query)
        node_types = {record['type']: record['count'] for record in node_types_result}
        
        # 获取关系类型统计
        relationship_types_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(r) as count
        """
        relationship_types_result = db_manager.execute_custom_query(relationship_types_query)
        relationship_types = {record['type']: record['count'] for record in relationship_types_result}
        
        # 获取关联星火知识库的节点数
        spark_repos_query = """
        MATCH (n:KnowledgeNode)
        WHERE n.spark_repo_ids IS NOT NULL AND size(n.spark_repo_ids) > 0
        RETURN count(n) as count
        """
        spark_repos_result = db_manager.execute_custom_query(spark_repos_query)
        spark_repos_count = spark_repos_result[0]['count'] if spark_repos_result else 0
        
        return StatisticsResponse(
            total_nodes=total_nodes,
            total_relationships=total_relationships,
            node_types=node_types,
            relationship_types=relationship_types,
            spark_repos_count=spark_repos_count,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计信息失败")

# ==================== Neo4j知识图谱API ====================

# 创建知识节点
@router.post("/nodes", response_model=StandardResponse, tags=["知识图谱"])
async def create_knowledge_node(
    node_data: KnowledgeNodeCreate,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """创建知识节点"""
    try:
        node_id = db_manager.create_knowledge_node(node_data.dict())
        if node_id:
            return StandardResponse(
                success=True,
                message="知识节点创建成功",
                data={"node_id": node_id}
            )
        else:
            raise HTTPException(status_code=400, detail="知识节点创建失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建知识节点失败: {e}")
        raise HTTPException(status_code=500, detail="创建知识节点失败")

# 获取知识节点
@router.get("/nodes", response_model=StandardResponse, tags=["知识图谱"])
async def get_knowledge_nodes(
    name: Optional[str] = Query(None, description="节点名称搜索"),
    node_type: Optional[str] = Query(None, description="节点类型"),
    limit: int = Query(default=50, ge=1, le=1000, description="返回数量限制"),
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """获取知识节点列表"""
    try:
        if name:
            nodes = db_manager.search_nodes_by_name(name, limit)
        else:
            # 获取所有节点，返回属性字典
            query = "MATCH (n:KnowledgeNode) RETURN properties(n) as node LIMIT $limit"
            nodes = [record['node'] for record in db_manager.execute_custom_query(query, {"limit": limit})]
        
        return StandardResponse(
            success=True,
            message="获取知识节点成功",
            data={"nodes": nodes}
        )
    except Exception as e:
        logger.error(f"获取知识节点失败: {e}")
        raise HTTPException(status_code=500, detail="获取知识节点失败")

# 获取单个节点
@router.get("/nodes/{node_id}", response_model=StandardResponse, tags=["知识图谱"])
async def get_knowledge_node(
    node_id: str,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """根据ID获取知识节点"""
    try:
        node = db_manager.get_node_by_id(node_id)
        if node:
            return StandardResponse(
                success=True,
                message="获取知识节点成功",
                data={"node": node}
            )
        else:
            raise HTTPException(status_code=404, detail="知识节点不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识节点失败: {e}")
        raise HTTPException(status_code=500, detail="获取知识节点失败")

# 更新知识节点
@router.put("/nodes/{node_id}", response_model=StandardResponse, tags=["知识图谱"])
async def update_knowledge_node(
    node_id: str,
    node_data: KnowledgeNodeUpdate,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """更新知识节点"""
    try:
        # 过滤掉None值
        update_data = {k: v for k, v in node_data.dict().items() if v is not None}
        if update_data:
            success = db_manager.update_node_properties(node_id, update_data)
            if success:
                return StandardResponse(
                    success=True,
                    message="知识节点更新成功",
                    data={"node_id": node_id}
                )
            else:
                raise HTTPException(status_code=400, detail="知识节点更新失败")
        else:
            raise HTTPException(status_code=400, detail="没有提供更新数据")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新知识节点失败: {e}")
        raise HTTPException(status_code=500, detail="更新知识节点失败")

# 删除知识节点
@router.delete("/nodes/{node_id}", response_model=StandardResponse, tags=["知识图谱"])
async def delete_knowledge_node(
    node_id: str,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """删除知识节点"""
    try:
        success = db_manager.delete_node(node_id)
        if success:
            return StandardResponse(
                success=True,
                message="知识节点删除成功",
                data={"node_id": node_id}
            )
        else:
            raise HTTPException(status_code=400, detail="知识节点删除失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识节点失败: {e}")
        raise HTTPException(status_code=500, detail="删除知识节点失败")

# 批量创建节点
@router.post("/nodes/batch", response_model=StandardResponse, tags=["知识图谱"])
async def batch_create_nodes(
    request: BatchNodeCreate,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """批量创建知识节点"""
    try:
        created_nodes = []
        for node_data in request.nodes:
            node_id = db_manager.create_knowledge_node(node_data.dict())
            if node_id:
                created_nodes.append({"node_id": node_id, "name": node_data.name})
        
        return StandardResponse(
            success=True,
            message=f"批量创建成功，共创建 {len(created_nodes)} 个节点",
            data={"created_nodes": created_nodes}
        )
    except Exception as e:
        logger.error(f"批量创建节点失败: {e}")
        raise HTTPException(status_code=500, detail="批量创建节点失败")

# 创建关系
@router.post("/relationships", response_model=StandardResponse, tags=["知识图谱"])
async def create_relationship(
    relationship_data: RelationshipCreate,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """创建节点间关系"""
    try:
        success = db_manager.create_relationship(
            from_node_id=relationship_data.from_node_id,
            to_node_id=relationship_data.to_node_id,
            relationship_type=relationship_data.relationship_type,
            properties=relationship_data.properties
        )
        if success:
            return StandardResponse(
                success=True,
                message="关系创建成功",
                data={
                    "from_node_id": relationship_data.from_node_id,
                    "to_node_id": relationship_data.to_node_id,
                    "relationship_type": relationship_data.relationship_type
                }
            )
        else:
            raise HTTPException(status_code=400, detail="关系创建失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建关系失败: {e}")
        raise HTTPException(status_code=500, detail="创建关系失败")

# 批量创建关系
@router.post("/relationships/batch", response_model=StandardResponse, tags=["知识图谱"])
async def batch_create_relationships(
    request: BatchRelationshipCreate,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """批量创建关系"""
    try:
        created_relationships = []
        for rel_data in request.relationships:
            success = db_manager.create_relationship(
                from_node_id=rel_data.from_node_id,
                to_node_id=rel_data.to_node_id,
                relationship_type=rel_data.relationship_type,
                properties=rel_data.properties
            )
            if success:
                created_relationships.append({
                    "from_node_id": rel_data.from_node_id,
                    "to_node_id": rel_data.to_node_id,
                    "relationship_type": rel_data.relationship_type
                })
        
        return StandardResponse(
            success=True,
            message=f"批量创建关系成功，共创建 {len(created_relationships)} 个关系",
            data={"created_relationships": created_relationships}
        )
    except Exception as e:
        logger.error(f"批量创建关系失败: {e}")
        raise HTTPException(status_code=500, detail="批量创建关系失败")

# 获取相关节点
@router.get("/nodes/{node_id}/related", response_model=StandardResponse, tags=["知识图谱"])
async def get_related_nodes(
    node_id: str,
    relationship_type: Optional[str] = Query(None, description="关系类型"),
    direction: str = Query(default="both", description="关系方向"),
    limit: int = Query(default=50, ge=1, le=1000, description="返回数量限制"),
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """获取节点的相关节点"""
    try:
        related_nodes = db_manager.get_related_nodes(
            node_id=node_id,
            relationship_type=relationship_type,
            direction=direction,
            limit=limit
        )
        return StandardResponse(
            success=True,
            message="获取相关节点成功",
            data={"related_nodes": related_nodes}
        )
    except Exception as e:
        logger.error(f"获取相关节点失败: {e}")
        raise HTTPException(status_code=500, detail="获取相关节点失败")

# 自定义查询
@router.post("/query", response_model=StandardResponse, tags=["知识图谱"])
async def execute_custom_query(
    query: CustomQuery,
    db_manager: KnowledgeGraphManager = Depends(get_db_manager)
):
    """执行自定义Cypher查询"""
    try:
        result = db_manager.execute_custom_query(
            query.cypher_query,
            query.parameters
        )
        return StandardResponse(
            success=True,
            message="查询执行成功",
            data={"result": result}
        )
    except Exception as e:
        logger.error(f"执行查询失败: {e}")
        raise HTTPException(status_code=500, detail="执行查询失败")

# ==================== 星火知识库API ====================

# 创建知识库
@router.post("/spark/knowledge-base/create", response_model=StandardResponse, tags=["星火知识库"])
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """创建星火知识库"""
    try:
        result = spark_service.create_knowledge_base(
            repo_name=request.repo_name,
            repo_desc=request.repo_desc,
            repo_tags=request.repo_tags
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="知识库创建成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail="创建知识库失败")

# 获取知识库列表
@router.post("/spark/knowledge-base/list", response_model=StandardResponse, tags=["星火知识库"])
async def get_knowledge_bases(
    request: KnowledgeBaseQuery,
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """获取星火知识库列表"""
    try:
        result = spark_service.get_knowledge_bases(
            repo_name=request.repo_name,
            current_page=request.current_page,
            page_size=request.page_size
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="获取知识库列表成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取知识库列表失败")

# 获取知识库详情
@router.post("/spark/knowledge-base/info", response_model=StandardResponse, tags=["星火知识库"])
async def get_knowledge_base_info(
    repo_id: str,
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """获取星火知识库详情"""
    try:
        result = spark_service.get_knowledge_base_info(repo_id=repo_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="获取知识库详情成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取知识库详情失败")

# 删除知识库
@router.delete("/spark/knowledge-base/delete", response_model=StandardResponse, tags=["星火知识库"])
async def delete_knowledge_base(
    repo_id: str,
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """删除星火知识库"""
    try:
        result = spark_service.delete_knowledge_base(repo_id=repo_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="知识库删除成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(status_code=500, detail="删除知识库失败")

# 上传文件
@router.post("/spark/file/upload", response_model=StandardResponse, tags=["星火知识库"])
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Query(default="wiki", description="文件类型"),
    need_summary: bool = Query(default=True, description="是否需要摘要"),
    step_by_step: bool = Query(default=False, description="是否分步骤处理"),
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """上传文件到星火知识库"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            result = spark_service.upload_file(
                file_path=temp_file_path,
                file_type=file_type,
                need_summary=need_summary,
                step_by_step=step_by_step
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            return StandardResponse(
                success=True,
                message="文件上传成功",
                data=result
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")

# 添加文件到知识库
@router.post("/spark/knowledge-base/file/add", response_model=StandardResponse, tags=["星火知识库"])
async def add_files_to_repo(
    repo_id: str,
    file_ids: List[str],
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """将文件添加到知识库"""
    try:
        result = spark_service.add_files_to_repo(
            repo_id=repo_id,
            file_ids=file_ids
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="文件添加成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加文件失败: {e}")
        raise HTTPException(status_code=500, detail="添加文件失败")

# 获取知识库文件列表
@router.post("/spark/knowledge-base/file/list", response_model=StandardResponse, tags=["星火知识库"])
async def get_repo_files(
    repo_id: str,
    file_name: str = Query(default="", description="文件名过滤"),
    ext_name: str = Query(default="", description="扩展名过滤"),
    current_page: int = Query(default=1, ge=1, description="当前页码"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页大小"),
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """获取知识库文件列表"""
    try:
        result = spark_service.get_repo_files(
            repo_id=repo_id,
            file_name=file_name,
            ext_name=ext_name,
            current_page=current_page,
            page_size=page_size
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="获取文件列表成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取文件列表失败")

# 从知识库移除文件
@router.delete("/spark/knowledge-base/file/remove", response_model=StandardResponse, tags=["星火知识库"])
async def remove_files_from_repo(
    repo_id: str,
    file_ids: List[str],
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """从知识库移除文件"""
    try:
        result = spark_service.remove_files_from_repo(
            repo_id=repo_id,
            file_ids=file_ids
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="文件移除成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移除文件失败: {e}")
        raise HTTPException(status_code=500, detail="移除文件失败")

# 与知识库对话
@router.post("/spark/chat", response_model=StandardResponse, tags=["星火知识库"])
async def chat_with_knowledge_base(
    request: SparkQAModel,
    spark_service: SparkAPIService = Depends(get_spark_service)
):
    """与星火知识库对话"""
    try:
        result = spark_service.chat_with_knowledge_base(
            question=request.question,
            repo_id=request.repo_id,
            file_ids=request.file_ids,
            temperature=request.temperature,
            wiki_filter_score=request.wiki_filter_score
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return StandardResponse(
            success=True,
            message="对话成功",
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail="对话失败")

# ==================== 混合知识查询API ====================

# 混合搜索
@router.post("/hybrid/search", response_model=HybridSearchResponse, tags=["混合查询"])
async def hybrid_search(
    query: HybridSearchQuery,
    hybrid_service: HybridKnowledgeService = Depends(get_hybrid_service_instance)
):
    """混合搜索：结合图数据库推理和星火知识库查询"""
    try:
        result = hybrid_service.hybrid_search(query)
        return result
    except Exception as e:
        logger.error(f"混合搜索失败: {e}")
        raise HTTPException(status_code=500, detail="混合搜索失败")

# 创建知识库节点
@router.post("/hybrid/knowledge-base/node", response_model=StandardResponse, tags=["混合查询"])
async def create_knowledge_base_node(
    repo_id: str,
    repo_name: str,
    repo_desc: str = "",
    hybrid_service: HybridKnowledgeService = Depends(get_hybrid_service_instance)
):
    """创建知识库节点"""
    try:
        node_id = hybrid_service.create_knowledge_base_node(repo_id, repo_name, repo_desc)
        if node_id:
            return StandardResponse(
                success=True,
                message="知识库节点创建成功",
                data={"node_id": node_id, "repo_id": repo_id}
            )
        else:
            raise HTTPException(status_code=400, detail="知识库节点创建失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建知识库节点失败: {e}")
        raise HTTPException(status_code=500, detail="创建知识库节点失败")

# 关联概念到知识库
@router.post("/hybrid/link/concept", response_model=StandardResponse, tags=["混合查询"])
async def link_concept_to_knowledge_base(
    concept_name: str,
    repo_id: str,
    file_ids: List[str] = None,
    hybrid_service: HybridKnowledgeService = Depends(get_hybrid_service_instance)
):
    """将概念关联到知识库"""
    try:
        success = hybrid_service.link_concept_to_knowledge_base(concept_name, repo_id, file_ids)
        if success:
            return StandardResponse(
                success=True,
                message="概念关联成功",
                data={"concept_name": concept_name, "repo_id": repo_id}
            )
        else:
            raise HTTPException(status_code=400, detail="概念关联失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"关联概念失败: {e}")
        raise HTTPException(status_code=500, detail="关联概念失败")

# 获取知识系统摘要
@router.get("/hybrid/summary", response_model=StandardResponse, tags=["混合查询"])
async def get_knowledge_summary(
    hybrid_service: HybridKnowledgeService = Depends(get_hybrid_service_instance)
):
    """获取知识系统摘要"""
    try:
        summary = hybrid_service.get_knowledge_summary()
        return StandardResponse(
            success=True,
            message="获取知识摘要成功",
            data=summary
        )
    except Exception as e:
        logger.error(f"获取知识摘要失败: {e}")
        raise HTTPException(status_code=500, detail="获取知识摘要失败") 