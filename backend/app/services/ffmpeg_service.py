# /app/services/ffmpeg_service.py
import asyncio
import os
import subprocess
from ..models.pipeline_context import ProcessingContext

UPLOAD_DIR = "./uploads"

class FFmpegService:
    async def step_3_extract_audio(self, context: ProcessingContext) -> ProcessingContext:
        """步骤3: 从视频文件中提取WAV格式的音频。 (跨平台兼容最终版)"""
        if not context.raw_video_filepath:
            raise ValueError("上下文中缺少原始视频文件路径。")

        print(f"[{context.task_id}] 步骤3: 开始提取音频...")
        
        input_video = context.raw_video_filepath
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        output_audio = os.path.join(UPLOAD_DIR, f"{context.task_id}.wav")
        
        command = [
            'ffmpeg', '-i', input_video, '-vn', 
            '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', 
            '-y', output_audio
        ]

        # 这是关键：将同步阻塞的 ffmpeg 调用封装成一个函数
        def _run_sync():
            try:
                print(f"[{context.task_id}] 在后台线程中执行FFmpeg: {' '.join(command)}")
                # subprocess.run 是同步阻塞的，它会在这里等待ffmpeg执行完毕
                result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
                # 成功执行后，result.stderr 可能包含一些警告信息，通常可以打印出来用于调试
                if result.stderr:
                    print(f"[{context.task_id}] FFmpeg 警告/信息: {result.stderr}")
            except subprocess.CalledProcessError as e:
                # 当 ffmpeg 返回非0退出码时，check=True会触发这个异常
                error_output = e.stderr.strip()
                error_msg = f"FFmpeg提取音频失败。错误详情: {error_output}"
                print(f"[{context.task_id}] {error_msg}")
                # 重新抛出异常，这样上层调用者可以捕获到它
                raise Exception(error_msg) from e
        
        try:
            # 使用 await asyncio.to_thread(...) 将上面那个阻塞函数扔到后台线程执行
            # 主事件循环不会被卡住，可以继续响应请求
            await asyncio.to_thread(_run_sync)

            # 代码能走到这里，说明 _run_sync() 函数在后台线程中成功执行完毕
            context.extracted_audio_filepath = output_audio
            print(f"[{context.task_id}] 音频提取成功: {output_audio}")
            return context

        except Exception as e:
            # 捕获 _run_sync 中抛出的异常，或者 to_thread 本身的错误
            # 这样可以确保任何失败都会被正确处理，而不会让服务无响应
            print(f"[{context.task_id}] 音频提取流程发生严重错误: {e}")
            # 向上抛出，让你的Web框架的异常处理中间件来返回一个标准的错误响应 (例如 HTTP 500)
            raise
