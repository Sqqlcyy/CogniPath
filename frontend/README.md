## 技术栈 

-   **框架:** [Vue 3](https://vuejs.org/) (使用 Composition API & `<script setup>`)
-   **构建工具:** [Vite](https://vitejs.dev/)
-   **状态管理:** [Pinia](https://pinia.vuejs.org/)
-   **UI 组件库:** [Element Plus](https://element-plus.org/)
-   **图标库:** `@element-plus/icons-vue`
-   **编程语言:** [TypeScript](https://www.typescriptlang.org/)
-   **HTTP客户端:** [Axios](https://axios-http.com/)
-   **CSS预处理器:** [Sass/SCSS](https://sass-lang.com/)
-   **代码格式化:** [Prettier](https://prettier.io/)
-   **Node.js版本管理:** [nvm](https://github.com/nvm-sh/nvm) (推荐使用 v20.x LTS)

---

## 架构设计

采用严格的**分层**和**模块化**架构，确保代码的**高内聚、低耦合**，便于团队协作和未来扩展。

### frontend目录结构

```
frontend/
├── src/
│   ├── api/              # 服务层 
│   │   └── modules/
│   │       ├── document.ts
│   │       └── query.ts
│   ├── assets/           # 静态资源
│   ├── components/       # 全局通用组件 (目前为空)
│   ├── layouts/          # 布局组件
│   │   └── DefaultLayout.vue
│   ├── modules/          # 【架构核心】业务模块
│   │   ├── chat/
│   │   │   └── components/
│   │   │       ├── ChatModule.vue
│   │   │       ├── ChatHistory.vue
│   │   │       ├── MessageInput.vue
│   │   │       └── CitationModule.vue
│   │   └── document/
│   │       └── components/
│   │           ├── DocumentModule.vue
│   │           └── UploadModal.vue
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # 状态管理层 
│   │   ├── index.ts
│   │   └── modules/
│   │       ├── document.ts
│   │       └── chat.ts
│   ├── styles/           # 全局样式
│   │   └── main.scss
│   ├── types/            # TypeScript类型定义
│   │   ├── api.ts
│   │   └── index.ts
│   ├── utils/            # 通用工具函数
│   │   └── request.ts
│   ├── views/            # 页面视图【新增并确认】
│   │   └── MainView.vue
│   ├── App.vue           # 根组件
│   ├── main.ts           # 应用入口
│   └── vite-env.d.ts     # Vite 环境变量类型声明
├── .prettierrc.json      # 代码格式化规则
├── package.json          # 依赖清单
├── tsconfig.json         # 主 TS 配置
├── tsconfig.node.json    # Node环境的 TS 配置【新增并确认】
└── vite.config.ts        # Vite 配置文件
```

### 核心文件职责详解

-   **`vite.config.ts`**: Vite的配置文件，核心是配置了 **`server.proxy`**，用于将前端的 `/api` 请求转发到后端服务。
-   **`.prettierrc.json`**: Prettier代码格式化工具的规则文件，用于统一团队代码风格。
-   **`tsconfig.json` & `tsconfig.node.json`**: TypeScript的编译配置文件，分离了浏览器和Node.js环境的配置，并通过`paths`和`baseUrl`支持了`@`路径别名。
-   **`src/main.ts`**: **应用入口**。负责创建Vue实例，并挂载Pinia、Router和Element Plus。
-   **`src/api/`**: **服务层 (Service Layer)**。封装所有与后端API的通信，与业务逻辑完全解耦。
-   **`src/stores/`**: **状态管理层 (Store Layer)**。基于Pinia，是应用的状态中心和业务逻辑处理核心。**组件应调用这里的Action，而不是直接调用API**。
-   **`src/views/MainView.vue`**: 应用的主视图，像一个“插线板”，负责**组合**各个独立的业务模块组件。
-   **`src/modules/`**: **【架构核心】业务模块**。每个文件夹都是一个高内聚的功能单元（如`document`, `chat`），包含只服务于自身的组件。

---

## 如何开始 

### 1. 环境准备
-   强烈建议使用 **nvm (Node Version Manager)** 来管理Node.js版本。
    ```bash
    # 安装并使用 Node.js v20 (LTS版本) # 一定要20或20以上才行
    nvm install 20
    nvm use 20
    ```
-   确保已安装 [Node.js](https://nodejs.org/) **v20.x**。
-   推荐使用 [Visual Studio Code](https://code.visualstudio.com/) 并安装 `Vue - Official` 和 `Prettier - Code formatter` 插件。

### 2. 安装依赖
在项目根目录 (`frontend/`) 下运行：
```bash
# 如果之前安装失败或切换了node版本，建议先清理
rm -rf node_modules package-lock.json
npm cache clean --force

# 安装所有依赖
npm install
npm install @element-plus/icons-vue # 确保图标库也被安装
```

### 3. 启动开发服务器
```bash
npm run dev
```
此命令会启动一个本地开发服务器，通常地址为 `http://localhost:5173`。

### 4. 开发须知
-   **后端API**: 请确保后端服务正在 `http://127.0.0.1:8000` 运行。如果后端地址不同，请修改 `vite.config.ts` 中的 `proxy.target` 配置。
-   **代码风格**: 项目已配置Prettier。推荐在VS Code设置中开启“保存时自动格式化”(Format On Save)，以保持代码风格一致。
-   **模块化开发**: 开发新功能时，要遵循现有的模块化结构，优先在对应的`modules`、`stores`和`api`目录下创建新文件。