from fastapi import APIRouter, HTTPException, Body
import os
import sys
import json
import re
from typing import Dict, List, Optional, Union
from pydantic import BaseModel

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入配置模块
try:
    from src.config import (
        API_KEY, API_BASE, DEFAULT_MODEL, MODEL,
        FALLBACK_MODELS, MAX_RETRIES, 
        RETRY_DELAY, REQUEST_TIMEOUT
    )
except ImportError as e:
    print(f"导入错误: {e}")
    # 默认值，以防导入失败
    API_KEY = None
    API_BASE = "http://localhost:11434"
    DEFAULT_MODEL = "llama2:7b"
    MODEL = DEFAULT_MODEL
    FALLBACK_MODELS = ["deepseek-r1:7b", "llama2:13b"]
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    REQUEST_TIMEOUT = 60

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                         "src", "config.py")

# 定义API路由
router = APIRouter()

# 定义配置模型
class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    api_base: str
    default_model: str
    fallback_models: List[str]
    max_retries: int
    retry_delay: int
    timeout: int

# 读取配置文件
def read_config():
    try:
        return {
            "api_key": API_KEY,
            "api_base": API_BASE,
            "default_model": MODEL or DEFAULT_MODEL,
            "fallback_models": FALLBACK_MODELS,
            "max_retries": MAX_RETRIES,
            "retry_delay": RETRY_DELAY,
            "timeout": REQUEST_TIMEOUT
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取配置失败: {str(e)}")

# 更新配置文件的安全方式
def update_config_file(config: Dict[str, Union[str, List[str], int]]):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 替换配置值
        if config.get("api_key") is not None:
            if config["api_key"]:
                content = replace_config_value(content, "API_KEY", f'"{config["api_key"]}"')
            else:
                content = replace_config_value(content, "API_KEY", "None")
        
        if config.get("api_base"):
            base_url = config["api_base"].rstrip("/")  # 移除末尾的斜杠，保持统一格式
            content = replace_config_value(content, "API_BASE", f'"{base_url}"')
        
        if config.get("default_model"):
            # 更新DEFAULT_MODEL和MODEL
            content = replace_config_value(content, "DEFAULT_MODEL", f'"{config["default_model"]}"')
            # 更新MODEL的赋值，保持使用DEFAULT_MODEL或环境变量
            model_pattern = r"MODEL\s*=\s*os\.getenv\([^)]+\)"
            if re.search(model_pattern, content):
                # 如果使用环境变量，保持原样
                pass
            else:
                # 否则直接设置
                content = replace_config_value(content, "MODEL", "DEFAULT_MODEL")  
        
        if config.get("fallback_models"):
            models_str = ", ".join([f'"{model}"' for model in config["fallback_models"]])
            content = replace_config_value(content, "FALLBACK_MODELS", f'[{models_str}]')
        
        if config.get("max_retries") is not None:
            content = replace_config_value(content, "MAX_RETRIES", str(config["max_retries"]))
        
        if config.get("retry_delay") is not None:
            content = replace_config_value(content, "RETRY_DELAY", str(config["retry_delay"]))
        
        if config.get("timeout") is not None:
            content = replace_config_value(content, "REQUEST_TIMEOUT", str(config["timeout"]))
        
        # 写回文件
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}\n{e.__class__.__name__}")

# 替换配置值的辅助函数
def replace_config_value(content, key, value):
    import re
    pattern = rf"{key}\s*=\s*[^\n]+"
    replacement = f"{key} = {value}"
    result = re.sub(pattern, replacement, content)
    # 如果没有匹配，可能变量在文件中不存在，尝试添加
    if result == content and key not in content:
        # 找到适当的位置添加
        if key.startswith("API_"):
            # API相关配置，添加到API配置区域
            marker = "# API 配置"
            if marker in content:
                # 在marker后添加换行和新配置
                position = content.find(marker) + len(marker)
                result = content[:position] + f"\n{key} = {value}" + content[position:]
        elif key in ["MAX_RETRIES", "RETRY_DELAY"]:
            # 重试相关配置
            marker = "# 重试配置"
            if marker in content:
                position = content.find(marker) + len(marker)
                result = content[:position] + f"\n{key} = {value}" + content[position:]
        elif key == "REQUEST_TIMEOUT":
            # 超时配置
            marker = "# 模型请求超时配置"
            if marker in content:
                position = content.find(marker) + len(marker)
                result = content[:position] + f"\n{key} = {value}" + content[position:]
        elif key in ["DEFAULT_MODEL", "MODEL", "FALLBACK_MODELS"]:
            # 模型相关配置
            marker = "# 使用本地部署的模型"
            if marker in content:
                position = content.find(marker) + len(marker)
                result = content[:position] + f"\n{key} = {value}" + content[position:]
    return result

# API端点：获取当前配置
@router.get("/llm")
def get_llm_config():
    """获取LLM配置"""
    return read_config()

# API端点：更新配置
@router.post("/llm")
def update_llm_config(config: LLMConfig):
    """更新LLM配置"""
    config_dict = config.dict()
    
    # 更新配置文件
    update_config_file(config_dict)
    
    return {"message": "配置已更新", "config": config_dict}

# API端点：获取可用模型列表
@router.get("/available-models")
def get_available_models():
    """获取可用的LLM模型列表"""
    # 这里可以实现从Ollama或其他服务获取可用模型的逻辑
    # 现在我们返回一个静态列表作为示例
    return {
        "models": [
            {"id": "llama2:7b", "name": "Llama 2 (7B)", "description": "适合一般用途的中等规模模型"},
            {"id": "llama2:13b", "name": "Llama 2 (13B)", "description": "更大规模的通用模型"},
            {"id": "deepseek-r1:7b", "name": "DeepSeek R1 (7B)", "description": "专注于代码和技术内容的模型"},
            {"id": "mistral:7b", "name": "Mistral (7B)", "description": "高性能开源模型"},
            {"id": "wizard-r1:13b", "name": "Wizard R1 (13B)", "description": "针对指令跟随优化的大型模型"},
            {"id": "deepseek-coder:6.7b", "name": "DeepSeek Coder (6.7B)", "description": "专注于代码生成的模型"}
        ]
    }

# API端点：测试LLM连接
@router.post("/test-connection")
def test_llm_connection():
    """测试LLM连接状态"""
    try:
        # 这里可以实现实际连接测试的逻辑
        # 现在我们只返回成功状态作为示例
        return {"status": "success", "message": "LLM连接正常"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连接测试失败: {str(e)}") 