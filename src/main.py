"""
主程序入口
演示如何使用测试用例生成器生成并导出测试用例
"""

import asyncio
import os
import argparse
from src.core.llm_engine import LLMEngine
from src.core.test_generator import TestGenerator
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.xmind_exporter import XMindExporter
from src.crawlers.web_crawler import WebCrawler
from src.config import CRAWLER_CONFIG, OUTPUT_DIR

def read_requirements(file_path: str) -> str:
    """
    从文件中读取需求文档
    
    Args:
        file_path (str): 需求文档的路径
        
    Returns:
        str: 需求文档的内容
        
    Raises:
        FileNotFoundError: 当文件不存在时抛出
        Exception: 当读取文件失败时抛出
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"需求文档 {file_path} 不存在")
    except Exception as e:
        raise Exception(f"读取需求文档失败: {str(e)}")

async def fetch_requirements_from_url(url: str, crawler_config=None) -> str:
    """
    从URL爬取需求文档
    
    Args:
        url (str): 需求文档的URL
        crawler_config (dict, optional): 爬虫配置
        
    Returns:
        str: 爬取的需求文档内容
        
    Raises:
        Exception: 当爬取失败时抛出
    """
    try:
        # 使用默认配置如果没有提供
        config = crawler_config or CRAWLER_CONFIG
        
        # 创建爬虫并获取内容
        crawler = WebCrawler(config)
        content = await crawler.extract_requirements(url)
        
        if not content:
            raise Exception("未能从URL获取有效内容")
            
        print(f"成功从URL获取内容，长度: {len(content)}")
        return content
    except Exception as e:
        raise Exception(f"从URL获取需求失败: {str(e)}")

async def process_requirements(requirements: str, output_excel="test_cases.xlsx", 
                              output_xmind="test_cases.xmind", verbose=False):
    """
    处理需求文档，生成并导出测试用例
    
    Args:
        requirements (str): 需求文档内容
        output_excel (str): Excel输出文件名
        output_xmind (str): XMind输出文件名
        verbose (bool): 是否显示详细输出
        
    Returns:
        tuple: 生成的Excel和XMind文件路径
    """
    # 初始化所需组件
    llm_engine = LLMEngine()
    test_generator = TestGenerator(llm_engine)
    excel_exporter = ExcelExporter()
    xmind_exporter = XMindExporter()
    
    try:
        # 生成测试用例
        if verbose:
            print("正在生成测试用例...")
        test_cases = await test_generator.generate_test_cases(requirements)
        
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 导出为Excel格式
        if verbose:
            print("导出为Excel格式...")
        excel_path = excel_exporter.export(test_cases, output_excel)
        if verbose:
            print(f"Excel文件已生成: {excel_path}")
        
        # 导出为XMind格式
        if verbose:
            print("导出为XMind格式...")
        xmind_path = xmind_exporter.export(test_cases, output_xmind)
        if verbose:
            print(f"XMind文件已生成: {xmind_path}")
        
        return excel_path, xmind_path
        
    except Exception as e:
        raise Exception(f"处理需求时出错: {str(e)}")

async def main():
    """
    主程序函数
    支持从文件或URL获取需求，并生成测试用例
    """
    parser = argparse.ArgumentParser(description='自动测试用例生成工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='需求文档文件路径')
    group.add_argument('--url', '-u', help='需求文档URL')
    parser.add_argument('--excel', '-e', default='test_cases.xlsx', help='Excel输出文件名')
    parser.add_argument('--xmind', '-x', default='test_cases.xmind', help='XMind输出文件名')
    parser.add_argument('--selector', '-s', help='网页内容选择器 (CSS选择器)')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    
    args = parser.parse_args()
    
    try:
        if args.file:
            # 从文件读取需求
            if args.verbose:
                print(f"从文件读取需求: {args.file}")
            requirements = read_requirements(args.file)
        else:
            # 从URL获取需求
            if args.verbose:
                print(f"从URL获取需求: {args.url}")
            
            # 如果提供了选择器，更新爬虫配置
            config = CRAWLER_CONFIG.copy()
            if args.selector:
                config['content_selector'] = args.selector
                
            requirements = await fetch_requirements_from_url(args.url, config)
        
        # 处理需求
        excel_path, xmind_path = await process_requirements(
            requirements, 
            output_excel=args.excel,
            output_xmind=args.xmind,
            verbose=args.verbose
        )
        
        print(f"处理完成! 生成了 {excel_path} 和 {xmind_path}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    # 运行异步主程序
    asyncio.run(main()) 