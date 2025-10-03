from app.services.tree_builder_service import TreeBuilderService

# 当需要问答时


# /app/api/v1/endpoints.py

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form, HTTPException
import uuid
import os
from typing import Optional, List

# 导入我们设计的任务管理器、后台任务、Pydantic模型和服务
from ...tasks import task_manager
from ...tasks.background_tasks import run_url_processing_task, run_file_processing_task
from ...models.schemas import TaskStatusResponse, QueryRequest, GenerateMaterialRequest, DocumentTreeNode
from ...services.tree_builder_service import TreeBuilderService

router = APIRouter()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/query/precise")
async def query_precise(request: QueryRequest):
    # 每次请求都针对特定的doc_id实例化服务
    # 构造函数会自动处理缓存加载
    service = TreeBuilderService(doc_id=request.doc_id)
    result = service.answer_precise_question(request.question)
    return result
@router.post("/documents/process", summary="处理新的文档源 (URL或文件)")
async def process_document_source(
    background_tasks: BackgroundTasks,
    source_type: str = Form(...),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    task_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    
    task_manager.create_task(task_id, doc_id)

    if source_type == 'url':
        if not url: raise HTTPException(status_code=400, detail="URL is required")
        background_tasks.add_task(run_url_processing_task, task_id, doc_id, url)
        return {"task_id": task_id, "doc_id": doc_id}
    
    elif source_type == 'file':
        if not file: raise HTTPException(status_code=400, detail="File is required")
        filepath = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())
        background_tasks.add_task(run_file_processing_task, task_id, doc_id, filepath, file.filename)
        return {"task_id": task_id, "doc_id": doc_id}

    raise HTTPException(status_code=400, detail="Invalid source_type.")


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse, summary="获取后台任务状态")
async def get_task_status(task_id: str):
    status = task_manager.get_task_status(task_id)
    if not status: raise HTTPException(status_code=404, detail="Task not found")
    return status


@router.get("/documents/{doc_id}/tree", response_model=List[DocumentTreeNode], summary="获取已构建完成的知识树")
async def get_document_tree(doc_id: str):
    try:
        service = TreeBuilderService(doc_id=doc_id)
        if not service.raptor_instance or not service.raptor_instance.tree:
            raise HTTPException(status_code=404, detail="Tree not found or not built yet.")
        return service._format_raptor_tree_to_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tree: {e}")


@router.post("/query/precise", summary="精确问答 (TreeRetriever)")
async def query_precise(request: QueryRequest):
    try:
        service = TreeBuilderService(doc_id=request.doc_id)
        return service.answer_precise_question(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/materials", summary="生成学习材料 (FaissRetriever)")
async def generate_materials(request: GenerateMaterialRequest):
    try:
        service = TreeBuilderService(doc_id=request.doc_id)
        return service.generate_learning_materials(request.topic, request.material_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}/node/{node_id}", summary="获取单个节点的原文")
async def get_node_content(doc_id: str, node_id: str):
    try:
        service = TreeBuilderService(doc_id=doc_id)
        node = service.raptor_instance.tree.all_nodes.get(int(node_id))
        if not node: raise HTTPException(status_code=404, detail="Node not found")
        # timestamp = getattr(service.raptor_instance.tree, 'node_id_to_timestamp', {}).get(int(node_id))
        return {"id": node_id, "full_text": node.text, "timestamp": None} # timestamp logic to be added
    except (AttributeError, ValueError, KeyError):
        raise HTTPException(status_code=404, detail="Document or Node not found.")