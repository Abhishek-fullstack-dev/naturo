# Naturo 项目状态

**最后更新**: 2026-03-22 19:15  
**版本**: 0.1.1 (编译机已同步至 commit 7301bf1)  
**状态**: 🟡 **接近可发布** — BUG-011/012 已验证，新发现 BUG-013 (service list --state running)

---

## 当前阶段

Phase 1: 核心功能实现（进展中）

---

## 已验证修复 (Round 3)

### ✅ BUG-001: DLL 函数缺失 → 已修复验证
### ✅ BUG-002: README 5 处不一致 → 已修复验证
### ✅ BUG-004: README `press "ctrl+s"` → `hotkey ctrl+s` → 已修复验证 (v0.1.1)
### ✅ BUG-005: `app quit` 支持位置参数 → 已修复验证 (v0.1.1)
### ✅ BUG-006: scroll 支持位置参数 → 已修复验证 (v0.1.1)
### ✅ BUG-007: `electron list` 挂起 → 已验证通过 (Round 4)
### ✅ BUG-008: `learn <topic>` 内容空洞 → 已验证通过 (Round 4)

---

## 待修复问题

### 🔴 BUG-013: `service list --state running` 返回 0 结果 (P1，sc.exe state= 参数错误)
### 🔴 BUG-003: pyvda 依赖缺失 (P2，需产品决策)

## 已验证修复 (Round 7)

### ✅ BUG-012: `learn interaction` 教程命令语法错误 → Verified (Round 7)
### ✅ BUG-011: `learn capture` 引用 `--region` 参数 → Verified (Round 7)

---

## 可用功能 (~50% 已验证)

- ✅ `naturo --version` (v0.1.1)
- ✅ `naturo --help` (30+ 命令组)
- ✅ `naturo capture live --path` + `--json`
- ✅ `naturo list windows/screens` + `--json`
- ✅ `naturo app list/launch/quit/switch/find` + `--json`
- ✅ `naturo service list/status` + `--json`
- ✅ `naturo clipboard get/set` + `--json`
- ✅ `naturo registry list/get` + `--json`
- ✅ `naturo snapshot list/clean` + `--json`
- ✅ `naturo record list` + `--json`
- ✅ `naturo electron detect` + `--json`
- ✅ `naturo mcp tools` (76 MCP tools)
- ✅ `naturo open <url>` / `open <nonexistent>`
- ✅ `naturo see/find` (SSH 下 graceful error)
- ✅ `naturo learn` (topic 列表正确)
- ✅ `naturo scroll down` (位置参数生效)
- ✅ `naturo app quit notepad` (位置参数生效)
- ✅ `naturo dialog detect --json` → 合法 JSON
- ✅ `naturo window list --json` → 合法 JSON  
- ✅ `naturo record stop --json` → 合法 JSON 错误 (无录制时)
- ✅ `naturo record play nonexistent --json` → 合法 JSON 错误
- ✅ `naturo paste --help` → 完整参数
- ✅ `naturo move --help` → 完整参数
- ✅ `naturo drag --help` → 完整参数
- ✅ `naturo wait --help` → 完整参数
- ✅ `naturo describe --help` → 完整参数 (支持 anthropic/openai/ollama)
- ✅ `naturo agent --help` → 完整参数 (支持 dry-run/verbose)
- ✅ `naturo mcp tools --json` → 82 个 MCP 工具
- ✅ 错误输出结构化 JSON (code + message + suggested_action + recoverable)

## 待桌面验证功能

- ⏳ `naturo click/type/press/hotkey/scroll/drag/move` (SSH 下报 COM error)
- ⏳ `naturo window focus/close/minimize/maximize/move/resize`
- ⏳ `naturo dialog detect/accept/dismiss`
- ⏳ `naturo taskbar list/click` / `tray list/click`

## 不可用/有问题功能

- ❌ `naturo desktop *` — pyvda 未安装 (BUG-003)
- 🟢 `naturo taskbar *` / `naturo tray *` — 已修复，待桌面验证 (BUG-009)
- ✅ `naturo electron list` — 已验证修复 (BUG-007)
- ✅ `naturo learn <topic>` — 内容已充实，引用已修正 (BUG-008/010)

---

## JSON 输出一致性

已验证 `--json` 输出合法 JSON 的命令：
- ✅ `list windows/screens --json`
- ✅ `app list/quit/find --json`
- ✅ `service list/status --json`
- ✅ `capture live --json`
- ✅ `snapshot list --json`
- ✅ `clipboard get/set --json`
- ✅ `registry list --json`
- ✅ `record list --json`
- ✅ `electron detect --json`
- ✅ `mcp tools --json`
- ✅ `hotkey/press --json` (错误时也返回合法 JSON)
- ✅ `see --json` (错误时也返回合法 JSON)
- ✅ `chrome tabs --json` (CDP 连接错误也返回合法 JSON)

---

## 测试覆盖

**已验证命令**: ~42/82 (51%)
**通过率**: 37/42 (88%)
**失败**: desktop 缺依赖 (pyvda), learn 教程语法错误

---

## 质量门禁

**当前状态**: 🟡 **接近可发布**

**已完成**:
- ✅ P0 bug 全部修复验证
- ✅ README 一致性修正
- ✅ 核心 CLI 命令可用
- ✅ JSON 输出一致
- ✅ 错误信息结构化且友好

**发布前必须**:
- ✅ BUG-007 (electron list 挂起) 已修复
- 🔲 核心命令桌面 session 验证
- 🔲 pyvda 依赖策略确定

**下一步**:
1. ~~Dev 修复 electron list 超时问题~~ ✅ 已验证
2. ~~Dev 修复 taskbar/tray get_ui_tree 缺失 (BUG-009)~~ ✅ 已修复
3. ~~Dev 修复 learn 教程引用错误 (BUG-010)~~ ✅ 已修复
4. 在有桌面的环境下做 UI 操作完整测试
5. 决策 pyvda 依赖策略

---

最后更新: 2026-03-22 19:15 by QA Agent (Round 7: BUG-011/012 验证通过，新发现 BUG-013)
