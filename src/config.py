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
API_KEY = None  # 本地模型不需要API密钥
# 使用本地部署的 Deepseek 模型
MODEL = "deepseek-r1:7b"  # Ollama模型名称
API_BASE = "http://localhost:11434"  # Ollama默认端口是11434

# 测试用例生成配置
# 定义测试用例优先级列表
DEFAULT_TEST_PRIORITY_LEVELS = ["High", "Medium", "Low"]
# 定义测试用例类别
DEFAULT_TEST_CATEGORIES = [
    "Functional",    # 功能测试
    "UI/UX",        # 界面和用户体验测试
    "Performance",   # 性能测试
    "Security",      # 安全测试
    "Edge Cases"    # 边界条件测试
]

# Excel导出配置
# 定义Excel表格的列标题
EXCEL_TEMPLATE_HEADERS = [
    "用例编号",           # ID
    "所属模块",           # Module
    "用例标题",           # Title
    "优先级",            # Priority
    "用例类型",           # Category
    "前置条件",           # Preconditions
    "测试步骤",           # Steps
    "预期结果"           # Expected Results
]

# LLM提示词配置
# 生成内容的最大令牌数
MAX_TOKENS = 4000  # 增加token数以确保完整的响应
# 温度参数，控制输出的随机性，越高越随机，越低越确定
TEMPERATURE = 0.1  # 降低温度使输出更加确定性

# 文件路径配置
# 定义输出目录，用于存放生成的Excel和XMind文件
OUTPUT_DIR = "output"
# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True) 