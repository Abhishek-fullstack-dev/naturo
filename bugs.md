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

（无）

---

### BUG-001: naturo_msaa_get_element_tree 函数缺失（P0）
**发现日期**: 2026-03-22  
**影响**: 所有依赖 UI 元素检测的命令直接崩溃  
**受影响命令**:
- `naturo list windows`
- `naturo window list/close/focus` 等所有 window 子命令
- `naturo see`
- `naturo click`
- `naturo type`
- `naturo press`
- `naturo find`
- `naturo dialog detect/accept/dismiss`
- `naturo taskbar list/click`
- `naturo tray list/click`

**错误信息**:
```
Error: function 'naturo_msaa_get_element_tree' not found
```

**复现步骤**:
```bash
naturo list windows
naturo window close --app notepad --force
naturo see --window-title Notepad --depth 5
```

**原因**: 编译机上的 DLL (3/20 编译) 早于 MSAA 函数添加时间，未包含新导出函数

**修复**: 从 CI artifacts 下载最新 DLL (113KB, 含 MSAA/IA2/JAB 全部导出) 并部署到编译机。验证 `NaturoCore()` 初始化成功。

**修复日期**: 2026-03-22

---

### BUG-002: README 命令示例与实际不符（P1 - DOC）
**发现日期**: 2026-03-22  
**影响**: 用户按文档操作会报错，初次体验直接劝退

**错误示例汇总**:

| README 示例 | 实际命令 | 状态 |
|-------------|---------|------|
| `naturo version` | `naturo --version` | ❌ 命令不存在 |
| `naturo list --type windows` | `naturo list windows` | ❌ 参数错误 |
| `naturo see --window "Notepad"` | `naturo see --window-title "Notepad"` | ❌ 参数名错误 |
| `naturo registry read KEY` | `naturo registry get KEY` | ❌ 子命令名错误 |
| `naturo registry write KEY` | `naturo registry set KEY` | ❌ 子命令名错误 |

**复现**: 按照 README "Quick Start" 部分逐行执行命令

**建议**: 需要全面审查 README 中所有命令示例，或直接从 `--help` 输出生成文档

**修复**: commit 1c89246 修正了 5 处不一致（version→--version, list --type→list windows, --window→--window-title, registry read/write→get/set）

**修复日期**: 2026-03-22

---

### BUG-003: 缺少 pyvda 依赖导致虚拟桌面功能不可用（P2）
**发现日期**: 2026-03-22  
**影响**: Virtual Desktop 命令全部报错

**错误信息**:
```
Error: Virtual desktop support requires pyvda. Install: pip install pyvda
```

**复现**:
```bash
naturo desktop list
```

**建议**: 
1. 如果 pyvda 是必需依赖，应该写入 requirements.txt / setup.py
2. 如果是可选功能，应该在 README 中说明
3. 错误提示已经很清楚，但用户期望 `pip install naturo` 后所有功能开箱即用

---

## 🟢 Fixed

（无）

---

## ✅ Verified

（无）

---

## 质量评估

**当前状态**: 🛑 **不可发布**

**核心问题**: BUG-001 导致产品核心价值（UI 自动化）完全不可用

**风险评估**:
- **用户流失风险**: 🔴 极高 — 用户安装后第一条命令就报错
- **声誉风险**: 🔴 极高 — "产品不能用" 会传播得很快
- **竞争力**: 🔴 为零 — Peekaboo/pywinauto 都能正常使用

**可用功能**:
- ✅ `naturo --version`
- ✅ `naturo app list`
- ✅ `naturo list screens`
- ✅ `naturo service list`
- ✅ `naturo clipboard get/set`
- ✅ `naturo snapshot list/clean`

**阻塞功能** (占 README 宣传功能的 ~80%):
- ❌ 所有 UI 元素操作（see/click/type/find）
- ❌ 所有窗口管理（window 子命令）
- ❌ 所有对话框处理（dialog 子命令）
- ❌ Taskbar/Tray 交互

**下一步行动**:
1. **立即修复 BUG-001** — 这是第一优先级，阻塞所有其他测试
2. 修复后重新测试所有受影响命令
3. 修复文档 (BUG-002)
4. 决定 pyvda 依赖策略

---

最后更新: 2026-03-22 by QA Agent
