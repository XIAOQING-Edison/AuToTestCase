"""
测试用例生成器模块
负责生成和管理测试用例，包括测试用例的数据模型定义和生成逻辑
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from src.core.llm_engine import LLMEngine
from src.config import DEFAULT_TEST_PRIORITY_LEVELS, PRIORITY_MAPPING, LEGACY_PRIORITY_MAPPING
import uuid
import json
import re
import datetime

class TestStep(BaseModel):
    """
    测试步骤数据模型
    定义单个测试步骤的结构
    """
    step_number: int      # 步骤编号
    description: str      # 步骤描述
    expected_result: str  # 预期结果

class TestCase(BaseModel):
    """
    测试用例数据模型
    定义完整测试用例的结构
    """
    id: str              # 测试用例唯一标识
    module: str          # 所属模块名称
    title: str           # 测试用例标题
    preconditions: List[str]  # 前置条件列表
    steps: List[TestStep]     # 测试步骤列表
    priority: str        # 优先级(高/中/低)

class TestGenerator:
    """
    测试用例生成器类
    负责基于需求生成完整的测试用例集
    """
    
    def __init__(self, llm_engine: LLMEngine):
        """
        初始化测试用例生成器
        
        Args:
            llm_engine (LLMEngine): LLM引擎实例，用于生成测试用例内容
        """
        self.llm_engine = llm_engine
        # 初始化计数器用于递增编号
        self.id_counter = 1
        # 设置日期前缀，用于测试用例ID
        self.date_prefix = datetime.datetime.now().strftime("%Y%m%d")

    def generate_test_id(self) -> str:
        """
        生成测试用例ID
        格式为：日期-递增编号(YYYYMMDD-XXX)
        
        Returns:
            str: 生成的测试用例ID
        """
        # 格式化计数器为3位数，如001, 002等
        formatted_counter = f"{self.id_counter:03d}"
        # 组合日期前缀和计数器
        test_id = f"{self.date_prefix}-{formatted_counter}"
        # 递增计数器
        self.id_counter += 1
        return test_id

    async def generate_test_cases(self, requirements: str) -> List[TestCase]:
        """
        基于需求生成测试用例
        
        Args:
            requirements (str): 需求文档文本
            
        Returns:
            List[TestCase]: 生成的测试用例列表
            
        Process:
            1. 首先分析需求文档
            2. 基于分析结果生成详细的测试用例
            3. 解析生成的内容为TestCase对象
        """
        # 重置ID计数器，确保每次生成测试用例时ID从1开始
        self.id_counter = 1
        # 更新日期前缀，以确保使用当前日期
        self.date_prefix = datetime.datetime.now().strftime("%Y%m%d")
        
        # 首先分析需求
        analysis = await self.llm_engine.analyze_requirements(requirements)
        
        # 生成测试用例的系统提示词
        system_prompt = self.get_system_prompt()
        
        # 获取测试用例生成结果
        test_cases_response = await self.llm_engine.generate_response(
            str(analysis),
            system_prompt
        )
        
        # 解析响应为TestCase对象列表
        test_cases = self._parse_test_cases(test_cases_response)
        return test_cases

    def get_system_prompt(self):
        return """警告：任何非JSON格式的输出都会导致系统崩溃！
你必须严格按照以下要求执行：

1. 你将只输出有效的JSON数据，不要输出任何非JSON内容
2. 你是一名专业测试工程师，根据需求来编写测试用例
3. 你需要思考各种测试场景，包括正常流程、边界条件、异常情况等
4. 每个测试用例应包含：标题、描述、优先级、测试步骤和预期结果
5. 支持的优先级有：高, 中, 低

你必须生成如下格式的JSON(不要有任何其他输出)：

```json
{
  "test_cases": [
    {
      "module": "登录模块",
      "title": "测试用例标题",
      "priority": "高",
      "preconditions": ["前置条件1", "前置条件2"],
      "steps": [
        {
          "step_number": 1,
          "description": "步骤描述",
          "expected_result": "预期结果"
        },
        {
          "step_number": 2,
          "description": "步骤描述",
          "expected_result": "预期结果"
        }
      ]
    }
  ]
}
```

