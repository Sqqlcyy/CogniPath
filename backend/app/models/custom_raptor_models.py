# /app/models/custom_raptor_models.py

import os
import logging
from abc import ABC, abstractmethod

# 导入所有必要的库
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_random_exponential

# 导入RAPTOR的基类
from ..raptor.QAModels import BaseQAModel
from ..raptor.SummarizationModels import BaseSummarizationModel
from ..raptor.EmbeddingModels import BaseEmbeddingModel

# 导入我们项目的配置
from ..core.config import settings

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# ==============================================================================
# 1. 问答模型 (QA Models)
# ==============================================================================

class SparkQAModel(BaseQAModel):
    """
    【最终版】
    基础问答模型，使用星火Web API (Bearer Token鉴权)。
    """
    def __init__(self, model_name: str = "generalv3.5"):
        self.model = model_name
        self.api_password = settings.SPARK_API_PASSWORD
        if not self.api_password:
            raise EnvironmentError("SPARK_API_PASSWORD 环境变量未设置!")
            
        self.client = OpenAI(
            api_key=self.api_password,
            base_url=settings.SPARK_BASE_URL_V1 # 使用v1的地址
        )

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def answer_question(self, context, question):
        prompt = (
            f"请你基于以下【背景知识】，用中文简洁、准确地回答用户提出的【问题】。\n\n"
            f"【背景知识】:\n---\n{context}\n---\n\n"
            f"【问题】:\n{question}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个基于给定知识的智能问答机器人，你的回答必须严格依据提供的背景知识，禁止发挥或想象。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"调用星火QA API (Model: {self.model}) 失败: {e}", exc_info=True)
            return f"AI回答服务异常: {e}"


# ==============================================================================
# 2. 摘要模型 (Summarization Models)
# ==============================================================================

class SparkSummarizationModel(BaseSummarizationModel):
    """
    【最终版】
    基础摘要模型，可用于调用星火X1等兼容OpenAI SDK的API。
    """
    def __init__(self, model_name: str = "x1"):
        self.model = model_name
        # X1模型使用AK:SK组合作为api_key
        api_key_combo = f"{settings.SPARK_API_KEY}:{settings.SPARK_API_SECRET}"
        if not all([settings.SPARK_API_KEY, settings.SPARK_API_SECRET]):
             raise EnvironmentError("SPARK_API_KEY 或 SPARK_API_SECRET 环境变量未设置!")

        self.client = OpenAI(
            api_key=api_key_combo,
            base_url=settings.SPARK_BASE_URL_V2 # X1模型使用v2地址
        )

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def summarize(self, context, max_tokens=500):
        prompt = f"请将以下内容精炼地总结成一段摘要，尽可能多地包含关键细节，摘要应客观、准确、不包含个人观点：\n\n---\n\n{context}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI文本摘要助手。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"调用星火摘要 API (Model: {self.model}) 失败: {e}", exc_info=True)
            return f"摘要生成失败: {e}"


# ==============================================================================
# 3. 嵌入模型 (Embedding Models)
# ==============================================================================

class SparkEmbeddingModel(BaseEmbeddingModel):
    """
    【最终版】
    使用讯飞星火Embedding API。
    注意：这个API的鉴权方式与其他Web API不同，需要手动构造请求头。
    (这部分代码我们之前已完成，现在整合进来)
    """
    def __init__(self, **kwargs):
        self.api_url = settings.SPARK_EMBEDDING_URL
        self.appid = settings.SPARK_APP_ID
        self.api_key = settings.SPARK_API_KEY
        self.api_secret = settings.SPARK_API_SECRET
        if not all([self.appid, self.api_key, self.api_secret]):
            raise EnvironmentError("讯飞Embedding API凭证 (APPID, APIKey, APISecret) 未完全设置!")
    
    # ... (这里应该包含我们之前实现的、完整的、带鉴权的create_embedding方法)
    # ... 为了简洁，暂时省略，请确保你的代码是完整的 ...
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def create_embedding(self, text):
        # 这是一个占位符，请使用我们之前实现的完整代码
        # 它应该包含构造请求头、请求体，发送httpx请求，并解析返回的向量
        raise NotImplementedError("请在此处填入完整的星火Embedding API调用逻辑")

# class SBertEmbeddingModel(BaseEmbeddingModel):
#     """本地SBERT模型，用于开发和调试，或作为备选方案。"""
#     def __init__(self, model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1"):
#         self.model = SentenceTransformer(model_name)
#     def create_embedding(self, text):
#         return self.model.encode(text)
