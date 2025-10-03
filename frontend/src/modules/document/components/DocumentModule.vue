<template>
  <div class="document-module">
    <el-button @click="isModalVisible = true" type="primary" style="width: 100%;">
      + 上传学习资料
    </el-button>
    <div class="health-score-container">
      <span>知识库健康度:</span>
      <el-progress :percentage="60" />
    </div>
    <el-divider />
    <h3>知识大纲</h3>
    <el-tree
      v-if="documentStore.documentTree.length > 0"
      :data="documentStore.documentTree"
      :props="{ children: 'children', label: 'title' }"
    />
    <el-empty v-else description="请先上传资料来构建知识大纲" />

    <!-- UploadModal组件的逻辑先注释掉，确保主流程能跑通 -->
    <!-- <UploadModal v-model="isModalVisible" /> -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDocumentStore } from '@/stores/document'
// import UploadModal from './UploadModal.vue' // 暂时不导入
import { ElProgress, ElButton, ElDivider, ElTree, ElEmpty } from 'element-plus'

const documentStore = useDocumentStore()
const isModalVisible = ref(false)
</script>

<style lang="scss" scoped>
.document-module {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.health-score-container {
  margin-top: 16px;
}
</style>