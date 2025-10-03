# app/services/xunfei_caller.py
import os
import requests
import hashlib
import hmac
import base64
import time
import json
import logging
from typing import IO, Dict, Any, List
import asyncio
from ..core.config import settings

class SparkSTTService:
    """
    封装与讯飞长语音转写（Long Form ASR）API的交互。
    """
    def __init__(self):
        self.host = "raasr.xfyun.cn"
        self.upload_url = "https://raasr.xfyun.cn/v2/api/upload"
        self.get_result_url = "https://raasr.xfyun.cn/v2/api/getResult"
        
        self.app_id = "56799f04"
        # 你的接口密钥，需要从讯飞开放平台获取
        self.secret_key = "e352d6a32590df68be30c94343d4ac25" # 示例, 应从settings读取
        
        self.logger = logging.getLogger(__name__)
    async def transcribe(self, audio_filepath: str) -> str:
        """
        高层级接口：接收一个音频文件路径，完成上传、轮询、解析，并返回最终的纯文本结果。
        这是一个异步方法，它将所有阻塞的网络操作放到后台线程执行。
        """
        self.logger.info(f"开始处理转写任务，文件: {audio_filepath}")
        
        # 定义一个同步函数，包含所有阻塞操作
        def _sync_transcribe_flow():
            # 1. 打开文件并上传
            try:
                with open(audio_filepath, 'rb') as audio_file:
                    file_name = os.path.basename(audio_filepath)
                    upload_content = self._upload_audio(audio_file, file_name)
                    order_id = upload_content['orderId']
            except FileNotFoundError:
                self.logger.error(f"音频文件未找到: {audio_filepath}")
                raise
            except Exception as e:
                self.logger.error(f"上传音频文件时出错: {e}")
                raise

            # 2. 轮询获取结果
            try:
                result_content = self._poll_for_result(order_id)
            except Exception as e:
                self.logger.error(f"轮询获取结果时出错: {e}")
                raise

            # 3. 解析结果
            try:
                full_text, _ = self._parse_result_to_srt(result_content)
                return full_text
            except Exception as e:
                self.logger.error(f"解析讯飞结果时出错: {e}")
                raise

        # 使用 asyncio.to_thread 执行整个同步流程，避免阻塞
        try:
            transcribed_text = await asyncio.to_thread(_sync_transcribe_flow)
            self.logger.info("语音转写任务成功完成。")
            return transcribed_text
        except Exception as e:
            # 捕获流程中任何环节的异常，并向上抛出
            self.logger.error(f"语音转写流程失败: {e}")
            raise

    def _generate_signa(self, ts: str) -> str:
        """根据讯飞文档生成签名"""
        base_string = f"{self.app_id}{ts}"
        base_string_md5 = hashlib.md5(base_string.encode('utf-8')).hexdigest()
        
        signature_sha = hmac.new(
            self.secret_key.encode('utf-8'),
            base_string_md5.encode('utf-8'),
            digestmod=hashlib.sha1
        ).digest()
        
        signa = base64.b64encode(signature_sha).decode('utf-8')
        return signa

    def _upload_audio(self, audio_file: IO[bytes], file_name: str) -> Dict[str, Any]:
        """
        第一步：上传音频文件，创建转写任务，并返回订单信息。
        """
        audio_file.seek(0, 2)
        file_size = audio_file.tell()
        audio_file.seek(0)
        
        # 估算音频时长（粗略），讯飞允许不精确
        # 假设 16k/16bit/单声道 -> 32000 bytes/sec
        duration = file_size // 32000 + 1 
        
        ts = str(int(time.time()))
        signa = self._generate_signa(ts)
        
        params = {
            "appId": self.app_id,
            "signa": signa,
            "ts": ts,
            "fileName": file_name,
            "fileSize": file_size,
            "duration": duration,
            "language": "cn", # 默认中文
            "pd": "edu"       # 领域：教育
        }
        
        headers = {'Content-Type': 'application/octet-stream'}
        
        self.logger.info(f"正在上传音频文件 {file_name} 到讯飞...")
        try:
            response = requests.post(self.upload_url, params=params, headers=headers, data=audio_file)
            response.raise_for_status()
            result = response.json()

            if result.get("code") != "000000":
                raise Exception(f"讯飞上传失败: {result.get('descInfo')}")
            
            self.logger.info(f"文件上传成功，订单ID: {result['content']['orderId']}")
            return result['content'] # 返回 {"orderId": "...", "taskEstimateTime": ...}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"上传音频到讯飞时网络错误: {e}")
            raise e

    def get_result(self, order_id: str) -> Dict[str, Any]:
        """
        第二步：根据订单ID查询转写结果。
        """
        ts = str(int(time.time()))
        signa = self._generate_signa(ts)
        
        params = {
            "appId": self.app_id,
            "signa": signa,
            "ts": ts,
            "orderId": order_id,
        }
        
        try:
            response = requests.post(self.get_result_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"查询讯飞转写结果时网络错误: {e}")
            raise e

    def _poll_for_result(self, order_id: str, interval: int = 10, timeout: int = 3600) -> Dict[str, Any]:
        """
        第三步：轮询直到获取到最终结果。
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.logger.info(f"正在查询订单 {order_id} 的转写状态...")
            result = self.get_result(order_id)
            
            if result.get("code") != "000000":
                raise Exception(f"查询结果失败: {result.get('descInfo')}")
            
            order_info = result.get("content", {}).get("orderInfo", {})
            status = order_info.get("status")
            
            if status == 4: # 4: 订单已完成
                self.logger.info(f"订单 {order_id} 转写成功！")
                return result['content']
            elif status == -1: # -1: 订单失败
                raise Exception(f"订单 {order_id} 转写失败，失败类型: {order_info.get('failType')}")
            else:
                self.logger.info(f"订单 {order_id} 仍在处理中 (状态: {status})，{interval}秒后重试...")
                time.sleep(interval)
        
        raise TimeoutError(f"查询订单 {order_id} 超时 ({timeout}秒)")
    
    @staticmethod
    def _parse_result_to_srt(result_content: Dict[str, Any]) -> tuple[str, str]:
        """将讯飞返回的JSON结果解析成纯文本和带时间戳的SRT格式"""
        full_text = ""
        srt_content = ""
        sentence_index = 1
        
        try:
            order_result_str = result_content.get("orderResult", "{}")
            order_result = json.loads(order_result_str)
            
            # 使用 lattice 字段获取带时间戳的句子
            if "lattice" in order_result:
                for segment in order_result["lattice"]:
                    json_1best_str = segment.get("json_1best", "{}")
                    json_1best = json.loads(json_1best_str)
                    
                    st = json_1best.get("st", {})
                    bg_ms = int(st.get("bg", 0))
                    ed_ms = int(st.get("ed", 0))
                    
                    sentence_text = "".join([cw['w'] for rt in st.get("rt", []) for ws in rt['ws'] for cw in ws['cw']])
                    
                    if sentence_text:
                        full_text += sentence_text
                        
                        # 构建SRT格式
                        start_time_str = SparkSTTService._format_srt_time(bg_ms)
                        end_time_str = SparkSTTService._format_srt_time(ed_ms)
                        srt_content += f"{sentence_index}\n"
                        srt_content += f"{start_time_str} --> {end_time_str}\n"
                        srt_content += f"{sentence_text}\n\n"
                        sentence_index += 1
            
            return full_text.strip(), srt_content.strip()

        except Exception as e:
            logging.error(f"解析讯飞结果失败: {e}")
            return "解析结果失败", ""

    @staticmethod
    def _format_srt_time(ms: int) -> str:
        """将毫秒转换为SRT时间格式 HH:MM:SS,mmm"""
        seconds, milliseconds = divmod(ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"