"""
LLM引擎模块
负责与模型交互，支持本地模型和远程API
"""

from typing import Dict, Any
import aiohttp
import json
import os
import ssl
import sys
import re

# 将项目根目录添加到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 现在可以导入config
from config import API_KEY, MODEL, API_BASE, MAX_TOKENS, TEMPERATURE, USE_REMOTE_API

class LLMEngine:
    """
    LLM引擎类
    处理与模型的所有交互，包括本地模型和远程API
    """
    
    def __init__(self):
        """
        初始化LLM引擎
        设置API配置
        """
        print(f"Using model: {MODEL}")
        print(f"API Base: {API_BASE}")
        print(f"Using remote API: {USE_REMOTE_API}")
        
        # 强制使用测试连接脚本中的API密钥
        self.api_key = "api-sk-67d140832e0cc3-45510241"  # 硬编码API密钥以确保正确格式
        print(f"实际使用的API密钥: {self.api_key}")
        
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        
        print(f"API请求头: {json.dumps(self.headers, ensure_ascii=False)}")
        print(f"API密钥配置成功")
                
        self.model = MODEL
        self.api_base = API_BASE
        self.use_remote_api = USE_REMOTE_API

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
            if self.use_remote_api:
                return await self._remote_api_request(prompt, system_prompt)
            else:
                return await self._local_model_request(prompt, system_prompt)
        except Exception as e:
            raise Exception(f"Error generating response from LLM: {str(e)}")
    
    async def _local_model_request(self, prompt: str, system_prompt: str) -> str:
        """
        发送请求到本地模型
        """
        # 构建请求数据
        data = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        }
        
        # 发送请求到本地模型
        print("Sending request to local model...")
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
    
    async def _remote_api_request(self, prompt: str, system_prompt: str) -> str:
        """
        发送请求到远程API（如Magic API）
        """
        # 构建请求数据 - 使用正确的Magic API格式
        # 尝试在message中添加指令，提示API返回JSON格式
        message = f"""请以JSON格式回复。
系统提示: {system_prompt}

用户输入: {prompt}

请记住：你的回复必须是有效的JSON格式，不要有任何其他文本。"""

        data = {
            "message": message,
            "conversation_id": ""  # 如果需要持续对话，可以保存并重用会话ID
        }
        
        # 创建SSL上下文，禁用证书验证
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 发送请求到远程API
        print(f"Sending request to remote API: {self.api_base}")
        print(f"Request data: {json.dumps(data, ensure_ascii=False)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_base, 
                                   headers=self.headers, 
                                   json=data,
                                   ssl=ssl_context) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    raise Exception(f"API请求失败，状态码 {response.status}: {error_text}")
                
                result = await response.json()
                print(f"Response status: {result.get('code')}, message: {result.get('message')}")
                
                # 处理Magic API的响应格式
                if result.get('code') == 1000 and result.get('message') == 'ok' and result.get('data'):
                    data = result['data']
                    if 'messages' in data and len(data['messages']) > 0:
                        message = data['messages'][0].get('message', {})
                        content = message.get('content', '')
                        if content:
                            return content
                
                # 如果无法解析，返回整个响应
                return f"无法解析API响应: {json.dumps(result, ensure_ascii=False)}"

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