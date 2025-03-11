"""
爬虫测试工具
用于测试网页爬虫的功能
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import ssl

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.crawlers.web_crawler import WebCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_crawler(url, config_file=None, output_file=None, content_selector=None, 
                       no_verify_ssl=False, use_selenium=True):
    """
    测试爬虫功能
    
    Args:
        url: 要爬取的URL
        config_file: 配置文件路径
        output_file: 输出文件路径
        content_selector: 内容选择器 (CSS选择器)
        no_verify_ssl: 是否禁用SSL验证
        use_selenium: 是否使用Selenium处理JavaScript
    """
    # 加载配置
    config = {}
    if config_file:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return
    
    # 如果命令行提供了选择器，覆盖配置文件中的选择器
    if content_selector:
        config['content_selector'] = content_selector
    
    # 设置use_selenium标志
    config['use_selenium'] = use_selenium
        
    # 初始化爬虫
    crawler = WebCrawler(config)
    
    try:
        print(f"开始爬取 {url}")
        content = await crawler.extract_requirements(url, no_verify_ssl=no_verify_ssl, use_selenium=use_selenium)
        
        print(f"成功提取内容，长度: {len(content)}")
        
        # 显示内容预览
        preview_length = min(100, len(content))
        print("\n内容预览 (前{}字符):".format(preview_length))
        print("-" * 50)
        print(content[:preview_length])
        print("-" * 50)
        
        # 保存到文件
        if output_file:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"内容已保存到: {output_file}")
            
    except Exception as e:
        logging.error(f"爬取失败: {e}")
        raise
    finally:
        await crawler.close()

async def login(page, username, password):
    """执行登录过程"""
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"]')
    # 等待登录完成
    await page.wait_for_navigation()

async def main():
    parser = argparse.ArgumentParser(description='测试爬虫功能')
    parser.add_argument('url', help='要爬取的URL')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--selector', '-s', help='内容选择器 (CSS选择器)')
    parser.add_argument('--no-verify-ssl', action='store_true', help='禁用SSL证书验证')
    parser.add_argument('--no-selenium', action='store_true', help='禁用Selenium (不处理JavaScript)')
    
    args = parser.parse_args()
    
    await test_crawler(
        args.url,
        config_file=args.config,
        output_file=args.output,
        content_selector=args.selector,
        no_verify_ssl=args.no_verify_ssl,
        use_selenium=not args.no_selenium
    )


if __name__ == "__main__":
    asyncio.run(main()) 