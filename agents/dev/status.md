# Dev Status

## 最近工作
- **Phase 5B.1 完成** — MSAA/IAccessible accessibility backend (commit f03ccfe)
  - C++ 层: `core/src/msaa.cpp` — IAccessible 树遍历 + BFS 元素查找
  - Bridge: `naturo_msaa_get_element_tree`/`find_element` 绑定
  - Backend: `get_element_tree()` 支持 `backend='uia'|'msaa'|'auto'`
  - CLI: `see`/`find` 新增 `--backend/-b` 选项
  - MCP: `see_ui_tree` 新增 `accessibility_backend` 参数
  - 15 个新测试
  - 支持 legacy 应用自动化: MFC, VB6, Delphi, Win32 native
- **Phase 5A backend 代码提交** (commit 67f4a3c)
  - Virtual desktop + DPI 坐标转换 WindowsBackend 实现

## 技术评估
- 代码健康度：良好
- 测试：1201 passed, 250 skipped
- MCP server: 38 tools (含 accessibility_backend 参数)
- 零 🔴 Open bug，BUG-055 待 QA 验证

## Phase 进度
- Phase 4: ✅ Complete
- Phase 4.5: ✅ Complete
- Phase 5A: ✅ Complete
- Phase 5B.1: ✅ Complete (MSAA/IAccessible)
- **下一步: Phase 5B.2 (IAccessible2) 或编译机验证 MSAA**

## 风险预警
- 编译机 192.168.31.52 凌晨不可达（SSH refused），MSAA C++ 代码尚未编译验证
- MSAA 的 "auto" 模式 fallback 逻辑基于 UIA 返回空树的判断，需实际测试 edge case
- BFS 搜索在大型 MSAA 树上可能较慢（无深度限制），需关注性能

## 下一步
1. 编译机上线后编译 + 测试 MSAA（最重要）
2. Phase 5B.2 — IAccessible2 (Firefox/Thunderbird)
3. 或 Phase 5B.7 — UIA 缓存优化（性能提升）
