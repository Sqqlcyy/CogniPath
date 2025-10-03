<template>
  <el-dialog
    :model-value="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    title="上传学习资料"
    width="550px"
    center
    class="upload-dialog"
  >
    <el-tabs v-model="activeTab" class="upload-tabs">
      <!-- 文件上传 Tab -->
      <el-tab-pane label="本地文件" name="file">
        <p class="tab-description">支持 .doc, .txt, .mp3, .pdf, .pptx 等格式。</p>
        <el-upload
          drag
          action="#" 
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
        </el-upload>
        <div v-if="selectedFile" class="file-info">
          <el-icon><Document /></el-icon>
          <span>已选择文件: {{ selectedFile.name }} ({{ (selectedFile.size / 1024).toFixed(2) }} KB)</span>
        </div>
        <div v-if="validationError" class="error-info">
          {{ validationError }}
        </div>
      </el-tab-pane>
      
      <!-- URL上传 Tab -->
      <el-tab-pane label="网络链接 (Bilibili)" name="url">
        <p class="tab-description">粘贴B站视频链接，AI将自动解析字幕并构建知识树。</p>
        <el-input
          v-model="urlInput"
          placeholder="https://www.bilibili.com/video/BV..."
          size="large"
          clearable
        />
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="$emit('update:modelValue', false)">取消</el-button>
        <el-button 
          type="primary" 
          @click="startProcessing" 
          :disabled="!isReadyToProcess"
          :loading="appStore.appState === 'processing'"
        >
          开始处理
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAppStore } from '@/stores/app'; // 导入我们重构后的主Store
import { ElMessage, type UploadFile } from 'element-plus';
import { UploadFilled, Document } from '@element-plus/icons-vue';

// Props and Emits for v-model
defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue']);

const appStore = useAppStore();

const activeTab = ref('file');
const urlInput = ref('');
const selectedFile = ref<File | null>(null);
const validationError = ref('');

// 定义支持的文件类型
const SUPPORTED_FILE_TYPES = ['application/msword', 'text/plain', 'audio/mpeg', 'application/pdf', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
const SUPPORTED_EXTENSIONS = ['.doc', '.txt', '.mp3', '.pdf', '.pptx'];

const isReadyToProcess = computed(() => {
  if (appStore.appState === 'processing') return false;
  if (activeTab.value === 'url') {
    return urlInput.value.startsWith('https://www.bilibili.com/video/');
  }
  if (activeTab.value === 'file') {
    return !!selectedFile.value && !validationError.value;
  }
  return false;
});

const handleFileChange = (uploadFile: UploadFile) => {
  validationError.value = '';
  const file = uploadFile.raw;
  if (!file) return;

  // 【前端文件类型校验】
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!SUPPORTED_EXTENSIONS.includes(fileExtension)) {
    validationError.value = `不支持的文件类型: ${fileExtension}。请上传 ${SUPPORTED_EXTENSIONS.join(', ')} 格式的文件。`;
    selectedFile.value = null;
    return;
  }

  // (可选) 文件大小校验
  if (file.size > 100 * 1024 * 1024) { // 100MB
    validationError.value = '文件大小不能超过100MB。';
    selectedFile.value = null;
    return;
  }
  
  selectedFile.value = file;
};

const startProcessing = () => {
  if (!isReadyToProcess.value) return;
  
  if (activeTab.value === 'url') {
    // 调用Store中的action处理URL
    appStore.processSource({ type: 'url', data: urlInput.value });
  } else if (selectedFile.value) {
    // 调用Store中的action处理文件
    appStore.processSource({ type: 'file', data: selectedFile.value });
  }
  
  // 关闭模态框
  emit('update:modelValue', false);
};
</script>

<style scoped>
.tab-description {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin-bottom: 16px;
  padding: 0 5px;
}
.file-info {
  margin-top: 15px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
}
.error-info {
  margin-top: 10px;
  color: #F56C6C;
}
.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>