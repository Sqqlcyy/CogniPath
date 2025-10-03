<template>
    <div class="chat-input-area" ref="inputAreaRef">
      <el-input
        v-model="userInput"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 5 }"
        placeholder="向AI提问，或让他“考考我”..."
        @keydown.enter.prevent="handleSend"
      />
      <el-button 
        type="primary" 
        @click="handleSend" 
        :disabled="!userInput.trim() || chatStore.isAwaitingResponse"
        class="send-btn"
        :icon="Promotion"
      >
        发送
      </el-button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, inject, nextTick } from 'vue';
  import { useChatStore } from '@/stores/chat';
  import { meteorShowerKey } from '@/keys'; // 导入我们定义的InjectionKey
  import { Promotion } from '@element-plus/icons-vue'; 
  const chatStore = useChatStore();
  const meteorShower = inject(meteorShowerKey); // 注入流星发射器
  
  const userInput = ref('');
  const inputAreaRef = ref<HTMLDivElement | null>(null); // 用于获取起点坐标
  
  const handleSend = async () => {
    const text = userInput.value.trim();
    if (!text || chatStore.isAwaitingResponse) return;
    
    // 先保存当前输入，因为之后会清空
    const questionToSend = userInput.value;
    userInput.value = '';
  
    // 1. 【调用Store】: 只传递业务逻辑需要的数据 (question)
    //    我们用 await 等待它完成，并接收返回的溯源ID
    const sourceIds = await chatStore.submitUserQuery(questionToSend);
  
    // 2. 【触发动画】: 在组件内部处理UI逻辑
    //    如果成功返回了溯源ID，就开始计算坐标并发射流星
    if (sourceIds && sourceIds.length > 0) {
      // 等待Vue的下一次DOM更新，确保高亮的节点已经渲染在页面上
      await nextTick();
  
      const startElement = inputAreaRef.value;
      if (!startElement || !meteorShower?.value) return;
  
      // 计算起点
      const startRect = startElement.getBoundingClientRect();
      const startPoint = { 
        x: startRect.left + startRect.width / 2, 
        y: startRect.top 
      };
  
      // 计算所有终点
      const endPoints = sourceIds.map(id => {
          const nodeElement = document.querySelector(`.el-tree-node[data-node-key="${id}"]`);
          if (!nodeElement) return null;
          const rect = nodeElement.getBoundingClientRect();
          return { x: rect.left, y: rect.top + rect.height / 2 };
      }).filter(p => p !== null) as { x: number; y: number }[];
  
      // 发射！
      if (endPoints.length > 0) {
        meteorShower.value.fire(startPoint, endPoints);
      }
    }
  };
  </script>

<style lang="scss" scoped>
.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-color); // 使用最深的背景色，与聊天区分隔
  display: flex;
  align-items: flex-end; /* 让发送按钮和输入框底部对齐 */
  gap: 12px;
}

// 深度选择器，用于修改Element Plus组件的内部样式
:deep(.el-textarea) {
  flex: 1;
  
  .el-textarea__inner {
    background: var(--panel-bg-color);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-medium);
    color: var(--text-primary);
    box-shadow: none;
    transition: all 0.3s ease;
    padding: 10px 15px;
    font-size: 15px;
    line-height: 1.6;
    resize: none;

    /* 覆盖 Element Plus 的 focus 样式 */
    &:focus {
      border-color: var(--accent-gold);
      box-shadow: 0 0 10px var(--accent-gold-glow);
    }
  }
}

.send-btn {
  height: 44px; /* 与输入框第一行的高度大致对齐 */
  width: 44px;
  border-radius: var(--border-radius-medium);
  font-size: 20px;
  
  /* Element Plus按钮的样式已在全局main.scss中通过覆盖.el-button--primary实现 */
  /* 这里可以添加一些微调 */
  &:disabled {
    background: #333 !important;
    border-color: #333 !important;
    box-shadow: none;
    cursor: not-allowed;
  }
}
</style>