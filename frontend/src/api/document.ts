// /src/api/index.ts
import request from '@/utils/request';
import type { ProcessSourceResponse, TaskStatusApiResponse, DocumentTreeApiResponse, NodeContentResponse } from '@/types/api';


export async function processNewSource(formData: FormData): Promise<ProcessSourceResponse> {
  console.log("【探针 1】: 即将发送上传请求...");
  
  try {
    const response = await request.post('/documents/process', formData);
    
    console.log("【探针 2】: 收到后端响应，原始response.data:", response.data);
    
    // 增加一个额外的健壮性检查
    if (!response.data || !response.data.task_id) {
        console.error("【严重错误】: 后端返回了200，但响应体中没有task_id!", response);
        throw new Error("后端响应格式不正确，缺少task_id。");
    }
    
    console.log(`【探针 3】: 解析成功，task_id = ${response.data.task_id}`);
    return response.data;
  } catch (error) {
    console.error("【探针 ERROR】: processNewSource API调用失败!", error);
    throw error;
  }
}
export function fetchTaskStatus(taskId: string): Promise<TaskStatusApiResponse> {
  return request.get(`/tasks/${taskId}/status`);
}
export function fetchDocumentTree(docId: string): Promise<DocumentTreeApiResponse> {
  return request.get(`/documents/${docId}/tree`);
}
export function fetchNodeContent(docId: string, nodeId: string): Promise<NodeContentResponse> {
  return request.get(`/documents/${docId}/node/${nodeId}`);
}