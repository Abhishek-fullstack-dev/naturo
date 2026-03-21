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

## 🆕 Round 37 自发现（open 命令审查）

### BUG-065: `open ""` 和 `open "   "` 空目标不校验，报 success
- **状态**: ✅ Verified (Round 38) — 空字符串和纯空白均返回 `{"success": false, "error": {"code": "INVALID_INPUT", "message": "Target cannot be empty"}}`，exit code 1
- **严重度**: 🟡 中等（违反用户体验原则 — 无意义操作报成功）
- **现象**: `naturo open "" --json` 返回 `{"success": true, "target": ""}`，`naturo open "   " --json` 返回 `{"success": true, "target": "   "}`。空字符串和纯空白应被拦截
- **命令**: `naturo open "" --json`, `naturo open "   " --json`
- **预期**: `{"success": false, "error": {"code": "INVALID_INPUT", "message": "Target cannot be empty"}}`，exit code 1
- **修复建议**: 在 `open_cmd` 函数入口处添加 `if not target.strip():` 校验
- **文件**: naturo/cli/system.py（open_cmd 函数，第 257 行附近）

### BUG-066: `open --app` 参数声明但未实现，静默忽略
- **状态**: ✅ Verified (Round 38) — `open --help` 不再显示 `--app` 参数，已隐藏
- **严重度**: 🟡 中等（违反设计原则 #4 — 帮助和实际行为一致；同 BUG-035/036 类型）
- **现象**: `naturo open https://example.com --app notepad --json` 返回 `{"success": true, ...}`，但 URL 仍然用默认浏览器打开，`--app notepad` 被完全忽略。代码注释写 `# Future: --app option for opening with specific application`
- **命令**: `naturo open https://example.com --app notepad --json`
- **预期**: 方案 A（推荐）— 隐藏 `--app` 参数（hidden=True），等实现后再暴露；方案 B — 实现 `--app`（Windows 上用 `start /D "" appname target`）
- **文件**: naturo/cli/system.py（open_cmd 函数，第 260 行 `# Future` 注释）

### BUG-067: `open nonexistent_file.xyz` 挂起（Windows `start` 弹对话框阻塞）
- **状态**: ✅ Verified (Round 38) — 不存在的文件返回 `{"success": false, "error": {"code": "FILE_NOT_FOUND", "message": "File not found: nonexistent_file_xyz.txt"}}`，exit code 1，不再挂起
- **严重度**: 🔴 严重（命令永远不返回，AI agent 会卡死）
- **现象**: `naturo open nonexistent_file.xyz --json` 在 SSH 下永远不返回。`subprocess.run(["start", uri], shell=True)` 调用 Windows `start` 命令，打开不存在的文件时弹出错误对话框，阻塞进程
- **命令**: `naturo open nonexistent_file.xyz --json`
- **预期**: 先检查文件是否存在（非 URL 时），不存在则返回 `FILE_NOT_FOUND` 错误。或者 `subprocess.run` 添加 timeout 参数防挂起
- **修复建议**: 
  1. 判断 target 是 URL（http/https）还是文件路径
  2. 文件路径时先检查 `os.path.exists(target)`，不存在则报错
  3. 无论如何给 `subprocess.run` 加 `timeout=10` 防止无限阻塞
- **文件**: naturo/backends/windows.py（open_uri 方法，第 1239 行）

---

## 🆕 Round 35 自发现

### BUG-063: `clipboard set/get` ctypes fallback 在 64 位 Windows 上完全失效
- **状态**: ✅ Verified (Round 36) — clipboard set→get 数据一致（英文+中文均正确），ctypes fallback 正常工作
- **严重度**: 🔴 严重（clipboard 核心功能在无 pyperclip 环境下完全不可用）
- **现象**: `naturo clipboard set "hello" --json` 报 `success: true`，但 `naturo clipboard get --json` 返回空字符串。数据丢失，set 操作静默失败
- **根因**: `clipboard_set` 和 `clipboard_get` 的 ctypes fallback（无 pyperclip 时使用）没有设置 `restype` 和 `argtypes`。在 64 位 Windows 上，`GlobalAlloc` 返回 64 位指针但 ctypes 默认截断为 32 位 `c_int`，导致 `GlobalLock` 返回 0（NULL），`memmove` 写入地址 0 触发 access violation（被 except 静默吞掉）
- **复现**:
  ```
  naturo clipboard set "hello" --json  → {"success": true, "length": 5}
  naturo clipboard get --json          → {"success": true, "text": ""}
  ```
