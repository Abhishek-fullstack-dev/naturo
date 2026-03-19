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
│         naturo capture / list / see / click   │
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
- `naturo/bin/` — Bundled native libraries (in wheel)
- `tests/` — Python tests
- `core/tests/` — C++ tests
