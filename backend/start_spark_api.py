# -*- coding:utf-8 -*-
"""
星火知识库API服务启动脚本
"""

import uvicorn
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """启动星火API服务"""
    logger.info("正在启动星火知识库API服务...")
    logger.info(f"启动时间: {datetime.now().isoformat()}")
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 