- **影响范围**: `clipboard set`、`clipboard get`、`paste`（内部调用 clipboard_set）— 所有剪贴板操作在无 pyperclip 环境下失效
- **修复建议**: 在 ctypes fallback 中添加：
  ```python
  kernel32.GlobalAlloc.restype = ctypes.c_void_p
  kernel32.GlobalLock.restype = ctypes.c_void_p
  kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
  kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
  user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
  user32.GetClipboardData.restype = ctypes.c_void_p
  ```
  或者将 pyperclip 加入 install_requires 确保始终可用
- **额外问题**: `clipboard_set` 返回 `success: true` 即使写入失败（GlobalLock 返回 0 时只 `return`，不 raise 错误）。应该在 fallback 失败时 raise NaturoError
- **文件**: naturo/backends/windows.py（clipboard_get 第 1023 行，clipboard_set 第 1060 行）

### BUG-064: `electron connect --port` 无边界校验
- **状态**: ✅ Verified (Round 36) — port -1/0/99999 均报 INVALID_INPUT "must be between 1 and 65535"，exit code 1
- **严重度**: 🟢 低（同 BUG-057 类型 — 一致性缺失）
- **现象**: `electron connect --port -1` 和 `--port 0` 不校验，直接传给 backend，错误信息泄漏中文 Windows WinError 内部错误。而同组的 `electron launch --port` 正确校验 1-65535
- **命令**: `naturo electron connect nonexistent --port -1 --json` → `CDP_CONNECTION_ERROR` + 中文 WinError
- **预期**: 校验 `--port` 在 1-65535 范围，报 `INVALID_INPUT` 错误（同 `electron launch`）
- **文件**: naturo/cli/extensions.py（electron_connect 函数，约第 769 行）

---

## 🆕 Round 34 自发现

### BUG-062: `window` 所有子命令只 catch NaturoError，非预期异常泄漏完整 traceback
- **状态**: ✅ Verified (Round 35) — window list/focus/close/minimize 等命令在非 NaturoError 异常时返回结构化 JSON `{"success": false, "error": {"code": "UNKNOWN_ERROR", "message": "..."}}`，纯文本模式输出 "Error: ..."，均无 traceback 泄漏，exit code 非零。
- **严重度**: 🟡 中等（违反设计原则 #5 — 错误信息面向用户，不暴露 traceback；违反 #6 — --json 必须合法 JSON）
- **现象**: `window_cmd.py` 中 9 个命令函数全部只有 `except NaturoError as exc:` 块，没有 `except Exception as exc:` 兜底。当出现非 NaturoError 异常（如 DLL 函数缺失的 `AttributeError`、COM 错误等）时，`--json` 模式直接输出 Python traceback 而非结构化 JSON
- **复现**: `naturo window list --json`（在 DLL 缺少 naturo_msaa_get_element_tree 的环境下）→ 输出完整 Python traceback
- **影响范围**: `window list/focus/close/minimize/maximize/restore/move/resize/set-bounds` — 全部 9 个命令
- **对比**: `core.py`（see/find 等）、`interaction.py`（click/type 等）、`desktop_cmd.py`、`dialog_cmd.py` 都有 `except Exception` 兜底块
- **修复建议**: 在每个函数的 `except NaturoError` 之后添加 `except Exception as exc:` 块，JSON 模式返回 `{"success": false, "error": {"code": "UNKNOWN_ERROR", "message": str(exc)}}`，纯文本模式输出 `Error: {exc}`
- **文件**: naturo/cli/window_cmd.py（9 个命令函数）
- **同类问题**: `chrome_cmd.py` 9 个命令也只 catch `CDPConnectionError`/`CDPError`，无 `except Exception` 兜底。`app_cmd.py` 6 处只有 `NaturoError`、2 处有 `Exception`（部分覆盖）

---

## 🆕 Round 33 自发现（backend NaturoError 缺 import 审查）

