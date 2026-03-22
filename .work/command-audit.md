# Command Audit — Keep vs Remove

## ✅ KEEP (Core: Eyes + Hands — only naturo can do this)

### Eyes (Perceive)
- `see` — UI tree inspection (UIA/MSAA/JAB/IA2)
- `find` — Element search
- `capture` — Screenshot (GDI/DXGI)
- `list` — Windows, screens, apps
- `wait` — Poll for element/window appearance
- `diff` — UI tree comparison (useful for change detection)
- `menu-inspect` — Menu structure extraction

### Hands (Act)
- `click` — Click element/coordinates
- `type` — Type text
- `press` — Press key
- `hotkey` — Key combo
- `scroll` — Scroll
- `drag` — Drag and drop
- `move` — Move cursor
- `paste` — Clipboard paste with restore
- `window` — Focus/close/minimize/maximize/move/resize
- `app` — Launch/quit/switch (process management)
- `dialog` — Detect and interact with system dialogs
- `taskbar` — Taskbar interaction
- `tray` — System tray interaction
- `desktop` — Virtual desktop management

### Integration
- `mcp` — MCP server (how AI agents connect)
- `snapshot` — Save/restore UI state

## ❌ REMOVE (Agent/skill can do this, not our job)

- `describe` — Screenshot + AI vision analysis → agent does this natively
- `agent` — Natural language automation → that's what OpenClaw IS
- `learn` — Tutorial content → put in docs/README
- `record` / replay — High-level orchestration → agent composes basic commands
- `chrome` — Browser automation → OpenClaw has browser tool, Playwright exists
- `registry` — Windows registry → PowerShell, not UI automation
- `service` — Windows services → PowerShell
- `clipboard` — Get/set clipboard → agent can do this
- `open` — Open URL/file → agent can do this
- `electron` — Electron app detection → fold into Unified App Model auto-detection
- `structure` — (unclear what this does, audit needed)
