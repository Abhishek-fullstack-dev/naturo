# Roadmap

## 0.1.0 ✅ — Core Automation + AI + MCP + macOS

First release. Full Windows automation with AI integration and cross-platform foundation.

### Core
- [x] Project structure (C++ core + Python wrapper)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Cross-platform backend abstraction layer
- [x] TDD infrastructure, 700+ tests
- [x] Error handling framework (Peekaboo-aligned error codes)
- [x] Wait/retry strategies (polling, exponential backoff)
- [x] Element cache (TTL-based, auto-invalidation)

### See
- [x] Screen capture (GDI → Pillow PNG)
- [x] Window enumeration
- [x] UI tree inspection (UIA)
- [x] Element attributes (name, role, bounds, state)
- [x] Annotated screenshots (numbered bounding boxes)
- [x] Element search/query (fuzzy match, role filter)
- [x] UI hierarchy (parent_id, children linkage)
- [x] Snapshot system (screenshot + UI tree bundling)

### Act
- [x] Mouse input (click, double-click, right-click, drag, scroll)
- [x] Keyboard input (type, press, hotkey, paste)
- [x] Element finding by selector
- [x] Coordinate-based and element-based actions
- [x] Menu bar traversal
- [x] Keyboard shortcut discovery

### Window Management
- [x] Window focus / close / minimize / maximize / restore
- [x] Window move / resize / set-bounds
- [x] App hide / unhide / switch
- [x] Window list with filters (--app / --pid / --process-name)
- [x] 105 window management tests

### AI Integration
- [x] MCP Server — 29 tools, stdio/sse/streamable-http transport
- [x] Screenshot → AI Vision analysis
- [x] Natural language element finding
- [x] Agent command — multi-step autonomous execution
- [x] Action recording and replay
- [x] Agent-friendly error messages with recovery suggestions
- [x] Multi AI provider (Anthropic / OpenAI / Ollama / custom)

### Dialog & System
- [x] Dialog detection and interaction (accept/dismiss/fill)
- [x] Clipboard get/set
- [x] Taskbar interaction (list/click)
- [x] System tray (list/click)
- [x] `naturo open <url/file>`

### Deep Capabilities
- [x] Multi-monitor capture
- [x] DPI/scaling awareness (125%/150%/200%)
- [x] Virtual desktop support
- [x] MSAA / IAccessible
- [x] IAccessible2 (Firefox, Thunderbird, LibreOffice)
- [x] Java Access Bridge (Swing/AWT)
- [x] Hardware-level keyboard (Phys32)
- [x] UIA cache optimization (CacheRequest, batch properties)
- [x] Chrome CDP (navigate/click/type/eval/screenshot)
- [x] Electron/CEF app support (detection + DOM-level ops)
- [x] Windows Registry read/write
- [x] Windows Service management
- [x] Process management (launch/quit/relaunch/find)
- [x] UI tree diff

### macOS Backend
- [x] Peekaboo CLI detection + subprocess wrapper
- [x] capture/list/see via Peekaboo
- [x] click/type/press/hotkey via Peekaboo
- [x] app/window/menu via Peekaboo
- [x] dock/space mapping
- [x] CI: macOS runner integration tests
- [x] Fallback: pyobjc for Peekaboo-free environments

## 0.1.x — Patch Releases

- [ ] Electron detection improvements (edge cases with custom CEF builds)
- [ ] Known issue fixes from community feedback
- [ ] CI stability improvements
- [ ] Documentation polish

## 0.2.0 — Unified App Model

Auto-detect application frameworks and route interactions through the optimal channel. Users don't need to know if it's Electron, Java, or WPF.

See [design doc](design/UNIFIED_APP_MODEL.md).

- [ ] Framework detection chain (CDP → UIA → MSAA → JAB → IA2 → Vision)
- [ ] `naturo app inspect` — probe app and report available interaction methods
- [ ] `naturo app inspect --all` — scan all visible windows
- [ ] Per-PID detection cache with TTL
- [ ] Auto-routing for action commands (click/type/press/find)
- [ ] `--method` override flag for explicit channel selection
- [ ] `--quick` mode for fast probe (skip slow checks)
- [ ] MCP tools for app inspect
- [ ] Integration tests across framework types

## 0.3.0 — Enterprise Features

Deep enterprise automation capabilities from Naturobot engine.

- [ ] Excel COM automation (read/write cells, run macros, create charts)
- [ ] SAP GUI Scripting
- [ ] MinHook injection (function hooks, intercept/modify Win32 API calls)
- [ ] Embedded Python 3.12 runtime (~40MB bundled)
- [ ] `naturo run my_script.py` — execute user scripts with bundled Python
- [ ] Standalone executable (Nuitka/PyInstaller → naturo.exe)

## 0.4.0 — Open Source Launch

Go public with maximum impact.

### Pre-launch
- [ ] Branch protection (require PR + CI)
- [ ] CONTRIBUTING.md + CODE_OF_CONDUCT.md
- [ ] Issue/PR templates
- [ ] README hero GIF (Notepad E2E demo)
- [ ] README badges
- [ ] Code signing certificate + CI integration
- [ ] First PyPI release (`pip install naturo`)
- [ ] npm package (`npx naturo mcp`)
- [ ] OpenClaw skill published to ClawHub

### Launch
- [ ] Flip repo to public
- [ ] Announcements: LinkedIn / Reddit / Twitter / HN / Discord
- [ ] "How Naturo Works" blog post
- [ ] Submit to awesome-python, awesome-automation
- [ ] Demo videos (YouTube + Bilibili)

## 0.5.0 — Linux Backend

X11 + Wayland support.

- [ ] X11: xdotool + python-xlib
- [ ] AT-SPI2 element inspection
- [ ] Screenshot via Xlib / dbus portal
- [ ] Wayland: ydotool + wlr protocols
- [ ] CI: Ubuntu + xvfb UI tests
- [ ] GNOME + KDE compatibility

## 0.6.0 — National OS + Enterprise Recording

UOS, Kylin, openEuler support and production recording engine.

- [ ] DDE (Deepin Desktop) compatibility
- [ ] Kylin adapters
- [ ] Self-hosted CI runner
- [ ] Enterprise recording/playback engine
- [ ] Enterprise visual regression testing

## 1.0.0 — Stable Release

API freeze, ecosystem partnerships.

- [ ] API stability guarantee (semver contract)
- [ ] Peekaboo collaboration — official Windows counterpart
- [ ] OpenClaw recommended Windows tool
- [ ] Conference talk (PyCon / EuroPython)
- [ ] RPA/testing community partnerships
