# AuToTestCase 贡献指南

非常感谢您有兴趣为AuToTestCase项目做出贡献！本文档将帮助您了解如何参与开发和贡献代码。

## 目录

1. [开发环境设置](#开发环境设置)
2. [代码风格指南](#代码风格指南)
3. [提交拉取请求](#提交拉取请求)
4. [报告问题](#报告问题)
5. [功能请求](#功能请求)
6. [项目结构](#项目结构)
7. [测试指南](#测试指南)

## 开发环境设置

1. 克隆仓库并创建一个新分支：

```bash
git clone https://github.com/yourusername/AuToTestCase.git
cd AuToTestCase
git checkout -b feature/your-feature-name
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

3. 安装开发依赖：

```bash
pip install -r requirements-dev.txt  # 如果存在的话，否则使用requirements.txt
```

4. 安装pre-commit钩子（如果使用）：

```bash
pre-commit install
```

## 代码风格指南

我们遵循PEP 8代码风格指南，并使用以下工具确保代码质量：

- **Black**：用于代码格式化
- **isort**：用于导入排序
- **flake8**：用于代码检查

请确保您的代码通过这些工具的检查：

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 运行代码检查
flake8 src/ tests/
```

## 提交拉取请求

1. 确保您的代码符合代码风格指南
2. 更新或添加适当的测试用例
3. 确保所有测试都通过
4. 更新文档（如有必要）
5. 提交一个描述性的拉取请求，说明您的更改及其目的

拉取请求模板：

```
## 描述
简要描述您的更改

## 相关问题
修复 #(问题编号)

## 更改类型
- [ ] 错误修复
- [ ] 新功能
- [ ] 性能改进
- [ ] 代码风格更新
- [ ] 文档更新
- [ ] 其他（请说明）

## 测试
- [ ] 添加/更新了单元测试
- [ ] 进行了手动测试

## 截图（如适用）

## 检查表
- [ ] 我的代码遵循项目的代码风格
- [ ] 我已更新文档
- [ ] 我的更改不会导致新的警告或错误
- [ ] 我已测试我的代码
```

## 报告问题

如果您遇到了问题或发现了bug，请使用GitHub的Issues功能创建一个新issue，并包含以下信息：

1. 问题的详细描述
2. 重现步骤
3. 预期行为与实际行为
4. 系统环境信息（操作系统、Python版本等）
5. 相关日志或截图

## 功能请求

如果您有新功能的想法，请创建一个issue并标记为"feature request"，包含以下信息：

1. 功能描述
2. 为什么这个功能对项目有用
3. 如何实现的初步想法（如果有）

## 项目结构

了解项目结构将帮助您更好地贡献代码：

```
AuToTestCase/
├── docs/                 # 文档
│   └── guides/           # 用户指南和开发者指南
├── requirements/         # 需求文档
├── src/                  # 源代码
│   ├── core/             # 核心功能
│   │   ├── llm_engine.py # LLM引擎
│   │   └── test_generator.py # 测试用例生成器
│   ├── crawlers/         # 爬虫模块
│   ├── exporters/        # 导出模块
│   ├── tools/            # 工具和实用函数
│   ├── batch_processor.py # 批处理功能
│   ├── cli.py            # 命令行接口
│   ├── config.py         # 配置文件
│   └── main.py           # 主程序入口
├── tests/                # 测试代码
├── output/               # 输出目录
│   ├── difference_inspection/ # 差异验收相关输出
│   └── user_management/  # 用户管理相关输出
├── temp/                 # 临时文件
└── README.md             # 项目说明
```

## 测试指南

我们使用pytest进行测试。在提交代码前，请确保所有测试都能通过：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_specific.py

# 运行带覆盖率报告的测试
pytest --cov=src tests/
```

### 编写测试

1. 测试文件应放在`tests/`目录下
2. 测试文件名应以`test_`开头
3. 测试函数名应以`test_`开头
4. 使用断言验证结果
5. 为不同的功能单元编写单独的测试

示例测试：

```python
def test_generate_test_id():
    from src.core.test_generator import TestGenerator
    
    generator = TestGenerator()
    test_id = generator.generate_test_id()
    
    # 验证测试ID格式是否符合YYYYMMDD-XXX格式
    assert len(test_id) == 11
    assert test_id[8] == '-'
    assert test_id[:8].isdigit()
    assert test_id[9:].isdigit()
```

## 版本控制

我们使用[语义化版本控制](https://semver.org/)。版本格式为：`MAJOR.MINOR.PATCH`。

## 行为准则

请参阅我们的[行为准则](CODE_OF_CONDUCT.md)，确保所有参与者都能在一个开放、尊重和包容的环境中进行贡献。

## 许可证

通过贡献您的代码，您同意您的贡献将根据项目的许可证进行许可。

感谢您的贡献！ 