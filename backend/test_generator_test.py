#!/usr/bin/env python
"""
测试脚本，用于测试TestGenerator的基本功能
"""

import os
import sys
import asyncio
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_generator_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TestScript")

from src.core.test_generator import TestGenerator
from src.core.llm_engine import LLMEngine
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.xmind_exporter import XMindExporter

async def test_generate_test_cases():
    """
    测试生成测试用例的功能
    """
    try:
        logger.info("开始测试TestGenerator")
        
        # 创建LLM引擎
        logger.info("初始化LLM引擎")
        llm_engine = LLMEngine()
        
        # 创建测试用例生成器
        logger.info("初始化TestGenerator")
        generator = TestGenerator(llm_engine)
        
        # 准备一个简单的需求文本
        requirement = """
        # 登录功能需求
        
        ## 功能描述
        
        系统需要提供用户登录功能，允许用户通过用户名和密码登录系统。
        
        ## 详细需求
        
        1. 用户可以通过输入用户名和密码登录系统
        2. 用户名长度应在6-20个字符之间
        3. 密码长度应在8-20个字符之间，且应包含字母和数字
        4. 如果用户名或密码不正确，应显示相应的错误消息
        5. 用户可以选择"记住我"选项，有效期为7天
        6. 连续5次登录失败后，账户将被锁定30分钟
        7. 用户可以通过"忘记密码"链接重置密码
        """
        
        # 生成测试用例
        logger.info("开始生成测试用例")
        test_cases = await generator.generate_test_cases(requirement)
        
        # 输出生成的测试用例数量
        logger.info(f"生成了 {len(test_cases)} 个测试用例")
        
        # 导出测试用例
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "test")
        os.makedirs(output_dir, exist_ok=True)
        
        # 导出为Excel
        logger.info("导出为Excel")
        excel_exporter = ExcelExporter()
        excel_path = os.path.join(output_dir, "test_cases.xlsx")
        excel_exporter.export(test_cases, excel_path)
        logger.info(f"Excel文件已导出到: {excel_path}")
        
        # 导出为XMind
        logger.info("导出为XMind")
        xmind_exporter = XMindExporter()
        xmind_path = os.path.join(output_dir, "test_cases.xmind")
        xmind_exporter.export(test_cases, xmind_path)
        logger.info(f"XMind文件已导出到: {xmind_path}")
        
        return True
    except Exception as e:
        logger.error(f"测试中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("开始运行测试脚本")
    
    # 运行测试
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_generate_test_cases())
    
    if success:
        logger.info("测试成功完成")
        print("测试成功！")
    else:
        logger.error("测试失败")
        print("测试失败！") 