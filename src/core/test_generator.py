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

    async def generate_test_cases(self, requirements: str, requirement_type: str = None) -> List[TestCase]:
        """
        基于需求生成测试用例
        
        Args:
            requirements (str): 需求文档文本
            requirement_type (str, optional): 需求类型，用于选择适当的提示模板
            
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
        
        # 根据需求类型选择系统提示词
        system_prompt = self.get_system_prompt(requirement_type)
        
        # 获取测试用例生成结果
        test_cases_response = await self.llm_engine.generate_response(
            str(analysis),
            system_prompt
        )
        
        # 解析响应为TestCase对象列表
        test_cases = self._parse_test_cases(test_cases_response, requirement_type)
        return test_cases

    def get_system_prompt(self, requirement_type: str = None):
        """
        根据需求类型获取系统提示
        
        Args:
            requirement_type (str, optional): 需求类型，用于选择适当的提示模板
            
        Returns:
            str: 适合该需求类型的系统提示
        """
        # 通用提示部分
        common_prompt = """警告：任何非JSON格式的输出都会导致系统崩溃！
你必须严格按照以下要求执行：

1. 你将只输出有效的JSON数据，不要输出任何非JSON内容
2. 你是一名专业测试工程师，根据需求来编写测试用例
3. 你需要思考各种测试场景，包括正常流程、边界条件、异常情况等
4. 每个测试用例应包含：标题、描述、优先级、测试步骤和预期结果
5. 支持的优先级有：高, 中, 低
6. 必须生成至少50个测试用例，确保测试覆盖尽可能全面
7. 必须覆盖以下所有测试类型：
   - 功能测试：验证所有核心功能是否按照需求正常工作
   - 边界测试：测试边界值和极限条件
   - 异常测试：验证系统对异常输入和环境的处理能力
   - 性能测试：验证系统性能指标
   - 安全测试：验证系统安全性能
   - 用户体验测试：验证系统的易用性
   - 集成测试：验证不同组件之间的交互"""

        # 根据需求类型选择特定提示
        type_specific_prompts = {
            "login": """
8. 对于登录功能，必须创建覆盖以下场景的测试用例：
   - 正常登录流程（各种登录方式）
   - 输入验证和错误处理
   - 会话管理和记住密码功能
   - 安全相关测试（密码策略、账户锁定、防暴力破解）
   - 性能和可靠性测试
9. 每个测试用例的测试步骤必须详细、具体，并关注用户交互和系统响应""",

            "register": """
8. 对于注册功能，必须创建覆盖以下场景的测试用例：
   - 正常注册流程
   - 各字段输入验证（格式、长度、唯一性）
   - 注册成功/失败的各种情况
   - 隐私政策和用户协议确认
   - 安全相关测试（密码强度、防机器人注册）
9. 每个测试用例的测试步骤必须详细、具体，关注用户体验和数据验证""",

            "task_management": """
8. 对于任务管理功能，必须创建覆盖以下场景的测试用例：
   - 任务创建的各种场景（正常、异常、边界）
   - 任务下发的各种情况（不同类型的任务、不同角色）
   - 任务审核的各种场景（多人审核、单人审核、审核超时等）
   - 任务执行和反馈的各种情况
   - 任务模板管理的全面测试
   - 任务撤销和复盘的不同情况
   - 任务状态流转和流程控制
   - 任务权限管理的各种情况
   - 各种异常情况的处理
   - 任务相关的安全测试
   - 任务管理的性能测试
   - 任务管理的用户体验测试
9. 确保每个主要功能点至少有4-5个测试用例，涵盖正常、边界、异常和权限等各种情况
10. 每个测试用例的测试步骤必须详细、具体，至少包含2-3个步骤
11. 必须生成至少60个测试用例，确保全面覆盖任务管理的各个方面""",

            "authorization": """
