# Naturo — Windows Desktop Automation Skill

## Description
Control Windows desktop applications via the Naturo CLI. Capture screenshots, inspect UI trees, click elements, type text, and automate workflows.

## Prerequisites
- `naturo` Python package installed (`pip install naturo`)
- Windows desktop session (for UI automation features)
- naturo_core.dll available (built from C++ core)

## Commands

```bash
# Version check
naturo version

# Screenshot
naturo capture --window "App Title" --output screenshot.png

# List windows
naturo list --type windows

# Inspect UI tree
naturo see --window "App Title" --depth 5

# Find element
naturo find "Button:Save"

# Click
naturo click "Button:Save"

# Type text
naturo type "Hello World"

# Press keys
naturo press "ctrl+s"
```

## Usage Notes
- All commands support `--json` flag for structured output
- Use `--verbose` for debug logging
- DLL tests are skipped on non-Windows platforms
- Phase 0: only `version` command is functional
