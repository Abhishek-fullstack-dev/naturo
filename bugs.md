# Naturo Bug Tracker

## 状态图标
- 🔴 **Open** — 未修复
- 🟢 **Fixed** — 已修复（Dev 声称）
- ✅ **Verified** — QA 验证通过
- 🚫 **Blocked** — 受其他 bug 阻塞
- 📋 **Needs Info** — 需要更多信息
- ⏸️ **On Hold** — 暂缓（低优先级或等待决策）

## 严重程度
- **P0** — 阻断性，用户无法使用核心功能
- **P1** — 严重，影响主要使用场景
- **P2** — 中等，影响次要功能或体验
- **P3** — 轻微，边界情况或改进建议

---

## 🔴 Open

(No open bugs)

---

### BUG-013: `service list --state running` 返回 0 结果（P1 - 功能缺陷） → 🟢 Fixed
**发现日期**: 2026-03-22 (Round 7)
**修复日期**: 2026-03-22 (commit ed454c2)
**类型**: 功能缺陷

**修复**: 当 `state == "running"` 时不传 `state=` 参数，使用 sc.exe 默认行为返回运行中的服务。待 QA 验证。

---

### BUG-012: `learn interaction` 教程多处命令语法错误（P2 - DOC） → ✅ Verified
**发现日期**: 2026-03-22 (Round 6)
**修复日期**: 2026-03-22 (commit cb4cb2e)
**验证日期**: 2026-03-22 (Round 7)
**类型**: 文档不一致

**问题**: `naturo learn interaction` 显示的命令示例与实际 CLI 不符：

| learn 教程写的 | 实际正确语法 | 错误类型 |
|----------------|-------------|---------|
| `naturo click 500 300` | `naturo click --coords 500 300` | click 不接受位置坐标参数 |
| `naturo click 500 300 --button right` | `naturo click --coords 500 300 --right` | 同上 + 参数名不对 |
| `naturo click 500 300 --double` | `naturo click --coords 500 300 --double` | 同上 |
| `naturo drag 100 200 400 500` | `naturo drag --from-coords 100 200 --to-coords 400 500` | drag 不接受位置参数 |
| `naturo move 500 300` | `naturo move --coords 500 300` | move 不接受位置参数 |
| `naturo scroll up 5` | `naturo scroll up --amount 5` | scroll 数量需要 --amount |

**复现**:
```
> naturo click 500 300
Error: Got unexpected extra argument (300)

> naturo drag 100 200 400 500
Error: Got unexpected extra arguments (100 200 400 500)

> naturo move 500 300
Error: Got unexpected extra arguments (500 300)

> naturo scroll up 5
Error: Got unexpected extra argument (5)
```

**修复**: 修正所有命令示例：
- `click 500 300` → `click --coords 500 300`
- `click --button right` → `click --right`  
- `drag 100 200 400 500` → `drag --from-coords 100 200 --to-coords 400 500`
- `move 500 300` → `move --coords 500 300`
- `scroll up 5` → `scroll up --amount 5`
- 新增 `click "Submit"` 文本点击示例

**Round 7 验证**: ✅ 通过 — 所有修正后的命令语法在编译机上验证：
- `naturo click --coords 500 300 --json` → 接受（COM error 是 SSH 预期行为）
- `naturo scroll up --amount 5 --json` → 接受
- `naturo move --coords 500 300 --json` → 接受
- `naturo drag --from-coords 100 200 --to-coords 400 500 --json` → 接受

---

### BUG-011: `learn capture` 引用不存在的 `--region` 参数（P2 - DOC） → ✅ Verified
**发现日期**: 2026-03-22 (Round 5)
**修复日期**: 2026-03-22 (commit 71a1217)
**类型**: 文档不一致

**根因**: learn capture 教程引用了 `--region` 参数，但 `capture live` 实际支持的是 `--app`、`--window-title`、`--hwnd`、`--screen`。
**修复**: 将 `--region 0,0,800,600` 示例替换为 `--app "Notepad"`，将 tip 中的 `--region` 替换为 `--app` / `--window-title`。

**Round 7 验证**: ✅ 通过 — 编译机已更新到 7301bf1。`learn capture` 不再引用 `--region`，改为 `--app "Notepad"` 和 `--app` / `--window-title` tips。

