# Naturo 项目状态

**最后更新**: 2026-03-22 17:28  
**版本**: 0.1.0 (编译机)  
**状态**: 🛑 **阻塞** — 核心功能不可用

---

## 当前阶段

Phase 1: 核心功能实现（受阻）

---

## 紧急问题

### 🚨 P0 阻塞性问题

**BUG-001: naturo_msaa_get_element_tree 函数缺失**
- **影响**: 所有 UI 自动化功能不可用（占产品核心价值 80%+）
- **受影响**: window/see/click/type/find/dialog/taskbar/tray 所有命令
- **状态**: 需要 Dev 立即修复 C++ DLL 导出或 Python 绑定

---

## 可用功能 (20%)

- ✅ 版本查询 (`--version`)
- ✅ 进程列表 (`app list`)
- ✅ 屏幕列表 (`list screens`)
- ✅ 服务管理 (`service list/start/stop`)
- ✅ 剪贴板操作 (`clipboard get/set`)
- ✅ 快照管理 (`snapshot list/clean`)

---

## 阻塞功能 (80%)

所有依赖 `naturo_msaa_get_element_tree` 的功能：
- ❌ UI 元素检测与交互
- ❌ 窗口管理
- ❌ 自动化输入
- ❌ 对话框处理
- ❌ Taskbar/Tray 交互

---

## 文档质量

**状态**: 🟡 **差** — README 与实际命令大量不一致

**已知不一致**:
- `naturo version` → 应为 `naturo --version`
- `naturo list --type windows` → 应为 `naturo list windows`
- `--window` 参数 → 应为 `--window-title`
- `registry read/write` → 应为 `registry get/set`

参见 bugs.md BUG-002

---

## 依赖问题

- `pyvda` 未包含在安装包中，导致 Virtual Desktop 功能不可用
- 需要决策：必需依赖还是可选功能？

---

## 测试覆盖

**已测命令**: ~15/76 (20%)  
**通过率**: 6/15 (40%)  
**阻塞率**: 9/15 (60%) — 全部因 BUG-001

**下一轮测试计划**:
1. 等待 BUG-001 修复
2. 全量测试所有 76 个 MCP 工具对应的 CLI 命令
3. README 一致性全覆盖验证
4. 错误处理和边界情况

---

## 风险评估

| 风险类型 | 等级 | 说明 |
|---------|------|------|
| 功能完整性 | 🔴 极高 | 核心功能不可用 |
| 用户体验 | 🔴 极高 | 首次运行即报错 |
| 文档质量 | 🟡 中等 | 大量示例错误 |
| 竞争力 | 🔴 极高 | 无法与 Peekaboo/pywinauto 竞争 |

---

## 下一步行动

1. **Dev 修复 BUG-001** (P0)
2. **QA 全量回归测试** (等 BUG-001 修复后)
3. **Dev 修复文档** (BUG-002)
4. **产品决策**: pyvda 依赖策略

---

## 质量门禁

**当前状态**: 🛑 **不可发布**

**发布前必须**:
- ✅ BUG-001 修复并验证
- ✅ README 与实际命令 100% 一致
- ✅ 核心命令（see/click/type/window）可用
- ✅ 错误信息清晰友好

**发布前建议**:
- 🔲 全部 76 个工具测试通过
- 🔲 至少 2 个完整用户旅程测试通过
- 🔲 与 Peekaboo (macOS) 行为一致性验证

---

最后更新: 2026-03-22 by QA Agent
