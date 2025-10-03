<script setup lang="ts">
import { inject, ref, nextTick } from 'vue';
import { useChatStore } from '../../stores/chat';

const chatStore = useChatStore();
const meteorShower = inject('meteorShower');

async function handleSend(question: string) {
    // 触发Store的Action
    // chatStore.submitUserQuery会异步地更新chatHistory和highlightedNodeIds
    const sourceIds = await chatStore.submitUserQuery(question); // 让action返回sourceIds

    // 等待DOM更新，确保高亮的节点已经渲染出来
    await nextTick();

    // 获取起点和终点的DOM元素
    const startElement = document.querySelector('.chat-input-area'); 
    
    // 【关键】根据后端返回的source_ids来查找目标DOM元素
    if (startElement && sourceIds && sourceIds.length > 0) {
        const endPoints = sourceIds.map(id => {
            // El-Tree的节点通常有一个唯一的class或attribute，例如 data-node-key
            const nodeElement = document.querySelector(`.el-tree-node[data-node-key="${id}"]`);
            if (!nodeElement) return null;
            const rect = nodeElement.getBoundingClientRect();
            return { x: rect.left, y: rect.top + rect.height / 2 };
        }).filter(p => p !== null); // 过滤掉没找到的节点

        const startRect = startElement.getBoundingClientRect();
        const startPoint = { x: startRect.left + startRect.width / 2, y: startRect.top };

        // 发射精确制导的流星！
        if (meteorShower?.value) {
            meteorShower.value.fire(startPoint, endPoints);
        }
    }
}
</script>