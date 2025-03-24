"""
主程序
演示如何生成和导出测试用例
"""

import asyncio
import os
import sys
import re

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

def detect_requirement_type(requirements: str) -> str:
    """
    根据需求文档内容检测需求类型
    
    Args:
        requirements (str): 需求文档内容
        
    Returns:
        str: 检测到的需求类型，用于文件命名
    """
    # 将需求文本转为小写以便不区分大小写匹配
    req_lower = requirements.lower()
    
    # 定义需求类型关键词映射
    type_keywords = {
        "login": ["登录", "login", "认证", "authentication", "用户名", "密码"],
        "register": ["注册", "register", "sign up", "用户注册"],
        "user_management": ["用户管理", "user management", "user profile", "用户信息"],
        "task_management": ["任务管理", "task management", "任务列表", "任务创建", "task list"],
        "dashboard": ["仪表盘", "dashboard", "数据统计", "报表"],
        "report": ["报告", "report", "reporting", "数据报表"],
        "api": ["api", "接口", "interface", "服务调用"],
        "module": ["模块", "module", "组件"],
        "system": ["系统", "system", "平台"],
        "performance": ["性能", "performance", "负载", "load"],
        "security": ["安全", "security", "权限", "permission"],
        "authorization": ["授权", "authorization", "授权码", "authorization code", "密码授权", "账号授权", "敏感操作"]
    }
    
    # 搜索所有可能的需求类型，并计算匹配度
    type_scores = {}
    for req_type, keywords in type_keywords.items():
        score = sum(req_lower.count(keyword) for keyword in keywords)
        if score > 0:
            type_scores[req_type] = score
    
    # 查找匹配度最高的需求类型
    if type_scores:
        best_type = max(type_scores.items(), key=lambda x: x[1])[0]
        return best_type
    
    # 如果没有匹配，则尝试从文本中提取可能的模块名称
    # 查找常见的标题格式如"xxx模块"、"xxx功能"等
    module_match = re.search(r'([^\s:：]+)[模块功能系统][:：]?', requirements)
    if module_match:
        return module_match.group(1)
    
    # 如果都没有找到，则返回默认值
    return "requirement"

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
        # 检测需求类型
        requirement_type = detect_requirement_type(requirements)
        print(f"Detected requirement type: {requirement_type}")
        
        # 添加调试输出
        print("Requirement type scores:")
        req_lower = requirements.lower()
        type_keywords = {
            "login": ["登录", "login", "认证", "authentication", "用户名", "密码"],
            "register": ["注册", "register", "sign up", "用户注册"],
            "user_management": ["用户管理", "user management", "user profile", "用户信息"],
            "task_management": ["任务管理", "task management", "任务列表", "任务创建", "task list"],
            "dashboard": ["仪表盘", "dashboard", "数据统计", "报表"],
            "report": ["报告", "report", "reporting", "数据报表"],
            "api": ["api", "接口", "interface", "服务调用"],
            "module": ["模块", "module", "组件"],
            "system": ["系统", "system", "平台"],
            "performance": ["性能", "performance", "负载", "load"],
            "security": ["安全", "security", "权限", "permission"],
            "authorization": ["授权", "authorization", "授权码", "authorization code", "密码授权", "账号授权", "敏感操作"]
        }
        for req_type, keywords in type_keywords.items():
            score = sum(req_lower.count(keyword) for keyword in keywords)
            if score > 0:
                print(f"{req_type}: {score}")
        
        # 根据需求类型生成文件名，确保使用正确的类型
        file_base_name = f"{requirement_type}_test_cases"
        
        # 生成测试用例
        print("Generating test cases...")
        test_cases = await test_generator.generate_test_cases(requirements, requirement_type)
        
        # 导出为Excel格式
        print("Exporting to Excel...")
        excel_path = excel_exporter.export(test_cases, f"{file_base_name}.xlsx")
        print(f"Excel file generated: {excel_path}")
        
        # 导出为XMind格式
        print("Exporting to XMind...")
        xmind_path = xmind_exporter.export(test_cases, f"{file_base_name}.json")
        print(f"XMind file generated: {xmind_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # 运行异步主程序
    asyncio.run(main()) 