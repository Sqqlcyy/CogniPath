# app/core/dependencies.py
from functools import lru_cache
from ..core.config import settings
from ..core.engine import AIEngine
from ..core.local_model_handler import LocalModelHandler
from ..services.ai_gateway import AIGateway
from ..services.query_service import QueryService
from ..services.document_service import DocumentService
from ..services.exam_service import ExamService
from ..services.stt_service import XunfeiLongFormASR
from ..storage.graph_store import KnowledgeGraphManager, Neo4jConnector
from ..storage.vector_store import VectorStore
# ... 其他storage的导入 ...

# 使用lru_cache(maxsize=None)作为创建单例的简单方式
@lru_cache(maxsize=None)
def get_settings() -> settings:
    return settings

@lru_cache(maxsize=None)
def get_neo4j_connector() -> Neo4jConnector:
    connector = Neo4jConnector(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database
    )
    connector.connect() # 应用启动时即连接
    return connector

@lru_cache(maxsize=None)
def get_knowledge_graph_manager() -> KnowledgeGraphManager:
    return KnowledgeGraphManager(connector=get_neo4j_connector())

@lru_cache(maxsize=None)
def get_vector_store() -> VectorStore:
    return VectorStore(path=settings.vector_db_path)

@lru_cache(maxsize=None)
def get_local_model_handler() -> LocalModelHandler:
    return LocalModelHandler()

@lru_cache(maxsize=None)
def get_ai_engine() -> AIEngine:
    return AIEngine(
        local_model_handler=get_local_model_handler(),
        score_model_path=settings.score_model_path
    )
    
@lru_cache(maxsize=None)
def get_stt_caller() -> XunfeiLongFormASR:
    return XunfeiLongFormASR()

@lru_cache(maxsize=None)
def get_ai_gateway() -> AIGateway:
    # AIGateway的实现需要GenerationService，这里先简化
    return AIGateway(engine=get_ai_engine(), stt_caller=get_stt_caller())

@lru_cache(maxsize=None)
def get_document_service() -> DocumentService:
    return DocumentService()

@lru_cache(maxsize=None)
def get_query_service() -> QueryService:
    return QueryService(
        ai_gateway=get_ai_gateway()
        # retrieval_service的依赖待注入
    )

# ... 其他服务的getter ...