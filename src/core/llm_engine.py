"""
LLM引擎模块
负责与本地部署的 Deepseek 模型交互，处理提示词生成和响应解析
"""

from typing import Dict, Any
import aiohttp
import json
import os
from src.config import API_KEY, MODEL, API_BASE, MAX_TOKENS, TEMPERATURE
import re

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
        print(f"Using model: {MODEL}")
        print(f"API Base: {API_BASE}")
        
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
            
            # 发送请求到本地Deepseek模型
            print("Sending request to local Deepseek model...")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/api/generate", json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                    
                    result = await response.json()
                    if "response" not in result:
                        raise Exception("Invalid response format from API")
                    
                    # 获取完整响应内容并返回
                    return result["response"]
                    
        except Exception as e:
            raise Exception(f"Error generating response from LLM: {str(e)}")

    async def analyze_requirements(self, requirements: str) -> str:
        """
        分析需求文档，提取关键测试点
        
        Args:
            requirements (str): 需求文档文本
            
        Returns:
            str: 分析结果，包含关键测试点
        """
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

        # 发送请求到LLM
        response = await self.generate_response(requirements, system_prompt)
        return response 