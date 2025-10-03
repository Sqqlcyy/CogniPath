# /app/tasks/background_tasks.py
import os
from .task_manager import task_manager 
from ..services.url_processing_service import UrlProcessingPipeline
from ..services.file_parser_service import FileParserService
from ..services.tree_builder_service import TreeBuilderService
from ..models.pipeline_context import ProcessingContext

# ==============================================================================
# 视频URL处理任务 (全自动流水线)
# ==============================================================================
async def run_url_processing_task(task_id: str, doc_id: str, url: str):
    try:
        task_manager.update_task_progress(task_id, 10, "启动视频解析流水线...")
        
        # 1. 初始化并运行URL处理流水线
        context = ProcessingContext(task_id=task_id, original_url=url)
        pipeline = UrlProcessingPipeline()
        # 这一步会自动完成：下载 -> 提取音频 -> STT转写 -> 保存为文本文件
        final_context = await pipeline.run(context)
        
        task_manager.update_task_progress(task_id, 60, "语音转写完成，开始构建语义树...")
        
        # 2. 读取转写结果
        raw_text_path = final_context.transcribed_text_filepath
        with open(raw_text_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        os.remove(raw_text_path) # 清理中间文本文件

        # 3. 将带时间戳的文本喂给RAPTOR
        tree_builder = TreeBuilderService(doc_id=doc_id)
        # 传入 is_timestamped=True，让Service知道要处理时间戳
        frontend_tree = tree_builder.build_tree_from_text(raw_text, is_timestamped=True)

        # 4. 任务完成，准备最终结果
        result = {
            "doc_id": doc_id,
            "doc_name": final_context.video_title,
            "doc_type": "video", # 告诉前端这是个视频
            "source_url": final_context.direct_video_url, # 返回可播放的视频链接
            "document_tree": [node.model_dump() for node in frontend_tree]
        }
        task_manager.set_task_completed(task_id, result)
        
    except Exception as e:
        task_manager.set_task_failed(task_id, str(e))


# ==============================================================================
# PPT/PDF文件处理任务
# ==============================================================================
async def run_file_processing_task(task_id: str, doc_id: str, filepath: str, filename: str):
    try:
        task_manager.update_task_progress(task_id, 20, "开始解析文件内容...")
        
        # 1. 解析文件
        parser = FileParserService()
        raw_text = await parser.parse(filepath) 
        os.remove(filepath) # 清理上传的临时文件

        task_manager.update_task_progress(task_id, 60, "文件解析完成，开始构建语义树...")
        
        # 2. 将纯文本喂给RAPTOR
        tree_builder = TreeBuilderService(doc_id=doc_id)
        frontend_tree = tree_builder.build_tree_from_text(raw_text, is_timestamped=False)
        
        # 3. 任务完成
        result = {
            "doc_id": doc_id,
            "doc_name": filename,
            "doc_type": "document",
            "source_url": None, # 文件类型没有直接的播放URL
            "document_tree": [node.model_dump() for node in frontend_tree]
        }
        task_manager.set_task_completed(task_id, result)
        
    except Exception as e:
        task_manager.set_task_failed(task_id, str(e))