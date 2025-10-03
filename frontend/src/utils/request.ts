// /src/utils/request.ts
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建一个axios实例
const service = axios.create({
  baseURL: '/api/v1', // 确保Vite代理配置正确
  timeout: 60000,   // 将超时时间设置得长一些，以应对大文件上传
});

// --- 请求拦截器 (通常保持简单) ---
service.interceptors.request.use(
  config => {
    // 可以在这里统一添加认证Token等
    // config.headers['Authorization'] = `Bearer ${getToken()}`;
    return config;
  },
  error => {
    console.error('[Request Error]', error);
    return Promise.reject(error);
  }
);

// --- 响应拦截器 (【核心修正】) ---
service.interceptors.response.use(
  /**
   * 如果HTTP状态码是2xx，说明请求成功。
   * 我们不再做任何关于响应体内部结构 (如 code 字段) 的假设。
   * 直接将 response 对象透传给发起请求的API函数，让它们自己去解析。
   */
  response => {
    // 直接返回完整的response对象
    return response;
  },
  /**
   * 如果HTTP状态码不是2xx (例如 404, 500)，或者请求本身就失败了 (如网络中断)。
   * axios会自动进入这个error处理函数。
   */
  error => {
    console.error('[Response Error]', error);
    
    // 构造一个更清晰的错误消息
    let errorMessage = '网络请求失败，请检查您的网络连接。';
    if (error.response) {
      // 请求已发出，但服务器返回了一个非2xx的状态码
      // 我们优先使用后端返回的 detail 字段作为错误信息
      errorMessage = error.response.data?.detail || `服务器错误: ${error.response.status}`;
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      errorMessage = '无法连接到服务器，请稍后重试。';
    } else {
      // 其他未知错误
      errorMessage = error.message || '发生未知错误。';
    }

    // 使用Element Plus弹出清晰的错误提示
    ElMessage({
      message: errorMessage,
      type: 'error',
      duration: 5 * 1000,
    });

    // 向上抛出一个带有明确信息的Error对象
    return Promise.reject(new Error(errorMessage));
  }
);

export default service;