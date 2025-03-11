# AuToTestCase 疑难解答指南

本文档帮助您解决在使用AuToTestCase过程中可能遇到的常见问题和错误。

## 目录

1. [LLM模型相关问题](#llm模型相关问题)
2. [爬虫相关问题](#爬虫相关问题) 
3. [测试用例生成问题](#测试用例生成问题)
4. [导出格式问题](#导出格式问题)
5. [批处理问题](#批处理问题)
6. [配置相关问题](#配置相关问题)
7. [常见错误消息解释](#常见错误消息解释)

## LLM模型相关问题

### 问题：生成LLM响应时出错

**症状**：运行程序时出现"分析需求时出错: 生成LLM响应时出错"的错误消息。

**可能原因**：
1. 本地模型服务（如Ollama）未启动
2. 连接超时
3. 模型不存在或未下载

**解决方案**：
1. 确保Ollama服务正在运行：
   ```bash
   ollama serve
   ```

2. 检查可用模型：
   ```bash
   ollama list
   ```

3. 如果需要的模型不存在，下载它：
   ```bash
   ollama pull llama2:7b
   ```

4. 修改`src/config.py`中的配置，使用已知可用的模型

5. 使用模型检查工具诊断问题：
   ```bash
   python -m src.tools.model_checker
   ```

### 问题：模型响应质量不佳

**症状**：生成的测试用例质量不高或不相关。

**解决方案**：
1. 尝试使用更强大的模型，如`deepseek-r1:7b`或`llama2:13b`
2. 检查需求文档的质量和格式
3. 调整系统提示，修改`src/core/test_generator.py`中的提示模板

## 爬虫相关问题

### 问题：SSL证书验证失败

**症状**：使用爬虫时出现SSL证书验证失败的错误。

**解决方案**：
1. 使用`--no-verify-ssl`参数禁用SSL验证：
   ```bash
   python -m src.crawlers.crawler_test "https://example.com/document" --output "temp/requirements.md" --no-verify-ssl
   ```

2. 或更新您系统的CA证书

### 问题：无法抓取动态内容

**症状**：抓取的页面内容不完整或缺少通过JavaScript加载的内容。

**解决方案**：
1. 使用Playwright爬虫代替基本爬虫：
   ```bash
   python -m src.crawlers.playwright_crawler "https://example.com/document" --output "temp/requirements.md"
   ```

2. 使用`--wait-for`参数指定等待条件：
   ```bash
   python -m src.crawlers.playwright_crawler "https://example.com/document" --output "temp/requirements.md" --wait-for "#content"
   ```

## 测试用例生成问题

### 问题：生成过程卡住或超时

**症状**：测试用例生成过程长时间无反应。

**解决方案**：
1. 检查本地模型服务是否仍在运行
2. 增加配置文件中的超时设置：
   ```python
   # 在src/config.py中
   TIMEOUT = 120  # 增加到120秒
   ```

3. 对于大型文档，尝试分割为小块处理
4. 使用`--verbose`参数运行，查看详细进度

### 问题：测试用例ID格式问题

**症状**：生成的测试用例ID不符合您的团队规范。

**解决方案**：
1. 修改`src/core/test_generator.py`中的`generate_test_id`方法
2. 当前格式为日期加序号（例如"20250311-001"）
3. 可以根据需要修改为其他格式

## 导出格式问题

### 问题：Excel文件格式不符合要求

**症状**：导出的Excel文件格式不符合团队要求。

**解决方案**：
1. 修改`src/exporters/excel_exporter.py`中的`export`方法
2. 在`src/config.py`中自定义`EXCEL_HEADERS`

### 问题：XMind文件无法打开

**症状**：生成的XMind文件无法在XMind软件中正确打开。

**解决方案**：
1. 确保使用的是XMind 8或更新版本
2. 检查`src/exporters/xmind_exporter.py`中的输出格式
3. 如果问题持续，尝试禁用XMind导出，仅使用Excel：
   ```bash
   python -m src.main --file requirements/your_requirements.md --excel output/test_cases.xlsx
   ```

## 批处理问题

### 问题：批处理失败或部分失败

**症状**：使用批处理功能时，某些文件处理失败。

**解决方案**：
1. 检查失败的文件格式是否正确
2. 减少并发处理数量：
   ```python
   # 在src/config.py中
   BATCH_MAX_CONCURRENT = 1  # 降低并发数
   ```

3. 增加批处理超时时间：
   ```python
   # 在src/config.py中
   BATCH_TIMEOUT = 1200  # 增加到20分钟
   ```

4. 使用`--verbose`参数运行批处理，查看详细日志

## 配置相关问题

### 问题：配置更改不生效

**症状**：修改配置文件后，更改似乎没有生效。

**解决方案**：
1. 确保修改了正确的配置文件（`src/config.py`）
2. 重新启动所有正在运行的服务和应用
3. 检查是否有环境变量覆盖了配置文件中的设置
4. 运行时使用`--verbose`参数查看加载的配置

## 常见错误消息解释

### "分析需求时出错: 生成LLM响应时出错"

这通常表示与LLM模型的连接问题，请参见[LLM模型相关问题](#llm模型相关问题)章节。

### "无法连接到API服务"

检查API_BASE配置是否正确，以及服务是否正在运行。

### "批处理超时"

批处理操作超过了预定的超时时间。尝试增加`BATCH_TIMEOUT`设置或减少一次处理的文件数量。

### "导出格式不支持"

指定的导出格式不受支持。确保使用`--excel`或`--xmind`参数指定支持的导出格式。

### "模型返回无效响应"

模型返回的响应无法被解析为有效的测试用例。尝试使用不同的模型或检查提示模板。

## 获取更多帮助

如果上述解决方案无法解决您的问题，请尝试以下方法：

1. 使用`--verbose`和`--debug`参数运行程序，获取更详细的日志
2. 检查`log/`目录中的日志文件，查找更多错误详情
3. 在GitHub仓库中提交Issue，附上详细的错误日志和复现步骤 