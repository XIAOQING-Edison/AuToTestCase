"""
测试与远程API的连接
"""
import asyncio
import json
import ssl
import os
import aiohttp

# 硬编码有效的API密钥
API_KEY = "api-sk-67d140832e0cc3-45510241"
API_BASE = "https://i-magic-service.letsmagic.cn/api/chat"

async def test_api_connection():
    """测试与远程API的连接"""
    print("Testing API connection...")
    print(f"Using API: {API_BASE}")
    print(f"Using API Key: {API_KEY}")
    
    # 创建请求数据
    data = {
        "message": "你好，请简短回复。",
        "context": {
            "system_prompt": "你是一个有用的助手。"
        }
    }
    
    # 创建headers
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 创建SSL上下文，禁用证书验证
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        print("Sending request...")
        print(f"Request data: {json.dumps(data, ensure_ascii=False)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(API_BASE, 
                                  headers=headers, 
                                  json=data,
                                  ssl=ssl_context) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"\nAPI请求失败: {error_text}")
                    return
                
                result = await response.json()
                print(f"\n成功获取响应:")
                print("-" * 50)
                
                if result.get('code') == 1000 and result.get('message') == 'ok' and result.get('data'):
                    data = result['data']
                    if 'messages' in data and len(data['messages']) > 0:
                        message = data['messages'][0].get('message', {})
                        content = message.get('content', '')
                        print(content)
                    else:
                        print(f"无法从响应中提取内容: {json.dumps(result, ensure_ascii=False)}")
                else:
                    print(f"API响应错误: {json.dumps(result, ensure_ascii=False)}")
                
                print("-" * 50)
                print("\nAPI 连接测试成功!")
    except Exception as e:
        print(f"\nAPI 连接测试失败: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_api_connection()) 