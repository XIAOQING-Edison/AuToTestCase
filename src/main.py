"""
主程序
演示如何生成和导出测试用例
"""

import asyncio
import os
import sys

# 将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.llm_engine import LLMEngine
from core.test_generator import TestGenerator
from exporters.excel_exporter import ExcelExporter
from exporters.xmind_exporter import XMindExporter

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

async def main():
    """
    主程序函数
    展示完整的测试用例生成和导出流程
    """
    # 初始化所需组件
    llm_engine = LLMEngine()
    test_generator = TestGenerator(llm_engine)
    excel_exporter = ExcelExporter()
    xmind_exporter = XMindExporter()
    
    # 从文件读取需求文档
    requirements_file = os.path.join('docs', 'requirements.txt')
    try:
        requirements = read_requirements(requirements_file)
    except FileNotFoundError:
        # 如果文件不存在，使用默认的示例需求
        print(f"Warning: {requirements_file} 不存在，使用示例需求")
        requirements = """
        用户登录功能：
        1. 支持用户名密码登录
           - 用户名长度限制：6-20个字符
           - 密码长度限制：8-20个字符，必须包含字母和数字
        2. 支持手机验证码登录
           - 手机号必须是有效的中国大陆手机号
           - 验证码为6位数字，有效期5分钟
        3. 支持记住密码功能
           - 可以保存登录状态7天
           - 用户可以随时手动退出登录
        4. 安全要求：
           - 密码输入错误5次后，账号锁定30分钟
           - 支持图形验证码防护
        """
    
    try:
        # 生成测试用例
        print("Generating test cases...")
        test_cases = await test_generator.generate_test_cases(requirements)
        
        # 导出为Excel格式
        print("Exporting to Excel...")
        excel_path = excel_exporter.export(test_cases, "login_test_cases.xlsx")
        print(f"Excel file generated: {excel_path}")
        
        # 导出为XMind格式
        print("Exporting to XMind...")
        xmind_path = xmind_exporter.export(test_cases, "login_test_cases.xmind")
        print(f"XMind file generated: {xmind_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # 运行异步主程序
    asyncio.run(main()) 