<template>
    <div class="right-panel-content">
      <div v-if="appStore.currentDoc.type === 'document'">
        <h4>
          <el-icon><Reading /></el-icon>
          知识溯源
        </h4>
        <div v-if="documentStore.isFetchingNodeContent" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="documentStore.selectedNodeContent" class="source-text-container">
          <pre>{{ documentStore.selectedNodeContent }}</pre>
        </div>
        <el-empty v-else description="点击知识树节点或答案中的来源标签以查看原文" />
      </div>
  
      <div v-if="appStore.currentDoc.type === 'video'">
         <el-empty description="笔记功能开发中..." />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { useAppStore } from '@/stores/app';
  import { useDocumentStore } from '@/stores/document';
  import { Reading, Loading } from '@element-plus/icons-vue';
  const appStore = useAppStore();
  const documentStore = useDocumentStore();
  </script>
  
  <style lang="scss" scoped>
  .right-panel-content {
    padding: 20px;
  }
  h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
  }
  .source-text-container pre {
    background-color: var(--bg-color);
    padding: 15px;
    border-radius: var(--border-radius-medium);
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.7;
    color: var(--text-secondary);
  }
  .loading-state { /* ... 加载状态样式 ... */ }
  </style>