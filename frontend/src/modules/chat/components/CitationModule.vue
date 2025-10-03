<template>
  <div class="citation-module">
    <h3>引用溯源</h3>
    <el-divider />
    <div class="content">
       <el-empty description="点击回答中的引用标签可在此处查看原文" />
       <!-- 
        未来这里会根据点击的引用动态显示内容:
        <div v-if="source.type === 'pdf'">
          <img :src="source.contentUrl" alt="PDF Page" />
        </div>
        <div v-if="source.type === 'video'">
          <video :src="source.contentUrl" controls></video>
        </div>
       -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElEmpty, ElDivider } from 'element-plus'
// const source = ref(null); // 未来用于存储引用源信息
</script>

<style lang="scss" scoped>
.citation-module {
  display: flex;
  flex-direction: column;
  height: 100%;
  h3 {
    margin: 0 0 16px;
  }
  .content {
    flex-grow: 1;
  }
}
</style>