8. 对于授权码功能，必须创建覆盖以下场景的测试用例：
   - 授权码生成的各种场景（正常、异常、边界条件）
   - 授权码验证的各种情况（有效、无效、过期等）
   - 授权码权限控制的测试（不同级别权限的授权验证）
   - 授权流程的各种情况（授权成功、失败、超时等）
   - 授权日志记录的完整性和正确性
   - 授权码安全机制的测试（防复制、防重放、加密安全等）
   - 不同操作场景下的授权码使用测试
   - 敏感操作权限控制的测试
   - 授权码管理的各种功能测试
   - 系统性能在大量授权操作下的表现
   - 用户体验和操作便捷性的测试
9. 确保每个主要功能点至少有4-5个测试用例，涵盖正常、边界、异常和权限等各种情况
10. 每个测试用例的测试步骤必须详细、具体，至少包含2-3个步骤
11. 必须生成至少60个测试用例，确保全面覆盖授权码功能的各个方面""",

            "api": """
8. 对于API接口测试，必须创建覆盖以下场景的测试用例：
   - 正常请求和响应验证
   - 参数验证（必填项、格式、范围）
   - 授权和认证测试
   - 错误处理和异常情况
   - 性能和负载测试（并发、响应时间）
   - 安全相关测试（注入攻击、跨站脚本等）
9. 每个测试用例的测试步骤必须详细描述请求参数、请求方法、预期响应状态码和响应内容""",

            "performance": """
8. 对于性能测试，必须创建覆盖以下场景的测试用例：
   - 负载测试（逐步增加用户量）
   - 压力测试（系统最大承载能力）
   - 耐久性测试（长时间运行）
   - 并发测试（多用户同时操作）
   - 资源使用测试（CPU、内存、磁盘IO、网络）
   - 响应时间测试（不同负载下的响应时间）
9. 每个测试用例必须详细描述测试环境、测试工具、测试参数和判断标准""",

            "security": """
8. 对于安全测试，必须创建覆盖以下场景的测试用例：
   - 认证和授权测试
   - 会话管理测试
   - 输入验证和数据保护
   - 密码策略和存储安全
   - 敏感数据处理和传输
   - 常见漏洞测试（SQL注入、XSS、CSRF等）
   - 访问控制和权限边界测试
9. 每个测试用例必须详细描述测试方法、测试工具和漏洞验证标准"""
        }

        # 输出JSON格式示例部分
        json_format = """
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
必须生成全面详尽的测试用例，覆盖所有功能点和边界条件！
"""

        # 如果提供了需求类型并且该类型有特定提示，使用该特定提示，否则使用默认提示
        if requirement_type and requirement_type in type_specific_prompts:
            return common_prompt + type_specific_prompts[requirement_type] + json_format
        else:
            # 默认提示，用于任何未指定类型的需求
            default_specific = """
8. 对于每个功能点，必须创建多个测试用例，包括：
   - 功能正常工作的场景
   - 功能的边界条件
   - 功能的异常处理
   - 权限控制和安全方面
   - 性能和并发方面
   - 用户体验和可访问性方面
   - 与其他功能的集成方面
