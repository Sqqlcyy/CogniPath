<template>
    <div class="chat-history-container" ref="historyContainerRef">
      <MessageBubble 
        v-for="msg in chatStore.messages" 
        :key="msg.id" 
        :message="msg" 
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch, nextTick } from 'vue';
  import { useChatStore } from '@/stores/chat';
  import MessageBubble from './MessageBubble.vue';
  
  const chatStore = useChatStore();
  const historyContainerRef = ref<HTMLElement | null>(null);
  
  // 监听消息数组的变化，自动滚动到底部
  watch(() => chatStore.messages.length, async () => {
    await nextTick();
    if (historyContainerRef.value) {
      historyContainerRef.value.scrollTop = historyContainerRef.value.scrollHeight;
    }
  });
  </script>
  
  <style scoped>
  .chat-history-container {
    flex-grow: 1;
    padding: 24px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  </style>