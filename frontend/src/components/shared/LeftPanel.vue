<template>
  <div class="left-panel-container">
    <div class="panel-header">
      <el-button @click="appStore.goHome()" type="primary" class="action-btn">
        + 新建/切换资料
      </el-button>
    </div>

    <div class="health-score-container">
      <span>知识库健康度</span>
      <el-progress :percentage="85" color="#e6a23c" :stroke-width="6" />
    </div>

    <el-divider />

    <div class="tree-wrapper">
      <h3>知识大纲: {{ appStore.currentDoc.name || '未命名' }}</h3>
      <el-tree
        v-if="appStore.documentTree && appStore.documentTree.length > 0"
        ref="treeRef"
        class="cognipath-tree"
        :data="appStore.documentTree"
        :props="{ children: 'children', label: 'label' }"
        node-key="id"
        highlight-current
        default-expand-all
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAppStore } from '@/stores/app'; // 【核心修正】: 导入主Store
import type { TreeNode } from '@/types';
import type { ElTree } from 'element-plus';
import { FolderOpened, Document } from '@element-plus/icons-vue';

// 1. 获取主Store实例
const appStore = useAppStore();

const treeRef = ref<InstanceType<typeof ElTree>>();

// 2. 【核心修正】: 调用appStore中的action
const handleNodeClick = (nodeData: TreeNode) => {
  appStore.selectNodeAndFetchContent(nodeData.id);
};

// 3. 【核心修正】: 监听appStore中的状态
watch(() => appStore.selectedNodeId, (newId) => {
  if (newId && treeRef.value) {
    treeRef.value.setCurrentKey(newId);
  }
});
</script>


  <style scoped>
  .left-panel-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 20px;
    background-color: var(--panel-bg-color);
  }
  .panel-header {
    margin-bottom: 20px;
  }
  .upload-btn {
    width: 100%;
    background: var(--accent-gradient) !important;
    border: none;
    color: #1a1a1a !important;
    font-weight: bold;
  }
  .health-score-container {
    margin-top: 20px;
  }
  .health-score-container span {
    font-size: 14px;
    color: var(--text-color-secondary);
    margin-bottom: 8px;
    display: block;
  }
  .el-divider {
    border-color: var(--border-color);
  }
  .tree-wrapper {
    flex: 1;
    overflow-y: auto;
  }
  h3 {
    margin-bottom: 15px;
    color: var(--text-primary);
  }
  </style>