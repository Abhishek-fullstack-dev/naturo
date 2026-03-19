# Technical Decisions

## 1. C++ Core vs Pure Python

**Decision:** C++ core with Python wrapper

**Why:**
- Windows UI automation APIs (MSAA, UIAutomation) are COM-based, natural in C++
- UIAutomation caching requires C++ for proper performance
- Hardware keyboard simulation (SendInput) needs low-level access
- Hook injection for protected applications
- Java Access Bridge integration
- DirectX screen capture for GPU-accelerated screenshots

**Trade-off:** More complex build, but significantly better capabilities.

## 2. ctypes vs pybind11

**Decision:** ctypes with C ABI

**Why:**
- No compile dependency for Python users (just `pip install`)
- Stable C ABI — no C++ name mangling issues
- Works with any Python 3.9+ without recompilation
- Simpler distribution — one DLL file

**Trade-off:** Manual function signature definitions, but the API surface is small.

## 3. click vs typer for CLI

**Decision:** click

**Why:**
- More mature and widely used
- Better documentation
- No dependency on typing_extensions
- Proven in production (used by Flask, pip, etc.)

## 4. CLI Alignment with Peekaboo

**Decision:** Mirror Peekaboo's command structure 1:1, plus Windows extensions.

**Why:**
- AI agents that work with Peekaboo can work with Naturo with minimal adaptation
- Consistent mental model across macOS and Windows
- Same command names, same parameter names where applicable
- Diverge only where Windows requires it (--input-mode, --hwnd, --process-name)

**Mapping:**
- Peekaboo `dock` → Naturo `taskbar`
- Peekaboo `menubar` → Naturo `tray`
- Peekaboo `space` → Naturo `desktop`
- Peekaboo `--bundle-id` → dropped (not a Windows concept)
- Added: `--input-mode`, `--hwnd`, `--process-name`

## 5. Windows-Only Extensions

**Decision:** Add excel, java, sap, registry, service commands.

**Why:**
- Enterprise Windows automation needs these — Peekaboo doesn't because macOS doesn't have them
- Excel COM automation is the #1 request for Windows RPA
- Java Access Bridge covers Swing/AWT apps common in enterprise
- SAP GUI Scripting is critical for ERP automation
- Registry and service management are basic Windows admin tasks

**Trade-off:** More commands, but they're isolated in `naturo/cli/extensions.py`.

## 6. Input Mode System

**Decision:** Three-tier input: normal, hardware, hook

**Why:**
- `normal` (SendInput) — works for 90% of apps, standard Windows API
- `hardware` (Phys32 driver) — bypasses software input hooks, needed for some protected apps
- `hook` (MinHook injection) — injects directly into target process, for games/anti-cheat

This is Naturo's core differentiator vs Peekaboo and other automation tools.

## 7. Cross-Platform Architecture (2026-03-19)

**Decision**: Build a unified API with platform-specific backends rather than separate tools per OS.

**Options considered**:
- A: Windows-only tool → limited market
- B: Separate tools per platform → fragmented, harder to maintain
- C: Unified API + native backends → one tool, maximum reach ✅

**Rationale**: Users and AI agents want one command (`naturo click`) that works everywhere. The backend abstraction isolates platform complexity. Peekaboo already proved the macOS approach; we add Windows depth and Linux breadth.

## 8. macOS Strategy: Wrap Peekaboo First (2026-03-19)

**Decision**: Use Peekaboo CLI as macOS backend initially, with pyobjc as future alternative.

**Rationale**: Peekaboo is MIT-licensed, mature, and actively maintained. Wrapping it gets us macOS support with minimal effort. If Peekaboo becomes unmaintained or we need deeper control, we switch to pyobjc direct calls. The backend abstraction makes this swap transparent to users.

## 9. Linux Strategy: AT-SPI2 + xdotool/ydotool (2026-03-19)

**Decision**: Use AT-SPI2 for accessibility/element inspection, xdotool (X11) or ydotool (Wayland) for input simulation.

**Rationale**: AT-SPI2 is the standard Linux accessibility framework (GNOME, KDE, UOS all support it). xdotool is the most mature X11 automation tool. ydotool provides Wayland compatibility. This combination covers >95% of Linux desktop environments including national OS distributions.

## 10. National OS Compatibility (2026-03-19)

**Decision**: Treat national OS (UOS, Kylin, openEuler) as Linux variants, not separate backends.

**Rationale**: UOS (Deepin) uses DDE desktop which is Qt-based and supports AT-SPI2. Kylin uses UKUI which also supports AT-SPI2. The Linux backend should work with minimal or no adaptation. We'll add targeted compatibility tests and adapters only if specific issues arise.

## 11. CI Matrix Strategy (2026-03-19)

**Decision**: Three-tier CI — Windows (full), Ubuntu (Python), macOS (Python) now; expand later.

**Rationale**: Windows is the primary target with C++ build. Ubuntu and macOS run Python-only tests to verify cross-platform compatibility of the API layer. Full UI tests on Linux (xvfb) and macOS (Peekaboo) will be added when those backends are implemented.
