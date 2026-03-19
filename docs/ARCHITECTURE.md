# Naturo Architecture

## Vision

Naturo is a **cross-platform desktop automation engine** built for AI agents.
One unified API, multiple native backends.

## System Architecture

```
                         User Code / AI Agent
                               │
                    ┌──────────┴──────────┐
                    │   naturo Python API  │   pip install naturo
                    │   + CLI + MCP        │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │  Backend Abstraction │   naturo/backends/base.py
                    │  (Platform-agnostic) │
                    └──┬──────┬───────┬───┘
                       │      │       │
            ┌──────────┴┐ ┌───┴────┐ ┌┴──────────┐
            │  Windows  │ │ macOS  │ │  Linux    │
            │  Backend  │ │Backend │ │ Backend   │
            └──────┬────┘ └───┬────┘ └────┬──────┘
                   │          │            │
            naturo_core.dll  Peekaboo    AT-SPI2
            (C++ engine)     CLI/pyobjc  xdotool/ydotool
```

### Layer Responsibilities

| Layer | Role | Technology |
|-------|------|-----------|
| **CLI** | User-facing commands | Python (click) |
| **Python API** | Programmatic access | Python |
| **MCP Server** | AI agent integration | Python (MCP protocol) |
| **AI Providers** | Vision + language | Anthropic, OpenAI, Ollama |
| **Backend Abstraction** | Platform-agnostic interface | Python ABC |
| **Windows Backend** | Native Windows automation | C++ DLL via ctypes |
| **macOS Backend** | Native macOS automation | Peekaboo CLI / pyobjc |
| **Linux Backend** | Native Linux automation | AT-SPI2 + xdotool |

### Backend Capabilities Matrix

| Capability | Windows | macOS | Linux |
|-----------|---------|-------|-------|
| **Input Modes** | normal, hardware, hook | normal | normal |
| **Accessibility** | UIA, MSAA, IA2 | AX (Accessibility) | AT-SPI2 |
| **Element Caching** | ✅ (C++ optimized) | Via Peekaboo | Basic |
| **Screenshot** | GDI/DXGI | ScreenCaptureKit | Xlib/portal |
| **Java Bridge** | ✅ (JAB) | ❌ | ❌ |
| **SAP** | ✅ (GUI Scripting) | ❌ | ❌ |
| **Excel** | ✅ (COM) | ❌ | ❌ |
| **Hook Injection** | ✅ (MinHook) | ❌ | ❌ |
| **Hardware Keyboard** | ✅ (Phys32) | ❌ | ❌ |
| **Browser** | ✅ (Chrome CDP) | Via Peekaboo | Basic |

### CLI ↔ Peekaboo Command Mapping

| Category | Peekaboo (macOS) | Naturo | Notes |
|----------|-----------------|--------|-------|
| **Core** | capture, list, see | capture, list, see | Full parity |
| **Interaction** | click, type, press, hotkey, scroll, drag, move, paste, swipe | click, type, press, hotkey, scroll, drag, move, paste | swipe → N/A |
| **System** | app, window, menu, menubar, clipboard, dialog, dock, space, open | app, window, menu, clipboard, dialog, open, taskbar, tray, desktop | Platform equivalents |
| **AI** | agent | agent | Same concept |
| **MCP** | mcp | mcp | Same protocol |
| **Extensions** | — | excel, java, sap, registry, service | Windows-only (for now) |
| **Guides** | learn, tools | learn, tools | Full parity |

### Windows-Specific Parameters

These parameters are available on Windows but not other platforms:

- `--input-mode normal|hardware|hook` — Input simulation method
  - `normal`: SendInput API (default, works for most apps)
  - `hardware`: Phys32/Port32 IO (bypasses software hooks, for anti-cheat/protected apps)
  - `hook`: MinHook injection (injects into target process, for apps that block external input)
- `--hwnd` — Direct window handle targeting
- `--process-name` — Target by process name

### C++ Core Architecture (Windows)

```
naturo_core.dll
├── exports.h          ← Pure C API (stable ABI)
├── auto/              ← Input simulation
│   ├── SendKeys       ← Normal mode (SendInput)
│   ├── Phys32         ← Hardware mode (IO ports)
│   └── AutoInput      ← Unified input dispatcher
├── uia/               ← UIAutomation + element caching
├── msaa/              ← MSAA / IAccessible
├── ia2/               ← IAccessible2 Proxy
├── element/           ← Unified element model
├── selector/          ← CSS-like selector engine
├── window/            ← Window management
├── image/             ← Screenshot + image matching
├── hook/              ← MinHook wrapper
├── java/              ← Java Access Bridge
├── chromium/          ← Chrome CDP + Native Host
├── sap/               ← SAP GUI Scripting
└── excel/             ← Excel COM automation
```

### CI/CD Matrix

```yaml
matrix:
  include:
    - os: windows-latest   # Primary — full build + test
      build-cpp: true
      test-level: full     # C++ + Python + UI (notepad/calc)
    - os: ubuntu-latest    # Python tests (no DLL)
      build-cpp: false
      test-level: python
    - os: macos-latest     # Python tests (no DLL)
      build-cpp: false
      test-level: python
  # Future:
  # - os: ubuntu-latest, xvfb + AT-SPI2 (Linux UI tests)
  # - os: macos-latest, Peekaboo integration tests
```
