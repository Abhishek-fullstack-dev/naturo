# Naturo Bug Tracker

状态说明: 🔴 Open | 🟡 Fixing | 🟢 Fixed | ✅ Verified

---

## 🔴 严重

### ✅ BUG-007: `app hide/unhide/switch` stub 暴露给用户
- **状态**: ✅ Verified
- **命令**: `naturo app --help`
- **修复**: hidden=True (commit d181eae)

### ✅ BUG-013: `app launch` 对不存在的应用假报成功
- **状态**: ✅ Verified (Round 4) — 友好错误 "Application not found: nonexistent_app_xyz"，无 traceback，exit code 非零。JSON 模式输出结构化 APP_NOT_FOUND 错误。
- **命令**: `naturo app launch nonexistent_app_xyz`
- **文件**: naturo/process.py

### ✅ BUG-014: `see/find/menu-inspect --json` 错误时输出纯文本
- **状态**: ✅ Verified
- **修复**: commit e6443ea

### ✅ BUG-015: `capture live --app X --json` 错误时输出纯文本
- **状态**: ✅ Verified (part of BUG-014 fix)

### ✅ BUG-016: `wait --json` 超时时输出两段 JSON
- **状态**: ✅ Verified (Round 4) — 只输出一段 JSON，success=false，"success" 仅出现一次，exit code 非零
- **命令**: `naturo wait --element "Button:Save" --timeout 1 --json`
- **修复**: try/except 只包裹 wait 调用本身，JSON 输出逻辑移到 try 外部；用 sys.exit(1) 替代 ctx.exit(1)
- **文件**: naturo/cli/wait_cmd.py

### ✅ BUG-010: Unicode 参数显示乱码
- **状态**: ✅ Verified
- **修复**: commit 77f3b1d

## 🟡 中等

### ✅ BUG-008: `app find` 找不到时退出码为 0
- **状态**: ✅ Verified
- **修复**: commit a97771a

### ✅ BUG-011: `find --json` 无窗口时输出纯文本
- **状态**: ✅ Verified (merged into BUG-014)

### BUG-017: 中文路径导致临时文件失败 + 残留
- **状态**: ✅ Verified (Round 3) — 中文路径创建成功，合法 PNG (magic bytes 89504e47)，无临时文件残留
- **命令**: `naturo capture live --path test_中文.png`
- **修复**: 使用 tempfile.mkstemp + 失败时清理
- **文件**: naturo/backends/windows.py

### ✅ BUG-018: `app relaunch` 对不存在的应用也假报成功
- **状态**: ✅ Verified (Round 4) — 友好错误 "Application not found: nonexistent_xyz"，无 traceback，exit code 非零
- **命令**: `naturo app relaunch nonexistent_xyz`
- **文件**: naturo/process.py

### ✅ BUG-019: `press --count 0` 和 `--count -1` 不报错
- **状态**: ✅ Verified
- **修复**: commit ae0ebcb

## 🟢 低

### ✅ BUG-009: `app find ""` 匹配到 System Idle Process
- **状态**: ✅ Verified
- **修复**: commit fe31b2c

### ✅ BUG-012: `list windows` 无桌面时返回空数组无提示
- **状态**: ✅ Verified
- **修复**: commit 259bf92

### ✅ BUG-020: `wait --timeout -1` 不校验
- **状态**: ✅ Verified
- **修复**: commit ce840ae

### ✅ BUG-021: `snapshot clean --days -1` 不校验
- **状态**: ✅ Verified
- **修复**: commit ce840ae

---

## 🆕 Round Full 新发现

### BUG-022: `snapshot clean` 无参数时 exit code 为 0
- **状态**: ✅ Verified (Round 5) — stderr 输出 "Error: Specify --days N or --all."，exit code 1。JSON 模式输出 INVALID_INPUT 结构化错误。
- **命令**: `naturo snapshot clean`
- **修复**: err=True + SystemExit(1)
- **文件**: naturo/cli/snapshot.py

### BUG-023: `learn` 不存在的 topic 静默 fallback
- **状态**: ✅ Verified (Round 5) — 报错 "Error: Unknown topic: nonexistent_topic"，列出可用 topics，exit code 1。
- **命令**: `naturo learn nonexistent_topic`
- **文件**: naturo/cli/core.py

