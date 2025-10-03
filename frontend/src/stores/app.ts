// /src/stores/modules/app.ts

import { defineStore } from 'pinia';
import { ref } from 'vue';
import router from '@/router';

// Import all necessary API functions and types
import { processNewSource, fetchTaskStatus, fetchDocumentTree, fetchNodeContent } from '@/api';
import type { 
  AppState, 
  ProcessingStatus, 
  DocumentContext, 
  TaskStatusApiResponse,
  TreeNode,
  Message
} from '@/types';

// We might still need chatStore for its specific logic
import { useChatStore } from './chat';

export const useAppStore = defineStore('app', () => {
  // ================== State ==================
  const appState = ref<AppState>('initial');
  const processingStatus = ref<ProcessingStatus>({ text: '', progress: 0 });
  const currentDoc = ref<DocumentContext>({ id: null, name: null, type: null, sourceUrl: undefined });
  
  // --- 【MERGED】State from documentStore is now here ---
  const documentTree = ref<TreeNode[]>([]);
  const selectedNodeId = ref<string | null>(null);
  const selectedNodeContent = ref<string>('');
  const isFetchingNodeContent = ref(false);
  const chatHistory = ref<Message[]>([]);
  const isAwaitingResponse = ref(false);
  // ================== Actions ==================
  const chatStore = useChatStore();

  async function handleSourceProcessing(source: { type: 'url'; data: string } | { type: 'file'; data: File }) {
    resetAllState();
    appState.value = 'processing';
    processingStatus.value = { text: '初始化任务...', progress: 5 };
    
    console.log("【探针 4】: handleSourceProcessing Action被调用。");

    try {
      const formData = new FormData();
      formData.append('source_type', source.type);
      if (source.type === 'url') formData.append('url', source.data);
      else formData.append('file', source.data);
      
      const response = await processNewSource(formData);
      
      console.log("【探针 5】: processNewSource成功返回，收到的response:", response);
      
      // 直接从这里解构，如果response是undefined或null，这里会报错
      const { task_id, doc_id } = response.data;
      
      console.log(`【探针 6】: 成功解构出 task_id = ${task_id}, doc_id = ${doc_id}`);
      
      // 启动轮询
      pollTaskStatus(task_id, doc_id); // 不再需要await

    } catch (error: any) {
      console.error("【探针 ERROR】: handleSourceProcessing 失败!", error);
    }
  }
  async function pollTaskStatus(taskId: string, docId: string) {
    const poller = setInterval(async () => {
      try {
        const status: TaskStatusApiResponse = await fetchTaskStatus(taskId);

        if (status.status === 'COMPLETED') {
          clearInterval(poller);
          const result = status.result!;
          
          currentDoc.value = {
            id: docId,
            name: result.doc_name,
            type: result.doc_type,
            sourceUrl: result.source_url,
          };
          
          const treeData = await fetchDocumentTree(docId);
          documentTree.value = treeData; // Directly set the tree

          chatStore.initializeChat(`"${result.doc_name}" 已准备就绪。`);
          
          appState.value = 'ready';
          router.push({ name: 'workspace', params: { docId }});
        }
        // ... (other status handling)
      } catch (error) {
        // ...
      }
    }, 2500);
  }

  // --- 【MERGED】Actions from documentStore are now here ---
  async function selectNodeAndFetchContent(nodeId: string) {
    selectedNodeId.value = nodeId;
    const docId = currentDoc.value.id;

    if (!docId) {
      selectedNodeContent.value = '错误：文档ID丢失。';
      return;
    }

    isFetchingNodeContent.value = true;
    selectedNodeContent.value = '正在加载节点内容...';
    try {
      const response = await fetchNodeContent(docId, nodeId);
      selectedNodeContent.value = response.full_text;
    } catch (error: any) {
      selectedNodeContent.value = `无法加载节点内容: ${error.message}`;
    } finally {
      isFetchingNodeContent.value = false;
    }
  }
  function resetAllState() {
    currentDoc.value = { id: null, name: null, type: null, sourceUrl: undefined };
    documentTree.value = [];
    selectedNodeId.value = null;
    selectedNodeContent.value = '';
    isFetchingNodeContent.value = false;
    chatHistory.value = [];
    isAwaitingResponse.value = false;
  }
  function resetDocumentState() {
    documentTree.value = [];
    selectedNodeId.value = null;
    selectedNodeContent.value = '';
    isFetchingNodeContent.value = false;
  }

  function goHome() {
    appState.value = 'initial';
    resetDocumentState();
    chatStore.reset();
    currentDoc.value = { id: null, name: null, type: null, sourceUrl: undefined };
    router.push('/');
  }

  return {
    // Global State
    appState,
    processingStatus,
    currentDoc,
    
    // Document State (Merged)
    documentTree,
    selectedNodeId,
    selectedNodeContent,
    isFetchingNodeContent,

    // Actions
    handleSourceProcessing,
    selectNodeAndFetchContent,
    goHome,
    // (We keep reset private, goHome is the public reset)
  };
});