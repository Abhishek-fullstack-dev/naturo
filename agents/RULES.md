# Agent Collaboration Rules

## Shared State
- **Project status**: `agents/STATE.md` — Read-only reference, maintained by Ace
- **Bug tracking**: **GitHub Issues** (https://github.com/AcePeak/naturo/issues) — All bugs created and tracked via `gh issue create`
- **History**: `.work/bugs.md` — Historical record only, no longer updated
- **External testing**: `.work/external-test/round-*.md` — Written by external testers, read by Dev/QA

## Role Boundaries
- **Dev**: Fix bugs, write code, run CI. Does not make testing decisions.
- **QA**: Find bugs, verify fixes, assess quality. Does not modify code.
- **External Tester**: Tests from user perspective, writes reports. Does not modify code or bugs.md.
- **Ace**: Coordinates, communicates externally, makes final decisions.

## External Test Report Handling

### QA Responsibilities
On each startup, check `.work/external-test/` for new round reports:
1. **Read** new external test round reports
2. **Evaluate** each ISSUE-E*:
   - Is it already in GitHub Issues? (deduplicate)
   - Is the severity reasonable? (can be adjusted)
   - Can it be reproduced?
3. **Convert** to GitHub Issue:
   - New issue -> `gh issue create --label "bug,P0,from:external"` to create issue
   - Duplicate -> `gh issue comment` to add external perspective to existing issue
   - Disagreed -> Write reasoning, keep in report without deleting
4. **Write back** processing status to the end of the round report:
   ```
   ## QA Processing Record
   - ISSUE-E001 -> Converted to GitHub Issue #XX (P0)
   - ISSUE-E002 -> Existing Issue #YY, added external perspective
   - ISSUE-E003 -> Disagreed, reason: ...
   ```
5. **After verifying fix**: `gh issue comment` to add verification result + `gh label add verified`

### Dev Responsibilities
- Get bugs to fix from GitHub Issues: `gh issue list --label bug --label P0`
- After fixing: `gh issue comment` explaining fix + commit message links `fixes #N`
- Bugs tagged `from:external` may have higher priority (real user perspective)

## ABSOLUTE RULES — VIOLATION = IMMEDIATE REMOVAL

1. **NEVER close a GitHub Issue without an actual merged commit that fixes it.** If you think it's already fixed, cite the EXACT commit hash. If unsure, leave it open. Closing issues without fixes has caused repeated data loss.
2. **NEVER close issues for future milestones (v0.3.1+).** You can only close issues in the milestone you are currently working on, and only after your fix is committed and CI passes.
3. **NEVER use `gh issue close` in your triage/classification phase.** During triage, you may only comment — not close.

## General Rules
1. Only operate within the naturo repository root
2. One bug = one commit, commit message references issue: `fix: description (fixes #N)`
3. Code quality must survive worldwide public review
4. README.md must be updated after feature progress
5. Version bump must sync Python + DLL
6. Bug tracking: GitHub Issues only, never `.work/bugs.md`
7. Assign yourself before working: `gh issue edit N --add-assignee @me`
8. Label `status:in-progress` when starting, `status:done` when complete
9. All issue comments must include your Agent ID
