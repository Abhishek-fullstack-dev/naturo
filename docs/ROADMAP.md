# Roadmap

## Phase 0 — Project Skeleton ✅
- Project structure (C++ core + Python wrapper)
- CI/CD pipeline (GitHub Actions)
- Version function + basic CLI
- TDD infrastructure
- Cross-platform backend abstraction layer

**Checkpoint:** CI green, `naturo version` works, backend auto-detection works on all platforms.

## Phase 1 — 看 (See)
- Screen capture (DirectX / GDI)
- Window enumeration
- UI tree inspection (MSAA + UIA)
- Element attributes (name, role, bounds, state)

**CLI commands:** `capture`, `list`, `see`

**Checkpoint:** Can capture screenshot, list windows, inspect UI tree.

## Phase 2 — 做 (Act)
- Mouse input (click, double-click, right-click, drag)
- Keyboard input (type text, press keys, combos)
- Element finding by selector
- Coordinate-based and element-based actions

**CLI commands:** `click`, `type`, `press`, `find`

**Checkpoint:** Can automate Notepad (open, type, save, close).

## Phase 3 — 稳 (Stabilize)
- Error handling and recovery
- Element wait/retry strategies
- Process management (launch, attach, monitor)
- Performance optimization (UIA caching)
- Accessibility tree diff (detect changes)

**Checkpoint:** Can handle real-world apps reliably.

## Phase 4 — 智 (AI Integration)
- MCP server implementation
- Screenshot → AI vision pipeline
- Natural language element finding
- Action recording and replay
- Agent-friendly error messages

**Checkpoint:** AI agent can drive Windows apps end-to-end.

## Phase 5 — 全 (Complete)
- Multi-monitor support
- DPI/scaling awareness
- Virtual desktop support
- Java Access Bridge
- Electron/CEF app support
- Package as standalone executable

**Checkpoint:** Production-ready for all common Windows apps.

## Phase 6 — macOS Backend

**Goal**: Full macOS support via Peekaboo CLI wrapper

| Step | Deliverable |
|------|------------|
| 6.1 | Peekaboo CLI detection + subprocess wrapper |
| 6.2 | capture/list/see via Peekaboo |
| 6.3 | click/type/press/hotkey via Peekaboo |
| 6.4 | app/window/menu via Peekaboo |
| 6.5 | dock/space mapping to Peekaboo equivalents |
| 6.6 | CI: macOS runner integration tests |
| 6.7 | Fallback: pyobjc direct calls for Peekaboo-free environments |

## Phase 7 — Linux Backend

**Goal**: Linux (X11 + Wayland) support

| Step | Deliverable |
|------|------------|
| 7.1 | X11 backend: xdotool + python-xlib |
| 7.2 | AT-SPI2 element inspection (pyatspi2) |
| 7.3 | Screenshot via Xlib / dbus portal |
| 7.4 | Wayland backend: ydotool + wlr protocols |
| 7.5 | CI: Ubuntu + xvfb UI tests |
| 7.6 | GNOME + KDE compatibility testing |

## Phase 8 — National OS & Enterprise

**Goal**: UOS, Kylin, openEuler support + enterprise features

| Step | Deliverable |
|------|------------|
| 8.1 | DDE (Deepin Desktop) compatibility testing |
| 8.2 | Kylin adapters (if needed beyond Linux backend) |
| 8.3 | Self-hosted CI runner for national OS |
| 8.4 | Enterprise: recording/playback engine |
| 8.5 | Enterprise: visual regression testing |

---

## TDD Requirements (All Phases)

Every feature follows this cycle:
1. Write failing test
2. Implement minimum code to pass
3. Refactor
4. Review (QA → PD → Security)

## Review Roles

- **QA:** Test coverage, edge cases, error paths
- **PD:** User experience, CLI design, documentation
- **Security:** No credential leaks, safe input handling, no privilege escalation
