
### **`README.md` (项目总览、部署与开发指南)**

```markdown
# 知语 CogniPath AI - 后端服务

欢迎来到“知语AI”的后端服务项目！本项目是“知语AI”强大的认知与备考引擎的核心，负责处理多模态数据、构建知识图谱、并运行先进的`LongRefiner`算法来提供智能问答和模拟题生成服务。

**项目Slogan:** 不止于记录，我们重塑你的思考路径。

## 一、技术栈 (Tech Stack)

- **框架:** Python 3.10+, FastAPI
- **AI核心:**
  - **引擎:** 自研`LongRefiner`算法框架
  - **本地模型:** Qwen2.5-3B (微调), BAAI/bge-reranker-v2-m3
  - **云端大模型:** 讯飞星火认知大模型 (X1)
- **数据库 & 中间件:**
  - **图数据库:** Neo4j
  - **向量数据库:** ChromaDB
  - **任务队列:** Celery
  - **消息中间件:** Redis
- **部署:** Docker, Docker Compose, Gunicorn, Uvicorn, Nginx

## 二、项目结构

```
backend/
├── app/
│   ├── api/routes.py         # API路由层
│   ├── core/                 # 核心算法、配置、依赖注入
│   ├── models/schemas.py     # Pydantic数据模型
│   ├── services/             # 业务逻辑服务层
│   ├── storage/              # 数据库与文件存储交互层
│   └── tasks/                # Celery异步任务定义
├── .env                      # 环境变量 (本地开发)
├── docker-compose.yml        # 依赖服务编排
├── Dockerfile                # 应用容器化配置
├── requirements.txt          # Python依赖
└── README.md                 # 本文档
```

## 三、本地开发环境搭建

### 1. 前置条件
- Python 3.10+
- Conda (或 venv)
- Docker 和 Docker Compose

### 2. Conda环境设置

```bash
# 创建并激活conda环境
conda create -n cognipath python=3.10 -y
conda activate cognipath

# 安装所有Python依赖
pip install -r requirements.txt
```

### 3. 启动依赖服务 (使用Docker Compose)
在项目根目录下，运行以下命令来一键启动Neo4j, ChromaDB和Redis：

```bash
docker-compose up -d
```
- **Neo4j:** 浏览器访问 `http://localhost:7474` (默认用户名: `neo4j`, 密码: `password`)
- **ChromaDB:** 服务运行在容器内部，由应用直接访问。
- **Redis:** 服务运行在容器内部。

### 4. 配置环境变量
复制 `.env.example` (如果存在) 为 `.env` 文件，并填入您的真实配置，特别是讯飞API的密钥和本地模型路径。

```ini
# .env file
NEO4J_PASSWORD=your_neo4j_password
SPARK_API_KEY=your_spark_api_key
SPARK_API_SECRET=your_spark_api_secret
# ... 其他配置 ...
```

### 5. 启动应用

本项目包含三个需要独立启动的进程：

**终端1: 启动FastAPI主应用 (使用Uvicorn进行热重载)**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
访问 `http://localhost:8000/docs` 查看自动生成的API文档。

**终端2: 启动Celery Worker**
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```
这个Worker会监听并执行所有后台任务（如文档处理）。

**终端3: (可选) 启动Celery Beat (用于定时任务)**
如果未来有定时任务，可以通过此命令启动调度器。
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

## 四、API核心入口

所有API都以`/api/v1`为前缀。核心接口包括：

- `POST /sources/file`: 上传本地文件 (PPT, PDF, MP3, MP4)。
- `POST /sources/url`: 提交Bilibili视频链接。
- `GET /tasks/{task_id}/status`: 查询后台任务处理状态。
- `POST /query`: 核心问答接口，执行`LongRefiner`流程。
- `POST /exams/generate`: 生成模拟试卷。

详细接口定义请参考 `http://localhost:8000/docs`。

## 五、部署到服务器

1. **打包应用:** 使用`Dockerfile`将FastAPI应用构建成一个Docker镜像。
   ```bash
   docker build -t cognipath-backend:latest .
   ```
2. **服务器部署:**
   - 在服务器上安装Docker和Docker Compose。
   - 将`docker-compose.yml`和`.env`文件上传到服务器。
   - 修改`docker-compose.yml`，添加我们自己构建的`cognipath-backend`镜像作为服务，并添加Celery Worker服务。
   - 运行 `docker-compose up -d` 在服务器上启动所有服务。
3. **配置Nginx:**
   - 安装并配置Nginx作为反向代理。
   - 将公网域名的80/443端口流量，代理到运行后端的容器端口（如8000）。
   - 配置静态文件托管，用于未来可能的Web前端。

## 六、开发规范

- **分层清晰:** 严格遵守`路由层` -> `服务层` -> `存储/引擎层`的调用顺序。
- **配置驱动:** 所有敏感信息、可变参数都必须通过`app/core/config.py`进行管理。
- **异步优先:** 所有耗时操作（> 1秒）都应封装成Celery任务，在后台执行。
- **类型提示:** 所有函数和方法都必须有清晰的类型提示 (Type Hinting)。

---
```