### BUG-024: JSON 输出格式不一致（`ok` vs `success`）
- **状态**: ✅ Verified (Round 5) — click/type/press/scroll 全部统一为 `{"success": bool, "error": {"code": "...", "message": "..."}}` 格式，exit code 与 success 字段一致。
- **严重度**: 中（影响 AI agent 集成）
- **文件**: naturo/cli/interaction.py

### BUG-025: `scroll -a 0` 和 `-a -1` 无边界校验
- **状态**: ✅ Verified (Round 5) — `scroll -a 0` 和 `-a -1` 均报 "Error: --amount must be >= 1, got X"，exit code 1。
- **命令**: `naturo scroll -a 0`, `naturo scroll -a -1`
- **文件**: naturo/cli/interaction.py

### BUG-026: `menu-inspect --app nonexistent` 不区分应用不存在
- **状态**: ✅ Verified (Round 5) — 输出 "Error: Application not found: nonexistent"，JSON 模式返回 APP_NOT_FOUND 错误码，exit code 1。
- **命令**: `naturo menu-inspect --app nonexistent`
- **文件**: naturo/cli/core.py

### BUG-027: `menu-inspect` success=false 时 exit code 为 0
- **状态**: ✅ Verified (Round 5) — success=false 时 exit code 为 1。
- **命令**: `naturo menu-inspect --json`
- **文件**: naturo/cli/core.py

### BUG-028: `see/find --depth` 边界值无校验
- **状态**: ✅ Verified (Round 5) — depth 0/-1/11 均报 "Error: --depth must be between 1 and 10, got X"，exit code 1。
- **命令**: `naturo see --depth 0`, `naturo see --depth -1`, `naturo find Save --depth 0`
- **文件**: naturo/cli/core.py

---

## 🆕 Round 6 自发现（E2E 验收前扫描）

### BUG-029: `list windows --json` 和 `snapshot list --json` 返回裸数组
- **状态**: ✅ Verified (Round 9) — `list windows --json` 返回 `{"success": true, "windows": [...]}`，`snapshot list --json` 返回 `{"success": true, "snapshots": [...]}`，格式统一。
- **严重度**: 中（影响 AI agent 集成 — JSON schema 不一致）
- **现象**: 其他命令的 `--json` 成功响应都是 `{"success": true, ...}` 对象，但 `list windows --json` 和 `snapshot list --json` 直接返回裸数组 `[...]`
- **命令**: `naturo list windows --json`, `naturo snapshot list --json`
- **预期**: `{"success": true, "windows": [...]}` 和 `{"success": true, "snapshots": [...]}`
- **文件**: naturo/cli/core.py (windows 函数), naturo/cli/snapshot.py (snapshot_list 函数)

### BUG-030: `capture live --json` 成功时缺少 `success` 字段
- **状态**: ✅ Verified (Round 7) — 成功时输出 `{"success": true, "path":..., "width":..., "height":..., "format":..., "snapshot_id":...}`。
- **严重度**: 中（JSON schema 不一致）
- **现象**: 成功时输出 `{"path":..., "width":..., "height":..., "format":..., "snapshot_id":...}`，缺少 `"success": true`
- **对比**: `app list --json` 和 `app find --json` 都有 `success` 字段
- **命令**: `naturo capture live --json`
- **文件**: naturo/cli/core.py (capture live 相关)

### BUG-031: `snapshot clean --json` 成功时缺少 `success` 字段
- **状态**: ✅ Verified (Round 9) — `snapshot clean --days 9999 --json --yes` 返回 `{"success": true, "deleted": 0}`，格式正确。
- **严重度**: 低（JSON schema 不一致）
- **现象**: 成功删除时输出 `{"deleted": N}`，缺少 `"success": true`
- **命令**: `naturo snapshot clean --days 30 --json`
- **文件**: naturo/cli/snapshot.py (snapshot_clean 函数 line 117-118)

### BUG-032: `type --wpm` 无边界校验
- **状态**: ✅ Verified (Round 9) — `--wpm 0` 报 "Error: --wpm must be >= 1, got 0"，`--wpm -1` 报错，均 exit code 非零。
- **严重度**: 低（同 BUG-019/BUG-025 类型）
- **现象**: `--wpm 0` 和 `--wpm -1` 不报错，直接传给后端
- **命令**: `naturo type --wpm 0 hello`, `naturo type --wpm -1 hello`
- **预期**: 校验 wpm >= 1，否则报 "Error: --wpm must be >= 1, got X"
- **文件**: naturo/cli/interaction.py

---

---

## 🆕 Round 7 自发现

