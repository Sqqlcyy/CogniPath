<template>
  <el-dialog
    :model-value="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
    title="新建学习资料"
    width="550px"
    center
    :close-on-click-modal="false"
    class="upload-dialog"
  >
    <el-tabs v-model="activeTab" class="upload-tabs">
      
      <el-tab-pane label="本地文件" name="file">
        <p class="tab-description">支持 .ppt, .pdf, .doc, .txt, .mp3 等多种格式。</p>
        <el-upload
          drag
          action="#" 
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <el-icon><Document /></el-icon>
          <span>{{ selectedFile.name }} ({{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB)</span>
        </div>
        <div v-if="validationError" class="error-info">
          {{ validationError }}
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="网络链接 (Bilibili)" name="url">
        <p class="tab-description">粘贴B站视频链接，AI将自动解析并构建伴学空间。</p>
        <el-input
          v-model="urlInput"
          placeholder="https://www.bilibili.com/video/BV..."
          size="large"
          clearable
        />
        <div v-if="urlInput && !isBilibiliUrl" class="error-info">
          请输入一个有效的Bilibili视频链接。
        </div>
      </el-tab-pane>

    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:modelValue', false)">取消</el-button>
        <el-button 
          type="primary" 
          @click="startProcessing" 
          :disabled="!isReadyToProcess"
          :loading="appStore.appState === 'processing'"
          class="process-btn"
        >
          开始构建
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAppStore } from '@/stores/app';
import type { UploadFile } from 'element-plus';
import { UploadFilled, Document } from '@element-plus/icons-vue';

// v-model的标准写法
defineProps<{ modelValue: boolean }>();
const emit = defineEmits(['update:modelValue']);

const appStore = useAppStore();

const activeTab = ref('file');
const urlInput = ref('');
const selectedFile = ref<File | null>(null);
const validationError = ref('');

// 支持的文件扩展名
const SUPPORTED_EXTENSIONS = ['.doc', '.txt', '.mp3', '.pdf', '.pptx'];

// 计算属性，用于判断B站链接是否合法
const isBilibiliUrl = computed(() => {
  return urlInput.value.startsWith('https://www.bilibili.com/video/');
});

// 计算属性，用于控制“开始构建”按钮是否可点击
const isReadyToProcess = computed(() => {
  if (appStore.appState === 'processing') return false;
  if (activeTab.value === 'url') return isBilibiliUrl.value;
  if (activeTab.value === 'file') return !!selectedFile.value && !validationError.value;
  return false;
});

const handleFileChange = (uploadFile: UploadFile) => {
  validationError.value = '';
  const file = uploadFile.raw;
  if (!file) return;

  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!SUPPORTED_EXTENSIONS.includes(fileExtension)) {
    validationError.value = `不支持的文件类型。请上传 ${SUPPORTED_EXTENSIONS.join(', ')} 格式的文件。`;
    selectedFile.value = null;
    return;
  }
  
  selectedFile.value = file;
};

// 【核心】点击按钮，调用appStore的action
const startProcessing = async() => {
  if (!isReadyToProcess.value) return;
  
  if (activeTab.value === 'url') {
    await appStore.handleSourceProcessing({ type: 'url', data: urlInput.value });
  } else if (selectedFile.value) {
    await appStore.handleSourceProcessing({ type: 'file', data: selectedFile.value });
  }
  
  // 关闭模态框
  emit('update:modelValue', false);
};
</script>