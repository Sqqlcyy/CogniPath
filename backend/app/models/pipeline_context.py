# /app/models/pipeline_context.py
from pydantic import BaseModel, Field
from typing import Optional

class ProcessingContext(BaseModel):
    """
    贯穿URL处理流水线的上下文对象，记录每一步的结果。
    """
    task_id: str
    original_url: str
    
    # BilibiliDownloaderService 的产物
    video_title: Optional[str] = None
    direct_video_url: Optional[str] = None
    
    # FFmpegService 的产物
    raw_video_filepath: Optional[str] = None
    extracted_audio_filepath: Optional[str] = None
    
    # STTService 的产物
    transcribed_text_filepath: Optional[str] = None
    
    # RAPTOR 的产物
    semantic_tree_built: bool = Field(default=False)