# /app/services/url_processing_pipeline.py
import os
import sys
from pathlib import Path
import getpass
import asyncio
import logging
import aiofiles
import yt_dlp  # 导入我们强大可靠的新工具

# 导入我们其他的服务和数据模型
from .ffmpeg_service import FFmpegService
from .stt_service import SparkSTTService
from ..models.pipeline_context import ProcessingContext
from ..core.config import UPLOADS_DIR
UPLOAD_DIR = "./uploads"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UrlProcessingPipeline:
    """
    【最终重构版】
    负责将视频URL通过一个完整的、全自动的流水线处理成可供RAPTOR分析的文本。
    核心下载引擎已替换为业界标准的 yt-dlp。
    """
    def __init__(self):
        # 【核心修改】: 我们不再需要那个不稳定的BilibiliDownloaderService了
        self.ffmpeg = FFmpegService()
        self.stt = SparkSTTService()

    async def _step_1_and_2_process_url_with_ytdlp(self, context: ProcessingContext) -> ProcessingContext:
        """
        【全新核心步骤】: 使用yt-dlp一步完成信息获取和视频下载。
        这个方法将取代之前所有的downloader步骤。
        """
        logger.info(f"[{context.task_id}] 步骤1+2: 使用yt-dlp处理URL: {context.original_url}")

        # yt-dlp的配置选项
        output_template = os.path.join(UPLOAD_DIR, f"{context.task_id}.%(ext)s")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True,
            'merge_output_format': 'mp4',
        }

        # yt-dlp是同步阻塞库，在async环境中必须用run_in_executor在单独线程中运行
        loop = asyncio.get_running_loop()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = await loop.run_in_executor(
                    None, 
                    lambda: ydl.extract_info(context.original_url, download=True)
                )
            
            # 从返回的信息中提取我们需要的一切
            context.video_title = info_dict.get('title', '未知视频')
            final_filepath = os.path.join(UPLOAD_DIR, f"{context.task_id}.mp4")
            
            if not os.path.exists(final_filepath):
                 raise FileNotFoundError(f"yt-dlp下载完成，但在预期路径未找到文件: {final_filepath}")

            context.raw_video_filepath = final_filepath
            context.direct_video_url = final_filepath 

            logger.info(f"[{context.task_id}] yt-dlp处理成功: '{context.video_title}'")
            return context

        except Exception as e:
            logger.error(f"[{context.task_id}] yt-dlp在处理URL时发生严重错误: {e}", exc_info=True)
            raise Exception(f"yt-dlp failed to process URL: {e}")

    async def step_4_transcribe_audio(self, context: ProcessingContext) -> ProcessingContext:
        """步骤4: 调用STT服务进行语音转写。【终极诊断版】"""
        logger.info(f"[{context.task_id}] 步骤4: 进入终极诊断版...")

        # --- 1. 环境探针 ---
        logger.info(f"[{context.task_id}] --- 环境探针 ---")
        logger.info(f"[{context.task_id}] Python可执行文件路径: {sys.executable}")
        logger.info(f"[{context.task_id}] 当前工作目录 (CWD): {os.getcwd()}")
        logger.info(f"[{context.task_id}] 当前运行用户: {getpass.getuser()}")
        logger.info(f"[{context.task_id}] UPLOADS_DIR绝对路径: {UPLOADS_DIR.resolve()}")
        logger.info(f"[{context.task_id}] UPLOADS_DIR是否存在: {UPLOADS_DIR.exists()}")
        logger.info(f"[{context.task_id}] UPLOADS_DIR是否是目录: {UPLOADS_DIR.is_dir()}")
        logger.info(f"[{context.task_id}] UPLOADS_DIR是否可写: {os.access(UPLOADS_DIR, os.W_OK)}")
        logger.info(f"[{context.task_id}] --------------------")
        
        # 2. 获取转写文本 (同前)
        transcribed_text = await self.stt.transcribe(context.extracted_audio_filepath)
        if not transcribed_text:
            raise ValueError("语音转写服务返回了空内容。")

        # 3. 构建绝对输出路径
        output_text_path = UPLOADS_DIR / f"{context.task_id}.txt"
        logger.info(f"[{context.task_id}] 准备将 {len(transcribed_text)} 字符写入目标路径: {output_text_path}")

        # 4. 执行写入并进行多重、冗余的验证
        try:
            # 4a. 写入文件
            async with aiofiles.open(output_text_path, 'w', encoding='utf-8') as f:
                await f.write(transcribed_text)
            logger.info(f"[{context.task_id}] aiofiles.write 操作完成。")

            # 4b. 【第一重验证】Python的Pathlib库
            path_obj = Path(output_text_path)
            exists_check_1 = path_obj.exists()
            logger.info(f"[{context.task_id}] [验证1 - Pathlib] 文件是否存在? -> {exists_check_1}")

            # 4c. 【第二重验证】Python的os模块
            exists_check_2 = os.path.exists(output_text_path)
            logger.info(f"[{context.task_id}] [验证2 - os.path] 文件是否存在? -> {exists_check_2}")
            
            # 4d. 如果存在，进行内容验证
            if exists_check_1 and exists_check_2:
                file_size = path_obj.stat().st_size
                logger.info(f"[{context.task_id}] 文件大小为: {file_size} 字节。")
                if file_size == 0:
                    raise IOError(f"验证失败：文件已创建但大小为0。")
                
                # 4e. 【第三重验证】尝试立即读回内容
                async with aiofiles.open(output_text_path, 'r', encoding='utf-8') as f:
                    content_read_back = await f.read()
                logger.info(f"[{context.task_id}] [验证3 - 读回] 成功读回 {len(content_read_back)} 字符。")
                if not content_read_back:
                    raise IOError("验证失败：文件存在但无法读回内容。")
            else:
                raise FileNotFoundError(f"验证失败：文件在写入后未能被找到！Pathlib检查: {exists_check_1}, os.path检查: {exists_check_2}")

        except Exception as e:
            logger.error(
                f"[{context.task_id}] 在写入或验证转写文件时发生致命错误: {e}",
                exc_info=True # 打印完整的traceback
            )
            raise

        # 5. 所有验证成功后，才算真正成功
        context.transcribed_text_filepath = str(output_text_path)
        logger.info(f"[{context.task_id}] 语音转写完成，结果已通过【多重验证】并保存: {output_text_path}")
        return context    
    async def cleanup(self, context: ProcessingContext):
        """步骤5 (可选): 清理中间文件。(此方法保持不变)"""
        logger.info(f"[{context.task_id}] 步骤5: 清理中间文件...")
        files_to_delete = [
            context.raw_video_filepath,
            context.extracted_audio_filepath,
        ]
        for f_path in files_to_delete:
            if f_path and os.path.exists(f_path):
                try:
                    os.remove(f_path)
                    logger.info(f"[{context.task_id}] 已删除: {f_path}")
                except Exception as e:
                    logger.warning(f"[{context.task_id}] 删除文件失败: {e}")

    async def run(self, context: ProcessingContext) -> ProcessingContext:
        """
        【核心修改】执行全新的、更可靠的全自动流水线。
        """
        try:
            # 1. 使用yt-dlp处理URL (一步到位)
            context = await self._step_1_and_2_process_url_with_ytdlp(context)
            
            # 2. 调用FFmpeg提取音频 (不变)
            context = await self.ffmpeg.step_3_extract_audio(context)
            
            # 3. 调用STT服务进行转写 (不变)
            context = await self.step_4_transcribe_audio(context)
            
            # 4. 清理 (不变)
            await self.cleanup(context)

            return context
        except Exception as e:
            logger.error(f"[{context.task_id}] 流水线执行失败: {e}", exc_info=True)
            # 向上抛出异常，让background_tasks可以捕获并更新任务状态
            raise