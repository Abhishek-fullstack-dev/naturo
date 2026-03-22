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

---

## 🟢 Fixed (待 QA 验证)

### BUG-004: README Quick Start `press "ctrl+s"` → `hotkey ctrl+s`（P1 - DOC）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**修复内容**: README 示例改为 `naturo hotkey ctrl+s`

### BUG-005: `app quit` API 不一致 → 支持位置参数（P1 - API）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**修复内容**: `app quit` 现在接受 NAME 作为位置参数（`naturo app quit notepad`），与 launch/switch/hide/unhide 一致。`--name` 保留为隐藏的向后兼容选项。

### BUG-006: scroll 不接受位置参数 → 支持位置参数（P2 - UX）
**发现日期**: 2026-03-22 (Round 2)
**修复日期**: 2026-03-22 (commit c9418ba)
**修复内容**: `scroll` 现在接受方向作为可选位置参数（`naturo scroll down`），同时保留 `--direction` 选项。

---

## ✅ Verified

### BUG-001: naturo_msaa_get_element_tree 函数缺失（P0）
**发现日期**: 2026-03-22
**修复日期**: 2026-03-22
**验证日期**: 2026-03-22 (Round 2)

**验证结果**: ✅ 通过
- `naturo list windows` → 正常（SSH 下无桌面窗口但不报错，提示清楚）
- `naturo list windows --json` → 合法 JSON，`{"success": true, "windows": []}`
- `naturo see` → "No window found or UI tree is empty"（合理，SSH 无桌面）
- 不再报 `function 'naturo_msaa_get_element_tree' not found`

---

### BUG-002: README 命令示例与实际不符（P1 - DOC）
**发现日期**: 2026-03-22
**修复日期**: 2026-03-22 (commit 1c89246)
**验证日期**: 2026-03-22 (Round 2)

**验证结果**: ✅ 部分通过（原报告的 5 处已修正）
- `naturo --version` ✅ 正确
- `naturo list windows` ✅ 正确
- `naturo see --window-title "Notepad"` ✅ 参数名正确
- `naturo registry get/set` ✅ 子命令名正确

**新增不一致**: → 已拆分为 BUG-004、BUG-005

---

## 质量评估

**当前状态**: 🟡 **条件可用** — 核心 DLL 问题已修复，但文档仍有不一致

**改善点**:
- BUG-001 (P0 核心阻塞) 已修复验证 ✅
- BUG-002 (P1 文档主要问题) 已部分修复 ✅
- 基础命令全部可用：app list、list screens、service list/status、clipboard get/set、registry get/list、capture live、snapshot list

**待解决**:
- 3 个文档不一致 (BUG-004/005/006)
- pyvda 依赖决策 (BUG-003)
- 输入命令 (press/hotkey/type/click/scroll) 在 SSH 下报 System/COM error（预期行为，但错误信息可以更友好）

**风险评估**:
| 风险类型 | 等级 | 说明 |
|---------|------|------|
| 功能完整性 | 🟡 中等 | 核心 DLL 已修复，需要桌面 session 验证 UI 操作 |
| 用户体验 | 🟡 中等 | 文档仍有 3 处不一致 |
| 文档质量 | 🟡 中等 | 大部分修正，仍有遗漏 |
| 竞争力 | 📋 待验证 | 需要桌面 session 做完整 UI 自动化测试 |

---

最后更新: 2026-03-22 18:02 by QA Agent (Round 2)
