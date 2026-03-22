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

### BUG-003: 缺少 pyvda 依赖导致虚拟桌面功能不可用（P2）
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

### BUG-009: taskbar/tray 全部命令报 `'NaturoCore' object has no attribute 'get_ui_tree'`（P1）
**发现日期**: 2026-03-22 (Round 4)
**影响**: taskbar list/click、tray list/click 全部不可用
**类型**: 功能缺陷

**复现**:
```
naturo taskbar list --json → {"success": false, "error": {"code": "UNKNOWN_ERROR", "message": "'NaturoCore' object has no attribute 'get_ui_tree'"}}
naturo tray list --json → 同上
naturo taskbar click Chrome --json → 同上
naturo tray click Volume --json → 同上
```

**分析**: NaturoCore 类缺少 `get_ui_tree` 方法，说明 DLL 没有导出这个函数或 Python 绑定未映射。taskbar/tray 功能的底层实现依赖 UIAutomation 树遍历，该方法未完成。

**建议**: 
1. 在 NaturoCore 中实现 get_ui_tree 或映射 DLL 导出
2. 若功能未完成，taskbar/tray 命令应标注"coming soon"或给出更清晰的错误消息
3. README Quick Start 不应列出不可用的命令

### BUG-010: `learn` 教程引用不存在的命令/参数（P2 - DOC）
**发现日期**: 2026-03-22 (Round 4)
**类型**: 文档不一致

**不一致列表**:
| learn 教程内容 | 实际情况 |
|---------------|---------|
| `naturo snapshot take --path snap.png` | ❌ 无 `snapshot take` 命令，只有 list/clean |
| `naturo mcp serve` | ❌ 应为 `naturo mcp start` |
| `naturo agent run "..."` | ❌ 应为 `naturo agent "..."` (无 run 子命令) |
| `naturo diff --path before.png` | ❌ diff 无 `--path` 参数 (有 --snapshot/--window) |
| `naturo java list` / `naturo sap list` | ⚠️ 标了 "coming soon" 但命令完全不存在 |

**建议**: learn 内容应与实际 CLI 100% 一致，这是用户学习路径的入口。建议从代码中的 --help 自动生成 learn 内容，避免手工维护的不一致。

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
| BUG-003 | P2 | pyvda 缺失，desktop 命令不可用 |
| BUG-007 | P1 | electron list 挂起 |
| BUG-008 | P2 | learn 内容空洞 |

**风险评估**:
| 风险 | 等级 | 说明 |
|------|------|------|
| electron list 挂起 | 🔴 高 | 用户可能以为工具卡死 |
| UI 操作未桌面验证 | 🟡 中等 | click/type/hotkey 等核心功能需桌面 session |
| learn 体验 | 🟡 中等 | 帮助系统框架在但内容空 |
| pyvda 依赖策略 | 🟢 低 | 错误提示清楚，不阻塞其他功能 |

---

最后更新: 2026-03-22 18:08 by QA Agent (Round 3)
