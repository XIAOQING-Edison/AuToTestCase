# AuToTestCase 安装指南

本文档将指导您如何安装和配置AuToTestCase工具，使其能够在您的环境中正常运行。

## 目录

1. [系统要求](#系统要求)
2. [安装步骤](#安装步骤)
   - [基础安装](#基础安装)
   - [安装大语言模型](#安装大语言模型)
   - [安装Playwright（可选）](#安装playwright可选)
3. [验证安装](#验证安装)
4. [常见安装问题](#常见安装问题)

## 系统要求

- Python 3.8 或更高版本
- 最少4GB RAM（推荐8GB以上）
- 对于本地运行大语言模型，至少需要8GB VRAM
- 操作系统要求：
  - Windows 10/11
  - macOS 10.15+
  - Ubuntu 20.04+ 或其他现代Linux发行版

## 安装步骤

### 基础安装

1. 克隆项目仓库：

```bash
git clone https://github.com/yourusername/AuToTestCase.git
cd AuToTestCase
```

2. 创建并激活虚拟环境（推荐）：

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖包：

```bash
pip install -r requirements.txt
```

### 安装大语言模型

AuToTestCase可以使用本地LLM模型（通过Ollama）或远程API。

#### 使用Ollama本地模型（推荐）

1. 安装Ollama：

- [Windows安装](https://ollama.ai/download/windows)
- [macOS安装](https://ollama.ai/download/mac)
- [Linux安装](https://ollama.ai/download/linux)

2. 下载所需模型：

```bash
# 下载默认的llama2模型
ollama pull llama2:7b

# 可选：下载更强大的模型
ollama pull deepseek-r1:7b
```

3. 确保Ollama服务运行：

```bash
ollama serve
```

#### 使用远程API

如果您希望使用远程API（如OpenAI），请在`src/config.py`中进行配置：

```python
API_KEY = "您的API密钥"
API_BASE = "https://api.openai.com/v1"
MODEL = "gpt-3.5-turbo"
```

### 安装Playwright（可选）

如果您需要使用高级网页抓取功能，需要安装Playwright：

```bash
pip install playwright
playwright install
```

## 验证安装

安装完成后，您可以运行以下命令验证安装是否成功：

```bash
# 检查大语言模型连接
python -m src.tools.model_checker

# 检查基本功能
python -m src.main --help
```

## 常见安装问题

### 依赖安装失败

如果安装依赖包时遇到问题：

```bash
# 更新pip
pip install --upgrade pip

# 分步安装
pip install pandas
pip install openpyxl
pip install aiohttp
```

### 无法连接到Ollama

如果遇到无法连接到Ollama服务的问题：

1. 确认Ollama服务是否运行：`ollama serve`
2. 检查配置文件中的API地址是否正确：`src/config.py`中的`API_BASE`
3. 检查防火墙设置是否阻止了端口11434

### 模型内存不足

如果运行时出现内存不足的错误：

1. 尝试使用较小的模型，例如从`deepseek-r1:7b`切换到`llama2:7b`
2. 在`src/config.py`中增加超时时间：`TIMEOUT = 120`
3. 减少批处理的并发数：`BATCH_MAX_CONCURRENT = 1`

### macOS安全限制

在macOS上，可能会遇到安全限制问题：

1. 在"系统偏好设置 > 安全性与隐私"中允许应用运行
2. 对于Playwright，可能需要授予"辅助功能"权限

### Python版本问题

确保使用Python 3.8或更高版本：

```bash
python --version
# 或
python3 --version
```

## 更新AuToTestCase

要更新到最新版本：

```bash
git pull
pip install -r requirements.txt --upgrade
```

## 下一步

安装完成后，请参阅[使用指南](usage_guide.md)了解如何使用AuToTestCase的各项功能。 