### BUG-061: `desktop`/`taskbar`/`tray` 后端方法缺少 NaturoError import，所有错误路径崩溃
- **状态**: ✅ Verified (Round 34) — `desktop list/switch/create/close --json` 均返回结构化 `DEPENDENCY_MISSING` 错误，`taskbar click --json` 返回结构化错误（DLL 函数问题），不再 NameError 崩溃。exit code 非零。
- **严重度**: 🔴 严重（7 个后端方法全部 NameError 崩溃，3 个 CLI 命令组完全不可用）
- **现象**: `naturo desktop list --json` 返回 `{"success":false,"error":{"code":"VIRTUAL_DESKTOP_ERROR","message":"name 'NaturoError' is not defined"}}`。`virtual_desktop_list()` 等方法内 `raise NaturoError(...)` 时触发 `NameError`，因为没有 import
- **影响范围** (AST 扫描确认 7 个方法):
  - `taskbar_click` (line 1666)
  - `tray_click` (line 1769)
  - `virtual_desktop_list` (line 1824)
  - `virtual_desktop_switch` (line 1861)
  - `virtual_desktop_create` (line 1903)
  - `virtual_desktop_close` (line 1938)
  - `virtual_desktop_move_window` (line 1996)
- **根因**: `naturo/backends/windows.py` 顶部没有 `from naturo.errors import NaturoError`。其他方法（如 `dialog_detect`, `dialog_type`）通过函数内 lazy import 解决了，但这 7 个方法直接使用 `NaturoError` 而没有局部 import
- **验证**: `naturo desktop list --json` → `"name 'NaturoError' is not defined"`
- **修复建议**: 在 `windows.py` 顶部添加 `from naturo.errors import NaturoError`（最干净），或在每个方法内添加 lazy import（与现有风格一致）
- **文件**: naturo/backends/windows.py（line 1666, 1769, 1824, 1861, 1903, 1938, 1996）

---

## 🆕 Round 32 自发现（diff 命令错误码审查）

### BUG-060: `diff --snapshot` 不存在的 snapshot 返回 UNKNOWN_ERROR 而非 SNAPSHOT_NOT_FOUND
- **状态**: ✅ Verified (Round 33) — 返回 `SNAPSHOT_NOT_FOUND` 错误码，exit code 非零
- **严重度**: 🟡 中等（同 BUG-049/050 类型 — 错误码不准确，影响 AI agent 错误恢复）
- **现象**: `naturo diff --snapshot nonexistent1 --snapshot nonexistent2 --json` 返回 `{"success": false, "error": {"code": "UNKNOWN_ERROR", "message": "Snapshot not found or expired: nonexistent1"}}`。消息正确但错误码是 `UNKNOWN_ERROR`，应为 `SNAPSHOT_NOT_FOUND`
- **根因**: 存在两个 `SnapshotNotFoundError` 类：
  1. `naturo/errors.py` → 继承 `NaturoError`，有 `code=ErrorCode.SNAPSHOT_NOT_FOUND`
  2. `naturo/models/snapshot.py` → 继承 `SnapshotError(Exception)`，无错误码
  `diff_cmd.py` 导入 `naturo.snapshot.SnapshotManager`，其 `get_snapshot()` 抛出的是 models 版本的错误（不是 NaturoError），落入 `except Exception` 被包装为 `UNKNOWN_ERROR`
- **命令**: `naturo diff --snapshot nonexistent1 --snapshot nonexistent2 --json`
- **预期**: `{"success": false, "error": {"code": "SNAPSHOT_NOT_FOUND", "message": "Snapshot not found or expired: nonexistent1"}}`
- **修复建议**: 统一使用 `naturo/errors.py` 中的 `SnapshotNotFoundError`，或在 `diff_cmd.py` 中明确 catch `models.snapshot.SnapshotNotFoundError` 并转换为正确错误码
- **文件**: naturo/cli/diff_cmd.py（第 107 行 except Exception 块），naturo/models/snapshot.py（第 218 行重复定义），naturo/snapshot.py（第 217 行 raise）

---

## 🆕 Round 31 自发现（文档准确性 + 代码审查）

### BUG-059: README.md MCP 工具数量过时（写 42，实际 76）
- **状态**: ✅ Verified (Round 31 代码审查) — README.md 第 27 行已写 "MCP server (76 tools)"，与 mcp_server.py 中 76 个 @server.tool() 一致
- **严重度**: 🟢 低（文档不准确，违反设计原则 #4 — 帮助和实际行为始终一致）
- **现象**: README.md 第 20 行写 "🤖 **AI-Ready** — JSON output, agent-friendly CLI, MCP server (42 tools)"，但实际 `mcp_server.py` 中 `@server.tool()` 共 76 个
- **修复**: 更新 README.md 中 MCP 工具数量为 76
- **文件**: README.md

---

## 🆕 Round 29 自发现（Phase 5A 代码审查 + JSON 一致性扫描）

