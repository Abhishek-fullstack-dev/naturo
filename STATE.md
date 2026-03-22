# Naturo 项目状态

**最后更新**: 2026-03-22 18:10  
**版本**: 0.1.0 (编译机)  
**状态**: 🟡 **条件可用** — 核心 DLL 已修复，文档仍需完善

---

## 当前阶段

Phase 1: 核心功能实现（进展中）

---

## 已修复问题

### ✅ BUG-001: DLL 函数缺失 → 已修复验证
- UI 自动化核心功能恢复
- `list windows`/`see`/`find` 不再崩溃
- 仍需桌面 session 做完整 UI 操作验证

### ✅ BUG-002: README 5 处不一致 → 已修复验证
- version、list、see、registry 命令文档已修正

---

## 待修复问题

### 🟢 BUG-004: README `press "ctrl+s"` → `hotkey ctrl+s` (P1) — 已修复 c9418ba
### 🟢 BUG-005: `app quit` 支持位置参数 (P1) — 已修复 c9418ba
### 🟢 BUG-006: scroll 支持位置参数 (P2) — 已修复 c9418ba
### 🔴 BUG-003: pyvda 依赖缺失 (P2，需产品决策)

---

## 可用功能 (~40% 已验证)

- ✅ `naturo --version`
- ✅ `naturo app list` / `app launch` / `app quit --name` / `app switch`
- ✅ `naturo list windows` / `list screens`
- ✅ `naturo see` (SSH 下无窗口但不崩溃)
- ✅ `naturo capture live --path`
- ✅ `naturo service list` / `service status`
- ✅ `naturo clipboard get` / `clipboard set`
- ✅ `naturo registry get` / `registry list`
- ✅ `naturo snapshot list` / `snapshot clean`
- ✅ `naturo learn` (帮助系统)
- ✅ `naturo find` (帮助格式正确，需桌面验证)

## 待桌面验证功能

以下功能在 SSH 下报 "System/COM error"（预期，需要交互式桌面）：
- ⏳ `naturo click` / `type` / `press` / `hotkey` / `scroll` / `drag` / `move`
- ⏳ `naturo window focus/close/minimize/maximize/move/resize`
- ⏳ `naturo dialog detect/accept/dismiss`
- ⏳ `naturo taskbar list/click` / `tray list/click`

## 不可用功能

- ❌ `naturo desktop *` — pyvda 未安装 (BUG-003)

---

## JSON 输出一致性

已验证 `--json` 输出合法 JSON 的命令：
- ✅ `list windows --json`
- ✅ `app list --json`
- ✅ `service list --json`
- ✅ `capture live --json`
- ✅ `snapshot list --json`
- ✅ `press enter --json` (错误时也返回合法 JSON)
- ✅ `app quit --name notepad --json`

---

## 测试覆盖

**已验证命令**: ~20/76 (26%)
**通过率**: 15/20 (75%)
**文档不一致**: 3 处 (BUG-004/005/006)

---

## 质量门禁

**当前状态**: 🟡 **接近可用** — 阻塞性问题已解决

**发布前必须**:
- ✅ BUG-001 修复并验证
- ✅ README 主要不一致已修正
- 🔲 BUG-004/005/006 修复
- 🔲 核心命令桌面 session 验证
- 🔲 pyvda 依赖策略确定

**下一步**:
1. Dev 修复 BUG-004/005/006（文档 + app quit API 一致性）
2. 在有桌面的环境下做 UI 操作完整测试
3. 决策 pyvda 依赖策略

---

最后更新: 2026-03-22 18:02 by QA Agent (Round 2)