### BUG-033: `drag --steps 0`/`--steps -1` 和 `--duration -1` 无边界校验
- **状态**: ✅ Verified (Round 8) — `--steps 0` 报 "Error: --steps must be >= 1, got 0"，`--steps -1` 报错，`--duration -1` 报 "Error: --duration must be >= 0, got -1.0"，全部 exit code 1。
- **严重度**: 低（同 BUG-019/025/032 类型）
- **现象**: `--steps 0`、`--steps -1`、`--duration -1` 均不报错，直接传给后端
- **命令**: `naturo drag --from-coords 100 100 --to-coords 200 200 --steps 0`, `--steps -1`, `--duration -1`
- **预期**: `--steps >= 1`，`--duration >= 0`，否则报 "Error: --steps must be >= 1, got X"
- **文件**: naturo/cli/interaction.py (drag 函数)

### BUG-034: `wait --interval -1` 泄漏 Python 内部错误
- **状态**: ✅ Verified (Round 9) — `--interval -1` 返回 `{"success": false, "error": {"code": "INVALID_INPUT", "message": "--interval must be > 0, got -1.0"}}`，`--interval 0` 同理，均 exit code 1。
- **严重度**: 中（错误信息面向用户原则违反 + 同类遗漏）
- **现象**: `naturo wait --interval -1 --element test --json` 返回 `{"success": false, "error": {"code": "UNKNOWN_ERROR", "message": "sleep length must be non-negative"}}`，泄漏 Python sleep 内部错误
- **命令**: `naturo wait --interval -1 --element test --json`
- **预期**: 校验 `--interval > 0`，报 "Error: --interval must be > 0, got -1.0"。同时 `--interval 0` 应该被拒绝（导致 CPU 空转）
- **文件**: naturo/cli/wait_cmd.py

---

---

## 🆕 Round 8 自发现

### BUG-035: `click --wait-for` 参数声明了但未实现
- **状态**: ✅ Verified (Round 9) — `click --help` 不再显示 `--wait-for` 参数，已隐藏。
- **严重度**: 中（帮助和行为不一致 — 设计原则 #4 违反）
- **现象**: `click --help` 显示 `--wait-for FLOAT  Wait for element (seconds)`，但函数体中 `wait_for` 参数被接收后从未使用，传任何值都无效
- **命令**: `naturo click --wait-for 5 --coords 100 100`（不会等待 5 秒）
- **修复**: hidden=True 隐藏参数，保留向后兼容（commit 9dcf5de）
- **文件**: naturo/cli/interaction.py (click 函数)

### BUG-036: `move --duration` 参数声明了但未传给 backend
- **状态**: ✅ Verified (Round 9) — `move --help` 不再显示 `--duration` 参数，已隐藏。
- **严重度**: 低（帮助和行为不一致 — 设计原则 #4 违反）
- **现象**: `move --help` 显示 `--duration FLOAT  Move duration (seconds)`，但 `move()` 函数中调用 `backend.move_mouse(x, y)` 时没传 duration 参数，且无边界校验
- **命令**: `naturo move --duration 2 --coords 100 100`（不会花 2 秒移动）
- **修复**: hidden=True 隐藏参数，保留向后兼容（commit 9cb6539）
- **文件**: naturo/cli/interaction.py (move 函数)

### BUG-037: `hotkey --hold-duration` 无边界校验
- **状态**: ✅ Verified (Round 9) — `--hold-duration -1` 报 "Error: --hold-duration must be >= 0, got -1.0"，exit code 非零。`--hold-duration 0` 正常接受。
- **严重度**: 低（同 BUG-019/025/032/033 类型）
- **现象**: `--hold-duration -1` 和 `--hold-duration 0` 不校验，负值直接传给 backend（`hold_duration_ms=int(hold_duration)`）
- **命令**: `naturo hotkey --hold-duration -1 ctrl+c`
- **修复**: 校验 hold_duration >= 0，负值报 INVALID_INPUT 错误（commit c35a0f7）
- **文件**: naturo/cli/interaction.py (hotkey 函数)

*Dev Agent 修复后更新状态为 🟢 Fixed，QA 验证后更新为 ✅ Verified*

---

## 🆕 Round 29 自发现（Phase 5A 代码审查 + JSON 一致性扫描）

