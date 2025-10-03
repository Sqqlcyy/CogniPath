<template>
    <div class="left-panel-container">
      <!-- 顶部操作区 -->
      <div class="panel-header">
        <el-button @click="isModalVisible = true" type="primary" :icon="UploadFilled" class="upload-btn">
          新建学习资料
        </el-button>
      </div>
  
      <!-- 知识健康度 (示例) -->
      <div class="health-score-container">
        <span>知识库健康度</span>
        <el-progress :percentage="85" color="#e6a23c" :stroke-width="6" />
      </div>
  
      <el-divider />
  
      <!-- 知识大纲 -->
      <div class="tree-wrapper">
        <h3>知识大纲: {{ appStore.currentDoc.name || '未命名' }}</h3>
        <el-tree
          v-if="appStore.documentTree.length > 0"
          :data="appStore.documentTree"
          :props="{ children: 'children', label: 'label' }"
          node-key="id"
          highlight-current
          default-expand-all
          @node-click="handleNodeClick"
        />
        <el-empty v-else description="请先上传资料以构建知识树" />
      </div>
  
      <!-- 上传模态框 -->
      <UploadModal v-model="isModalVisible" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import { useAppStore } from '@/stores/modules/app'; // 导入主Store
  import UploadModal from './UploadModal.vue'; // 假设UploadModal也成为共享组件
  import type { TreeNode } from '@/types';
  import { UploadFilled } from '@element-plus/icons-vue';
  
  const appStore = useAppStore();
  const isModalVisible = ref(false);
  
  const handleNodeClick = (node: TreeNode) => {
    // 调用Store中的action来处理节点点击事件
    appStore.selectNodeAndFetchContent(node.id);
  };
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