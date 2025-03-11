import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import './App.css';

// Pages
import HomePage from './pages/HomePage';
import TestCaseGenerator from './pages/TestCaseGenerator';
import SettingsPage from './pages/SettingsPage';

// Components
import AppHeader from './components/AppHeader';
import AppFooter from './components/AppFooter';

const { Content } = Layout;

function App() {
  return (
    <Router>
      <Layout className="layout" style={{ minHeight: '100vh' }}>
        <AppHeader />
        <Content style={{ padding: '0 50px', marginTop: 64 }}>
          <div className="site-layout-content" style={{ padding: 24, minHeight: 380 }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/generator" element={<TestCaseGenerator />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </Content>
        <AppFooter />
      </Layout>
    </Router>
  );
}

export default App;
