<template>
  <el-aside width="300px" class="side-panel">
    <DocumentModule />
  </el-aside>
  <el-main class="main-content">
    <ChatModule />
  </el-main>
  <el-aside width="350px" class="side-panel right">
    <CitationModule />
  </el-aside>
</template>

<script setup lang="ts">
import { ElAside, ElMain } from 'element-plus'
import DocumentModule from '@/modules/document/components/DocumentModule.vue'
import ChatModule from '@/modules/chat/components/ChatModule.vue'
import CitationModule from '@/modules/chat/components/CitationModule.vue'
</script>

<style lang="scss" scoped>
.side-panel {
  background-color: #fcfcfc;
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  border-right: 1px solid #e4e7ed;
  &.right {
    border-right: none;
    border-left: 1px solid #e4e7ed;
  }
}
.main-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  background-color: #f4f6f8;
}
</style>