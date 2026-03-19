# AGENTS.md — AI Agent Working Guide

## Project: Naturo

Windows desktop automation engine. C++ core + Python wrapper.

## Language

- **All code, comments, docstrings, commit messages, docs, and issue titles must be in English.**
- No Chinese or other non-English text in the codebase, including TODOs and inline comments.
- Variable names, function names, class names — all English.
- This is non-negotiable for open-source readiness.

## Code Style

### General
- **Comments must be complete and meaningful.** Every public function, class, and module needs a docstring or header comment explaining what it does, its parameters, and return values.
- Avoid "TODO" without context — always include what needs to be done and why.
- Self-documenting code is preferred, but complex logic requires inline comments.

### C++ (core/)
- Standard: C++17
- Compiler: MSVC (primary), GCC/Clang (secondary)
- Naming: `snake_case` for functions, `PascalCase` for classes
- All public APIs must be `extern "C"` with `NATURO_API` macro
- Include guards, not `#pragma once`
- Every exported function in `exports.h` must have a Doxygen-style comment

### Python (naturo/, tests/)
- Version: 3.9+
- Type hints on all public APIs (required), internal functions (encouraged)
- Docstrings for all public classes, methods, and functions (Google style)
- No `from __future__` imports needed (3.9+ baseline)
- Test functions must have descriptive names and a brief docstring

## Testing

**TDD is mandatory.** Write tests first, then implement.

1. Write a failing test
2. Implement minimum code to pass
3. Refactor
4. Get review

### C++ Tests
- Location: `core/tests/`
- Framework: Simple main() with pass/fail printf (no gtest dependency for now)
- Run: `ctest --test-dir build --build-config Release`

### Python Tests
- Location: `tests/`
- Framework: pytest
- Markers: `@pytest.mark.ui` for tests needing a desktop session
- DLL tests: Use `@pytest.mark.skipif(platform.system() != "Windows")`

## Review Roles

Before merging, consider these perspectives:

- **QA:** Test coverage? Edge cases? Error paths handled?
- **PD:** Good UX? CLI intuitive? Docs clear?
- **Security:** No credential leaks? Safe input? No privilege escalation?

## Commit Messages

Use [conventional commits](https://www.conventionalcommits.org/):

```
feat: add screen capture API
fix: handle DPI scaling in click coordinates
test: add UI tree depth tests
docs: update architecture diagram
chore: bump vcpkg dependencies
```

## Branch Strategy

- `main` only (for now)
- Feature branches when team grows
- All CI must pass before merge

## Build

### C++ Core
```bash
cmake -B build -S core -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build --build-config Release
```

### Python
```bash
pip install -e ".[dev]"
pytest -v
```

## Key Files

- `core/include/naturo/exports.h` — Public C API (add new functions here)
- `naturo/bridge.py` — Python ↔ DLL bridge (mirror new C functions)
- `naturo/cli.py` — CLI commands (user-facing)
- `.github/workflows/build.yml` — CI pipeline