### BUG-055: `find --json` 和 `menu-inspect --json` 成功时返回裸数组
- **状态**: 🟢 Fixed (commit 05b4b7d)
- **严重度**: 🟡 中等（同 BUG-029 类型 — JSON schema 不一致，影响 AI agent 集成）
- **现象**: BUG-029 修复了 `list windows --json` 和 `snapshot list --json` 的裸数组问题，但 `find --json` 和 `menu-inspect --json` 存在相同问题：
  - `find --json` 返回 `[{"id":..., "role":...}, ...]`（裸数组，第 646 行）
  - `menu-inspect --json` 返回 `[{"label":...}, ...]`（裸数组，第 823/825 行）
  - 其他成功响应都是 `{"success": true, ...}` 对象格式
- **预期**: 
  - `find --json` → `{"success": true, "elements": [...], "count": N}`
  - `menu-inspect --json` → `{"success": true, "menu_items": [...]}`
- **文件**: naturo/cli/core.py（find_cmd 函数第 646 行，menu_inspect 函数第 823/825 行）

---

## 🆕 Round 27 自发现（MCP Server 代码审查）

### BUG-054: Dialog MCP 工具缺少 `@server.tool()` 装饰器，AI Agent 完全无法访问
- **状态**: ✅ Verified (Round 28) — 代码审查确认 5 个 dialog 函数（dialog_detect/accept/dismiss/click_button/type）全部已添加 `@server.tool()` + `@_safe_tool` 双装饰器，与其他工具格式一致
- **严重度**: 🔴 严重（Phase 4.5 的 5 个 dialog 工具全部未注册到 MCP server）
- **现象**: `dialog_detect`, `dialog_accept`, `dialog_dismiss`, `dialog_click_button`, `dialog_type` 五个函数只有 `@_safe_tool` 装饰器，缺少 `@server.tool()` 装饰器。导致这些函数不会被 FastMCP 注册为工具，AI agent 通过 MCP 协议无法发现和调用任何 dialog 功能
- **对比**: 同文件中的 `describe_screen`, `identify_element`, `ai_find_element` 等函数都正确使用了 `@server.tool()` + `@_safe_tool` 双装饰器
- **影响**: AI agent 在自动化流程中遇到对话框时完全无法处理（无法检测、接受、拒绝、点击按钮或输入文本）
- **修复**: 在每个 dialog 函数的 `@_safe_tool` 上方添加 `@server.tool()`
- **文件**: naturo/mcp_server.py（第 1249-1430 行，5 个 dialog 函数）

---

## 🆕 Round 25 自发现（record 命令系统性测试）

### BUG-053: `record start/stop` 录制状态不跨进程持久化，整个录制流程无法工作
- **状态**: ✅ Verified (Round 26) — start→stop 跨进程正常，重复 start 被拒绝(RECORDING_ACTIVE)，无活跃录制 stop 返回 NO_RECORDING，record list 正确列出历史录制，JSON 格式和 exit code 均正确
- **严重度**: 🔴 严重（核心功能完全不可用）
- **现象**: `record start` 将录制状态存储在进程内存变量 `_active_recording` 中（`record_cmd.py` 第 21 行）。由于每次 naturo CLI 调用都是独立进程，`record start` 结束后状态丢失。后续的 `record stop` 永远报 "No recording in progress"
- **复现**:
  ```
  naturo record start --name "test" --json  → success
  naturo record stop --json                 → {"success": false, "error": {"code": "NO_RECORDING", ...}}
  ```
- **连锁问题**: 
  1. 连续多次 `record start` 都能成功（因为每次进程都是新的，`_active_recording` 始终为 None），不报 "A recording is already in progress"
  2. `record start` 不生成录制文件（只在 stop 时 save），所以 start 后 list 仍为空
  3. 其他命令中的 `record_action()` 调用也永远不会记录任何步骤（`_active_recording` 在新进程中是 None）
- **根因**: 录制状态必须持久化到文件系统（如 `~/.naturo/recordings/.active_recording.json`），而非内存变量
- **修复建议**: 
  - `record start` → 创建 `~/.naturo/recordings/.active` 文件，写入 recording_id、name、created_at
  - 其他命令的 `record_action()` → 检查 `.active` 文件存在则追加 step 到录制文件
  - `record stop` → 读取 `.active` 文件，保存完整录制，删除 `.active`
  - `record start` 再次调用时 → 检查 `.active` 文件存在则拒绝
- **文件**: naturo/cli/record_cmd.py（`_active_recording` 全局变量 + `_get/_set_active_recording` 函数）, naturo/recording.py

---

## 🆕 Round 20 自发现

