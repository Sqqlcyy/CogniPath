<template>
    <div class="upload-view-container">
      <!-- 
        【核心修正 1】: 使用 v-if 来控制欢迎界面的显示。
        只有当appStore的状态是'initial'时，我们才看到这个欢迎界面。
      -->
      <div v-if="appStore.appState === 'initial'" class="center-content">
        <img src="@/assets/logo.png" alt="CogniPath AI Logo" class="logo" />
        <h1 class="title">CogniPath AI</h1>
        <p class="subtitle">重塑你的思考路径</p>
        
        <!-- 点击这个按钮会通过v-model将isModalVisible设为true -->
        <el-button @click="isModalVisible = true" type="primary" size="large" class="start-btn">
          + 开始学习
        </el-button>
      </div>
  
      <!-- 
        上传模态框。
        它也只在'initial'状态下才应该存在，并通过自己的v-model控制显示/隐藏。
      -->
      <UploadModal 
        v-if="appStore.appState === 'initial'"
        v-model="isModalVisible"
      />
  
      <!-- 
        【核心修正 2】: 全局加载动画。
        当appStore的状态变为'processing'时，上面两个v-if会变为false，
        这个v-if会变为true，整个屏幕就会被加载动画接管。
      -->
      <LoadingScreen 
        v-if="appStore.appState === 'processing'"
        :status="appStore.processingStatus" 
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import { useAppStore } from '../stores/app'; // 确保路径正确
  import UploadModal from '@/components/common/UploadModal.vue';
  import LoadingScreen from '@/components/common/LoadingScreen.vue';
  
  const appStore = useAppStore();
  // 这个组件内部只负责控制模态框的显示与否
  const isModalVisible = ref(false); 
  </script>
  
  <style lang="scss" scoped>
  .upload-view-container {
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    z-index: 1;
  }
  
  .center-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    animation: fadeIn 1.5s ease-out;
  }
  
  /* ... 其他所有酷炫的样式代码保持不变 ... */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .upload-view {
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    /* 确保它在星空背景之上 */
    position: relative;
    z-index: 1;
  }
  
  .center-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    
    /* 为整个内容区域添加一个微妙的入场动画 */
    animation: fadeIn 1.5s ease-out;
  }
  
  .logo {
    width: 120px;
    height: 120px;
    margin-bottom: 20px;
    /* (可选) 如果你的logo需要，可以加上发光效果 */
    // filter: drop-shadow(0 0 15px var(--accent-gold-glow));
  }
  
  .title {
    font-size: 48px;
    font-weight: 700;
    letter-spacing: 2px;
    /* 应用金色渐变文字效果 */
    background: var(--accent-gold-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  
  .subtitle {
    font-size: 18px;
    color: var(--text-secondary);
    margin-top: 8px;
    margin-bottom: 40px;
    letter-spacing: 1px;
  }
  
  .start-btn {
    font-size: 18px;
    padding: 20px 40px;
    height: auto;
    border-radius: var(--border-radius-medium);
    /* 增加一个微妙的呼吸光晕动画 */
    animation: pulseGlow 3s infinite ease-in-out;
  }
  
  /* 定义动画 */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes pulseGlow {
    0% {
      box-shadow: 0 0 15px var(--accent-gold-glow);
    }
    50% {
      box-shadow: 0 0 30px var(--accent-gold-glow);
    }
    100% {
      box-shadow: 0 0 15px var(--accent-gold-glow);
    }
  }
  </style>