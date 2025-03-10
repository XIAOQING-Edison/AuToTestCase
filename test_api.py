import openai
import os
import asyncio
from dotenv import load_dotenv
import traceback
import ssl
import certifi
import aiohttp

# 加载环境变量
load_dotenv()

# 获取API密钥
api_key = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY"))
api_base = "https://api.deepseek.com/v1/chat"

# 配置OpenAI客户端
openai.api_key = api_key
openai.api_base = api_base

async def test_api():
    try:
        # 设置代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
        
        print("环境变量:")
        print(f"HTTP_PROXY: {os.getenv('HTTP_PROXY')}")
        print(f"HTTPS_PROXY: {os.getenv('HTTPS_PROXY')}")
        
        print("\n正在测试API连接...")
        print(f"API Key长度: {len(api_key)}")
        print(f"API Key前10个字符: {api_key[:10]}...")
        print(f"API Base: {api_base}\n")

        # 创建SSL上下文
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # 创建自定义的aiohttp会话
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn) as session:
            openai.aiosession.set(session)
            
            # 创建测试消息
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello"}
            ]

            # 发送API请求
            print("发送API请求...")
            response = await openai.ChatCompletion.acreate(
                model="deepseek-chat-1.1t-32k",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            print("\nAPI响应:")
            print(response)
            print("\nAPI测试成功!")
        
    except Exception as e:
        print("\nAPI测试失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print("\n详细错误信息:")
        print(traceback.format_exc())
        
        print("\n当前环境变量:")
        for key, value in os.environ.items():
            # 隐藏敏感信息
            if 'key' in key.lower() or 'secret' in key.lower() or 'password' in key.lower():
                print(f"{key}: {'*' * len(value)}")
            else:
                print(f"{key}: {value}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_api()) 