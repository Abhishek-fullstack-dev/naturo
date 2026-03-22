# Changelog

All notable changes to Naturo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-03-21

### Added
- **Screen Capture** — GDI-based screenshot of any window or full screen
- **UI Tree Inspection** — Walk accessibility tree (UIA / MSAA / IAccessible2 / Java Access Bridge)
- **Element Finding** — CSS-like selectors + fuzzy search for UI elements
- **Mouse Input** — Click, double-click, right-click, drag, scroll, move
- **Keyboard Input** — Type text, press keys, hotkey combos, hardware-level scan codes
- **Annotated Screenshots** — AI-ready screenshots with numbered bounding boxes
- **Menu Traversal** — Extract app menu structures with keyboard shortcuts
- **Window Management** — Focus, close, minimize, maximize, move, resize, set-bounds
- **App Control** — Launch, quit, switch, hide/unhide, relaunch applications
- **Dialog Handling** — Detect and interact with system dialogs (message boxes, file pickers)
- **Taskbar & System Tray** — List and click taskbar items and tray icons
- **Multi-Monitor** — Enumerate monitors, capture specific screens, DPI-aware coordinates
- **Virtual Desktops** — List, switch, create, close desktops and move windows between them
- **Chrome DevTools** — Control Chrome via CDP (navigate, click, type, screenshot, eval JS)
- **Electron/CEF Support** — Detect, list, launch, connect to Electron apps
- **Windows Registry** — Read, write, list, delete, search registry keys/values
- **Windows Services** — List, start, stop, restart, query service status
- **Clipboard** — Get/set clipboard text and files
- **Action Recording** — Record and replay user operation sequences
- **AI Integration** — Vision describe, natural language find, agent command, multi-provider
- **MCP Server** — 82 tools via stdio/SSE/streamable-http transport
- **npm Package** — `npx naturo mcp` for Node.js ecosystem
- **JSON Output** — Every command supports `--json` for structured output
- **macOS Backend** — Full Peekaboo CLI wrapper (40+ methods) for cross-platform support
- **1461 Tests** — Comprehensive test suite with 0 failures
