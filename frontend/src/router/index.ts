// /src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import UploadView from '@/views/UploadView.vue';
import WorkspaceLayout from '@/views/WorkspaceLayout.vue';

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: UploadView,
    meta: { title: 'CogniPath - 新建资料' }
  },
  {
    // 所有工作区都使用这一个路由，通过docId来区分
    path: '/workspace/:docId',
    name: 'Workspace',
    component: WorkspaceLayout,
    props: true, // 这会将URL中的:docId作为prop传递给WorkspaceLayout组件
    meta: { title: 'CogniPath - 学习空间' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;