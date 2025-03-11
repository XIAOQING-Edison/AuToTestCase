# AuToTestCase 配置指南

本文档详细介绍了AuToTestCase的配置选项和自定义设置，帮助您根据自己的需求调整系统行为。

## 目录

1. [配置文件位置](#配置文件位置)
2. [LLM模型配置](#llm模型配置)
3. [优先级配置](#优先级配置)
4. [输出格式配置](#输出格式配置)
5. [爬虫配置](#爬虫配置)
6. [高级选项](#高级选项)

## 配置文件位置

AuToTestCase的主要配置文件位于`src/config.py`。您可以通过修改此文件来自定义系统的行为。

## LLM模型配置

```python
# API相关配置
API_KEY = None  # 本地模型不需要API密钥
API_BASE = "http://localhost:11434/api"  # 本地Ollama API地址
API_VERSION = ""

# 模型配置
DEFAULT_MODEL = "llama2:7b"  # 默认模型
FALLBACK_MODELS = ["deepseek-r1:7b", "llama2:13b", "mistral:7b"]  # 备选模型

# 配置环境变量覆盖
MODEL = os.environ.get("AUTOTESTCASE_MODEL", DEFAULT_MODEL)

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）
TIMEOUT = 60  # 请求超时时间（秒）
```

### 配置说明

- **API_KEY**: API密钥，本地模型设置为`None`
- **API_BASE**: API基础URL，默认是本地Ollama服务
- **DEFAULT_MODEL**: 首选LLM模型
- **FALLBACK_MODELS**: 备选模型列表，当首选模型不可用时使用
- **MAX_RETRIES**: 请求失败时的最大重试次数
- **RETRY_DELAY**: 重试之间的延迟时间（秒）
- **TIMEOUT**: 请求超时时间（秒）

## 优先级配置

您可以根据公司或团队的标准调整测试用例优先级：

```python
# 测试用例优先级配置
DEFAULT_TEST_PRIORITY_LEVELS = ["高", "中", "低"]  # 默认为中文表示
# 优先级映射（用于英文/中文转换）
PRIORITY_MAPPING = {
    "High": "高",
    "Medium": "中",
    "Low": "低",
    "高": "High",
    "中": "Medium",
    "低": "Low"
}
```

## 输出格式配置

导出格式相关配置：

```python
# Excel导出配置
EXCEL_HEADERS = [
    "用例编号", "所属模块", "用例标题", "优先级", 
    "前置条件", "测试步骤", "预期结果"
]

# 是否启用XMind导出
ENABLE_XMIND_EXPORT = True
```

## 爬虫配置

爬虫相关配置：

```python
# 默认爬虫设置
DEFAULT_CRAWLER_TIMEOUT = 30  # 秒
VERIFY_SSL = False  # 是否验证SSL证书
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Playwright爬虫特定配置
PLAYWRIGHT_DEFAULT_WAIT = "networkidle"  # 默认等待事件
```

## 高级选项

高级配置选项：

```python
# 批处理配置
BATCH_MAX_CONCURRENT = 2  # 最大并发处理数量
BATCH_TIMEOUT = 600  # 批处理超时时间（秒）

# 调试配置
DEBUG = False  # 调试模式
VERBOSE = False  # 详细输出

# 本地化配置
LANGUAGE = "zh_CN"  # 默认语言
```

## 通过环境变量覆盖配置

您可以通过设置环境变量来覆盖配置，无需修改配置文件：

```bash
# 设置模型
export AUTOTESTCASE_MODEL="deepseek-r1:7b"

# 设置API地址
export AUTOTESTCASE_API_BASE="http://localhost:8000/v1"

# 设置调试模式
export AUTOTESTCASE_DEBUG="true"
```

## 样例配置

以下是一个完整的配置样例：

```python
# 使用OpenAI API
API_KEY = "sk-your-api-key"
API_BASE = "https://api.openai.com/v1"
MODEL = "gpt-3.5-turbo"
FALLBACK_MODELS = ["gpt-4"]

# 自定义优先级
DEFAULT_TEST_PRIORITY_LEVELS = ["P0", "P1", "P2", "P3"]
```

注意：修改配置后，建议重新启动应用以确保更改生效。 