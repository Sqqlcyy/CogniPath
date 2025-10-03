import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { TreeNode } from '@/types';
import { fetchNodeContent } from '@/api'; // 导入API

export const useDocumentStore = defineStore('document', () => {
  // State
  const documentTree = ref<TreeNode[]>([]);
  const selectedNodeId = ref<string | null>(null);
  const selectedNodeContent = ref<string>(''); // 用于右侧溯源面板展示
  const isFetchingNodeContent = ref(false);
  // Actions
  /**
   * 由 appStore 在任务完成后调用，用于设置知识树数据。
   */
  function setDocumentTree(tree: TreeNode[]) {
    documentTree.value = tree;
  }
  const getNodeById = computed(() => {
    return (nodeId: string): TreeNode | null => {
      // 定义一个递归的内部辅助函数来遍历树
      function findNode(nodes: TreeNode[]): TreeNode | null {
        for (const node of nodes) {
          if (node.id === nodeId) return node;
          // 如果当前节点不是，就去它的子节点里找
          if (node.children && node.children.length > 0) {
            const found = findNode(node.children);
            if (found) return found;
          }
        }
        return null; // 遍历完所有节点都没找到
      }
      // 从根节点开始查找
      return findNode(documentTree.value);
    };
  });

  /**
   * 【新增Getter 2】根据视频的当前播放时间，同步查找对应的叶子节点ID。
   * 用于实现“视频 -> 知识树高亮”的联动。
   */
  const getNodeIdByTimestamp = computed(() => {
    // 这是一个昂贵的计算，但computed会缓存结果。
    // 只有当documentTree变化时，它才会重新计算。
    const timestampedNodes: TreeNode[] = [];
    function collectLeafNodes(nodes: TreeNode[]) {
      for (const node of nodes) {
        // 我们只关心带时间戳的叶子节点
        if (node.type === 'leaf' && node.timestamp !== undefined) {
          timestampedNodes.push(node);
        }
        if (node.children && node.children.length > 0) {
          collectLeafNodes(node.children);
        }
      }
    }
    collectLeafNodes(documentTree.value);
    // 按时间戳升序排序
    timestampedNodes.sort((a, b) => a.timestamp! - b.timestamp!);

    return (currentTime: number): string | null => {
      if (timestampedNodes.length === 0) return null;

      // 遍历查找当前时间所在的区间
      for (let i = 0; i < timestampedNodes.length; i++) {
        const currentNode = timestampedNodes[i];
        const nextNode = timestampedNodes[i + 1];

        if (currentTime >= currentNode.timestamp!) {
            // 如果是最后一个节点，或者当前时间小于下一个节点的时间，那么就匹配成功
            if (!nextNode || currentTime < nextNode.timestamp!) {
                return currentNode.id;
            }
        }
      }
      return null;
    };
  });

  /**
   * 当用户点击知识树节点时调用。
   */
  async function selectNodeAndFetchContent(nodeId: string) {
    selectedNodeId.value = nodeId; // 立即高亮
    
    // 获取全局Store中的当前文档ID
    const { useAppStore } = await import('./app'); // 动态导入避免循环依赖
    const appStore = useAppStore();
    const docId = appStore.currentDoc.id;

    if (!docId) return;

    try {
      const response = await fetchNodeContent(docId, nodeId);
      selectedNodeContent.value = response.full_text;
    } catch (error) {
      console.error(`获取节点 ${nodeId} 内容失败:`, error);
      selectedNodeContent.value = '无法加载节点内容。';
    }
  }

  function reset() {
    documentTree.value = [];
    selectedNodeId.value = null;
    selectedNodeContent.value = '';
    isFetchingNodeContent.value = false;
  }
  return {
    // State
    documentTree,
    selectedNodeId,
    selectedNodeContent,
    // Actions
    setDocumentTree,
    selectNodeAndFetchContent,
    getNodeById,
    getNodeIdByTimestamp,
    isFetchingNodeContent,
    reset
  };
});