---

### BUG-003: 缺少 pyvda 依赖导致虚拟桌面功能不可用（P2 — 需产品决策）
**发现日期**: 2026-03-22
**影响**: Virtual Desktop 命令全部报错

**错误信息**:
```
Error: Virtual desktop support requires pyvda. Install: pip install pyvda
```

**建议**: 
1. 如果 pyvda 是必需依赖，应该写入 requirements.txt / setup.py
2. 如果是可选功能，应该在 README 中说明
3. 错误提示已经很清楚，但用户期望 `pip install naturo` 后所有功能开箱即用

### BUG-009: taskbar/tray 全部命令报 `'NaturoCore' object has no attribute 'get_ui_tree'`（P1） → ✅ Verified
**发现日期**: 2026-03-22 (Round 4)
**修复日期**: 2026-03-22 (commit 6a189b3)
**影响**: taskbar list/click、tray list/click 全部不可用
**类型**: 功能缺陷

**根因**: 代码调用了不存在的 `core.get_ui_tree()` 方法。NaturoCore 只有 `get_element_tree(hwnd, depth)`。
**修复**: 使用 `FindWindowW("Shell_TrayWnd")` 定位 taskbar 窗口句柄，再调 `get_element_tree(hwnd, depth)` 获取 UIA 树。Tray 额外检查 `NotifyIconOverflowWindow`。集合方法从 dict 访问改为 ElementInfo dataclass 属性访问。

**验证日期**: 2026-03-22 (Round 5)
**验证结果**: ✅ 通过
- `naturo taskbar list --json` → 返回合法 JSON `{"success": true, "items": [], "count": 0}`（SSH 下空结果是预期行为）
- `naturo tray list --json` → 返回合法 JSON `{"success": true, "icons": [], "count": 0}`
- 不再报 `get_ui_tree` 错误

### BUG-010: `learn` 教程引用不存在的命令/参数（P2 - DOC） → ✅ Verified (部分遗漏见 BUG-011)
**发现日期**: 2026-03-22 (Round 4)
**修复日期**: 2026-03-22 (commit 6a189b3)
**类型**: 文档不一致

**修复内容**:
| 原内容 | 修复后 |
|--------|--------|
| `naturo snapshot take --path snap.png` | `naturo capture live --path snap.png` |
| `naturo mcp serve` | `naturo mcp start` |
| `naturo agent run "..."` | `naturo agent "..."` |
| `naturo diff --path before.png` | `naturo diff --snapshot ID1 --snapshot ID2` / `--window` |
| `naturo java list` / `naturo sap list` | 改为"planned"说明文字，不再列出假命令 |
| MCP config `"args": ["mcp", "serve"]` | `"args": ["mcp", "start"]` |

**验证日期**: 2026-03-22 (Round 5)
**验证结果**: ✅ 主要修复通过
- `learn capture` → 引用 `capture live --path snap.png` ✅
- `learn capture` → `diff --snapshot ID1 --snapshot ID2` ✅
- `learn ai` → MCP config `"args": ["mcp", "start"]` ✅
- `learn ai` → `naturo agent "..."` ✅
- `learn extensions` → java/sap 标为 "planned" ✅
- ⚠️ `learn capture` 仍引用 `--region` 参数（实际不存在），见 BUG-011

### BUG-007: `electron list` 命令挂起不返回（P1） → ✅ Verified
**发现日期**: 2026-03-22 (Round 3)
**修复日期**: 2026-03-22 (commit bfe0509)
**验证日期**: 2026-03-22 (Round 4)

**验证结果**: ✅ 通过
- `naturo electron list --json` → 几秒内返回合法 JSON，发现 3 个 Electron 应用 (msedge, naturo, msedgewebview2)
- 不再挂起

### BUG-008: `learn <topic>` 只返回一句话描述，无实际教程内容（P2 - UX） → ✅ Verified
**发现日期**: 2026-03-22 (Round 3)
**修复日期**: 2026-03-22 (commit bfe0509)
**验证日期**: 2026-03-22 (Round 4)

