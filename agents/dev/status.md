# Dev Status

## 最近工作
- **Phase 6 macOS Backend** — 完整 Peekaboo CLI wrapper，40+ methods，791 行测试
- **Phase 5.1 Open Source Launch** — npm 包 `npx naturo mcp` 完成，CHANGELOG.md 首版
- **代码质量** — 1461 tests passing, 0 failures

## 技术评估
- 代码健康度：良好
- 测试：1461 passed, 295 skipped, 0 failed ✅
- MCP server: 76 tools
- **零 🔴 Open bug** — 全部 bugs 已 Fixed 或 Verified
- 无 TODO/FIXME/HACK
- macOS backend: 40+ 方法完整实现（capture/list/see/click/type/window/app/clipboard/dialog）

## Phase 进度
- Phase 4 ~ 5C: ✅ Complete
- Phase 5.1 Open Source Launch: 🔄 In Progress (阻塞于 Ace 创建 GitHub Release)
- **Phase 6 macOS Backend: 🔄 In Progress (核心完成，需要 macOS 集成测试)**
  - [x] Peekaboo CLI wrapper (subprocess)
  - [x] capture/list/see
  - [x] click/type/press/hotkey/scroll/drag
  - [x] window management (focus/close/minimize/maximize/move/resize)
  - [x] app lifecycle (launch/quit/list)
  - [x] clipboard get/set
  - [x] menu inspection
  - [x] dialog handling
  - [x] multi-monitor support
  - [x] 791 行 mock 测试
  - [ ] macOS 真机集成测试（需要 Peekaboo 安装）
  - [ ] CI macOS runner

## 阻塞
- 编译机 192.168.31.52 不可达（connection refused）
- Phase 5B.4 SAP GUI Scripting — 需要 SAP 测试环境
- Phase 5B.6 MinHook — 需要编译机编译 C++
- Phase 5C.1 Excel COM — 需要编译机
- Phase 5.1 PyPI 发布 — 需 Ace 创建 GitHub Release

## 下一步
- 等 Ace 创建 GitHub Release 触发首次 PyPI 发布
- macOS 真机测试（需安装 Peekaboo）
- 编译机恢复后录制 hero GIF + 继续 Windows 功能测试
