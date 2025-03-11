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
import logging

# 配置日志记录
logger = logging.getLogger("TestGenerator")

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
        logger.info("初始化测试用例生成器")
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
            logger.info("开始解析测试用例响应")
            logger.debug(f"响应内容: {response[:200]}...")
            
            # 移除<think>...</think>标签及其内容
            response = re.sub(r'<think>[\s\S]*?</think>', '', response)
            
            # 查找JSON部分
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                # 从代码块中提取JSON
                json_str = json_match.group(1)
                logger.info("在代码块中找到JSON格式响应")
            else:
                # 尝试直接从响应中提取JSON
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info("在响应中直接找到JSON格式内容")
                else:
                    logger.error("无法从响应中提取JSON格式内容")
                    logger.debug(f"响应全文: {response}")
                    return [self._create_sample_test_case()]
            
            # 清理JSON字符串
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # 移除尾随逗号
            
            logger.debug(f"尝试解析JSON: {json_str[:200]}...")
            
            try:
                data = json.loads(json_str)
                logger.info("JSON解析成功")
                
                if 'test_cases' in data:
                    test_cases = []
                    logger.info(f"找到 {len(data['test_cases'])} 个测试用例")
                    
                    for tc in data['test_cases']:
                        logger.debug(f"处理测试用例: {tc.get('title', 'Untitled')}")
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
                        
                        logger.info(f"创建测试用例: {test_case.title}, ID: {test_case.id}, 步骤数: {len(test_case.steps)}")
                        test_cases.append(test_case)
                    
                    if test_cases:
                        logger.info(f"成功解析 {len(test_cases)} 个测试用例")
                        return test_cases
                    else:
                        logger.warning("没有解析出有效的测试用例，创建样例测试用例")
                        return [self._create_sample_test_case()]
                else:
                    logger.error("JSON中未找到test_cases字段")
                    return [self._create_sample_test_case()]
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                logger.debug(f"错误的JSON内容: {json_str}")
                return [self._create_sample_test_case()]
                
        except Exception as e:
            logger.error(f"解析测试用例时发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return [self._create_sample_test_case()]

    def _create_sample_test_case(self) -> TestCase:
        """
        创建一个样例测试用例，用于当解析失败时返回
        
        Returns:
            TestCase: 样例测试用例
        """
        logger.info("创建样例测试用例")
        return TestCase(
            id=self.generate_test_id(),
            module="示例模块",
            title="示例测试用例 (LLM响应解析失败)",
            preconditions=["系统正常运行", "用户已登录"],
            steps=[
                TestStep(
                    step_number=1,
                    description="执行操作1",
                    expected_result="预期结果1"
                ),
                TestStep(
                    step_number=2,
                    description="执行操作2",
                    expected_result="预期结果2"
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

    def generate(self, file_path: str) -> List[TestCase]:
        """
        从文件生成测试用例（同步版本，为了向后兼容）
        
        Args:
            file_path (str): 需求文档文件路径
            
        Returns:
            List[TestCase]: 生成的测试用例列表
        """
        import asyncio
        import os
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            with open(file_path, 'rb') as f:
                content_bytes = f.read()
                for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        content = content_bytes.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # 如果所有编码都失败，使用latin-1（它可以解码任何字节序列）
                    content = content_bytes.decode('latin-1')
        
        # 检查是否在事件循环中
        try:
            # 如果我们在FastAPI环境中，这个方法将被异步调用
            # 所以我们需要使用nest_asyncio来允许嵌套的事件循环
            import nest_asyncio
            nest_asyncio.apply()
            
            # 获取或创建事件循环
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # 如果当前线程没有事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # 使用事件循环运行异步方法
            if loop.is_running():
                # 创建一个Future用于在当前事件循环中获取结果
                future = asyncio.run_coroutine_threadsafe(self.generate_test_cases(content), loop)
                test_cases = future.result()
            else:
                # 如果事件循环不在运行，使用run_until_complete
                test_cases = loop.run_until_complete(self.generate_test_cases(content))
                
            return test_cases
            
        except ImportError:
            # 如果找不到nest_asyncio库，我们退回到创建一个新的事件循环
            logger.warning("找不到nest_asyncio库，创建新的事件循环")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            test_cases = loop.run_until_complete(self.generate_test_cases(content))
            return test_cases 