请确保生成的JSON格式严格正确！不要有任何注释！
请生成多个测试用例，覆盖所有功能点和边界条件！
"""

    def _parse_test_cases(self, response: str) -> List[TestCase]:
        """
        将LLM响应解析为TestCase对象列表
        
        Args:
            response (str): LLM生成的响应文本
            
        Returns:
            List[TestCase]: 测试用例对象列表
        """
        try:
            print("Response content:")
            print(response)
            
            # 移除<think>...</think>标签及其内容
            response = re.sub(r'<think>[\s\S]*?</think>', '', response)
            
            # 查找JSON部分
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                # 从代码块中提取JSON
                json_str = json_match.group(1)
            else:
                # 尝试直接从响应中提取JSON
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    print("No JSON found in response")
                    return [self._create_sample_test_case()]
            
            # 清理JSON字符串
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # 移除尾随逗号
            
            print("\nTrying to parse JSON:")
            print(json_str)
            
            try:
                data = json.loads(json_str)
                
                if 'test_cases' in data:
                    test_cases = []
                    for tc in data['test_cases']:
                        print(f"\nProcessing test case: {tc.get('title', 'Untitled')}")
                        # 尝试提取必要的字段
                        module = tc.get('module', '')
                        title = tc.get('title', '')
                        
                        # 处理优先级，确保使用中文格式
                        priority = tc.get('priority', '中') 
                        # 如果是英文优先级，转换为中文
                        if priority.lower() in PRIORITY_MAPPING:
                            priority = PRIORITY_MAPPING[priority.lower()]
                        elif priority in LEGACY_PRIORITY_MAPPING:
                            priority = LEGACY_PRIORITY_MAPPING[priority]
                        
                        # 处理前置条件
                        preconditions = tc.get('preconditions', [])
                        if isinstance(preconditions, str):
                            preconditions = [preconditions]
                        
                        # 处理测试步骤
                        steps = []
                        tc_steps = tc.get('steps', [])
                        if isinstance(tc_steps, list):
                            for i, step in enumerate(tc_steps, 1):
                                if isinstance(step, dict):
                                    # 只处理必要的字段
                                    step_number = step.get('step_number', step.get('step', i))
                                    description = step.get('description', step.get('action', ''))
                                    expected_result = step.get('expected_result', '')
                                    
                                    # 确保字段值不为空
                                    if description and expected_result:
                                        steps.append(TestStep(
                                            step_number=step_number,
                                            description=description,
                                            expected_result=expected_result
                                        ))
                        
                        # 如果没有有效的步骤，创建一个默认步骤
                        if not steps:
                            steps = [TestStep(
                                step_number=1,
                                description="执行测试步骤",
                                expected_result="验证测试结果"
                            )]
                        
                        # 创建测试用例
                        test_case = TestCase(
                            id=self.generate_test_id(),  # 使用新的ID生成方法
                            module=module or '登录模块',
                            title=title or '未命名测试用例',
                            preconditions=preconditions or [],
                            steps=steps,
                            priority=priority  # 使用处理后的中文优先级
                        )
                        
                        print(f"\nCreated test case: {test_case.title}")
                        print(f"ID: {test_case.id}")  # 打印生成的ID
                        print(f"Module: {test_case.module}")
                        print(f"Priority: {test_case.priority}")
                        print(f"Steps count: {len(test_case.steps)}")
                        
                        # 验证测试用例
                        if self.validate_test_case(test_case):
                            test_cases.append(test_case)
                            print(f"Test case validated and added successfully")
                        else:
                            print(f"Test case validation failed")
                    
                    if test_cases:
                        print(f"\nTotal valid test cases: {len(test_cases)}")
                        return test_cases
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                print("JSON content:")
                print(json_str)
            
            # 如果解析失败或没有test_cases字段，返回样例测试用例
            print("No valid test cases found in response")
            return [self._create_sample_test_case()]
            
        except Exception as e:
            print(f"Error parsing test cases: {str(e)}")
            return [self._create_sample_test_case()]

    def _create_sample_test_case(self) -> TestCase:
        """
        创建一个示例测试用例
        
        Returns:
            TestCase: 示例测试用例对象
        """
        return TestCase(
            id=self.generate_test_id(),  # 使用新的ID生成方法
            module="登录模块",
            title="用户名密码登录-正常流程",
            preconditions=[
                "系统正常运行",
                "数据库连接正常",
                "用户未登录"
            ],
            steps=[
                TestStep(
                    step_number=1,
                    description='输入有效的用户名（长度6-20个字符）',
                    expected_result='用户名输入框显示输入的内容'
                ),
                TestStep(
                    step_number=2,
                    description='输入有效的密码（长度8-20个字符，包含字母和数字）',
                    expected_result='密码输入框显示掩码字符'
                ),
                TestStep(
                    step_number=3,
                    description='点击登录按钮',
                    expected_result='登录成功，跳转到首页'
                )
            ],
            priority="高"  # 使用中文优先级
        )

    def validate_test_case(self, test_case: TestCase) -> bool:
        """
        验证测试用例的有效性
        
        Args:
            test_case (TestCase): 待验证的测试用例
            
        Returns:
            bool: 测试用例是否有效
        """
        try:
            # 确保优先级有效，使用中文优先级
            if test_case.priority not in DEFAULT_TEST_PRIORITY_LEVELS:
                # 尝试转换英文优先级到中文
                if test_case.priority.lower() in PRIORITY_MAPPING:
                    test_case.priority = PRIORITY_MAPPING[test_case.priority.lower()]
                elif test_case.priority in LEGACY_PRIORITY_MAPPING:
                    test_case.priority = LEGACY_PRIORITY_MAPPING[test_case.priority]
                else:
                    test_case.priority = '中'  # 默认使用"中"优先级
            
            # 验证其他字段
            assert len(test_case.steps) > 0
            assert all(step.description and step.expected_result for step in test_case.steps)
            return True
        except AssertionError:
            return False 