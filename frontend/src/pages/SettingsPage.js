import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Card, 
  Form, 
  Input, 
  Select, 
  InputNumber, 
  Button, 
  notification, 
  Space, 
  Divider, 
  Spin, 
  Alert, 
  Tag, 
  Switch,
  Tabs
} from 'antd';
import { 
  SaveOutlined, 
  ReloadOutlined, 
  ApiOutlined, 
  ExperimentOutlined, 
  SettingOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const SettingsPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [models, setModels] = useState([]);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // 获取配置
  const fetchConfig = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/config/llm');
      
      // 处理API_BASE路径，确保它以/api结尾
      let configData = response.data;
      if (configData.api_base && !configData.api_base.endsWith('/api')) {
        configData.api_base = `${configData.api_base}/api`;
      }
      
      form.setFieldsValue(configData);
    } catch (error) {
      console.error('Error fetching config:', error);
      notification.error({
        message: '获取配置失败',
        description: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  // 获取可用模型
  const fetchModels = async () => {
    setModelsLoading(true);
    try {
      const response = await axios.get('/api/config/available-models');
      setModels(response.data.models);
    } catch (error) {
      console.error('Error fetching models:', error);
      notification.error({
        message: '获取模型列表失败',
        description: error.response?.data?.detail || error.message
      });
    } finally {
      setModelsLoading(false);
    }
  };

  // 测试连接
  const testConnection = async () => {
    setTestingConnection(true);
    try {
      const response = await axios.post('/api/config/test-connection');
      if (response.data.status === 'success') {
        setConnectionStatus('success');
        notification.success({
          message: '连接测试成功',
          description: '与LLM服务器的连接正常。'
        });
      } else {
        setConnectionStatus('error');
        notification.error({
          message: '连接测试失败',
          description: response.data.message
        });
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      setConnectionStatus('error');
      notification.error({
        message: '连接测试失败',
        description: error.response?.data?.detail || error.message
      });
    } finally {
      setTestingConnection(false);
    }
  };

  // 保存配置
  const handleSubmit = async (values) => {
    setLoading(true);
    setSaveSuccess(false);
    try {
      // 处理API_BASE，确保它的格式正确
      let submitValues = {...values};
      if (submitValues.api_base && submitValues.api_base.endsWith('/api')) {
        submitValues.api_base = submitValues.api_base.replace(/\/api$/, '');
      }
      
      await axios.post('/api/config/llm', submitValues);
      notification.success({
        message: '配置已保存',
        description: 'LLM配置已成功更新。'
      });
      setSaveSuccess(true);
    } catch (error) {
      console.error('Error saving config:', error);
      notification.error({
        message: '保存配置失败',
        description: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    fetchConfig();
    fetchModels();
  }, []);

  // 定义Tabs项
  const tabItems = [
    {
      key: 'llm',
      label: (
        <span>
          <ExperimentOutlined />
          大语言模型
        </span>
      ),
      children: (
        <Card>
          <Spin spinning={loading}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              initialValues={{
                api_key: '',
                api_base: 'http://localhost:11434/api',
                default_model: 'llama2:7b',
                fallback_models: ['deepseek-r1:7b'],
                max_retries: 3,
                retry_delay: 2,
                timeout: 60
              }}
            >
              <Alert
                style={{ marginBottom: '24px' }}
                message="LLM模型配置"
                description="配置用于生成测试用例的大语言模型参数。本地模型通常不需要API密钥。"
                type="info"
                showIcon
              />

              <Form.Item 
                label="API服务器" 
                name="api_base"
                rules={[{ required: true, message: '请输入API服务器地址' }]}
                tooltip="LLM服务器的URL，例如Ollama的本地地址或OpenAI的API地址"
              >
                <Input 
                  placeholder="例如：http://localhost:11434/api" 
                  prefix={<ApiOutlined />} 
                />
              </Form.Item>

              <Form.Item 
                label="API密钥" 
                name="api_key"
                tooltip="API密钥/令牌，本地Ollama服务通常不需要"
              >
                <Input.Password 
                  placeholder="API密钥（本地Ollama不需要）" 
                />
              </Form.Item>

              <Form.Item 
                label="默认模型" 
                name="default_model"
                rules={[{ required: true, message: '请选择默认模型' }]}
                tooltip="首选的LLM模型"
              >
                <Select
                  loading={modelsLoading}
                  showSearch
                  placeholder="选择默认模型"
                  optionFilterProp="children"
                >
                  {models.map(model => (
                    <Option key={model.id} value={model.id}>
                      {model.name} - {model.description}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item 
                label="备选模型" 
                name="fallback_models"
                tooltip="当默认模型不可用时，将使用这些备选模型"
              >
                <Select
                  mode="multiple"
                  loading={modelsLoading}
                  placeholder="选择备选模型"
                  optionFilterProp="children"
                >
                  {models.map(model => (
                    <Option key={model.id} value={model.id}>
                      {model.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Divider orientation="left">高级设置</Divider>

              <Form.Item 
                label="最大重试次数" 
                name="max_retries"
                rules={[{ required: true, message: '请输入最大重试次数' }]}
                tooltip="请求失败时的最大重试次数"
              >
                <InputNumber min={0} max={10} />
              </Form.Item>

              <Form.Item 
                label="重试延迟(秒)" 
                name="retry_delay"
                rules={[{ required: true, message: '请输入重试延迟' }]}
                tooltip="两次重试之间的延迟时间(秒)"
              >
                <InputNumber min={1} max={60} />
              </Form.Item>

              <Form.Item 
                label="超时时间(秒)" 
                name="timeout"
                rules={[{ required: true, message: '请输入超时时间' }]}
                tooltip="请求超时时间(秒)"
              >
                <InputNumber min={10} max={300} />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    htmlType="submit"
                    loading={loading}
                  >
                    保存配置
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={fetchConfig}
                  >
                    重置
                  </Button>
                  <Button
                    icon={testingConnection ? <Spin size="small" /> : <ApiOutlined />}
                    onClick={testConnection}
                    loading={testingConnection}
                  >
                    测试连接
                  </Button>
                  {connectionStatus === 'success' && (
                    <Tag color="success" icon={<CheckCircleOutlined />}>连接正常</Tag>
                  )}
                  {connectionStatus === 'error' && (
                    <Tag color="error" icon={<CloseCircleOutlined />}>连接失败</Tag>
                  )}
                  {saveSuccess && (
                    <Tag color="success" icon={<CheckCircleOutlined />}>保存成功</Tag>
                  )}
                </Space>
              </Form.Item>
            </Form>
          </Spin>
        </Card>
      )
    },
    {
      key: 'system',
      label: (
        <span>
          <SettingOutlined />
          系统设置
        </span>
      ),
      children: (
        <Card>
          <Alert
            style={{ marginBottom: '24px' }}
            message="此功能即将推出"
            description="系统全局设置页面正在开发中，敬请期待。"
            type="info"
            showIcon
          />
        </Card>
      )
    }
  ];

  return (
    <div className="settings-page">
      <Typography>
        <Title level={2}>系统设置</Title>
        <Paragraph>
          配置大语言模型和系统参数，优化测试用例生成效果。
        </Paragraph>
      </Typography>

      <Tabs defaultActiveKey="llm" items={tabItems} />
    </div>
  );
};

export default SettingsPage; 