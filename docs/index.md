# AuToTestCase 文档中心

欢迎来到AuToTestCase文档中心！本文档将帮助您了解如何安装、配置和使用AuToTestCase工具生成高质量的测试用例。

## 入门指南

- [安装指南](guides/installation.md) - 如何安装和配置AuToTestCase
- [使用指南](guides/usage_guide.md) - 如何使用AuToTestCase生成测试用例
- [配置指南](guides/configuration.md) - 如何配置AuToTestCase以满足您的需求
- [实例教程](guides/examples.md) - 通过实际示例学习如何使用AuToTestCase

## 进阶主题

- [疑难解答](guides/troubleshooting.md) - 解决使用过程中的常见问题
- [贡献指南](guides/contributing.md) - 如何参与项目开发和贡献代码

## 关于AuToTestCase

AuToTestCase是一个基于大语言模型的测试用例自动生成工具，旨在帮助测试工程师从需求文档中快速生成高质量的测试用例。主要特点包括：

1. **智能需求分析** - 使用大语言模型分析需求文档，理解功能和业务逻辑
2. **多种导出格式** - 支持Excel和XMind格式导出，方便集成到现有测试流程
3. **批量处理能力** - 支持批量处理多个需求文档，提高工作效率
4. **爬虫功能** - 内置爬虫可以从网页直接抓取需求文档
5. **高度可配置** - 提供丰富的配置选项，满足不同团队的需求

## 快速链接

- [项目主页](https://github.com/yourusername/AuToTestCase) - 项目GitHub仓库
- [发布说明](https://github.com/yourusername/AuToTestCase/releases) - 了解各版本的更新内容
- [问题反馈](https://github.com/yourusername/AuToTestCase/issues) - 报告问题或提出建议

## 系统要求

- Python 3.8 或更高版本
- 最少4GB RAM（推荐8GB以上）
- 支持的操作系统：Windows、macOS、Linux

## 开始使用

安装完成后，您可以使用以下命令生成测试用例：

```bash
python -m src.main --file requirements/your_requirements.md --excel output/test_cases.xlsx
```

更多详细信息，请参阅[使用指南](guides/usage_guide.md)。

## 文档总览

```
docs/
├── index.md                    # 本文档（主页）
├── guides/
│   ├── installation.md         # 安装指南
│   ├── usage_guide.md          # 使用指南
│   ├── configuration.md        # 配置指南
│   ├── examples.md             # 实例教程
│   ├── troubleshooting.md      # 疑难解答
│   └── contributing.md         # 贡献指南
``` 