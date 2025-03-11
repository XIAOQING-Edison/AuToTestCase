# AuToTestCase 实例教程

本文档提供了一些实际示例，展示如何使用AuToTestCase处理不同类型的需求文档并生成测试用例。

## 目录

1. [基本用法示例](#基本用法示例)
2. [差异验收系统测试](#差异验收系统测试)
3. [用户管理系统测试](#用户管理系统测试)
4. [批量处理示例](#批量处理示例)
5. [爬虫抓取示例](#爬虫抓取示例)

## 基本用法示例

### 场景：从本地文件生成测试用例

假设您有一个需求文档文件`requirements/login_requirements.md`，内容如下：

```markdown
# 登录功能需求

## 1. 基本登录流程
用户可以使用用户名和密码登录系统。系统验证凭据后允许用户访问。

## 2. 密码规则
密码必须至少8个字符，包含大小写字母和数字。

## 3. 登录失败处理
连续3次登录失败后，账户将被锁定30分钟。

## 4. 记住登录状态
用户可选择"记住我"选项保持登录状态7天。
```

要从此文档生成测试用例，运行以下命令：

```bash
python -m src.main --file requirements/login_requirements.md --excel output/login_test_cases.xlsx --verbose
```

生成的Excel文件将包含基于这些需求的测试用例，包括：
- 成功登录测试
- 密码规则验证测试
- 多次失败登录测试
- "记住我"功能测试

### 输出示例

生成的测试用例将类似于下面的格式：

| 用例编号 | 所属模块 | 用例标题 | 优先级 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|-------|---------|---------|---------|
| 20250315-001 | 登录功能 | 验证用户使用有效凭据登录 | 高 | 用户已注册 | 1. 访问登录页面<br>2. 输入有效用户名<br>3. 输入有效密码<br>4. 点击登录按钮 | 1. 用户成功登录系统<br>2. 显示主页面<br>3. 用户名显示在界面上 |
| 20250315-002 | 登录功能 | 验证密码规则 - 长度不足 | 中 | 用户已注册 | 1. 访问登录页面<br>2. 输入有效用户名<br>3. 输入少于8个字符的密码<br>4. 点击登录按钮 | 1. 登录失败<br>2. 显示密码长度不足的错误提示 |
| ... | ... | ... | ... | ... | ... | ... |

## 差异验收系统测试

### 场景：生成差异验收测试用例

假设我们有一个差异验收系统的需求文档`requirements/difference_inspection_requirements.md`，包含以下内容：

```markdown
# 差异验收系统V1.3

## 功能描述
系统允许质检员对比物料清单与实际交付物料，标记差异并生成验收报告。

## 主要功能

### 1. 物料清单导入
- 支持Excel格式导入物料清单
- 支持手动录入物料信息
- 导入后显示物料清单预览

### 2. 实际物料记录
- 通过扫码录入实际物料
- 支持手动添加实际物料
- 记录物料的数量、批次、生产日期

### 3. 差异对比与标记
- 自动标识缺失物料
- 自动标识多余物料
- 自动标识数量不符物料
- 允许质检员添加备注说明差异原因

### 4. 报告生成
- 生成验收报告，包含所有差异信息
- 支持导出为PDF和Excel格式
- 报告包含统计数据和差异详情
```

使用以下命令生成测试用例：

```bash
python -m src.main --file requirements/difference_inspection_requirements.md --excel output/difference_inspection/test_cases.xlsx --xmind output/difference_inspection/test_cases.xmind
```

该命令将为差异验收系统生成测试用例，并以Excel和XMind两种格式保存。

## 用户管理系统测试

### 场景：复杂功能测试用例生成

对于更复杂的系统，如用户管理模块，我们可能有如下需求：

```markdown
# 用户管理系统需求

## 1. 用户注册
- 支持邮箱和手机号注册
- 验证码验证
- 用户协议确认
- 初始密码设置

## 2. 用户资料管理
- 基本信息编辑
- 头像上传
- 联系方式维护
- 隐私设置调整

## 3. 权限管理
- 角色分配
- 功能权限设置
- 数据访问权限设置
- 临时权限授予

## 4. 账户安全
- 密码修改
- 登录设备管理
- 登录历史查看
- 账户锁定与解锁
```

使用以下命令生成更全面的测试用例：

```bash
python -m src.main --file requirements/user_management_requirements.txt --excel output/user_management/test_cases.xlsx --priority-levels "高,中,低" --verbose
```

这个命令使用自定义优先级级别（中文），并生成用户管理系统的全面测试用例。

## 批量处理示例

### 场景：处理多个需求文档

如果您有多个需求文档需要处理，可以使用批处理功能：

```bash
python -m src.batch_processor --pattern "requirements/*.md" --output-dir "output/batch_results" --excel-only
```

这个命令会处理`requirements`目录下所有的`.md`文件，为每个文件生成Excel格式的测试用例，并将结果保存在`output/batch_results`目录中。

### 批处理报告示例

批处理完成后，会生成一个汇总报告：

```
批处理任务完成！
总处理文件数: 5
成功处理: 5
失败处理: 0

处理详情:
- requirements/login_requirements.md: 成功 (15个测试用例)
- requirements/user_management_requirements.txt: 成功 (32个测试用例)
- requirements/difference_inspection_requirements.md: 成功 (28个测试用例)
- requirements/reporting_system.md: 成功 (18个测试用例)
- requirements/api_interface.md: 成功 (22个测试用例)

输出保存在: output/batch_results/
```

## 爬虫抓取示例

### 场景：从网页获取需求并生成测试用例

如果需求文档在网页上，您可以使用内置爬虫获取内容：

```bash
# 使用基础爬虫
python -m src.crawlers.crawler_test "https://company-intranet.example/docs/payment-system-requirements" --output "temp/payment_requirements.md" --no-verify-ssl

# 使用获取的内容生成测试用例
python -m src.main --file temp/payment_requirements.md --excel output/payment_test_cases.xlsx
```

对于需要JavaScript渲染的现代网站，使用Playwright爬虫：

```bash
python -m src.crawlers.playwright_crawler "https://modern-app.example/requirements/inventory-system" --output "temp/inventory_requirements.md" --wait-for "networkidle"

python -m src.main --file temp/inventory_requirements.md --excel output/inventory_test_cases.xlsx
```

### 一步到位方法

您还可以直接从URL生成测试用例，无需分两步操作：

```bash
python -m src.main --url "https://company-intranet.example/docs/payment-system-requirements" --no-verify-ssl --excel output/payment_test_cases.xlsx
```

这个命令会先抓取网页内容，然后直接生成测试用例，省去了中间文件保存步骤。

## 小贴士和最佳实践

1. **使用清晰的需求文档** - 结构化的需求文档能产生更好的测试用例
2. **优先级划分** - 根据需要适当调整优先级设置
3. **批量处理大型项目** - 对于大型项目，按模块划分需求文档并使用批处理
4. **保留原始需求** - 将需求文档保存在`requirements/`目录，方便回溯
5. **使用有意义的文件名** - 输出文件使用有意义的名称，如`login_test_cases.xlsx`而不是`output1.xlsx` 