import React from 'react';
import { Layout, Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { HomeOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons';

const { Header } = Layout;

const AppHeader = () => {
  const location = useLocation();
  
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: <Link to="/">首页</Link>,
    },
    {
      key: '/generator',
      icon: <AppstoreOutlined />,
      label: <Link to="/generator">测试用例生成</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">设置</Link>,
    },
  ];

  // 确定当前选中的菜单项
  const selectedKey = menuItems.find(item => 
    location.pathname === item.key || 
    (item.key !== '/' && location.pathname.startsWith(item.key))
  )?.key || '/';

  return (
    <Header style={{ position: 'fixed', zIndex: 1, width: '100%' }}>
      <div className="logo" style={{ float: 'left', color: 'white', marginRight: '20px', fontSize: '18px', fontWeight: 'bold' }}>
        AuToTestCase
      </div>
      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[selectedKey]}
        items={menuItems}
      />
    </Header>
  );
};

export default AppHeader; 