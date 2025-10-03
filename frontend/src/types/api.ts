// /src/types/index.ts

// --- 业务实体类型 ---

export interface TreeNode {
  id: string;
  label: string;
  type: 'section' | 'leaf';
  children: TreeNode[];
  full_text: string;
  timestamp?: number;
}

export type MessageRole = 'user' | 'assistant' | 'system';
export type MessageType = 'text' | 'loading' | 'error' | 'exam' | 'welcome';
export interface Message {
  id: string | number;
  role: MessageRole;
  type: MessageType;
  content?: string;
  data?: {
    examContent?: string;
    sourceIds?: string[];
  };
}

// --- 全局应用状态类型 ---

export type AppState = 'initial' | 'processing' | 'ready';
export interface ProcessingStatus { text: string; progress: number; }
export interface DocumentContext {
  id: string | null;
  name: string | null;
  type: 'video' | 'document' | null;
  sourceUrl?: string; // 修正了大小写，并设为可选
}

// --- API 数据传输对象 (DTO) 类型 ---

export interface ProcessSourceResponse { task_id: string; doc_id: string; }
export interface TaskStatusApiResponse {
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'NOT_FOUND';
  progress?: number;
  step?: string;
  result?: {
    doc_id: string;
    doc_name: string;
    doc_type: 'video' | 'document';
    source_url?: string;
    document_tree: TreeNode[];
  };
  error?: string;
}export interface GeneralQueryRequest {
  question: string;
}

/**
 * 对应后端 POST /query/general 接口的成功响应体。
 */
export interface GeneralQueryResponse {
  answer: string;
}
export interface PreciseQueryResponse { answer: string; source_ids: string[]; }
export interface GenerateMaterialsResponse { content: string; material_type: string; }
export interface NodeContentResponse { id: string; full_text: string; timestamp?: number; }
export type DocumentTreeApiResponse = TreeNode[];