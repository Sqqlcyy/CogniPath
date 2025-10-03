// /src/api/modules/query.ts

import request from '@/utils/request';
// 从统一的类型出口导入所有需要的类型
import type { 
    PreciseQueryResponse, 
    GenerateMaterialsResponse,
    GeneralQueryResponse // 假设为postGeneralQuery定义一个类型
} from '@/types';

// --- 定义每个函数接收的参数对象的类型 ---
interface PreciseQueryPayload {
  doc_id: string;
  question: string;
}

interface GenerateMaterialsPayload {
  doc_id: string;
  topic: string;
  material_type: 'exam' | 'summary';
}

interface GeneralQueryPayload {
    question: string;
}

/**
 * 【精确问答API】
 * @param payload - 包含 doc_id 和 question 的对象。
 */
export function postPreciseQuery(payload: PreciseQueryPayload): Promise<PreciseQueryResponse> {
  // 我们将整个 payload 对象作为 axios 的 data 发送
  return request.post('/query/precise', payload);
}

/**
 * 【学习材料生成API】
 * @param payload - 包含 doc_id, topic 和 material_type 的对象。
 */
export async function generateLearningMaterials(payload: GenerateMaterialsPayload): Promise<GenerateMaterialsResponse> {
  try {
    const response = await request.post('/generate/materials', payload);
    return response.data;
  } catch (error: any) {
    console.error(`[API Error] generateLearningMaterials failed:`, error.response?.data || error.message);
    throw new Error('Failed to generate learning materials.');
  }
}

/**
 * 【(可选) 简单问答API】
 * @param payload - 包含 question 的对象。
 */
export async function postGeneralQuery(payload: GeneralQueryPayload): Promise<GeneralQueryResponse> {
    try {
        const response = await request.post('/query/general', payload);
        return response.data;
    } catch (error: any) {
        console.error(`[API Error] postGeneralQuery failed:`, error.response?.data || error.message);
        throw new Error('Failed to get a general answer.');
    }
}