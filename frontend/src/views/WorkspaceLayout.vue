<template>
    <div class="workspace-layout" :class="[store.currentDoc.type, store.currentTheme]">
      <!-- 全局动画层 -->
      <div class="animation-overlay">
        <div class="stars-container"></div>
        <MeteorShower ref="meteorShower" />
      </div>
  
      <!-- 左侧面板 (共享) -->
      <aside class="panel left-panel">
        <KnowledgeTree />
      </aside>
  
      <!-- 中间主面板 (动态内容) -->
      <main class="panel main-panel">
        <!-- 这里是关键：根据文档类型，动态渲染不同的中央面板 -->
        <component :is="activeCenterPanel" />
      </main>
  
      <!-- 右侧面板 (共享，但内容动态) -->
      <aside class="panel right-panel" :class="{ 'is-collapsed': isRightPanelCollapsed }">
        <div class="panel-content">
          <RightPanelContent />
        </div>
        <button class.="collapse-toggle" @click="isRightPanelCollapsed = !isRightPanelCollapsed">
          <i :class="isRightPanelCollapsed ? 'arrow-left' : 'arrow-right'"></i>
        </button>
      </aside>
    </div>
  </template>
  
  <script setup lang="ts">
  import { computed, ref, provide } from 'vue';
  import { useAppStore } from '../stores/app.ts';
  import MeteorShower from '@/components/common/MeteorShower.vue';

  const meteorShowerRef = ref<InstanceType<typeof MeteorShower> | null>(null);

  // 使用Provide/Inject将流星发射器实例提供给所有子孙组件
  provide('meteorShower', meteorShowerRef);
  // 导入所有可能用到的组件
  import KnowledgeTree from '@/components/shared/KnowledgeTree.vue';
  import RightPanelContent from '@/components/shared/RightPanelContent.vue';
  import VideoCenterPanel from '@/components/video_workspace/VideoCentrePanel.vue';
  import DocumentCenterPanel from '@/components/document_workspace/DocChatPanel.vue';
  
  const store = useAppStore();
  const isRightPanelCollapsed = ref(true); // 右侧面板默认折叠
  
  // 【核心逻辑】根据当前文档类型，决定中间面板应该渲染哪个组件
  const activeCenterPanel = computed(() => {
    if (store.currentDoc.type === 'video') {
      return VideoCenterPanel;
    }
    if (store.currentDoc.type === 'document') {
      return DocumentCenterPanel;
    }
    return null; // 或者一个空状态组件
  });
  
  // 流星动画控制
  const meteorShower = ref();
  provide('meteorShower', meteorShower); // 向所有子组件提供流星雨控制器
  </script>
  
  <style lang="scss" scoped>
  .workspace-layout {
    display: flex;
    height: 100vh;
    width: 100vw;
    position: relative;
    /* ... 其他布局样式，如flex, gap等 ... */
  }
  .right-panel {
    transition: width 0.3s ease;
    width: 400px;
    &.is-collapsed {
      width: 20px;
    }
  }
  .animation-overlay {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
  }
  </style>