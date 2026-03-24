# Application E2E Test Playbook

## 目标

在真实 Windows 机器上，对每个已安装的应用执行**真实操作流程**，通过 naturo 自动化完成，并用**截图+AI 识别**验证每一步结果。

## 流程

### 1. 发现已安装应用

```bash
# 列出所有已安装应用（从注册表 + 开始菜单）
naturo app list --all
# 或者通过 PowerShell
powershell "Get-StartApps | Select-Object Name, AppID | Sort-Object Name"
```

### 2. 为每个应用设计 E2E Case

**原则：像真实用户一样操作。** 不是简单的 open/close，而是完成一个有意义的任务。

每个 case 包含：
- **Setup**: 打开应用，等待就绪
- **Actions**: 执行 3-8 步有意义的操作
- **Verify**: 每步操作后截图 + AI 验证
- **Cleanup**: 关闭应用，清理产生的文件

### 3. 验证方法

每步操作后：
```bash
# 1. 执行操作
naturo click --app "AppName" --id eN

# 2. 截图
naturo capture --app "AppName" -o step_N.png

# 3. AI 验证（由 QA agent 用 vision 分析截图）
# 确认：操作是否生效？UI 状态是否符合预期？
```

### 4. 记录结果

每个应用测试完成后，更新 `docs/SUPPORTED_APPS.md` 的兼容性矩阵。

## 预设 Case 库（按类别）

### 文本编辑器
**Notepad / 记事本**
1. 打开记事本
2. 输入多行文本（含中英文）
3. Ctrl+A 全选 → 验证选中
4. 修改字体（Format → Font）
5. Ctrl+S 保存到桌面 → 验证文件存在
6. 关闭

**WordPad / 写字板**
1. 打开写字板
2. 输入文本 → 加粗 → 改颜色
3. 插入日期时间
4. 另存为 RTF
5. 关闭

### 电子表格
**Excel**
1. 打开 Excel → 新建空白工作簿
2. 在 A1:A5 输入数据
3. 在 B1 输入公式 =SUM(A1:A5)
4. 选中区域 → 加边框
5. 另存为到指定位置
6. 关闭

### 计算器
**Calculator / 计算器**
1. 打开计算器
2. 执行 123 × 456
3. 验证结果显示 56088
4. 切换到科学模式
5. 执行 sin(30)
6. 关闭

### 文件管理
**File Explorer / 文件资源管理器**
1. 打开到指定目录
2. 新建文件夹（右键 → New → Folder）
3. 重命名文件夹
4. 进入文件夹
5. 返回上级
6. 删除文件夹
7. 关闭

### 浏览器
**Edge / Chrome**
1. 打开浏览器
2. 导航到 about:blank
3. 地址栏输入 URL
4. 等待页面加载
5. 点击页面元素
6. 关闭标签页

### 系统工具
**Settings / 设置**
1. 打开设置
2. 导航到 System → Display
3. 读取分辨率信息
4. 返回主页
5. 关闭

**Task Manager / 任务管理器**
1. 打开任务管理器
2. 切换到 Performance 标签
3. 读取 CPU 使用率
4. 关闭

### 画图
**Paint / 画图**
1. 打开画图
2. 选择画笔工具
3. 画一条线（drag 操作）
4. 选择颜色
5. 填充区域
6. 另存为 PNG
7. 关闭（不保存）

## Case 变异（防止测试固化）

每次执行可以变化：
- 输入的文本内容随机
- 保存的文件名带时间戳
- 计算器的数字随机
- 文件夹名称随机
- 操作顺序在合理范围内调整

## 输出格式

```markdown
## [App Name] vX.Y — Round N

**环境**: Windows 11 / 编译机 / naturo vX.Y.Z
**日期**: YYYY-MM-DD

| Step | Action | naturo Command | Expected | Actual | Screenshot | Result |
|------|--------|----------------|----------|--------|------------|--------|
| 1 | Open app | `naturo app launch notepad` | 窗口出现 | 窗口出现 | step1.png | ✅ |
| 2 | Type text | `naturo type "Hello"` | 文本显示 | 文本显示 | step2.png | ✅ |
| ... | ... | ... | ... | ... | ... | ... |

**Overall**: ✅ Pass / ⚠️ Partial / ❌ Fail
**Issues**: (如有)
```

## 发现问题时

1. 截图保存证据
2. `gh issue create --label "bug,from:qa,app-compat"` 
3. 更新 SUPPORTED_APPS.md 标记状态
4. 如果是 P0（完全不可用）→ 飞书立即通知
