import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Upload, 
  Button, 
  Select, 
  Spin, 
  notification, 
  Tabs, 
  Form, 
  Input,
  Card,
  Divider,
  Steps,
  Result,
  Progress,
  Space,
  Modal
} from 'antd';
import { 
  UploadOutlined, 
  FileTextOutlined, 
  CodeOutlined, 
  CheckCircleOutlined, 
  LoadingOutlined,
  PictureOutlined,
  EditOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const TestCaseGenerator = () => {
  const [activeTab, setActiveTab] = useState('file');
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [outputFormat, setOutputFormat] = useState('excel');
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const [progressMessage, setProgressMessage] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  
  // OCR相关状态
  const [ocrVisible, setOcrVisible] = useState(false);
  const [ocrImage, setOcrImage] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrTaskId, setOcrTaskId] = useState(null);
  const [ocrPollingInterval, setOcrPollingInterval] = useState(null);
  const [ocrProgress, setOcrProgress] = useState(0);
  const [ocrMessage, setOcrMessage] = useState('');
  const [recognizedText, setRecognizedText] = useState('');

  // 轮询任务状态
  useEffect(() => {
    if (taskId && currentStep === 1) {
      const interval = setInterval(() => {
        checkTaskStatus(taskId);
      }, 2000);
      setPollingInterval(interval);
      return () => clearInterval(interval);
    }
  }, [taskId, currentStep]);

  // 当任务完成时停止轮询
  useEffect(() => {
    if (taskStatus && (taskStatus.status === 'completed' || taskStatus.status === 'failed')) {
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }

      // 无论成功还是失败，都要重置加载状态
      setLoading(false);

      if (taskStatus.status === 'completed') {
        downloadTaskResult(taskId);
        setCurrentStep(2);
        notification.success({ message: '测试用例生成成功' });
      } else if (taskStatus.status === 'failed') {
        setCurrentStep(0);
        notification.error({ 
          message: '生成失败', 
          description: taskStatus.message 
        });
      }
    }
  }, [taskStatus]);

  // OCR任务轮询
  useEffect(() => {
    if (ocrTaskId && ocrLoading) {
      const interval = setInterval(() => {
        checkOcrStatus(ocrTaskId);
      }, 1000);
      setOcrPollingInterval(interval);
      return () => clearInterval(interval);
    }
  }, [ocrTaskId, ocrLoading]);

  // 当OCR任务完成时停止轮询
  useEffect(() => {
    if (
      ocrTaskId && 
      (ocrProgress === 100 || 
       ocrMessage.includes('失败') || 
       ocrMessage.includes('完成') ||
       ocrMessage.includes('error'))
    ) {
      console.log('停止OCR轮询:', ocrMessage, ocrProgress);
      
      if (ocrPollingInterval) {
        clearInterval(ocrPollingInterval);
        setOcrPollingInterval(null);
        setOcrLoading(false);
      }
    }
  }, [ocrProgress, ocrMessage, ocrTaskId, ocrPollingInterval]);

  const checkTaskStatus = async (id) => {
    try {
      // 使用绝对URL直接指向后端服务器
      const response = await axios.get(`http://localhost:8080/api/test-cases/status/${id}`);
      setTaskStatus(response.data);
      
      // 更新进度信息
      setProgressMessage(response.data.message || '');
      setProgressPercent(response.data.progress || 0);
    } catch (error) {
      console.error('Error checking task status:', error);
    }
  };

  const checkOcrStatus = async (id) => {
    try {
      // 使用绝对URL直接指向后端服务器
      const response = await axios.get(`http://localhost:8080/api/ocr/status/${id}`);
      
      console.log('OCR状态:', response.data);
      
      // 更新OCR进度信息
      setOcrProgress(response.data.progress || 0);
      setOcrMessage(response.data.message || '');
      
      // 如果OCR完成，获取识别的文本
      if (response.data.status === 'completed' && response.data.text) {
        setRecognizedText(response.data.text);
        notification.success({ message: '图片文字识别成功' });
        
        // 立即清除轮询
        if (ocrPollingInterval) {
          clearInterval(ocrPollingInterval);
          setOcrPollingInterval(null);
          setOcrLoading(false);
        }
      } else if (response.data.status === 'failed') {
        notification.error({ 
          message: '图片识别失败', 
          description: response.data.message 
        });
        
        // 立即清除轮询
        if (ocrPollingInterval) {
          clearInterval(ocrPollingInterval);
          setOcrPollingInterval(null);
          setOcrLoading(false);
        }
      }
    } catch (error) {
      console.error('Error checking OCR status:', error);
      
      // 出错时也停止轮询
      if (ocrPollingInterval) {
        clearInterval(ocrPollingInterval);
        setOcrPollingInterval(null);
        setOcrLoading(false);
      }
      
      notification.error({
        message: '检查OCR状态失败',
        description: error.message
      });
    }
  };

  const downloadTaskResult = async (id) => {
    try {
      // 使用绝对URL直接指向后端服务器
      const response = await axios.get(`http://localhost:8080/api/test-cases/download/${id}`, {
        responseType: 'blob'
      });
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setDownloadUrl(url);
      
      // 设置文件名
      const contentDisposition = response.headers['content-disposition'];
      let downloadFilename = `test_cases.${outputFormat}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch && filenameMatch[1]) {
          downloadFilename = filenameMatch[1];
        }
      }
      
      setFileName(downloadFilename);
    } catch (error) {
      console.error('Error downloading task result:', error);
      notification.error({ 
        message: '下载失败', 
        description: error.response?.data?.detail || error.message 
      });
      // 确保在下载失败时也重置加载状态
      setLoading(false);
    }
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
  };

  const handleFileChange = (info) => {
    if (info.fileList.length > 0) {
      setFile(info.fileList[0].originFileObj);
    } else {
      setFile(null);
    }
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleFormatChange = (value) => {
    setOutputFormat(value);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setCurrentStep(1);
    setProgressPercent(0);
    setProgressMessage('正在准备生成测试用例...');
    
    try {
      let response;
      const formData = new FormData();
      
      if (activeTab === 'file') {
        if (!file) {
          notification.error({ message: '请先上传需求文档' });
          setLoading(false);
          setCurrentStep(0);
          return;
        }
        
        formData.append('file', file);
        formData.append('output_format', outputFormat);
        
        // 使用绝对URL直接指向后端服务器
        response = await axios.post(
          'http://localhost:8080/api/test-cases/generate-from-file',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );
      } else {
        if (!text.trim()) {
          notification.error({ message: '请输入需求文本' });
          setLoading(false);
          setCurrentStep(0);
          return;
        }
        
        formData.append('text', text);
        formData.append('output_format', outputFormat);
        
        // 使用绝对URL直接指向后端服务器
        response = await axios.post(
          'http://localhost:8080/api/test-cases/generate-from-text',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        );
      }
      
      // 保存任务ID并开始轮询
      setTaskId(response.data.task_id);
      
    } catch (error) {
      console.error('Error generating test cases:', error);
      notification.error({ 
        message: '生成失败', 
        description: error.response?.data?.detail || error.message 
      });
      setCurrentStep(0);
      setLoading(false);
    }
  };

  const downloadFile = () => {
    if (!downloadUrl) return;
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', fileName || `test_cases.${outputFormat}`);
    document.body.appendChild(link);
    link.click();
    
    // 清理
    if (link.parentNode) {
      link.parentNode.removeChild(link);
    }
  };

  const resetForm = () => {
    setFile(null);
    setText('');
    setCurrentStep(0);
    setDownloadUrl(null);
    setFileName(null);
  };

  // 打开OCR模态窗
  const showOcrModal = () => {
    setOcrVisible(true);
    setOcrImage(null);
    setRecognizedText('');
    setOcrProgress(0);
  };

  // 关闭OCR模态窗
  const handleOcrCancel = () => {
    // 确保清除所有轮询
    if (ocrPollingInterval) {
      clearInterval(ocrPollingInterval);
      setOcrPollingInterval(null);
    }
    setOcrVisible(false);
    setOcrLoading(false);
    setOcrTaskId(null); // 重置任务ID
  };

  // 处理OCR图片上传
  const handleOcrImageChange = (info) => {
    if (info.fileList.length > 0) {
      setOcrImage(info.fileList[0].originFileObj);
    } else {
      setOcrImage(null);
    }
  };

  // 启动OCR识别
  const startOcrRecognition = async () => {
    if (!ocrImage) {
      notification.error({ message: '请先上传图片' });
      return;
    }

    // 确保清除之前的轮询
    if (ocrPollingInterval) {
      clearInterval(ocrPollingInterval);
      setOcrPollingInterval(null);
    }

    setOcrLoading(true);
    setOcrProgress(0);
    setOcrMessage('准备识别图片...');
    
    try {
      const formData = new FormData();
      formData.append('file', ocrImage);
      
      // 使用绝对URL直接指向后端服务器
      const response = await axios.post(
        'http://localhost:8080/api/ocr/recognize',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 30000 // 30秒超时
        }
      );
      
      console.log('OCR识别请求响应:', response.data);
      
      // 保存OCR任务ID并开始轮询
      if (response.data && response.data.task_id) {
        setOcrTaskId(response.data.task_id);
      } else {
        throw new Error('未获取到有效的任务ID');
      }
      
    } catch (error) {
      console.error('Error recognizing image:', error);
      notification.error({ 
        message: '图片识别失败', 
        description: error.response?.data?.detail || error.message 
      });
      setOcrLoading(false);
    }
  };

  // 应用识别文本到需求输入框
  const applyRecognizedText = () => {
    if (recognizedText) {
      setText(recognizedText);
      setActiveTab('text');
      handleOcrCancel();
      notification.success({ message: '文本已应用到需求输入框' });
    }
  };

  const renderSteps = () => {
    return (
      <Steps
        current={currentStep}
        style={{ marginBottom: '2rem' }}
        items={[
          {
            title: '准备需求',
            description: '上传文件或输入文本',
            icon: <FileTextOutlined />
          },
          {
            title: '生成测试用例',
            description: '处理中...',
            icon: currentStep === 1 ? <LoadingOutlined /> : <CodeOutlined />
          },
          {
            title: '完成',
            description: '下载结果',
            icon: <CheckCircleOutlined />
          },
        ]}
      />
    );
  };

  // OCR模态窗内容
  const renderOcrModalContent = () => {
    return (
      <div>
        <Paragraph>
          上传包含需求的图片，系统将自动识别图片中的文字内容。
        </Paragraph>
        
        <Upload
          beforeUpload={() => false}
          onChange={handleOcrImageChange}
          maxCount={1}
          accept="image/jpeg,image/png,image/jpg,image/bmp,image/tiff"
          fileList={ocrImage ? [{ uid: '-1', name: ocrImage.name, status: 'done' }] : []}
        >
          <Button icon={<UploadOutlined />}>选择图片</Button>
        </Upload>
        
        {ocrLoading && (
          <div style={{ marginTop: '20px' }}>
            <Progress percent={ocrProgress} status="active" />
            <p>{ocrMessage || '识别中...'}</p>
          </div>
        )}
        
        {recognizedText && (
          <div style={{ marginTop: '20px' }}>
            <Title level={5}>识别结果:</Title>
            <TextArea
              value={recognizedText}
              onChange={(e) => setRecognizedText(e.target.value)}
              rows={8}
              style={{ marginBottom: '10px' }}
            />
          </div>
        )}
        
        {ocrMessage && ocrMessage.includes('无法识别') && (
          <div style={{ marginTop: '20px', border: '1px solid #ffccc7', padding: '10px', backgroundColor: '#fff2f0', borderRadius: '2px' }}>
            <p style={{ fontWeight: 'bold', color: '#cf1322' }}>图片识别失败</p>
            <ul style={{ paddingLeft: '20px' }}>
              <li>图片质量可能较低或文字不清晰</li>
              <li>尝试上传更清晰的图片</li>
              <li>如果有文字，可以手动输入到下方文本框</li>
              <li>尝试不同角度或光线条件下拍摄图片</li>
            </ul>
            <TextArea
              placeholder="如果您能看清图片内容，可以在此手动输入文字..."
              rows={6}
              onChange={(e) => setRecognizedText(e.target.value)}
              style={{ marginTop: '10px' }}
            />
          </div>
        )}
      </div>
    );
  };

  // 定义Tabs项
  const tabItems = [
    {
      key: 'file',
      label: '上传需求文档',
      children: (
        <>
          <Upload
            beforeUpload={() => false}
            onChange={handleFileChange}
            fileList={file ? [{ uid: '-1', name: file.name }] : []}
            maxCount={1}
          >
            <Button icon={<UploadOutlined />}>选择文件</Button>
          </Upload>
          <Paragraph style={{ marginTop: '1rem' }}>
            支持Markdown和文本格式的需求文档。
          </Paragraph>
        </>
      )
    },
    {
      key: 'text',
      label: '输入需求文本',
      children: (
        <>
          <TextArea
            rows={10}
            placeholder="在这里粘贴或输入需求文本..."
            value={text}
            onChange={handleTextChange}
          />
          <div style={{ marginTop: '10px' }}>
            <Button 
              type="default" 
              icon={<PictureOutlined />} 
              onClick={showOcrModal}
              style={{ marginTop: '5px' }}
            >
              从图片识别文字
            </Button>
          </div>
        </>
      )
    }
  ];

  const renderProgressInfo = () => {
    if (currentStep !== 1) return null;
    
    return (
      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <Progress percent={progressPercent} status="active" />
        <p style={{ marginTop: '10px' }}>{progressMessage || '请耐心等待...'}</p>
      </div>
    );
  };

  return (
    <div className="test-case-generator">
      <Typography>
        <Title level={2}>测试用例生成器</Title>
        <Paragraph>
          上传需求文档或直接输入需求文本，快速生成高质量测试用例。
        </Paragraph>
      </Typography>

      <Card style={{ marginTop: '1rem' }}>
        {renderSteps()}
        
        {currentStep === 2 ? (
          <Result
            status="success"
            title="测试用例生成成功！"
            subTitle="您可以下载生成的测试用例文件"
            extra={[
              <Button type="primary" key="download" onClick={downloadFile}>
                下载测试用例
              </Button>,
              <Button key="new" onClick={resetForm}>
                生成新的测试用例
              </Button>,
            ]}
          />
        ) : (
          <>
            <Tabs activeKey={activeTab} onChange={handleTabChange} items={tabItems} />
            
            <Divider />
            
            {renderProgressInfo()}
            
            <div style={{ marginTop: '1rem' }}>
              <Select
                defaultValue={outputFormat}
                onChange={handleFormatChange}
                style={{ width: 120, marginRight: '1rem' }}
                options={[
                  { value: 'excel', label: 'Excel格式' },
                  { value: 'xmind', label: 'XMind格式' },
                ]}
              />
              <Button 
                type="primary" 
                onClick={handleSubmit} 
                loading={loading}
                disabled={currentStep === 1}
              >
                生成测试用例
              </Button>
            </div>
          </>
        )}
      </Card>

      {/* OCR模态窗 */}
      <Modal
        title="图片文字识别"
        open={ocrVisible}
        onCancel={handleOcrCancel}
        footer={[
          <Button key="back" onClick={handleOcrCancel}>
            取消
          </Button>,
          <Button 
            key="recognize" 
            type="default" 
            onClick={startOcrRecognition}
            loading={ocrLoading}
            disabled={!ocrImage || ocrLoading}
          >
            {ocrTaskId && ocrMessage && ocrMessage.includes('失败') ? '重新识别' : '识别文字'}
          </Button>,
          <Button 
            key="apply" 
            type="primary" 
            onClick={applyRecognizedText}
            disabled={!recognizedText}
          >
            应用到需求
          </Button>,
        ]}
        width={700}
      >
        {renderOcrModalContent()}
      </Modal>
    </div>
  );
};

export default TestCaseGenerator; 