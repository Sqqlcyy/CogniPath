<template>
  <el-container class="default-layout">
    <el-header class="top-bar">
      <span class="logo-text">知语 CogniPath AI</span>
      <span class="course-title">计算机网络原理</span>
      <el-avatar>AI</el-avatar>
    </el-header>
    <el-container class="main-container">
      <router-view />
    </el-container>
  </el-container>
</template>
<script setup lang="ts">
import { ElContainer, ElHeader, ElAvatar } from 'element-plus'
</script>
<style lang="scss" scoped>
.default-layout { height: 100vh; display: flex; flex-direction: column; }
.top-bar { display: flex; align-items: center; justify-content: space-between; background-color: #fff; border-bottom: 1px solid #e4e7ed; padding: 0 20px; }
.main-container { height: calc(100vh - 60px); }
.logo-text { font-weight: bold; font-size: 20px; }
</style>