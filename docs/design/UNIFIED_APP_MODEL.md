# Unified App Model

## Problem

Users shouldn't need to know whether an app is built with Electron, Java/Swing, WinForms, WPF, or Qt. Today, naturo exposes framework-specific commands (`naturo electron`, `naturo chrome`, etc.), forcing users to understand implementation details before they can automate anything.

## Design

A single entry point that **auto-detects** the application framework and **routes interactions** through the optimal channel — transparently.

### Core Principle

```
naturo click --app "飞书" --name "Send"
```

The user says *what* to click. Naturo figures out *how*.

## Architecture

### 1. App Inspect

```bash
naturo app inspect "飞书"
```

Probes the target application and reports available interaction methods:

```json
{
  "app": "飞书",
  "pid": 12840,
  "exe": "C:\\Users\\ace\\AppData\\Local\\Feishu\\Feishu.exe",
  "framework": {
    "detected": ["electron", "uia"],
    "version": "electron@28.2.1"
  },
  "interaction_methods": [
    {
      "method": "cdp",
      "priority": 1,
      "status": "available",
      "capabilities": ["dom", "click", "type", "evaluate", "screenshot", "network"],
      "debug_port": 9222
    },
    {
      "method": "uia",
      "priority": 2,
      "status": "available",
      "capabilities": ["click", "type", "find", "tree", "screenshot"]
    },
    {
      "method": "msaa",
      "priority": 3,
      "status": "available",
      "capabilities": ["click", "type", "find"]
    },
    {
      "method": "vision",
      "priority": 6,
      "status": "fallback",
      "capabilities": ["click", "screenshot"]
    }
  ],
  "recommended": "cdp",
  "notes": "Electron app detected. CDP provides full DOM access."
}
```

### 2. Framework Detection Chain

For each target process, naturo runs a detection chain (fast checks first):

```
1. Is CDP available?       → Check debug port / --remote-debugging-port
2. Is it Electron/CEF?     → Check DLL signatures (libcef.dll, electron.exe)
3. UIA reachable?          → IUIAutomation::ElementFromHandle
4. WPF?                    → Check for PresentationFramework.dll
5. Qt?                     → Check for Qt5Core.dll / Qt6Core.dll
6. Java Access Bridge?     → Check for WindowsAccessBridge-64.dll + JAB API
7. MSAA reachable?         → AccessibleObjectFromWindow
8. IAccessible2?           → QueryInterface for IA2
9. Fallback                → Vision (screenshot + AI)
```

Detection is cached per-process (invalidated on process restart).

### 3. Interaction Priority

Methods ranked by reliability and capability:

| Priority | Method | Strengths | Limitations |
|----------|--------|-----------|-------------|
| 1 | **CDP** | Full DOM, JS eval, network, precise selectors | Electron/Chrome only |
| 2 | **UIA** | Native Windows, rich tree, patterns | Cross-process COM overhead |
| 3 | **MSAA** | Legacy app coverage | Limited properties |
| 4 | **Java Bridge** | Java/Swing/AWT apps | JAB must be enabled |
| 5 | **IA2** | Firefox, LibreOffice, Thunderbird | Niche |
| 6 | **Vision** | Works on anything | Slower, less precise, needs AI |

When multiple methods are available, naturo picks the highest-priority one. Users can override:

```bash
naturo click --app "飞书" --name "Send" --method uia   # Force UIA
```

### 4. Auto-Routing

All action commands (`click`, `type`, `press`, `find`, `see`) route through the unified model:

```
User Command
    │
    ▼
┌─────────────┐
│  App Resolve │  ← find process by name/pid/hwnd
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Method Pick │  ← cached detection result → best method
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Execute    │  ← dispatch to CDP/UIA/MSAA/JAB/IA2/Vision backend
└─────────────┘
```

The routing is invisible to the user. `naturo click` just works.

### 5. CLI Compatibility

Existing framework-specific commands remain as **explicit/advanced interfaces**:

| Command | Purpose | When to use |
|---------|---------|-------------|
| `naturo chrome` | Direct CDP control | Browser automation, JS eval |
| `naturo electron` | Electron-specific ops | Debug port management |
| `naturo java` | Java Bridge ops | JAB diagnostics |

These are power-user tools. The default path is always through the unified model.

### 6. Inspect Flags

```bash
naturo app inspect "飞书"              # Full probe
naturo app inspect "飞书" --quick      # Skip slow checks (IA2, JAB)
naturo app inspect --pid 12840         # By PID
naturo app inspect --all               # All visible windows
```

## Implementation Plan

1. **Detection module** (`naturo/detect/`) — framework fingerprinting per process
2. **Method registry** — maps method → backend implementation
3. **Router** — selects method, dispatches action
4. **Cache** — per-PID detection results with TTL
5. **CLI integration** — wire `app inspect` + modify action commands to use router

## Non-Goals

- No new automation capabilities — this is a routing/discovery layer over existing backends
- No GUI — CLI and MCP only
- No plugin system yet — hardcoded detection chain is fine for v0.2.0
