# /app/services/bilibili_downloader_service.py (最终yt-dlp驱动版)

import os
import asyncio
import logging
from typing import Dict, Any

import yt_dlp # 导入我们可靠的新工具

from ..models.pipeline_context import ProcessingContext

UPLOAD_DIR = "./uploads"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BilibiliDownloaderService:
    """
    【最终版】
    使用业界标准的yt-dlp库来可靠地处理Bilibili视频。
    这个服务现在一步就能完成信息获取和视频下载。
    """
    def __init__(self):
        # 我们不再需要那个不稳定的api_client了
        pass

    async def process_url(self, context: ProcessingContext) -> ProcessingContext:
        """
        【全新核心方法】: 使用yt-dlp一步完成信息获取和视频下载。
        这个方法将取代之前的所有step_1, step_2。
        """
        logger.info(f"[{context.task_id}] 步骤1: 使用yt-dlp处理URL: {context.original_url}")

        # yt-dlp的配置选项
        output_template = os.path.join(UPLOAD_DIR, f"{context.task_id}.%(ext)s")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # 下载最佳画质的mp4
            'outtmpl': output_template,
            'quiet': True,
            'merge_output_format': 'mp4',
            # (可选) 如果下载慢，可以加上代理
            # 'proxy': 'http://127.0.0.1:7890', 
        }

        # yt-dlp的库是同步阻塞的，在async函数中，我们必须用run_in_executor
        # 把它放到一个单独的线程中运行，以避免阻塞整个应用。
        loop = asyncio.get_running_loop()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 在线程池中执行阻塞的下载操作，并等待其完成
                info_dict = await loop.run_in_executor(
                    None, # 使用默认的线程池
                    lambda: ydl.extract_info(context.original_url, download=True)
                )
            
            # 下载完成后，从返回的信息字典中提取我们需要的一切
            context.video_title = info_dict.get('title', '未知视频')
            
            # 因为我们定义了输出模板，所以我们确切地知道下载后的文件路径
            final_filepath = os.path.join(UPLOAD_DIR, f"{context.task_id}.mp4")
            
            if not os.path.exists(final_filepath):
                 raise FileNotFoundError(f"yt-dlp下载完成，但在预期路径未找到文件: {final_filepath}")

            context.raw_video_filepath = final_filepath
            # 对于后端流程，直接的本地文件路径就是视频源URL
            context.direct_video_url = final_filepath 

            logger.info(f"[{context.task_id}] yt-dlp处理成功: '{context.video_title}'")
            return context

        except Exception as e:
            logger.error(f"[{context.task_id}] yt-dlp在处理URL时发生严重错误: {e}", exc_info=True)
            raise Exception(f"yt-dlp failed to process URL: {e}")