**验证结果**: ✅ 通过
- 6 个 topic 全部验证：capture、interaction、system、windows、extensions、ai
- 每个 topic 包含分类命令示例、使用模式和 Tips
- 内容丰富实用（capture ~25 行，interaction ~20 行，system ~25 行）
- ⚠️ 但发现部分命令引用不正确（见 BUG-010）

---

## ✅ Verified

### BUG-001: naturo_msaa_get_element_tree 函数缺失（P0）
**发现日期**: 2026-03-22
**修复日期**: 2026-03-22
**验证日期**: 2026-03-22 (Round 2)

**验证结果**: ✅ 通过

### BUG-002: README 命令示例与实际不符（P1 - DOC）
**发现日期**: 2026-03-22
**修复日期**: 2026-03-22 (commit 1c89246)
**验证日期**: 2026-03-22 (Round 2)

**验证结果**: ✅ 通过

### BUG-004: README Quick Start `press "ctrl+s"` → `hotkey ctrl+s`（P1 - DOC）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**验证日期**: 2026-03-22 (Round 3, v0.1.1)

**验证结果**: ✅ 通过
- README 已改为 `naturo hotkey ctrl+s`
- `naturo hotkey ctrl+s --json` → 命令被接受（SSH 下报 COM error 是预期行为）

### BUG-005: `app quit` API 不一致 → 支持位置参数（P1 - API）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**验证日期**: 2026-03-22 (Round 3, v0.1.1)

**验证结果**: ✅ 通过
- `naturo app quit notepad` → 接受位置参数（报 "Application not found" 而不是 "unexpected extra argument"）
- `naturo app quit --help` → 显示 `[NAME]` 位置参数

### BUG-006: scroll 不接受位置参数 → 支持位置参数（P2 - UX）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**验证日期**: 2026-03-22 (Round 3, v0.1.1)

**验证结果**: ✅ 通过
- `naturo scroll down` → 接受位置参数（SSH 下报 COM error 是预期行为）
- `naturo scroll --help` → 显示 `[[up|down|left|right]]` 位置参数

---

## 质量评估

**当前状态**: 🟡 **接近可发布** — 核心功能稳定，版本已升至 0.1.1

**已验证通过 (v0.1.1)**:
- ✅ `naturo --version` → "naturo, version 0.1.1"
- ✅ `naturo --help` → 完整命令列表（30+ 命令组）
- ✅ `naturo capture live --path X --json` → 截图成功，合法 JSON
- ✅ `naturo list windows/screens --json` → 合法 JSON
- ✅ `naturo app list/launch/quit/switch/find --json` → 正常
- ✅ `naturo service list/status --json` → 正常
- ✅ `naturo clipboard get/set --json` → 正常
- ✅ `naturo registry list/get --json` → 正常
- ✅ `naturo snapshot list/clean --json` → 正常
- ✅ `naturo record list --json` → 合法 JSON
- ✅ `naturo electron detect msedge --json` → 正常
- ✅ `naturo mcp tools --json` → 76 个 MCP 工具
- ✅ `naturo open <url>` → 正常（打开浏览器）
- ✅ `naturo open <nonexistent>` → 友好错误 "File not found"
- ✅ `naturo open` (无参数) → 友好错误 "Missing argument 'TARGET'"
- ✅ `naturo find/click/type/press/hotkey/scroll/drag` → help 输出完整
- ✅ `naturo window focus/close/minimize/maximize/move/resize/set-bounds` → help 正确
- ✅ `naturo diff/wait/describe/agent/record/chrome/mcp` → help 正确
- ✅ 错误信息质量：结构化 JSON error（code + message + suggested_action + recoverable）

**Open 问题**:
| Bug | 严重度 | 影响 |
|-----|--------|------|
| BUG-003 | P2 | pyvda 缺失，desktop 命令不可用（需产品决策） |

**风险评估**:
| 风险 | 等级 | 说明 |
|------|------|------|
| UI 操作未桌面验证 | 🟡 中等 | click/type/hotkey 等核心功能需桌面 session |
| taskbar/tray 需桌面验证 | 🟡 中等 | BUG-009 修复后需实机验证 |
| pyvda 依赖策略 | 🟢 低 | 错误提示清楚，不阻塞其他功能 |

---

最后更新: 2026-03-22 18:08 by QA Agent (Round 3)
