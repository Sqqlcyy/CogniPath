# /app/models/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ==============================================================================
# 1. 核心数据结构 (Core Data Structures)
# ==============================================================================

class DocumentTreeNode(BaseModel):
    """
    【前端契约】定义了知识树中单个节点的结构。
    这个模型必须与 TreeBuilderService._format_raptor_tree_to_schema 的输出
    以及前端 /src/types/index.ts 中的 TreeNode 类型严格一致。
    """
    id: str = Field(..., description="节点唯一ID，对应RAPTOR内部的index")
    label: str = Field(..., description="节点显示的文本 (通常是原文或摘要的截断)")
    type: Literal["section", "leaf"] = Field(..., description="节点类型，'section'为非叶子节点，'leaf'为叶子节点")
    children: List['DocumentTreeNode'] = Field([], description="子节点列表")
    full_text: str = Field(..., description="该节点的完整原文或摘要内容")
    timestamp: Optional[float] = Field(None, description="对于视频，表示该节点对应的起始时间戳 (单位: 秒)")

# 启用Pydantic对递归模型的支持
DocumentTreeNode.model_rebuild()


# ==============================================================================
# 2. 异步任务与处理模型 (Task & Processing Models)
# ==============================================================================

class TaskCreationResponse(BaseModel):
    """
    对应后端 POST /documents/process 接口的响应体。
    在启动后台任务后立即返回。
    """
    task_id: str = Field(..., description="后台任务的唯一ID，用于后续状态轮询")
    doc_id: str = Field(..., description="为本次上传的资源分配的唯一文档ID")


class TaskResult(BaseModel):
    """
    当后台任务成功完成时，包含在 TaskStatusResponse 中的结果对象。
    """
    doc_id: str
    doc_name: str
    doc_type: Literal['video', 'document']
    source_url: Optional[str] = Field(None, description="对于视频，这是可直接播放的URL")
    # 注意：为了避免在单次请求中传输过多数据，这里不包含完整的树。
    # 前端应在任务完成后，通过另一个API来获取树。


class TaskStatusResponse(BaseModel):
    """
    对应后端 GET /tasks/{task_id}/status 接口的响应体。
    前端通过轮询此接口来获取任务的实时状态。
    """
    status: Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED", "NOT_FOUND"]
    progress: Optional[int] = Field(None, description="任务进度 (0-100)")
    step: Optional[str] = Field(None, description="当前处理步骤的文本描述")
    result: Optional[TaskResult] = Field(None, description="仅当status为'COMPLETED'时存在")
    error: Optional[str] = Field(None, description="仅当status为'FAILED'时存在")


# ==============================================================================
# 3. 交互模型 (Interaction Models)
# ==============================================================================

class QueryRequest(BaseModel):
    """
    对应后端 POST /query/precise 接口的请求体。
    """
    doc_id: str
    question: str


class QueryResponse(BaseModel):
    """
    对应后端 POST /query/precise 接口的响应体。
    """
    answer: str
    source_ids: List[str] = Field([], description="答案引用的叶子节点ID列表，用于前端溯源高亮")


class GenerateMaterialRequest(BaseModel):
    """
    对应后端 POST /generate/materials 接口的请求体。
    """
    doc_id: str
    topic: str
    material_type: Literal["exam", "summary"]


class GenerateMaterialResponse(BaseModel):
    """
    对应后端 POST /generate/materials 接口的响应体。
    """
    content: str = Field(..., description="生成的材料内容 (Markdown格式的考卷或复习大纲)")
    material_type: str


class NodeContentResponse(BaseModel):
    """
    对应后端 GET /documents/{doc_id}/node/{node_id} 接口的响应体。
    """
    id: str
    full_text: str
    timestamp: Optional[float]