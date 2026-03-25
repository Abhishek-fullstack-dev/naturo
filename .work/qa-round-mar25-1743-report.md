# QA Round — 2026-03-25 17:43 CST

## Environment
- **Machine**: robot-compile (100.113.29.45)
- **Version**: naturo 0.3.0 (commit abf3ae5, latest main)
- **Desktop**: Console session active, but SSH cannot interact with it

## Test Results

### CI Tests (on compile machine)
- **1848 passed**, 90 failed, 261 skipped (1 warning)
- **All 90 failures are SSH/desktop-session limitation** — System/COM errors on input injection (mouse, keyboard, phys) and desktop-dependent commands
- These failures are expected in SSH context and not product bugs
- 1 collection error: `test_uia_input.py` — COM threading model conflict (comtypes CoInitializeEx)

### CLI Smoke Tests (SSH-safe commands)
| Command | Status | Notes |
|---------|--------|-------|
| `naturo --version` | ✅ | Shows 0.3.0 |
| `naturo --help` | ✅ | Clean, all v0.3.0 commands listed |
| `naturo app inspect --help` | ✅ | v0.3.0 feature present |
| `naturo see --help` | ✅ | --cascade, --fill-gaps, --method visible |
| `naturo click --help` | ✅ | --method, --verify/--no-verify visible |
| `naturo type --help` | ✅ | --method, --verify, --on targeting visible |
| `naturo press --help` | ✅ | Unified press with combo support |
| `naturo find --help` | ✅ | --ai, --method visible |
| `naturo get --help` | ✅ | New v0.3.0 command, clean |
| `naturo config show` | ✅ | Clean output, no credentials |
| `naturo snapshot list --json` | ✅ | Valid JSON |
| `naturo snapshot sessions --json` | ✅ | Valid JSON |
| `naturo snapshot clean --help` | ✅ | Proper options |

### Error Handling Tests
| Scenario | Status | Notes |
|----------|--------|-------|
| `click --coords abc def` | ✅ | "Invalid value... not a valid integer" |
| `type` (no args) | ✅ | "TEXT argument is required (or use --paste)" |
| `press` (no args) | ✅ | "Missing argument 'KEY'. Provide a key name" |
| `app inspect --pid 0` | ✅ | "Invalid PID: 0. PID must be a positive integer" |
| `app inspect --pid 99999` | ✅ | "No process found with PID 99999" |
| `wait abc` | ✅ | "Invalid value... not a valid float" |
| `wait -- -1` | ✅ | "Duration must be >= 0" |
| `wait 0` | ✅ | "Waited 0.0s" |

### Consistency Issues Found
| Issue | Severity | Details |
|-------|----------|---------|
| Desktop detection inconsistency | P2 | `list windows --json` returns NO_DESKTOP_SESSION error (exit 1), but `list apps --json` returns `{success:true, apps:[], count:0}` (exit 0). Same for `dialog detect` (returns empty success), `tray list`, `taskbar list`. Only `menu-inspect`, `see`, `find` properly detect SSH limitation. |
| Snapshot accumulation | P3 | 330 snapshots in default session, 100+ empty sessions. No auto-cleanup. Heavy QA use will keep growing. Consider TTL-based auto-purge. |

## Open v0.3.0 Issues (8 open)
- #304 P0 — see --app matches wrong window (multi-window)
- #295 bug (in-progress) — JSON output automation_id/parent_id
- #282 documentation — Release guide references wrong command
- #281 bug (in-progress) — find --app returns no results without AI provider
- #280 bug — capture UX inconsistencies
- #279 bug — capture --ref not implemented
- #275 bug — see --cascade AI vision fallback
- #274 enhancement — app list vs window list inconsistency

## Verification Queue
No `status:done` issues pending verification.

## Quality Assessment

### Current Level: **Functional but SSH-limited testing**
The v0.3.0 feature surface (Unified App Model, --method override, --verify, element ref caching, `get` command, `press` unification) is code-complete and visible in CLI help. Error handling has improved significantly — invalid inputs give clear, actionable messages.

**Cannot fully verify** desktop-interaction features (app inspect, see, click verification, see --cascade) from SSH. Previous rounds with RDP have tested these.

### Top 3 Risks
1. **Desktop-only testing gap**: SSH cannot test the core value proposition (see → click → type → verify). Full E2E testing requires RDP/console access.
2. **Inconsistent desktop detection**: Some commands silently return empty results in SSH instead of NO_DESKTOP_SESSION error. An AI agent using naturo via SSH would think "no apps running" instead of "wrong session type" — misleading.
3. **Snapshot storage growth**: 330+ snapshots accumulating with no auto-cleanup could impact disk space and list performance over time.

### Recommendations
1. Unify desktop detection across all commands — every desktop-dependent command should return NO_DESKTOP_SESSION in SSH context, not empty success
2. Add `naturo snapshot clean --days 1 --session all --yes` to QA cleanup routine
3. Consider auto-TTL for snapshots (e.g., >24h old auto-purge)
