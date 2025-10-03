<template>
    <div class="knowledge-tree-container">
      <el-tree
        v-if="documentStore.documentTree && documentStore.documentTree.length > 0"
        ref="treeRef"
        class="cognipath-tree"
        :data="documentStore.documentTree"
        :props="treeProps"
        node-key="id"
        default-expand-all
        highlight-current
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="tree-node-label">
            <el-icon class="node-icon">
              <FolderOpened v-if="data.type === 'section'" />
              <Document v-else />
            </el-icon>
            <span>{{ node.label }}</span>
          </span>
        </template>
      </el-tree>
  
      <el-empty v-else description="知识大纲将在此处构建" class="tree-empty-state" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch } from 'vue';
  // 导入我们已经设计好的Pinia Store
  import { useDocumentStore } from '@/stores/document';
  // 导入我们需要的数据类型
  import type { TreeNode } from '@/types';
  // 导入Element Plus的类型和图标
  import type { ElTree } from 'element-plus';
  import { FolderOpened, Document } from '@element-plus/icons-vue';
  
  // 1. 获取Store实例
  const documentStore = useDocumentStore();
  
  // 2. 配置el-tree，告诉它我们的数据中哪个字段是“标签”，哪个是“子节点”
  const treeProps = {
    label: 'label',
    children: 'children',
  };
  
  // 3. 创建一个模板引用(ref)，这样我们就可以在代码中直接操作el-tree组件实例
  const treeRef = ref<InstanceType<typeof ElTree>>();
  
  // 4. 【核心交互1: 用户点击 -> 通知Store】
  //    当用户点击树上的任何一个节点时，此函数被调用。
  const handleNodeClick = (nodeData: TreeNode) => {
    // 我们不在这里处理复杂逻辑，而是将任务委托给Store。
    // 这使得组件本身非常“干净”，只负责UI。
    documentStore.selectNodeAndFetchContent(nodeData.id);
  };
  
  // 5. 【核心交互2: Store变化 -> 更新UI】
  //    我们使用watch来“监听”Store中selectedNodeId的变化。
  //    当AI回答溯源，或者用户通过其他方式选中节点时，这个监听就会被触发。
  watch(() => documentStore.selectedNodeId, (newId) => {
    if (newId && treeRef.value) {
      // 调用el-tree组件的内置方法setCurrentKey，
      // 以编程方式高亮显示指定的节点。
      // 这就实现了“响应返回值”的功能！
      treeRef.value.setCurrentKey(newId);
    }
  });
  
  </script>
  
  <style lang="scss" scoped>
  .knowledge-tree-container {
    width: 100%;
    height: 100%;
    overflow-y: auto; // 当树很长时，容器内部出现滚动条
    padding: 10px;
    box-sizing: border-box;
  }
  
  /* 深度定制Element Plus Tree的样式，使其融入我们的黑金主题 */
  .cognipath-tree {
    // 我们在全局 main.scss 中已经定义了大部分基础样式 (如背景、颜色)
    // 这里我们添加一些更精细的调整
    :deep(.el-tree-node__content) {
      height: 40px;
      border-radius: var(--border-radius-medium);
      margin: 4px 0;
    }
    
    // 覆盖is-current的默认样式，使用更酷炫的金色辉光
    :deep(.el-tree-node.is-current > .el-tree-node__content) {
      background-color: var(--accent-gold) !important;
      color: var(--bg-color) !important;
      font-weight: bold;
      box-shadow: 0 0 15px var(--accent-gold-glow);
  
      .node-icon {
        color: var(--bg-color) !important;
      }
    }
  }
  
  .tree-node-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
  
  .node-icon {
    // 默认图标颜色
    color: var(--text-secondary);
  }
  
  .tree-empty-state {
    // 让空状态提示不那么突兀
    :deep(.el-empty__description p) {
      color: var(--text-secondary);
    }
  }
  </style>