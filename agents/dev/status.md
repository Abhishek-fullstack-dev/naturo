# Dev Status

## 最近工作
- **Phase 5B.2 完成** — IAccessible2 backend (commit 1266292)
  - C++ 层: `core/src/ia2.cpp` — IAccessible2 via IServiceProvider::QueryService
  - IA2-extended roles: Heading, Paragraph, Landmark, Form, Footer, etc.
  - IA2 object attributes, states, unique IDs
  - BFS 元素搜索 + IA2 role matching
  - `naturo_ia2_check_support` 运行时检测
  - Bridge: `ia2_get_element_tree`/`ia2_find_element`/`ia2_check_support`
  - Backend: `get_element_tree()` 支持 `backend='ia2'`
  - auto 模式: UIA → IA2 → MSAA 三级 fallback
  - CLI: `see`/`find` 新增 `--backend ia2` 选项
  - MCP: `see_ui_tree` 接受 `ia2` 参数
  - 19 个新测试
- **Phase 5B.1 完成** — MSAA/IAccessible accessibility backend (commit f03ccfe)

## 技术评估
- 代码健康度：良好
- 测试：1220 passed, 256 skipped
- MCP server: 38 tools (含 accessibility_backend 参数支持 uia/msaa/ia2/auto)
- 零 🔴 Open bug，BUG-055 待 QA 验证

## Phase 进度
- Phase 4: ✅ Complete
- Phase 4.5: ✅ Complete
- Phase 5A: ✅ Complete
- Phase 5B.1: ✅ Complete (MSAA/IAccessible)
- Phase 5B.2: ✅ Complete (IAccessible2)
- **下一步: Phase 5B.3 (Java Access Bridge) 或编译机验证 MSAA + IA2**

## 风险预警
- 编译机 192.168.31.52 凌晨不可达（SSH refused），MSAA + IA2 C++ 代码均未编译验证
- IA2 interface vtable 布局需实际 Firefox 测试验证（COM vtable 偏移量是关键）
- auto 模式三级 fallback 逻辑（UIA → IA2 → MSAA）需实际 edge case 测试

## 下一步
1. 编译机上线后编译 + 测试 MSAA + IA2（最重要）
2. Phase 5B.3 — Java Access Bridge (Java/Swing/AWT)
3. 或 Phase 5B.7 — UIA 缓存优化（性能提升）
