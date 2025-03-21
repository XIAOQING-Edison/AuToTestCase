"""
测试连接到LetsMAGIC API
"""
import os
import json
import asyncio
from dotenv import load_dotenv
import aiohttp
import ssl

# 加载环境变量
load_dotenv()

# 获取配置 - 直接使用正确的API密钥
api_key = "api-sk-67d140832e0cc3-45510241"  # 从.env文件获取的密钥
api_base = os.getenv("API_BASE", "https://i-magic-service.letsmagic.cn/api/chat")

async def test_api():
    print(f"使用API: {api_base}")
    print(f"API密钥: {api_key}")
    
    # 创建请求数据
    # 基本请求数据 - 尝试使用message字段
    data = {
        "message": "你好，请简短回复。",
        "context": {
            "system_prompt": "你是一个有用的助手。"
        }
    }
    
    # 创建headers - 尝试不同的授权方式
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,  # 在头部使用api-key
        "Authorization": f"Bearer {api_key}"  # 标准授权头
    }
    
    # 创建SSL上下文，禁用证书验证
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # 发送请求
        print("发送请求...")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_base, 
                                headers=headers, 
                                json=data,
                                ssl=ssl_context) as response:
                print(f"响应状态: {response.status}")
                
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                
                if response.status == 200:
                    try:
                        response_json = json.loads(response_text)
                        print("\n请求成功!")
                        print(f"响应JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                    except json.JSONDecodeError:
                        print("响应不是有效的JSON格式")
                else:
                    print(f"请求失败，状态码: {response.status}")
    
    except Exception as e:
        print(f"请求出错: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_api())