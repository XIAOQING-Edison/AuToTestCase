# AuToTestCase 使用指南

本指南将帮助您了解如何使用AuToTestCase工具的各项功能，包括爬虫爬取需求文档和生成测试用例。

## 目录

1. [爬取需求文档](#爬取需求文档)
   - [使用基本爬虫功能](#使用基本爬虫功能)
   - [使用高级Playwright爬虫](#使用高级playwright爬虫)
   - [爬虫常见问题解决](#爬虫常见问题解决)
2. [生成测试用例](#生成测试用例)
   - [从文件生成测试用例](#从文件生成测试用例)
   - [直接生成测试用例](#直接生成测试用例)
3. [导出格式说明](#导出格式说明)
   - [Excel格式](#excel格式)
   - [XMind格式](#xmind格式)
4. [高级功能](#高级功能)
   - [批量处理](#批量处理)
   - [自定义配置](#自定义配置)

## 爬取需求文档

### 使用基本爬虫功能

基本爬虫适用于静态网页内容的抓取：

```bash
python -m src.crawlers.crawler_test "https://example.com/document" --output "temp/requirements.md" --no-verify-ssl
```

参数说明：
- `--output`: 指定输出文件路径
- `--no-verify-ssl`: 禁用SSL验证（适用于内部自签名证书）
- `--selector`: 可选，指定内容选择器（CSS选择器）

### 使用高级Playwright爬虫

对于需要JavaScript渲染的现代网站，使用Playwright爬虫：

```bash
python -m src.crawlers.playwright_crawler "https://example.com/document" --output "temp/requirements.md" --wait-for "networkidle"
```

参数说明：
- `--output`: 指定输出文件路径
- `--wait-for`: 等待条件，可以是"networkidle"或CSS选择器
- `--selector`: 可选，指定内容选择器（CSS选择器）

### 爬虫常见问题解决

1. **SSL证书问题**: 使用`--no-verify-ssl`参数
2. **JavaScript渲染问题**: 使用Playwright爬虫
3. **登录问题**: 目前需要手动登录后获取文档

## 生成测试用例

### 从文件生成测试用例

使用已有的需求文档文件生成测试用例：

```bash
python -m src.main --file requirements/your_requirements.md --excel output/your_project/test_cases.xlsx --xmind output/your_project/test_cases.xmind --verbose
```

参数说明：
- `--file`: 需求文档文件路径
- `--excel`: Excel输出文件名
- `--xmind`: XMind输出文件名
- `--verbose`: 显示详细输出

### 直接生成测试用例

从URL直接生成测试用例（结合爬虫功能）：

```bash
python -m src.main --url "https://example.com/document" --excel output/your_project/test_cases.xlsx --xmind output/your_project/test_cases.xmind --verbose
```

## 导出格式说明

### Excel格式

Excel导出格式包含以下列：
- 用例编号
- 所属模块
- 用例标题
- 优先级
- 前置条件
- 测试步骤
- 预期结果

### XMind格式

XMind格式以JSON方式导出，可以导入到XMind软件中查看。

## 高级功能

### 批量处理

使用批量处理功能处理多个需求文档：

```bash
python -m src.batch_processor --pattern "requirements/*.md" --output-dir "output/batch_results"
```

### 自定义配置

您可以通过修改`src/config.py`文件自定义配置：
- 修改API设置
- 更改优先级级别
- 调整导出格式

更多详细配置选项，请参考[配置文档](../configuration.md)。 