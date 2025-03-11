"""
LLM引擎模块
负责与本地部署的 Deepseek 模型交互，处理提示词生成和响应解析
"""

from typing import Dict, Any
import aiohttp
import json
import os
import logging
import traceback
from src.config import API_KEY, MODEL, API_BASE, MAX_TOKENS, TEMPERATURE
import re

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LLMEngine")

class LLMEngine:
    """
    LLM引擎类
    处理与本地部署的 Deepseek 模型的所有交互，包括生成测试用例和分析需求
    """
    
    def __init__(self):
        """
        初始化LLM引擎
        设置API配置
        """
        logger.info(f"初始化LLM引擎，使用模型: {MODEL}, API地址: {API_BASE}")
        
        self.headers = {
            "Content-Type": "application/json"
        }
        self.model = MODEL
        self.api_base = API_BASE

    async def generate_response(self, prompt: str, system_prompt: str) -> str:
        """
        生成响应
        
        Args:
            prompt (str): 用户提示词
            system_prompt (str): 系统提示词
            
        Returns:
            str: 生成的响应文本
        """
        try:
            # 构建请求数据
            data = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 降低温度使输出更加确定性
                    "num_predict": 4000  # 增加token数以确保完整的响应
                }
            }
            
            # 记录请求信息
            logger.info(f"发送请求到API: {self.api_base}/api/generate")
            logger.debug(f"使用模型: {self.model}")
            
            # 发送请求到本地Deepseek模型
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/api/generate", json=data, timeout=120) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API请求失败，状态码: {response.status}，错误信息: {error_text}")
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    result = await response.json()
                    logger.info("API请求成功，收到响应")
                    
                    if "response" not in result:
                        logger.error(f"API响应格式无效: {result}")
                        raise Exception("Invalid response format from API")
                    
                    # 获取完整响应内容并返回
                    return result["response"]
                    
        except aiohttp.ClientError as e:
            logger.error(f"网络请求错误: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Network error communicating with LLM API: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error decoding JSON response from LLM API: {str(e)}")
        except Exception as e:
            logger.error(f"生成响应时发生错误: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error generating response from LLM: {str(e)}")

    async def analyze_requirements(self, requirements: str) -> str:
        """
        分析需求文档，提取关键测试点
        
        Args:
            requirements (str): 需求文档文本
            
        Returns:
            str: 分析结果，包含关键测试点
        """
        try:
            logger.info("开始分析需求文档")
            
            # 记录需求文档内容（仅用于调试）
            logger.debug(f"需求文档内容: {requirements[:100]}...")
            
            system_prompt = """你是一个专业的测试需求分析师。请分析需求并返回JSON格式的分析结果。

警告：必须严格遵守以下规则：
1. 只返回JSON格式的数据
2. 不要有任何其他文本
3. 不要有任何解释或说明
4. 不要显示思考过程
5. 响应必须以'{'开始
6. 响应必须以'}'结束

JSON格式示例：
{
    "analysis": {
        "test_points": [
            "测试点1",
            "测试点2"
        ],
        "business_rules": [
            "规则1",
            "规则2"
        ],
        "edge_cases": [
            "边界条件1",
            "边界条件2"
        ]
    }
}"""

            logger.info("发送需求分析请求")
            # 发送请求到LLM
            response = await self.generate_response(requirements, system_prompt)
            logger.info("需求分析完成")
            return response
        except Exception as e:
            logger.error(f"分析需求时发生错误: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error analyzing requirements: {str(e)}") 