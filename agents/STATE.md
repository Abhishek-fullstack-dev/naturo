# Naturo Project Status

> Agents: read this on every startup.
> **Bug tracking**: GitHub Issues only -> https://github.com/AcePeak/naturo/issues

## Current State

**v0.3.0 released** (PyPI + GitHub Release). Current focus is v0.3.1 and v0.3.2.

## Active Milestones

### v0.3.1 — Current highest priority
- #405 P0 regression: type/press fails on Win11 Notepad
- #367 P0: Hybrid per-node recognition engine
- #312 P1: Win32+UIA hybrid mode
- #382 P2: get --all multi-element return
- #313 P2: highlight all elements simultaneously

### v0.3.2 — Next
- Unified Selector engine (#102, #103, #104, #105)
- Stable ID system (#361)
- Enterprise: Excel (#38), SAP (#39), MinHook (#40)
- Open source prep: README GIF (#47), CONTRIBUTING (#45), public repo (#54)
- npm publish (#52), standalone exe (#43)

## Getting your work list

```bash
# What should I work on now?
gh issue list --milestone "v0.3.1" --state open --label bug     # Fix bugs first
gh issue list --milestone "v0.3.1" --state open                 # Then enhancements
gh issue list --milestone "v0.3.2" --state open                 # After v0.3.1 is clear
```

## Completed Releases

- v0.1.0 — Core features
- v0.1.1 — 67 bug fixes (PyPI published)
- v0.2.0 — Unified App Model + DPI
- v0.2.1 — Auto-routing + get command
- v0.3.0 — QA-tested release, 21 issues fixed (PyPI published)

## Agent Roles

- **Dev-Sirius**: Fix bugs, push features, maintain code quality. Clear bugs first, then enhancements; when milestone is clear, move to the next.
- **QA-Mariana**: Test alongside Dev progress. Periodic full regression testing.

## Rules

- Bug tracking: GitHub Issues (`gh issue list`, `gh issue create`)
- One bug = one commit, reference issue: `fixes #N`
- All issue comments must include Agent ID
- Code quality must survive public scrutiny
- Only operate within the naturo repository root
- **v0.3.0 is released — do not look at v0.3.0 milestone anymore**
