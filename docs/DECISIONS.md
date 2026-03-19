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

## 7. Modular CLI Files

**Decision:** Split CLI into `naturo/cli/` package with separate modules.

**Why:**
- Single cli.py was getting unwieldy with 30+ commands
- Each module is independently testable
- Clear separation of concerns (core/interaction/system/ai/extensions)
- Easy to add new command groups without touching existing files

## 8. vcpkg for C++ Dependencies

**Decision:** vcpkg

**Why:**
- Standard C++ package manager
- Excellent CI/CD support (GitHub Actions integration)
- Cross-platform (Windows primary, but also Linux/macOS)
- Manifest mode (vcpkg.json) for reproducible builds

## 9. GitHub Actions Windows Runner

**Decision:** Use GitHub-hosted Windows runners for CI

**Why:**
- Zero local build requirement
- Pre-installed MSVC compiler
- Consistent build environment
- Free for public repos, included in private repo minutes

## 10. MIT License

**Decision:** MIT

**Why:**
- Matches Peekaboo (macOS counterpart)
- Maximizes adoption — no restrictions on commercial use
- Simple and well-understood
- Standard for developer tools