### BUG-049: `see --app nonexistent` 返回 UNKNOWN_ERROR 而非 WINDOW_NOT_FOUND
- **状态**: ✅ Verified (Round 21) — `--json` 返回 `WINDOW_NOT_FOUND` 错误码，exit code 非零
- **严重度**: 🟡 中等（错误码不准确 — 影响 AI agent 错误恢复逻辑）
- **现象**: `naturo see --app nonexistent_app --json` 返回 `{"success": false, "error": {"code": "UNKNOWN_ERROR", "message": "Window not found: nonexistent_app"}}`。消息正确但错误码是 `UNKNOWN_ERROR`，应为 `WINDOW_NOT_FOUND`
- **根因**: `see` 命令的 generic `except Exception as e` 不区分 `WindowNotFoundError`，统一报 `UNKNOWN_ERROR`。而 `diff --window` 正确使用了 `WINDOW_NOT_FOUND`
- **命令**: `naturo see --app nonexistent_app --json`
- **预期**: `{"success": false, "error": {"code": "WINDOW_NOT_FOUND", "message": "Window not found: nonexistent_app"}}`
- **修复建议**: 在 except 块中 catch `WindowNotFoundError` 先于 `Exception`，使用 `e.code` 或直接 `WINDOW_NOT_FOUND`
- **文件**: naturo/cli/core.py（see 函数的 except 块，约第 435 行）

### BUG-050: `capture live --app nonexistent` 返回 CAPTURE_ERROR 而非 WINDOW_NOT_FOUND
- **状态**: ✅ Verified (Round 21) — `--json` 返回 `WINDOW_NOT_FOUND` 错误码，exit code 非零
- **严重度**: 🟡 中等（同 BUG-049 — 错误码不准确）
- **现象**: `naturo capture live --app nonexistent_app --json` 返回 `{"success": false, "error": {"code": "CAPTURE_ERROR", "message": "Window not found: nonexistent_app"}}`。消息正确但错误码是 `CAPTURE_ERROR`，应为 `WINDOW_NOT_FOUND`
- **根因**: `capture live` 的 generic except 统一用 `CAPTURE_ERROR`，不区分 `WindowNotFoundError`
- **命令**: `naturo capture live --app nonexistent_app --json`
- **预期**: `{"success": false, "error": {"code": "WINDOW_NOT_FOUND", "message": "Window not found: nonexistent_app"}}`
- **修复建议**: 同 BUG-049，在 except 块中优先 catch `WindowNotFoundError`
- **文件**: naturo/cli/core.py（capture live 函数的 except 块，约第 100 行）

### BUG-051: `describe --max-tokens 0` 和 `--max-tokens -1` 无边界校验
- **状态**: ✅ Verified (Round 21) — `--max-tokens 0` 报 INVALID_INPUT "must be >= 1, got 0"，`--max-tokens -1` 同理，exit code 非零
- **严重度**: 🟡 中等（同 BUG-019/025/032/033 类型 — 边界值无校验）
- **现象**: `--max-tokens 0` 和 `--max-tokens -1` 不报错，直接传给 AI provider。当前测试机因无 API key 先报 `AI_PROVIDER_UNAVAILABLE` 掩盖了问题，但有 key 时会导致 API 层错误泄漏
- **命令**: `naturo describe --max-tokens 0 --json`, `naturo describe --max-tokens -1 --json`
- **预期**: 校验 `--max-tokens >= 1`，报 "Error: --max-tokens must be >= 1, got X"
- **文件**: naturo/cli/ai.py（describe 函数，`max_tokens` 参数声明后无校验）

---

## 🆕 Round 15 自发现

### BUG-046: 隐藏 stub 命令仍可执行，输出纯文本且 exit code 为 0
- **状态**: ✅ Verified (Round 16) — 5 个 stub 命令均 exit code 1，JSON 模式输出 NOT_IMPLEMENTED 结构化错误，纯文本模式输出到 stderr
- **严重度**: 🟡 中等（违反设计原则 #1 + #6 — 未实现功能不暴露、--json 必须合法 JSON）
- **现象**: 多个 hidden=True 的 stub 子命令虽不在 `--help` 显示，但仍可通过直接输入命令名调用。调用后输出 "Not implemented yet — coming in Phase N"（纯文本），exit code 为 0，`--json` 模式也不输出 JSON
- **影响范围**:
  - `naturo list screens` → "Not implemented yet — coming in Phase 2"，exit 0
  - `naturo list apps` → "Not implemented yet — coming in Phase 2"，exit 0
  - `naturo list permissions` → "Not implemented yet — coming in Phase 2"，exit 0
  - `naturo capture video` → "Not implemented yet — coming in Phase 3"，exit 0
  - `naturo capture watch` → "Not implemented yet — coming in Phase 3"，exit 0
