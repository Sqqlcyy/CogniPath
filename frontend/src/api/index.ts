// /src/api/index.ts
import request from '@/utils/request';
import type { ProcessSourceResponse, TaskStatusApiResponse, PreciseQueryResponse } from '@/types';
// 这个文件应该导出所有API模块
export * from './document';
export * from './query';

export function processNewSource(formData: FormData): Promise<ProcessSourceResponse> {
  return request.post('/documents/process', formData);
}

export function fetchTaskStatus(taskId: string): Promise<TaskStatusApiResponse> {
  return request.get(`/tasks/${taskId}/status`);
}

export function postPreciseQuery(docId: string, question: string): Promise<PreciseQueryResponse> {
  return request.post('/query/precise', { doc_id: docId, question });
}