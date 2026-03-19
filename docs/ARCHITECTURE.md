# Architecture

## Overview

Naturo is a layered system: a C++ core handles Windows APIs, exposed through a C ABI,
loaded by Python via ctypes, and surfaced as a CLI and (future) MCP server.

```
┌──────────────────────────────────────────────┐
│              AI Agent / MCP Client            │
├──────────────────────────────────────────────┤
│           MCP Server (Phase 4)               │
├──────────────────────────────────────────────┤
│         Python CLI (click framework)          │
│         Modular command structure             │
├──────────────────────────────────────────────┤
│         Python Bridge (ctypes)                │
│         NaturoCore class — loads DLL           │
├──────────────────────────────────────────────┤
│         C API (exports.h)                     │
│         naturo_version / naturo_capture / ...  │
├──────────────────────────────────────────────┤
│         C++ Core Engine                       │
│  ┌────────────┬───────────┬────────────────┐ │
│  │ Capture    │ UI Tree   │ Input          │ │
│  │ DirectX    │ MSAA/UIA  │ SendInput      │ │
│  │ GDI+       │ Caching   │ HW Keyboard    │ │
│  └────────────┴───────────┴────────────────┘ │
├──────────────────────────────────────────────┤
│              Windows APIs                     │
│  Win32 / COM / DirectX / UIAutomation         │
└──────────────────────────────────────────────┘
```

## CLI Structure

The CLI is organized into modular files under `naturo/cli/`:

```
naturo/cli/
├── __init__.py      # Main click.Group, registers all commands
├── core.py          # capture, list, see, learn, tools
├── interaction.py   # click, type, press, hotkey, scroll, drag, move, paste
├── system.py        # app, window, menu, clipboard, dialog, open, taskbar, tray, desktop
├── ai.py            # agent, mcp
└── extensions.py    # excel, java, sap, registry, service
```

## Command Mapping: Naturo ↔ Peekaboo

| Category     | Peekaboo (macOS)    | Naturo (Windows)    | Notes                                    |
|-------------|---------------------|---------------------|------------------------------------------|
| **Core**    | capture live/video/watch | capture live/video/watch | Same structure                      |
|             | list apps/windows/screens/permissions | list apps/windows/screens/permissions | Same |
|             | see                 | see                 | Same params                              |
|             | learn               | learn               | Same                                     |
|             | tools               | tools               | Same                                     |
| **Input**   | click               | click               | + --input-mode (normal/hardware/hook), --hwnd, --process-name |
|             | type                | type                | + --input-mode, same profiles            |
|             | press               | press               | + --input-mode                           |
|             | hotkey              | hotkey              | + --input-mode                           |
|             | scroll              | scroll              | Same                                     |
|             | drag                | drag                | Same                                     |
|             | move                | move                | Same                                     |
|             | paste               | paste               | Same                                     |
| **System**  | app                 | app                 | No --bundle-id, uses process names       |
|             | window              | window              | Uses --hwnd instead of --window-id       |
|             | menu                | menu                | Same                                     |
|             | clipboard           | clipboard           | Same                                     |
|             | dialog              | dialog              | Same                                     |
|             | open                | open                | Same                                     |
|             | dock                | **taskbar**         | Windows equivalent                       |
|             | menubar             | **tray**            | Windows equivalent                       |
|             | space               | **desktop**         | Windows virtual desktops                 |
| **AI**      | agent               | agent               | Same                                     |
|             | mcp                 | mcp                 | Same                                     |
| **Windows** | —                   | **excel**           | Excel COM automation                     |
|             | —                   | **java**            | Java Access Bridge                       |
|             | —                   | **sap**             | SAP GUI Scripting                        |
|             | —                   | **registry**        | Windows Registry ops                     |
|             | —                   | **service**         | Windows Service management               |

## Windows-Specific Parameters

These params appear on interaction commands and have no Peekaboo equivalent:

- `--input-mode normal|hardware|hook` — Input injection method
  - `normal` — SendInput API (default, works for most apps)
  - `hardware` — Phys32 driver (bypasses software input filtering)
  - `hook` — MinHook injection (for protected/game apps)
- `--hwnd` — Window handle (integer), direct targeting
- `--process-name` — Filter by process executable name

## Why C++ Core?

1. **MSAA / UIAutomation** — COM-based APIs, natural in C++
2. **Caching** — UIA tree caching for performance
3. **Hardware keyboard simulation** — Low-level SendInput
4. **Hook injection** — For protected apps
5. **Java Bridge** — Java Access Bridge for Swing/AWT apps
6. **DirectX capture** — For GPU-accelerated screenshots

## Why ctypes (not pybind11)?

1. **No compile dependency** for Python users — just pip install
2. **Stable C ABI** — no C++ name mangling issues
3. **Simple** — one .dll file, no complex build chain for Python side
4. **Cross-version** — works with any Python 3.9+

## Data Flow

```
User/Agent → CLI command → Python bridge → C API → C++ Core → Windows API
                                                         ↓
User/Agent ← JSON output ← Python bridge ← C API ← Results
```

## File Layout

- `core/` — C++ source, CMake build
- `naturo/` — Python package
- `naturo/cli/` — CLI command modules
- `naturo/bin/` — Bundled native libraries (in wheel)
- `tests/` — Python tests
- `core/tests/` — C++ tests