### BUG-055: `find --json` 和 `menu-inspect --json` 成功时返回裸数组
- **状态**: ✅ Verified (Round 30 代码审查) — `find --json` 返回 `{"success": true, "elements": [...], "count": N}`，`menu-inspect --json` 返回 `{"success": true, "menu_items": [...]}`。编译机离线，运行时验证待补。
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

---

## 🆕 Round 30 自发现（Phase 5B/5C 新代码审查）

### BUG-056: `chrome screenshot --quality` 无边界校验
- **状态**: ✅ Verified (Round 33) — `--quality 0` 和 `--quality -1` 均报 INVALID_INPUT "must be between 1 and 100"，exit code 非零
- **严重度**: 🟢 低（同 BUG-019/025/032 类型 — 边界值无校验）
- **现象**: `--quality 0`、`--quality -1`、`--quality 999` 不报错，直接传给 CDP backend。帮助文档写 "1-100" 但无校验
- **命令**: `naturo chrome screenshot --quality 0`, `naturo chrome screenshot --quality -1`
- **预期**: 校验 `--quality` 在 1-100 范围，否则报 "Error: --quality must be between 1 and 100, got X"
- **文件**: naturo/cli/chrome_cmd.py（chrome_screenshot 函数，第 173 行）

### BUG-057: `chrome` 所有子命令 `--port` 无边界校验
- **状态**: ✅ Verified (Round 33) — `--port 0` 和 `--port 99999` 均报 INVALID_INPUT "must be between 1 and 65535"，exit code 非零
- **严重度**: 🟢 低（同 BUG-056 — electron launch 有校验但 chrome 没有）
- **现象**: `--port 0`、`--port -1`、`--port 99999` 不报错，直接传给 `_get_client()`。`electron launch` 已有 1-65535 校验，chrome 一致性缺失
- **影响范围**: chrome tabs/version/eval/screenshot/navigate/click/type/title/html — 全部 9 个子命令
- **预期**: 校验 `--port` 在 1-65535 范围
- **文件**: naturo/cli/chrome_cmd.py（所有子命令的 port 参数）

### BUG-058: Registry/Service MCP 工具缺失
- **状态**: ✅ Verified (Round 33) — 代码审查+编译机运行时确认，registry/service CLI 命令工作正常，MCP 工具均注册 @server.tool() + @_safe_tool
- **严重度**: 🟡 中等（AI agent 通过 MCP 无法使用 Phase 5C.2/5C.3 功能）
- **现象**: `naturo registry` 和 `naturo service` 有完整的 CLI 实现，但 MCP server 中无对应的 `@server.tool()` 注册。AI agent 通过 MCP 协议无法发现或调用这些功能
- **影响**: registry get/set/list/delete/search 和 service list/start/stop/restart/status 共 10 个命令无 MCP 入口
- **对比**: chrome 和 electron 的 MCP 工具已注册
- **文件**: naturo/mcp_server.py（需添加 registry 和 service 相关 @server.tool）

## BUG-068 — naturo_core.dll 缺失导致整个工具不可用 🔴 Open
- **严重度**: 🔴 P0
- **来源**: 用户报告 (Ace)
- **复现**: `pip install git+https://github.com/AcePeak/naturo.git` 后运行任何需要 native 的命令
- **现象**: `Error: Cannot find naturo_core.dll`，所有命令不可用
- **期望行为**:
  1. 不依赖 DLL 的命令（`--help`、`version`、`electron list`、`chrome tabs` 等纯 Python 功能）应该正常工作，即使没有 DLL
  2. 需要 DLL 的命令（`capture`、`see`、`click` 等）在 DLL 缺失时给出清晰的错误提示，而不是在 import 时就崩
  3. 理想情况：从源码安装时自动下载预编译 DLL（从 GitHub Release assets），或在首次使用时自动下载
- **根因**: `bridge.py` 在 import 时就加载 DLL，失败则整个模块不可用。应该改为延迟加载（lazy loading），只在真正需要 native 功能时才报错

## BUG-069 — --app 参数应该按进程名匹配而不是窗口标题 🟡 Open
- **严重度**: 🟡 P1
- **来源**: 用户报告 (Ace)
- **复现**: `naturo see --app explorer`
- **现象**: 匹配到了当前 CMD 窗口（因为标题包含命令文本），而不是 explorer.exe 的窗口
- **期望行为**: `--app explorer` 应该找到 explorer.exe 进程的窗口，按进程名匹配
- **补充**: 同时 `--app` 在 CMD 里运行时会匹配到 CMD 自身（因为 CMD 标题栏会显示正在执行的命令）
