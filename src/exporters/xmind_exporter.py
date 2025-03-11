"""
XMind导出器模块
负责将测试用例导出为XMind思维导图格式，支持层级结构和主题组织
"""

from typing import List, Dict, Any
import json
import os
from src.core.test_generator import TestCase
from src.config import OUTPUT_DIR

class XMindExporter:
    """
    XMind导出器类
    将测试用例转换为结构化的思维导图格式
    """
    
    def export(self, test_cases: List[TestCase], output_filename: str) -> str:
        """
        将测试用例导出为XMind格式的JSON文件
        
        Args:
            test_cases (List[TestCase]): 待导出的测试用例列表
            output_filename (str): 输出文件名
            
        Returns:
            str: 导出文件的完整路径
        """
        # 创建思维导图结构
        mindmap = {
            "title": "Test Cases",
            "children": []
        }
        
        # 按模块分组测试用例
        module_dict = {}
        for test_case in test_cases:
            if test_case.module not in module_dict:
                module_dict[test_case.module] = []
            module_dict[test_case.module].append(test_case)
        
        # 创建模块节点
        for module_name, module_cases in module_dict.items():
            module_node = {
                "title": module_name,
                "children": []
            }
            
            # 添加该模块的所有测试用例
            for test_case in module_cases:
                # 创建测试用例节点
                case_node = {
                    "title": f"{test_case.id}: {test_case.title}",
                    "children": []
                }
                
                # 添加优先级信息
                info_node = {
                    "title": f"优先级: {test_case.priority}",
                    "children": []
                }
                case_node["children"].append(info_node)
                
                # 添加前置条件
                if test_case.preconditions:
                    precond_node = {
                        "title": "前置条件",
                        "children": [{"title": precond} for precond in test_case.preconditions]
                    }
                    case_node["children"].append(precond_node)
                
                # 添加测试步骤和预期结果
                steps_node = {
                    "title": "测试步骤",
                    "children": []
                }
                for step in test_case.steps:
                    step_node = {
                        "title": f"{step.step_number}. {step.description}",
                        "children": [{
                            "title": f"预期结果: {step.expected_result}"
                        }]
                    }
                    steps_node["children"].append(step_node)
                case_node["children"].append(steps_node)
                
                module_node["children"].append(case_node)
            
            mindmap["children"].append(module_node)
        
        # 确保输出文件名以.json结尾
        if not output_filename.endswith('.json'):
            output_filename = output_filename.replace('.xmind', '.json')
            if not output_filename.endswith('.json'):
                output_filename += '.json'
        
        # 创建输出路径
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 保存为JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)
        
        print(f"XMind file generated: {output_path}")
        return output_path 