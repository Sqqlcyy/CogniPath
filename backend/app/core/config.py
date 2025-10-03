# /app/core/config.py (最终版)

from pydantic_settings import BaseSettings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

class Settings(BaseSettings):
    """
    应用的统一配置中心。
    Pydantic会自动从.env文件中读取并验证所有字段。
    """
    # --- 应用基础配置 ---
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    # --- 讯飞API凭证 ---
    SPARK_APP_ID: str
    SPARK_API_SECRET: str
    SPARK_API_KEY: str
    SPARK_API_PASSWORD: str

    # --- 服务URL ---
    SPARK_STT_HOST: str
    SPARK_EMBEDDING_URL: str
    SPARK_BASE_URL_V1: str
    SPARK_BASE_URL_V2: str
    SPARK_OCR_URL: str
    # --- 数据库与中间件配置 ---
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    class Config:
        # 指定Pydantic从哪个文件读取环境变量
        env_file = ".env"
        env_file_encoding = 'utf-8'

# 创建一个全局的配置实例，供项目其他地方导入
# from app.core.config import settings
settings = Settings()
