"""
爬虫测试工具
用于测试网页爬虫的功能
"""

import argparse
import asyncio
import json
import os
import sys
import ssl

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crawlers.web_crawler import WebCrawler


async def test_crawler(url, config_file=None, output_file=None, content_selector=None, no_verify_ssl=False):
    """
    测试爬虫功能
    
    Args:
        url (str): 要爬取的URL
        config_file (str, optional): 配置文件路径
        output_file (str, optional): 输出文件路径
        content_selector (str, optional): 内容选择器
        no_verify_ssl (bool, optional): 是否禁用SSL验证
    """
    # 加载配置
    config = {}
    if config_file:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    # 如果提供了内容选择器，覆盖配置
    if content_selector:
        config['content_selector'] = content_selector
    
    # 如果设置了不验证SSL
    if no_verify_ssl:
        # 禁用SSL验证警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # 修改aiohttp会话配置
        config['verify_ssl'] = False
    
    # 创建爬虫
    crawler = WebCrawler(config)
    
    # 执行爬取
    print(f"开始爬取 {url}")
    content = await crawler.extract_requirements(url)
    
    # 输出结果
    if not content:
        print("未能提取到内容")
        return
    
    print(f"成功提取内容，长度: {len(content)}")
    
    # 预览内容
    preview_length = min(500, len(content))
    print(f"\n内容预览 (前{preview_length}字符):")
    print("-" * 50)
    print(content[:preview_length] + ("..." if len(content) > preview_length else ""))
    print("-" * 50)
    
    # 保存到文件
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"内容已保存到: {output_file}")
        except Exception as e:
            print(f"保存内容到文件失败: {str(e)}")


async def main():
    parser = argparse.ArgumentParser(description='测试爬虫功能')
    parser.add_argument('url', help='要爬取的URL')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--selector', '-s', help='内容选择器 (CSS选择器)')
    parser.add_argument('--no-verify-ssl', action='store_true', help='禁用SSL证书验证')
    
    args = parser.parse_args()
    
    await test_crawler(
        args.url,
        config_file=args.config,
        output_file=args.output,
        content_selector=args.selector,
        no_verify_ssl=args.no_verify_ssl
    )


if __name__ == "__main__":
    asyncio.run(main()) 