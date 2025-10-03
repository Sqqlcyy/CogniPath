<template>
  <div class="chat-history-container" ref="historyContainer">
    <div v-if="chatStore.messages.length === 0 && !chatStore.isLoading" class="welcome-message">
      <el-avatar :size="60">AI</el-avatar>
      <h2>你好，我是知语AI</h2>
      <p>上传你的学习资料，开始智能学习之旅吧！</p>
    </div>

    <div v-for="message in chatStore.messages" :key="message.id">
      <div :class="['message-wrapper', message.role]">
        <div class="message-bubble">
          <!-- 这里未来可以渲染Markdown -->
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
    </div>
    
    <div v-if="chatStore.isLoading" class="message-wrapper assistant">
      <div class="message-bubble">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>AI正在思考中...</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElAvatar, ElIcon, ElEmpty } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const chatStore = useChatStore()
const historyContainer = ref<HTMLElement | null>(null)

// 监听消息列表的变化，自动滚动到底部
watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick() // 等待DOM更新
    if (historyContainer.value) {
      historyContainer.value.scrollTop = historyContainer.value.scrollHeight
    }
  }
)
</script>

<style lang="scss" scoped>
.chat-history-container {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
}
.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  text-align: center;
}
.message-wrapper {
  display: flex;
  margin-bottom: 16px;
  &.user {
    justify-content: flex-end;
  }
  &.assistant {
    justify-content: flex-start;
  }
}
.message-bubble {
  padding: 10px 15px;
  border-radius: 18px;
  max-width: 80%;
  background-color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  .message-content {
    white-space: pre-wrap; /* 保持换行 */
    word-break: break-word; /* 避免长单词溢出 */
  }
  &.user {
    background-color: #409eff;
    color: white;
    border-bottom-right-radius: 5px;
  }
  &.assistant {
    border: 1px solid #e4e7ed;
    border-bottom-left-radius: 5px;
  }
}
</style>