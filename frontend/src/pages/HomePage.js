import React from 'react';
import { Typography, Card, Button, Row, Col } from 'antd';
import { FileTextOutlined, RocketOutlined, SettingOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  return (
    <div className="home-page">
      <Typography>
        <Title level={1}>AuToTestCase</Title>
        <Paragraph>
          基于大语言模型的测试用例自动生成工具，帮助测试工程师从需求文档快速生成高质量测试用例。
        </Paragraph>
      </Typography>
      
      <Row gutter={[16, 16]} style={{ marginTop: '2rem' }}>
        <Col xs={24} sm={12} md={8}>
          <Card 
            title="从需求生成测试用例" 
            bordered={true}
            hoverable
            actions={[
              <Link to="/generator">
                <Button type="primary">开始使用</Button>
              </Link>
            ]}
          >
            <FileTextOutlined style={{ fontSize: '3rem', color: '#1890ff', marginBottom: '1rem' }} />
            <Paragraph>
              上传需求文档或直接输入需求文本，自动分析并生成测试用例。
            </Paragraph>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={8}>
          <Card 
            title="多种导出格式" 
            bordered={true}
            hoverable
            actions={[
              <Link to="/generator">
                <Button>查看示例</Button>
              </Link>
            ]}
          >
            <RocketOutlined style={{ fontSize: '3rem', color: '#52c41a', marginBottom: '1rem' }} />
            <Paragraph>
              支持Excel和XMind格式导出，便于集成到您的测试流程中。
            </Paragraph>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} md={8}>
          <Card 
            title="高度可配置" 
            bordered={true}
            hoverable
            actions={[
              <Link to="/settings">
                <Button>配置</Button>
              </Link>
            ]}
          >
            <SettingOutlined style={{ fontSize: '3rem', color: '#fa8c16', marginBottom: '1rem' }} />
            <Paragraph>
              自定义LLM模型参数、优先级和输出格式，满足不同的需求。
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage; 