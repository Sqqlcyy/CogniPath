<template>
    <div class="video-center-panel">
      <div class="video-player-container">
        <video-player
          v-if="appStore.currentDoc.sourceUrl"
          ref="videoPlayerRef"
          class="the-player"
          :src="appStore.currentDoc.sourceUrl"
          :options="playerOptions"
          @timeupdate="handleTimeUpdate"
        />
        <div v-else class="player-placeholder">
          <el-icon :size="50"><VideoPlay /></el-icon>
          <p>视频加载中...</p>
        </div>
      </div>
  
      <div class="companion-chat-container">
        <ChatHistory />
        <MessageInput />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch, onMounted } from 'vue';
  import { useAppStore } from '@/stores/app';
  import { useDocumentStore } from '@/stores/document'; // 导入Document Store
  // 导入强大的第三方Vue播放器
  // npm install vue3-video-play -S
  import VideoPlayer from 'vue3-video-play';
  import 'vue3-video-play/dist/style.css';
  import { VideoPlay } from '@element-plus/icons-vue';
  
  // 导入我们已经设计好的聊天组件
  import ChatHistory from '@/components/shared/ChatHistory.vue';
  import MessageInput from '@/components/shared/MessageInput.vue';
  
  const appStore = useAppStore();
  const documentStore = useDocumentStore();
  
  const videoPlayerRef = ref(); // 创建对播放器组件的引用
  
  // 播放器配置
  const playerOptions = {
    width: '100%',
    height: '100%',
    color: "#e6c069", // 主题金色
    title: '',
    src: appStore.currentDoc.sourceUrl,
    muted: false,
    webFullScreen: false,
    speedRate: ["1.0", "1.25", "1.5", "2.0"],
    autoPlay: false,
    loop: false,
    mirror: false,
    ligthOff: false,
    volume: 0.3,
    control: true,
  };
  
  // --- 【核心联动逻辑】 ---
  
  // 1. 知识树 -> 视频
  //    监听documentStore中被选中的节点ID
  watch(() => documentStore.selectedNodeId, (newId) => {
    if (newId && appStore.currentDoc.type === 'video' && videoPlayerRef.value) {
      // 从documentStore中获取该节点的详细信息 (我们需要一个getter)
      const node = documentStore.getNodeById(newId);
      if (node && node.timestamp !== undefined) {
        // 调用播放器的seek方法，跳转到指定时间
        videoPlayerRef.value.seek(node.timestamp);
        videoPlayerRef.value.play(); // 跳转后自动播放
      }
    }
  });
  
  // 2. 视频 -> 知识树
  //    监听播放器的timeupdate事件
  let lastUpdateTime = 0;
  const handleTimeUpdate = (payload: any) => {
    const currentTime = payload.currentTime;
    // 节流，避免过于频繁地更新
    if (currentTime - lastUpdateTime < 2) return;
    lastUpdateTime = currentTime;
    
    // 从documentStore中查找当前时间对应的节点ID (我们需要一个getter)
    const nodeIdToHighlight = documentStore.getNodeIdByTimestamp(currentTime);
    if (nodeIdToHighlight && documentStore.selectedNodeId !== nodeIdToHighlight) {
      // 调用action，只高亮节点，不触发反向的seek
      documentStore.selectNodeAndFetchContent(nodeIdToHighlight, false);
    }
  };
  </script>
  
  <style lang="scss" scoped>
  .video-center-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--bg-color);
  }
  
  .video-player-container {
    flex: 0 0 55%; /* 视频区域占55%的高度 */
    background-color: #000;
    position: relative;
    
    .the-player {
      width: 100%;
      height: 100%;
    }
  }
  
  .companion-chat-container {
    flex: 1; /* 聊天区域占据剩余空间 */
    display: flex;
    flex-direction: column;
    border-top: 1px solid var(--border-color);
    overflow: hidden; /* 防止子组件溢出 */
  }
  
  .player-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: var(--text-secondary);
  }
  </style>