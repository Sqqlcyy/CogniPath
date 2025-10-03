<template>
  <div class="chat-module">
    <ChatHistory />
    <MessageInput />
  </div>
</template>

<script setup lang="ts">
import ChatHistory from './ChatHistory.vue'
import MessageInput from './MessageInput.vue'
</script>

<style lang="scss" scoped>
.chat-module {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>