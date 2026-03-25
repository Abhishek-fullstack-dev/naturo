# QA Round — 2026-03-25 09:34 AM

## Environment
- Machine: Compile (100.113.29.45), Windows 11, Console session active
- Code: naturo 0.2.5, commit 7c9ba5a (latest main)
- Noisy environment: Calculator (pre-existing) + Notepad + Paint (opened by QA)

## Test Summary

### Verified (Previous Fixes)
| Issue | Title | Result |
|-------|-------|--------|
| #262 | chrome/electron CLI removal | ✅ Both return "No such command" |
| #256 | app inspect --pid validation | ✅ PID 0, -1 rejected; 99999 = process not found |
| #257 | UWP Calculator framework detection | ✅ Detected as "uwp" with dll_signatures |

### Verification Failed
| Issue | Title | Result |
|-------|-------|--------|
| #263 | Click verification ui_text_diff fallback | ❌ Fallback never triggers, still focus_check only |

### New Bugs Filed
| Issue | Severity | Title |
|-------|----------|-------|
| #266 | P1 | Click verification ui_text_diff fallback never triggers on UWP Calculator |
| #267 | P2 | app list vs app inspect report different PIDs for Calculator (AFH vs CalculatorApp) |
| #268 | P1 | app inspect reports only 'vision' method for Calculator despite UIA working perfectly |

### Feature Tests
| Feature | Test | Result |
|---------|------|--------|
| type --verify | Notepad type + value_compare | ✅ `verified: true`, text confirmed |
| see --app isolation | Notepad see with Paint open | ✅ No cross-app element leakage |
| app list | Multiple apps open | ✅ All apps listed correctly |
| app launch | Notepad, Paint launch | ✅ Both launched successfully |
| see (Calculator) | Full UIA tree | ✅ 56 elements enumerated including all buttons |
| click (Calculator) | Click buttons by ID | ✅ Physically works (display changes), but verification broken |

## Product Quality Assessment

**Overall: 6.5/10 — Core functionality solid, verification layer incomplete**

Positives:
- `see` command works reliably across UWP and Win32 apps
- `type --verify` works perfectly with value_compare method
- `--app` filtering correctly isolates window trees
- UWP framework detection works
- Error messages are clear and actionable (PID validation)
- Click routing via UIA works correctly (InvokePattern)

Concerns:
- **Click verification (#266)** is the headline v0.3.0 feature but doesn't work for the primary use case (UWP Calculator). This is a release blocker.
- **app inspect** understates capabilities — reports "vision only" when UIA is fully functional
- **PID inconsistency** between `app list` and `app inspect` confuses the data model

## Top 3 Priorities
1. **#266 (P1)**: Fix click verification — resolve app→HWND in `_capture_ui_texts()` instead of relying on GetForegroundWindow
2. **#268 (P1)**: Fix app inspect to detect UIA as interaction method for UWP apps
3. **#267 (P2)**: Unify PID reporting — use actual app PID, not ApplicationFrameHost

## Risk Assessment
- Click verification is a v0.3.0 feature. If it doesn't work for UWP apps, the "post-action verification engine" milestone claim is overstated.
- AI agents relying on `app inspect` for strategy selection would make suboptimal choices (vision over UIA).
- The schtasks execution context may mask additional issues. Consider testing with direct Console session access.

## Cleanup
- Notepad (PID 39792): killed
- Paint (PID 43200): killed  
- schtasks NaturoQA: deleted
- Pre-existing apps (Calculator, Edge, Clash): NOT touched ✅
