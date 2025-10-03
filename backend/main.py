# /main.py

import sys
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# --- 【最终核心修正】: 解决Windows下的NotImplementedError ---
# 这段代码必须放在所有asyncio相关操作（包括FastAPI初始化）的最前面。
# 它会检查当前操作系统，如果是Windows，就设置一个支持异步子进程的事件循环策略。
if sys.platform == "win32":
    print("检测到Windows系统，正在设置ProactorEventLoopPolicy以支持异步子进程...")
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ---------------------------------------------------------

# 确保RAPTOR库能被正确导入 (假设你已将raptor代码放入libs目录)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))

# 导入我们自己的模块
from app.core.config import settings
from app.api.v1 import endpoints

# 创建FastAPI应用
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 开发阶段允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

if __name__ == "__main__":
    # 使用uvicorn来运行应用
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)