// /src/stores/modules/chat.ts

// ----------------- 导入所有依赖 (修正后) -----------------
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Message } from '@/types'; // 确保 @/types/index.ts 中有 Message 类型

// 从统一的API出口导入，而不是具体的API模块
import { postPreciseQuery, generateLearningMaterials, postGeneralQuery  } from '@/api';

// 导入其他Store以便进行联动
import { useAppStore } from './app';
import { useDocumentStore } from './document';

// ----------------- Store 定义 -----------------

export const useChatStore = defineStore('chat', () => {
  // ================== State ==================
  const messages = ref<Message[]>([]);
  const isAwaitingResponse = ref(false); // 防止用户在AI响应期间重复发送

  // ================== Actions ==================

  /**
   * 由 appStore 调用，用于在文档处理完成后初始化聊天。
   */
  function initializeChat(welcomeMessage: string) {
    messages.value = [{ 
      id: 'welcome', 
      role: 'system', 
      type: 'welcome', 
      content: welcomeMessage
    }];
  }

  /**
   * 【核心】当用户在输入框点击发送时调用。
   * 这个方法智能地根据用户意图调用不同的后端服务。
   */
  async function submitUserQuery(question: string) {
    // 动态地在Action内部获取其他Store的实例，这是Pinia推荐的做法
    const appStore = useAppStore();
    const docId = appStore.currentDoc.id;

    // 基本校验
    if (!docId || !question.trim() || isAwaitingResponse.value) {
      return;
    }

    // 1. 更新UI状态
    isAwaitingResponse.value = true;
    messages.value.push({ id: Date.now(), role: 'user', type: 'text', content: question });
    const loadingMessage: Message = { id: 'loading', role: 'assistant', type: 'loading' };
    messages.value.push(loadingMessage);
    let sourceIds: string[] | undefined = undefined;
    try {
      if (!docId) {
        // **情况一：没有文档上下文，执行通用问答**
        const response = await postGeneralQuery({ question });
        const answerMessage: Message = { id: Date.now(), role: 'assistant', type: 'text', content: response.answer };
        messages.value.splice(messages.value.indexOf(loadingMessage), 1, answerMessage);
      }else{
      // 2. 智能意图分发
      const lowerQuestion = question.toLowerCase();
      if (lowerQuestion.includes('出题') || lowerQuestion.includes('考考我') || lowerQuestion.includes('模拟卷')) {
        
        // 调用“生成材料”API
        const response = await generateLearningMaterials({ doc_id: docId, topic: question, material_type: 'exam' });
        
        // 用真实的考卷消息替换掉loading消息
        const examMessage: Message = { id: Date.now(), role: 'assistant', type: 'exam', data: { examContent: response.content } };
        messages.value.splice(messages.value.indexOf(loadingMessage), 1, examMessage);

      } else {
        
        // 否则，执行标准的“精确问答”
        const response = await postPreciseQuery({ 
          doc_id: docId, 
          question: question 
      });
        
        // 【这里就是你说的 "answerMessage"】
        // 用带溯源信息的答案替换loading消息
        const answerMessage: Message = { id: Date.now(), role: 'assistant', type: 'text', content: response.answer, data: { sourceIds: response.source_ids } };
        messages.value.splice(messages.value.indexOf(loadingMessage), 1, answerMessage);
        sourceIds = response.source_ids;
        // 【联动】调用 documentStore 来高亮溯源节点
        const documentStore = useDocumentStore();
        if (response.source_ids?.length > 0) {
          // 这个action在你的document.ts中必须存在
          documentStore.selectNodeAndFetchContent(response.source_ids[0]);
        }
        return response.source_ids; 
      }
    }
    } catch (error: any) {
      // 3. 统一的错误处理
      console.error('Query failed:', error);
      const errorMessage: Message = { id: 'error', role: 'assistant', type: 'error', content: `抱歉，AI服务暂时不可用: ${error.message}` };
      messages.value.splice(messages.value.indexOf(loadingMessage), 1, errorMessage);
    } finally {
      // 4. 无论成功失败，最终都结束等待状态
      isAwaitingResponse.value = false;
      return sourceIds; 
    }
  }

  /**
   * 【新增】一个重置状态的action，在处理新文档时由appStore调用。
   */
  function reset() {
    messages.value = [];
    isAwaitingResponse.value = false;
  }

  return {
    // State
    messages,
    isAwaitingResponse,
    // Actions
    initializeChat,
    submitUserQuery,
    reset, // 导出reset方法
  };
});