9. 确保每个功能点至少有4-5个测试用例，覆盖不同的测试场景
10. 每个测试用例的测试步骤必须详细、具体，至少包含2-3个步骤
11. 必须生成至少60个测试用例，确保全面覆盖需求的各个方面"""
            return common_prompt + default_specific + json_format

    def _parse_test_cases(self, response: str, requirement_type: str = None) -> List[TestCase]:
        """
        将LLM响应解析为TestCase对象列表
        
        Args:
            response (str): LLM生成的响应文本
            requirement_type (str, optional): 需求类型，可用于特定的解析逻辑
            
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
                    return [self._create_sample_test_case(requirement_type)]
            
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
                            module=module or '通用模块',
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
            return [self._create_sample_test_case(requirement_type)]
            
        except Exception as e:
            print(f"Error parsing test cases: {str(e)}")
            return [self._create_sample_test_case(requirement_type)]

    def _create_sample_test_case(self, requirement_type: str = None) -> TestCase:
        """
        创建一个示例测试用例
        
        Args:
            requirement_type (str, optional): 需求类型，用于创建相应的示例测试用例
            
        Returns:
            TestCase: 示例测试用例对象
        """
        # 根据需求类型选择不同的示例测试用例
        if requirement_type == "login":
            return TestCase(
                id=self.generate_test_id(),
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
                priority="高"
            )
        elif requirement_type == "register":
            return TestCase(
                id=self.generate_test_id(),
                module="注册模块",
                title="新用户注册-正常流程",
                preconditions=[
                    "系统正常运行",
                    "数据库连接正常",
                    "用户未注册"
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        description='输入有效的用户名（未被注册）',
                        expected_result='用户名输入框显示输入的内容'
                    ),
                    TestStep(
                        step_number=2,
                        description='输入有效的密码和确认密码',
                        expected_result='密码输入框显示掩码字符'
                    ),
                    TestStep(
                        step_number=3,
                        description='输入有效的邮箱地址',
                        expected_result='邮箱输入框显示输入的内容'
                    ),
                    TestStep(
                        step_number=4,
                        description='点击注册按钮',
                        expected_result='注册成功，发送验证邮件并提示用户查收'
                    )
                ],
                priority="高"
            )
        elif requirement_type == "task_management":
            return TestCase(
                id=self.generate_test_id(),
                module="任务管理模块",
                title="创建新任务-正常流程",
                preconditions=[
                    "用户已登录",
                    "用户具有创建任务的权限"
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        description='点击"新建任务"按钮',
                        expected_result='显示任务创建表单'
                    ),
                    TestStep(
                        step_number=2,
                        description='输入任务标题、描述和截止日期',
                        expected_result='表单字段显示输入的内容'
                    ),
                    TestStep(
                        step_number=3,
                        description='选择任务负责人',
                        expected_result='负责人选择列表显示选定的用户'
                    ),
                    TestStep(
                        step_number=4,
                        description='点击"保存"按钮',
                        expected_result='任务创建成功，显示在任务列表中'
                    )
                ],
                priority="高"
            )
        elif requirement_type == "api":
            return TestCase(
                id=self.generate_test_id(),
                module="API接口模块",
                title="获取用户信息接口-正常流程",
                preconditions=[
                    "API服务正常运行",
                    "用户已认证",
                    "用户令牌有效"
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        description='准备请求参数和认证信息',
                        expected_result='参数和认证信息准备完毕'
                    ),
                    TestStep(
                        step_number=2,
                        description='发送GET请求到/api/users/me接口',
                        expected_result='接收到HTTP 200响应'
                    ),
                    TestStep(
                        step_number=3,
                        description='验证响应数据格式和内容',
                        expected_result='响应包含用户ID、用户名和邮箱等必要字段'
                    )
                ],
                priority="高"
            )
        else:
            # 默认示例测试用例
            return TestCase(
                id=self.generate_test_id(),
                module="通用模块",
                title="基本功能测试-正常流程",
                preconditions=[
                    "系统正常运行",
                    "用户具有必要权限"
                ],
                steps=[
                    TestStep(
                        step_number=1,
                        description='准备测试数据和环境',
                        expected_result='测试环境准备完毕'
                    ),
                    TestStep(
                        step_number=2,
                        description='执行被测功能的主要操作',
                        expected_result='系统正确响应操作'
                    ),
                    TestStep(
                        step_number=3,
                        description='验证操作结果',
                        expected_result='结果符合预期要求'
                    )
                ],
                priority="中"
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

    async def generate(self, requirements: str) -> list:
        """
        生成测试用例
        
        Args:
            requirements (str): 需求文档文本
            
        Returns:
            list: 测试用例列表
        """
        try:
            # 使用LLM分析需求，提取测试点
            print("Generating test cases...")
            analysis = await self.llm_engine.analyze_requirements(requirements)
            
            # 尝试生成测试用例JSON
            try:
                json_response = await self.llm_engine.generate_response(
                    requirements, 
                    self.get_system_prompt()
                )
                
                print("Response content:")
                print(json_response)
                
                # 解析返回的JSON
                print("Trying to parse JSON:")
                print(json_response)
                
                try:
                    # 尝试解析JSON
                    if json_response.startswith('{'):
                        json_data = json.loads(json_response)
                        if "test_cases" in json_data and len(json_data["test_cases"]) > 0:
                            print(f"成功生成测试用例: {len(json_data['test_cases'])}个")
                            return json_data["test_cases"]
                    
                    print("生成的JSON无效或不包含测试用例，使用备选方案...")
                
                except json.JSONDecodeError:
                    print("Failed to parse JSON response, using fallback...")
            
            except Exception as e:
                print(f"生成测试用例时出错: {str(e)}")
            
            # 如果上面的尝试都失败了，生成示例测试用例
            return self._generate_example_test_cases(requirements)
                
        except Exception as e:
            print(f"Error generating test cases: {str(e)}")
            # 出错时，也返回示例测试用例
            return self._generate_example_test_cases(requirements)
    
    def _generate_example_test_cases(self, requirements: str) -> list:
        """
        生成示例测试用例 (当API请求失败时使用)
        """
        print("生成示例测试用例...")
        
        # 提取需求标题作为模块名
        lines = requirements.strip().split('\n')
        module_name = "登录模块" if "登录" in requirements else "未知模块"
        for line in lines:
            if line.startswith('#'):
                module_name = line.replace('#', '').strip()
                break
        
        # 创建三个示例测试用例
        test_cases = [
            {
                "module": module_name,
                "title": "验证正确的用户名和密码登录",
                "priority": "高",
                "preconditions": ["用户已注册", "用户账户处于正常状态"],
                "steps": [
                    {
                        "step_number": 1,
                        "description": "打开登录页面",
                        "expected_result": "成功显示登录页面，包含用户名、密码输入框和登录按钮"
                    },
                    {
                        "step_number": 2,
                        "description": "输入正确的用户名",
                        "expected_result": "用户名输入框显示输入的用户名"
                    },
                    {
                        "step_number": 3,
                        "description": "输入正确的密码",
                        "expected_result": "密码输入框显示掩码密码"
                    },
                    {
                        "step_number": 4,
                        "description": "点击登录按钮",
                        "expected_result": "登录成功，跳转到系统主页"
                    }
                ]
            },
            {
                "module": module_name,
                "title": "验证错误的密码登录失败",
                "priority": "高",
                "preconditions": ["用户已注册", "用户账户处于正常状态"],
                "steps": [
                    {
                        "step_number": 1,
                        "description": "打开登录页面",
                        "expected_result": "成功显示登录页面"
                    },
                    {
                        "step_number": 2,
                        "description": "输入正确的用户名",
                        "expected_result": "用户名输入框显示输入的用户名"
                    },
                    {
                        "step_number": 3,
                        "description": "输入错误的密码",
                        "expected_result": "密码输入框显示掩码密码"
                    },
                    {
                        "step_number": 4,
                        "description": "点击登录按钮",
                        "expected_result": "登录失败，显示密码错误提示"
                    }
                ]
            },
            {
                "module": module_name,
                "title": "验证账户被锁定后无法登录",
                "priority": "中",
                "preconditions": ["用户已注册", "用户连续5次输入错误密码，账户被锁定"],
                "steps": [
                    {
                        "step_number": 1,
                        "description": "打开登录页面",
                        "expected_result": "成功显示登录页面"
                    },
                    {
                        "step_number": 2,
                        "description": "输入被锁定账户的用户名",
                        "expected_result": "用户名输入框显示输入的用户名"
                    },
                    {
                        "step_number": 3,
                        "description": "输入正确的密码",
                        "expected_result": "密码输入框显示掩码密码"
                    },
                    {
                        "step_number": 4,
                        "description": "点击登录按钮",
                        "expected_result": "登录失败，显示账户锁定提示，包含剩余锁定时间"
                    }
                ]
            }
        ]
        
        return test_cases 