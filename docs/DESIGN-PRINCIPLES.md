# Naturo 设计原则

## 核心理念：软件复杂，使用简单

底层引擎可以同时用 UIA / MSAA / Win32 HWND / AI Vision 多种技术，
但用户永远只需要最简单的命令。

## 用户三步操作

```bash
# 1. 看 — 自动选最佳引擎，显示所有可操作元素
naturo see --app U8

# 2. 找 — 用自然语言找元素
naturo find "发票号" --app U8

# 3. 做 — 用 ref 直接操作
naturo click e70
naturo type e85 "12345"
naturo select e71 "增值税专用发票"
```

## 设计规则

### 1. 引擎透明 + 逐层混合
- 用户不需要知道 UIA / MSAA / Win32 / AI Vision 的区别
- `--backend auto` 是默认值（不是 `uia`）
- **逐层引擎选择**（参考自然机器人 selector 架构）：
  - 元素树的每一层独立选择最佳引擎
  - 外层容器用 Win32 HWND 枚举（穿透 VB6/ActiveX）
  - 到达可交互控件后切 UIA（获取内部 Row/Cell）
  - UIA 也拿不到的用 AI Vision
  - 示例：Window[HWND] → Pane[HWND] → ThunderRT6[HWND] → VSFlexGrid[HWND] → Row[UIA] → Cell[UIA]
- 每个 ElementInfo 记录自己的来源引擎（hwnd/uia/msaa/ai）
- 结果合并去重，用户只看到统一的元素树

### 2. --app 即全部
- `--app feishu` = 飞书的所有窗口的所有元素
- 不需要用户用 `app windows` 找 HWND 再 `--hwnd` 指定
- 多窗口自动合并，ref 全局唯一

### 3. 元素可见即可操作
- `see` 返回的每个元素都可以用 ref 直接 click/type/find
- 元素类型自动识别：Edit 可输入、Button 可点击、ComboBox 可选择
- `naturo type e85 "hello"` 自动处理：定位元素 → 聚焦 → 清除旧值 → 输入

### 4. find 是核心入口
- `naturo find "发票号"` 不需要 --ai，默认就搜索
- 搜索范围：name、class name、value、role
- 支持模糊匹配和中文
- 返回元素的 ref + 位置，可以直接 click/type

### 5. highlight 即所见即所得
- `naturo highlight --app U8` 在屏幕上直接画出所有可操作元素
- 每个元素显示 ref + 名字
- 用户看到屏幕上的标注，就知道该用哪个 ref

### 6. 错误信息有用
- 不说 "No window found"，说 "找不到 'U8'，可用的应用: EnterprisePortal, cmd, explorer"
- 不说 "element not found"，说 "e85 不存在，最近的 snapshot 有 e1-e64，试试 naturo see 刷新"

### 7. 企业应用是一等公民
- 用友、金蝶、SAP、浪潮这类 VB6/MFC/ActiveX 应用不是边缘场景
- auto 模式必须能处理它们（Win32 HWND fallback）
- 不能要求用户装额外依赖或以管理员运行（基本功能）
