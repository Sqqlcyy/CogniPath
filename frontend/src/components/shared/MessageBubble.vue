<template>
    <div class="message-wrapper" :class="[message.role, message.type]">
      <el-avatar v-if="message.role === 'assistant'" class="ai-avatar">AI</el-avatar>
      <div class="message-bubble">
        <!-- 根据消息类型渲染不同内容 -->
        <div v-if="message.type === 'text' || message.type === 'welcome' || message.type === 'error'" v-html="renderMarkdown(message.content || '')"></div>
        
        <div v-if="message.type === 'loading'" class="loading-content">
          <div class="nebula-loader">
            <div class="orbit orbit-1"></div>
            <div class="orbit orbit-2"></div>
            <div class="orbit orbit-3"></div>
          </div>
        </div>
        
        <div v-if="message.type === 'exam'" class="exam-content">
          <h4>模拟试卷</h4>
          <pre>{{ message.data?.examContent }}</pre>
        </div>
  
        <!-- 渲染溯源标签 -->
        <div v-if="message.data?.sourceIds && message.data.sourceIds.length > 0" class="references">
          <el-tag
            v-for="id in message.data.sourceIds"
            :key="id"
            class="reference-tag"
            @click="handleReferenceClick(id)"
          >
            <el-icon><Link /></el-icon>
            知识来源 #{{ id }}
          </el-tag>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { marked } from 'marked';
  import { useDocumentStore } from '@/stores/document';
  import type { Message } from '@/types';
  import { Link } from '@element-plus/icons-vue';
  
  const props = defineProps<{ message: Message }>();
  const documentStore = useDocumentStore();
  
  const renderMarkdown = (text: string) => {
    // 注意：在生产环境中，需要使用DOMPurify等库来防止XSS攻击
    return marked.parse(text);
  };
  
  const handleReferenceClick = (nodeId: string) => {
    documentStore.selectNodeAndFetchContent(nodeId);
  };
  </script>
  
  <style lang="scss" scoped>
  /* 请将 app.less 中所有与 .message, .message-bubble, .ai-avatar, .references, 
     .reference-tag, .loading-bubble, .nebula-loader 相关的样式代码
     “翻译”并粘贴到这里。 */
  .message-wrapper { /* ... */ }
  .message-bubble { /* ... */ }
  .references { /* ... */ }
  /* ... */
  </style>