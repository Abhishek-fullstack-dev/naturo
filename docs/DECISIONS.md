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

## 4. vcpkg for C++ Dependencies

**Decision:** vcpkg

**Why:**
- Standard C++ package manager
- Excellent CI/CD support (GitHub Actions integration)
- Cross-platform (Windows primary, but also Linux/macOS)
- Manifest mode (vcpkg.json) for reproducible builds

## 5. GitHub Actions Windows Runner

**Decision:** Use GitHub-hosted Windows runners for CI

**Why:**
- Zero local build requirement
- Pre-installed MSVC compiler
- Consistent build environment
- Free for public repos, included in private repo minutes

## 6. MIT License

**Decision:** MIT

**Why:**
- Matches Peekaboo (macOS counterpart)
- Maximizes adoption — no restrictions on commercial use
- Simple and well-understood
- Standard for developer tools
