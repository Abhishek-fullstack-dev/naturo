# Roadmap

## Phase 0 — Project Skeleton ✅
- Project structure (C++ core + Python wrapper)
- CI/CD pipeline (GitHub Actions)
- Version function + basic CLI
- TDD infrastructure

**Checkpoint:** CI green, `naturo version` works.

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