- **预期**: 方案 A（推荐）— 完全移除 stub 注册，未实现命令返回 "Error: No such command 'screens'"；方案 B — stub 函数输出结构化错误 `{"success": false, "error": {"code": "NOT_IMPLEMENTED", ...}}`，exit code 非零
- **文件**: naturo/cli/core.py（list 组的 screens/apps/permissions）, naturo/cli/capture.py 或类似（video/watch）

---

## 🆕 Round 12 自发现（clipboard/window/paste 新命令测试）

### BUG-044: Click 参数验证绕过 `--json` 输出（系统性问题）
- **状态**: ✅ Verified (Round 13)
- **严重度**: 🟡 中等（违反设计原则 #6 — --json 模式下任何输出必须是合法 JSON）
- **现象**: 当 Click 框架自身的参数验证失败时（`required=True` 缺失、`click.Path(exists=True)` 文件不存在），错误输出是 Click 的纯文本 Usage 信息，即使传了 `--json` 也无法拦截
- **影响范围**:
  - `clipboard set --file nonexistent.txt --json` → 纯文本 "Error: Invalid value for '--file'"
  - `paste --file nonexistent.txt --json` → 纯文本 "Error: Invalid value for '--file'"
  - `window move --app x --json`（缺少 --x/--y）→ 纯文本 "Error: Missing option '--x'"
  - `window resize --app x --json`（缺少 --width/--height）→ 纯文本 "Error: Missing option"
  - `window set-bounds --app x --x 0 --y 0 --json`（缺少 --width/--height）→ 纯文本
- **根因**: Click 在调用命令函数之前就验证 required 参数和 Path 类型，此时还没进入 try/except JSON 错误处理逻辑
- **修复建议**: 方案 A — 自定义 Click Group/Command 的 `invoke()` 方法，检测 `--json` 参数后用 try/except 包裹 Click 的参数解析；方案 B — 把 `required=True` 改成函数内手动校验 + 改 `click.Path(exists=True)` 为 `click.Path()`（不自动校验）然后函数内检查
- **文件**: naturo/cli/system.py, naturo/cli/interaction.py, naturo/cli/window_cmd.py

---

## 🆕 Phase 4 (MCP Server) — Round 10 续

### BUG-038: `hotkey` MCP tool 使用 `*keys` 导致完全无法调用
- **状态**: ✅ Verified — 已改为 `keys: list[str]`，空列表返回 INVALID_INPUT 错误
- **严重度**: 🔴 严重（AI Agent 核心功能完全不可用）
- **现象**: `hotkey` 工具定义为 `def hotkey(*keys: str)`，使用 Python varargs。FastMCP 将其转换为 JSON schema `{"keys": {"type": "string"}}`（单个 string），MCP 客户端传 `keys="ctrl+s"` 时报 `got an unexpected keyword argument 'keys'`
- **影响**: 所有 AI agent 尝试按快捷键时都会失败。这是 MCP 26 个工具中唯一一个完全无法工作的
- **修复**: 改为 `def hotkey(keys: list[str])`，空列表返回 INVALID_INPUT
- **文件**: naturo/mcp_server.py (hotkey 函数)

### BUG-039: MCP tool 缺少统一异常处理，backend 异常泄漏 Python 内部错误
- **状态**: ✅ Verified — 已添加 `@_safe_tool` 装饰器包装所有 26 个工具
- **严重度**: 🟡 中等（影响 AI agent 体验和错误恢复）
- **现象**: MCP 工具没有 try/except 包装 backend 调用。当 backend 抛出异常（如 COM error、NaturoCoreError）时，异常直接冒泡给 MCP 框架，AI agent 收到的是 Python traceback 而非结构化错误
- **修复**: `_safe_tool` 装饰器捕获所有异常，返回 `{"success": false, "error": {"code": "...", "message": "..."}}`
- **文件**: naturo/mcp_server.py（所有 tool 函数）

