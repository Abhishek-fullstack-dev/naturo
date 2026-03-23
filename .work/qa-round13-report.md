# QA Round 13 Report — 2026-03-23 10:44 CST

**QA-Mariana** | L0 Smoke + L1 Verification | Compile Machine (SSH, no desktop session)

## Status: Dev Completions Check

No `status:done` issues pending QA verification. All recently closed issues (#112, #114, #121, #123, #124) were closed via merged PRs with CI passing.

## Verification of Recent Fixes

### ✅ #114 — `list apps` returns NOT_IMPLEMENTED
- `naturo list apps --json` → proper JSON, delegates to `app list`
- `naturo app list --json` → identical output
- Both produce `{"success": true, "apps": [...], "count": N}`
- **Verified**

### ✅ #112 — `find --all` flag for SSH-safe wildcard
- `naturo find --all --json` available in help
- `--query` option also present as alternative
- Error output is proper JSON when no window found
- **Verified** (full GUI verification needs desktop session)

### ✅ #123 — `press --json` error format
- `naturo press --json` (no args) → `{"success": false, "error": {"code": "INVALID_INPUT", "message": "Missing argument 'KEY'..."}}`
- Proper JSON, non-zero exit code
- **Verified**

### ✅ #124 — `find --actionable` standalone
- Help shows `--actionable` without requiring QUERY
- Example in help: `naturo find --all --actionable`
- **Verified** (full test needs desktop session)

### ✅ #121 — `get --json` error format
- `naturo get --json` (no target) → proper JSON error with `INVALID_INPUT` code
- `naturo get e999 --json` → proper JSON error with element-not-found message
- Non-zero exit codes on errors
- **Verified**

## L0 Smoke Test Results

| Command | Status | Notes |
|---------|--------|-------|
| `--help` | ✅ | All 21 commands listed |
| `--version` | ✅ | `naturo, version 0.2.0` |
| `list apps --json` | ✅ | Valid JSON |
| `list windows --json` | ✅ | Valid JSON (empty, no desktop) |
| `list screens --json` | ✅ | Valid JSON, correct monitor info |
| `capture live --json` | ✅ | Works even via SSH! 1024x768, DPI 96 |
| `find --all --json` | ✅ | Proper error JSON (no window) |
| `see --json` | ✅ | Proper error JSON (no window) |
| `press --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `type --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `click --json` (no args) | ✅ | Proper NO_DESKTOP_SESSION error |
| `get --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `drag --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `move --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `wait --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `hotkey --json` (no args) | ✅ | Proper INVALID_INPUT error |
| `scroll --json` (no desktop) | ✅ | Proper NO_DESKTOP_SESSION error |
| `snapshot list --json` | ✅ | Valid JSON, lists cached snapshots |
| `type "" --json` | ✅ | Properly rejects empty string |

**Exit codes**: All errors return exit code 1, successes return 0. ✅

**CI**: Latest 3 runs all green (Build & Test on main). ✅

## Observations

1. **No desktop session** — Compile machine (100.113.29.45) has Naturobot session 1 in disconnected state. GUI-dependent tests (see → click flow, see → get flow, find with results) cannot be fully exercised. RDP reconnection needed for L2/L3 testing.

2. **`press` validates key name after desktop check** — When no desktop session, `press zzznotakey` returns NO_DESKTOP_SESSION instead of INVALID_KEY. The desktop check fires before key validation. This is technically correct (can't press anything without a desktop) but means invalid key names won't be caught until desktop is available.

3. **`type ""` (empty string)** returns INVALID_INPUT which is correct, but the message says "TEXT argument is required" rather than "TEXT cannot be empty" — minor clarity issue.

## Open Issues (0 bugs)

No open bugs in the tracker. All v0.2.0 milestone bugs have been resolved.

## Quality Assessment

**Current level: CLI error handling is solid.** All 21 commands produce consistent JSON errors with proper exit codes. The recent batch of fixes (#112-#124) has significantly improved CLI robustness.

**Readiness**: For non-GUI scenarios (error handling, help output, list/capture), naturo is at a publishable quality level. GUI interaction quality cannot be assessed this round due to disconnected desktop session.

## Top 3 Priorities for Next Round

1. **L2/L3 GUI testing** — Need RDP desktop session to test see → click → get flow end-to-end on real apps (Notepad, Explorer, etc.)
2. **`press` key validation** — Should validate key name before desktop check (or provide both errors)
3. **Regression on core flow** — see → find → click → get → capture full pipeline hasn't been tested since recent refactors

## Risk

- **No open bugs** looks clean, but GUI interaction hasn't been deeply tested since the recent #109 (get), #112-#124 batch. The fixes touched `core.py`, `interaction.py`, `get_cmd.py` — these are core paths. A desktop session regression test is overdue.
