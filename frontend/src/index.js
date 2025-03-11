import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';
import axios from 'axios';
import { notification } from 'antd';

// 配置通知显示
notification.config({
  maxCount: 3,
  duration: 3 // 通知显示3秒
});

// 配置Axios默认设置
axios.defaults.timeout = 60000; // 60秒超时
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

// 配置CORS支持
axios.defaults.withCredentials = true;

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN} theme={{
      token: {
        colorPrimary: '#1890ff',
      },
    }}>
      <App />
    </ConfigProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