### BUG-040: `test_process.py::TestLaunchApp` 5 个测试因 mock 问题全挂
- **状态**: ✅ Verified — 已 mock `subprocess.run` alongside `subprocess.Popen`，Windows Python 3.14 全过
- **严重度**: 🟡 中等（测试基础设施问题，不影响产品功能）
- **现象**: `@patch("subprocess.Popen")` 同时影响了 `subprocess.run()`（run 内部用 Popen），导致 `where` 命令的 mock 结果格式错误：`ValueError: not enough values to unpack (expected 2, got 0)`
- **修复**: mock `naturo.process.subprocess.run` 和 `naturo.process.subprocess.Popen`（commit 8c8fb7a）
- **文件**: tests/test_process.py (TestLaunchApp 类)

---

## 🆕 Round 11 自发现（MCP Server 深度测试）

### BUG-041: `mcp start --port/--host` 参数被忽略，始终绑定 127.0.0.1:8000
- **状态**: ✅ Verified (Round 12) — `--port 3200` 实际绑定到 `localhost:3200`，参数正确传递
- **严重度**: 🔴 严重（MCP server 端口不可配置，多实例/代理场景完全不可用）
- **现象**: `naturo mcp start --transport sse --port 3100` 实际绑定到 `127.0.0.1:8000`。`--port 9999 --host 0.0.0.0` 同样无效。help 文档声称默认端口 3100，实际是 uvicorn 默认 8000
- **根因**: `run_server()` 接收了 host/port 参数但 `server.run(transport=transport)` 没传递
- **命令**: `naturo mcp start --transport sse --port 3100`
- **预期**: 绑定到 `localhost:3100`
- **实际**: 绑定到 `127.0.0.1:8000`
- **文件**: naturo/mcp_server.py (run_server 函数，第 881 行)

### BUG-042: `mcp install --json` 在 JSON 前混入纯文本 "Installing MCP dependencies..."
- **状态**: ✅ Verified (Round 12) — stdout 只输出 `{"success": true, "message": "MCP dependencies installed successfully"}`，无前缀文本
- **严重度**: 🟡 中等（违反设计原则 #6 — --json 模式下任何输出必须是合法 JSON）
- **现象**: stdout 输出 `Installing MCP dependencies...\n{"success": true, ...}`，前缀文本导致 JSON 解析失败
- **命令**: `naturo mcp install --json`
- **预期**: stdout 只输出 JSON，进度信息走 stderr 或不输出
- **文件**: naturo/cli/ai.py (install 函数，约第 110 行 `click.echo("Installing MCP dependencies...")`)

### BUG-043: `mcp start` 失败时 `--json` 不输出 JSON（uvicorn 日志泄漏）
- **状态**: ✅ Verified (Round 12) — JSON 模式下 uvicorn 日志被抑制至 CRITICAL，OSError 时输出结构化 JSON 错误
- **严重度**: 🟡 中等（违反设计原则 #6 + 错误信息不友好）
- **现象**: `naturo mcp start --transport sse --json` 端口被占用时，输出 uvicorn 的 INFO/ERROR 日志文本而非 JSON。异常被 uvicorn 内部处理，没到 CLI 的 except 分支
- **命令**: `naturo mcp start --transport sse --json`（端口被占用时）
- **预期**: `{"success": false, "error": {"code": "SERVER_ERROR", "message": "Port 8000 already in use"}}`
- **实际**: `INFO: Started server process...` + `ERROR: [Errno 10048]...`
- **文件**: naturo/cli/ai.py (start 函数) + naturo/mcp_server.py (run_server)

---

## 🆕 Round 14 自发现

### BUG-045: `diff --interval` 无边界校验（负值/零值）
- **状态**: ✅ Verified (Round 15) — `--interval -1` 报 "Error: --interval must be > 0, got -1.0"，`--interval 0` 同理，JSON 模式输出 INVALID_INPUT 结构化错误，均 exit code 非零。
- **严重度**: 🟡 中等（同 BUG-034 类型 — 负值导致 Python 内部错误泄漏）
- **现象**: `diff --interval -1 --window <存在的窗口>` 时，`time.sleep(-1)` 会抛出 `ValueError: sleep length must be non-negative`，泄漏 Python 内部错误。`--interval 0` 虽不崩溃但无意义（两次捕获间零间隔）
- **命令**: `naturo diff --interval -1 --window "Notepad"`, `naturo diff --interval 0 --window "Notepad"`
- **预期**: 校验 `--interval > 0`，报 "Error: --interval must be > 0, got X"
- **文件**: naturo/cli/diff_cmd.py (diff 函数，time.sleep(interval) 前无校验)

---

## 🆕 Round 16 自发现

