import os
from .stt_service import XunfeiLongFormASR # 导入你提供的STT Caller
from .tree_builder_service import TreeBuilderService

class AudioProcessingService:
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.stt_caller = XunfeiLongFormASR()
        self.tree_builder = TreeBuilderService(doc_id=doc_id)

    def process_audio_file(self, audio_filepath: str, audio_filename: str):
        """
        处理MP3文件的完整流水线。
        """
        print(f"[{self.doc_id}] 开始处理音频文件: {audio_filename}")
        
        # 1. 调用讯飞服务进行语音转写
        with open(audio_filepath, 'rb') as audio_file:
            # 上传并轮询获取结果
            upload_content = self.stt_caller.upload_audio(audio_file, audio_filename)
            order_id = upload_content['orderId']
            result_content = self.stt_caller.poll_for_result(order_id)
            
            # 解析结果
            full_text, _ = self.stt_caller.parse_result_to_srt(result_content)

        print(f"[{self.doc_id}] 语音转写完成，开始构建语义树...")
        if not full_text:
            raise Exception("语音转写结果为空，无法构建树。")

        # 2. 将转写文本喂给RAPTOR
        frontend_tree = self.tree_builder.build_tree_from_text(full_text)
        
        print(f"[{self.doc_id}] 音频处理流程全部完成。")
        return frontend_tree