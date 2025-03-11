import axios from 'axios';
import { notification } from 'antd';

// 创建自定义Axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8080', // 直接指向后端服务器
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 处理错误响应
    const message = error.response?.data?.detail || error.message || '请求失败';
    
    notification.error({
      message: '请求错误',
      description: message,
    });
    
    return Promise.reject(error);
  }
);

export default apiClient; 