### BUG-047: `describe --screenshot nonexistent.png` 报错 "AI provider unavailable" 而非 "file not found"
- **状态**: ✅ Verified (Round 17) — 文件不存在时返回 `FILE_NOT_FOUND` 错误码，纯文本模式输出 "Error: Screenshot file not found: nonexistent.png"，exit code 1
- **严重度**: 🟡 中等（误导性错误信息 — 违反设计原则 #5）
- **现象**: `naturo describe --screenshot nonexistent.png --json` 返回 `{"success": false, "error": {"code": "AI_PROVIDER_UNAVAILABLE", "message": "AI provider unavailable: auto"}}`。文件存在性检查在 provider 初始化之后，当无 API key 时先报 provider 错误，掩盖了真正的问题
- **命令**: `naturo describe --screenshot nonexistent.png --json`
- **预期**: 先检查 `--screenshot` 文件是否存在，报 `FILE_NOT_FOUND` 错误
- **修复建议**: 将 screenshot 文件存在性检查移到 provider 初始化之前
- **文件**: naturo/cli/ai.py (describe 函数，第 147 行附近)

---

## 🆕 Round 18 自发现

### BUG-048: `ctx.exit(1)` 在 Windows 上不设置 exit code — 系统性问题（39 处）
- **状态**: ✅ Verified (Round 19) — window resize/focus/close、diff、wait、app find 等错误路径全部 exit code 非零，JSON 输出 success=false 与 exit code 一致
- **严重度**: 🔴 严重（影响所有 AI agent 集成 — agent 无法判断命令是否成功）
- **现象**: 所有使用 `ctx.exit(1)` 的错误路径，实际 exit code 都为 0。`success=false` 但 exit code=0，AI agent 和脚本无法通过退出码判断命令执行结果
- **影响范围**: 
  - `window_cmd.py` — 19 处（focus/close/minimize/maximize/restore/move/resize/set-bounds 全部命令）
  - `app_cmd.py` — 9 处（quit/launch/relaunch/list/find）
  - `diff_cmd.py` — 6 处
  - `wait_cmd.py` — 5 处
  - **共 39 处**
- **验证**: 
  - `naturo window resize --app notepad --width 0 --height 100 --json` → `{"success": false, ...}` 但 exit code 0
  - `naturo window focus --json` → `{"success": false, ...}` 但 exit code 0
  - `naturo diff --json` → `{"success": false, ...}` 但 exit code 0
  - `naturo wait --element test --timeout 1 --json` → `{"success": false, ...}` 但 exit code 0
- **根因**: Click 的 `ctx.exit(1)` 在某些场景下（特别是 Windows Python 3.12）不能可靠地设置进程 exit code。BUG-016 已发现此问题并在 wait_cmd.py 部分位置改用了 `sys.exit(1)`，但修复不彻底
- **修复建议**: 全局替换所有 `ctx.exit(1)` 为 `sys.exit(1)`（39 处），或封装统一的 exit 函数
- **文件**: naturo/cli/window_cmd.py, naturo/cli/app_cmd.py, naturo/cli/diff_cmd.py, naturo/cli/wait_cmd.py

---

## 🆕 Round 23 自发现（Phase 4.7/4.8 新代码验证）

### BUG-052: `agent ""` 和 `agent "   "` 空指令不校验，报 AI_PROVIDER_UNAVAILABLE
- **状态**: ✅ Verified (Round 24) — 空字符串和纯空白均返回 INVALID_INPUT "Instruction cannot be empty"，exit code 非零，纯文本模式输出到 stderr
- **严重度**: 🟡 中等（同 BUG-047 类型 — 验证顺序问题，误导性错误信息）
- **现象**: `naturo agent "" --json` 返回 `{"success": false, "error": {"code": "AI_PROVIDER_UNAVAILABLE", "message": "AI provider unavailable: anthropic"}}`。空指令应该在 provider 初始化之前被拦截
- **命令**: `naturo agent "" --json`, `naturo agent "   " --json`
- **预期**: `{"success": false, "error": {"code": "INVALID_INPUT", "message": "Instruction cannot be empty"}}`
- **根因**: agent 函数在 max_steps 校验后直接调用 `_get_agent_provider()`，没有先校验 instruction 是否为空或纯空白
- **修复建议**: 在 max_steps 校验之后、provider 初始化之前，加入 `if not instruction.strip():` 校验
- **文件**: naturo/cli/ai.py（agent 函数，约第 55 行）
