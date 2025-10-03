import { createPinia } from 'pinia';

const pinia = createPinia();

export default pinia;

// 统一导出所有模块，方便在组件中按需导入
export * from './app';
export * from './chat';
export * from './document';