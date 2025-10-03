# app/tasks/processor_tasks.py
import logging
import os
from io import BytesIO

from .celery_app import celery_app
from ..services.refinement_service import RefinementService 
from ..core.dependencies import get_refinement_service
from ..services.xunfei_caller import XunfeiLongFormASR

@celery_app.task(name="process_document_task")
def process_document_task(file_path: str, original_filename: str, course_name: str, is_exam_paper: bool):
    logger = logging.getLogger(__name__)
    logger.info(f"开始后台处理任务: {original_filename}")
    
    refinement_service: RefinementService = get_refinement_service()
    
    try:
        with open(file_path, "rb") as f:
            file_content_bytes = f.read()

        file_extension = original_filename.split('.')[-1].lower()
        
        doc_content = ""
        srt_content = "" # 我们现在可以生成SRT了

        if file_extension in ['mp3', 'wav', 'm4a', 'mp4', 'flac']: # 支持更多格式
            logger.info("检测到长音频/视频文件，调用长语音转写服务...")
            asr_caller = XunfeiLongFormASR()
            audio_file_obj = BytesIO(file_content_bytes)

            # 1. 上传并创建订单
            upload_result = asr_caller.upload_audio(audio_file_obj, original_filename)
            order_id = upload_result['orderId']
            
            # 2. 轮询获取结果 (Celery任务是异步的，所以这里的阻塞是OK的)
            transcription_result = asr_caller.poll_for_result(order_id)
            
            # 3. 解析结果
            doc_content, srt_content = XunfeiLongFormASR.parse_result_to_srt(transcription_result)

        elif file_extension in ['pdf', 'ppt', 'pptx', 'txt']:
            # ... 文档解析逻辑 ...
            doc_content = file_content_bytes.decode('utf-8', errors='ignore') 
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")

        if not doc_content:
            raise ValueError("未能从文件中提取任何有效内容。")

        # 调用服务层的方法来完成后续所有处理
        # 我们需要把SRT内容也传递下去，或者存起来
        refinement_service.process_and_store_document(
            doc_content=doc_content,
            srt_content=srt_content, # 新增
            doc_name=original_filename,
            course_name=course_name,
            is_exam_paper=is_exam_paper
        )
        logger.info(f"文档 {original_filename} 处理成功。")
        
        os.remove(file_path) # 清理临时文件
        return {"status": "SUCCESS", "filename": original_filename}
        
    except Exception as e:
        logger.error(f"文档 {original_filename} 处理失败: {e}", exc_info=True)
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"status": "FAILURE", "filename": original_filename, "error": str(e)}