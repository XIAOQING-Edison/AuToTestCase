import React from 'react';
import { Layout } from 'antd';

const { Footer } = Layout;

const AppFooter = () => {
  return (
    <Footer style={{ textAlign: 'center' }}>
      AuToTestCase © {new Date().getFullYear()} - 基于大语言模型的测试用例生成工具
    </Footer>
  );
};

export default AppFooter; 