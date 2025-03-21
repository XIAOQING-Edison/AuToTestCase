"""
全局配置文件
包含所有系统级别的配置参数，如API密钥、模型参数、输出配置等
"""

import os
from dotenv import load_dotenv

# 加载环境变量配置
load_dotenv()

# API 配置
# 从环境变量中获取API密钥，确保安全性
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")  # 支持多种API密钥

# 检查API密钥格式并处理
if API_KEY:
    # 确保API密钥格式正确
    print(f"已加载API密钥: {API_KEY[:15]}...")
else:
    # 如果环境变量中没有找到API密钥，使用默认值进行测试
    API_KEY = "api-sk-67d140832e0cc3-45510241"  # 默认测试密钥
    print(f"未找到API密钥环境变量，使用默认测试密钥")

# 模型配置
# 使用环境变量决定接入远程API还是本地模型
USE_REMOTE_API = os.getenv("USE_REMOTE_API", "true").lower() in ["true", "1", "yes", "y", "t"]

# 远程API默认配置
DEFAULT_REMOTE_MODEL = "gpt-3.5-turbo"  # 默认使用的远程模型
DEFAULT_REMOTE_API_BASE = "https://api.openai.com"  # 默认API基础URL

# 本地模型默认配置
DEFAULT_LOCAL_MODEL = "deepseek-r1:7b"  # 本地默认模型
DEFAULT_LOCAL_API_BASE = "http://localhost:11434"  # Ollama默认端口

# 根据使用远程还是本地模型选择默认值
if USE_REMOTE_API:
    DEFAULT_MODEL = DEFAULT_REMOTE_MODEL
    DEFAULT_API_BASE = DEFAULT_REMOTE_API_BASE
else:
    DEFAULT_MODEL = DEFAULT_LOCAL_MODEL
    DEFAULT_API_BASE = DEFAULT_LOCAL_API_BASE

# 优先使用环境变量指定的值，否则使用默认值
MODEL = os.getenv("MODEL", DEFAULT_MODEL)
API_BASE = os.getenv("API_BASE", DEFAULT_API_BASE)

# 如果需要可以尝试的备选模型列表（按优先级排序）
FALLBACK_MODELS = ["deepseek-r1:7b", "llama2:7b", "mistral:7b", "deepseek-coder:6.7b", "mistral:latest", "llama2"]

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 1  # 重试间隔(秒)

# 测试用例生成配置
# 定义测试用例优先级列表（中文）
DEFAULT_TEST_PRIORITY_LEVELS = ["高", "中", "低"]

# 优先级映射字典，用于处理英文优先级与中文优先级的转换
PRIORITY_MAPPING = {
    # 英文到中文
    "high": "高",
    "medium": "中",
    "low": "低",
    # 中文到英文（内部使用）
    "高": "高",
    "中": "中", 
    "低": "低"
}

# 旧版优先级映射（兼容已有数据）
LEGACY_PRIORITY_MAPPING = {
    "High": "高",
    "Medium": "中",
    "Low": "低"
}

# Excel导出配置
# 定义Excel表格的列标题
EXCEL_TEMPLATE_HEADERS = [
    "用例编号",           # ID
    "所属模块",           # Module
    "用例标题",           # Title
    "优先级",            # Priority
    "前置条件",           # Preconditions
    "测试步骤",           # Steps
    "预期结果"           # Expected Results
]

# LLM提示词配置
# 生成内容的最大令牌数
MAX_TOKENS = 4000  # 增加token数以确保完整的响应
# 温度参数，控制输出的随机性，越高越随机，越低越确定
TEMPERATURE = 0.1  # 降低温度使输出更加确定性

# 模型请求超时配置(秒)
REQUEST_TIMEOUT = 60

# 文件路径配置
# 定义输出目录，用于存放生成的Excel和XMind文件
OUTPUT_DIR = "output"
# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True) 