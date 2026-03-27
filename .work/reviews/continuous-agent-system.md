# Continuous Dev/QA Agent System — 24/7 Iteration Design

## Overview

A self-sustaining dual-agent system where **Dev Agent** and **QA Agent** operate as product co-founders, continuously developing, testing, and improving naturo with minimal human intervention. Each agent thinks at the product level, not just the task level.

---

## 1. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR (cron)                      │
│  Schedule: every 30 minutes                                 │
│  Responsibilities:                                          │
│  - Health check agents                                      │
│  - Budget guard (daily API cost cap)                        │
│  - Conflict resolution (priority arbitration)               │
│  - Weekly review trigger (Friday 00:00 UTC)                 │
│  - Feishu/Slack daily digest                                │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
    ┌──────▼──────┐               ┌───────▼──────┐
    │  DEV AGENT  │◄─── Issues ──►│  QA AGENT    │
    │  (Dev-Sirius)│   feedback    │ (QA-Mariana) │
    │              │   loop        │              │
    │ Product +    │               │ Test +       │
    │ Technical    │               │ Operations + │
    │ Cofounder    │               │ Growth       │
    └──────┬──────┘               └───────┬──────┘
           │                              │
           ▼                              ▼
    ┌─────────────┐               ┌──────────────┐
    │ GitHub      │               │ Compile      │
    │ (code+CI)   │               │ Machine      │
    │             │               │ (desktop)    │
    └─────────────┘               └──────────────┘
```

---

## 2. Agent Roles (Expanded)

### Dev Agent — Product + Technical Cofounder

**Core Loop**: Assess → Plan → Implement → Verify → Advance

| Phase | Activity | Duration |
|-------|----------|----------|
| **Startup** | Read STATE.md, check CI status, scan open issues | 3 min |
| **Triage** | Comment on new issues, classify, assign self | 5 min |
| **Execute** | Fix bugs / implement features / refactor | 40 min |
| **Verify** | Run tests, check CI, update docs | 5 min |
| **Advance** | Update STATE.md, push, notify, plan next | 5 min |

**Product Thinking Responsibilities** (beyond coding):
- After fixing bugs: "What pattern caused this bug? Are there similar issues elsewhere?"
- After implementing features: "Does the CLI feel intuitive? Is the error message helpful?"
- When idle: "What would make a developer choose naturo over pywinauto? What's missing?"
- Weekly: "Review ROADMAP — are we building the right things? Should priorities change?"

**Self-Healing Behaviors**:
- CI red → stop all feature work, fix CI first
- PR merge conflict → rebase, resolve, retry
- DLL build failure → check CMake config, vcpkg deps
- Test flaky → add retry or fix root cause, never skip

### QA Agent — Test + Operations + Growth Cofounder

**Core Loop**: Verify → Explore → Report → Promote

| Phase | Activity | Duration |
|-------|----------|----------|
| **Startup** | Pull latest code on compile machine, check status:done issues | 3 min |
| **Verify** | Test Dev's completed fixes (screenshot validation) | 15 min |
| **Explore** | Scenario testing, new app testing, edge cases | 20 min |
| **Report** | Create issues, update SUPPORTED_APPS.md | 5 min |
| **Growth** | Monitor competitive landscape, draft content ideas | 5 min |

**Operations + Growth Responsibilities** (beyond testing):
- Track PyPI download stats weekly
- Monitor GitHub stars/forks/traffic after launch
- Draft announcement posts (Reddit, HN, Twitter) when triggers are met (see GROWTH.md)
- Identify user feedback patterns from issues/discussions
- Benchmark against competitors each month

**Self-Healing Behaviors**:
- Compile machine SSH fails → try Tailscale IP, internal IP, troubleshoot, notify
- Desktop session lost → reconnect with `tscon`
- naturo version mismatch → `pip install -e .` on compile machine
- git pull fails → configure proxy, retry

---

## 3. Orchestrator Design

### `agents/orchestrator.sh`

```bash
#!/bin/bash
# Naturo Agent Orchestrator
# Runs continuously, launching Dev and QA agents on schedule
# with health checks, budget guards, and conflict resolution.

NATURO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$NATURO_DIR/.work/logs"
STATE_FILE="$NATURO_DIR/agents/STATE.md"
BUDGET_FILE="$NATURO_DIR/.work/agent-budget.json"

# Configuration
CYCLE_INTERVAL_MIN=30          # Minutes between agent cycles
DAILY_BUDGET_USD=50            # Max daily API spend
MAX_CONSECUTIVE_FAILURES=3     # Failures before cooldown
COOLDOWN_MINUTES=60            # Cooldown after max failures
WEEKLY_REVIEW_DAY=5            # Friday (1=Mon, 7=Sun)

# Health check
check_health() {
    local agent=$1
    local pid_file="$LOG_DIR/${agent}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "running"
            return 0
        fi
    fi
    echo "stopped"
    return 1
}

# Budget guard
check_budget() {
    if [ ! -f "$BUDGET_FILE" ]; then
        echo '{"date":"'$(date +%Y-%m-%d)'","spent":0}' > "$BUDGET_FILE"
    fi

    local today=$(date +%Y-%m-%d)
    local budget_date=$(python3 -c "import json; print(json.load(open('$BUDGET_FILE'))['date'])")

    if [ "$today" != "$budget_date" ]; then
        echo '{"date":"'"$today"'","spent":0}' > "$BUDGET_FILE"
    fi

    local spent=$(python3 -c "import json; print(json.load(open('$BUDGET_FILE'))['spent'])")
    if (( $(echo "$spent > $DAILY_BUDGET_USD" | bc -l) )); then
        echo "BUDGET_EXCEEDED"
        return 1
    fi
    echo "OK"
    return 0
}

# Main loop
main_loop() {
    local dev_failures=0
    local qa_failures=0

    while true; do
        # Check pause flag
        if [ -f "$NATURO_DIR/agents/PAUSE.md" ]; then
            log "PAUSED — sleeping 5 min"
            sleep 300
            continue
        fi

        # Budget check
        if [ "$(check_budget)" = "BUDGET_EXCEEDED" ]; then
            log "Daily budget exceeded — sleeping until midnight"
            sleep_until_midnight
            continue
        fi

        # Launch Dev (if not running and under failure limit)
        if [ "$(check_health dev)" = "stopped" ]; then
            if [ $dev_failures -lt $MAX_CONSECUTIVE_FAILURES ]; then
                run_agent dev && dev_failures=0 || ((dev_failures++))
            else
                log "Dev in cooldown ($dev_failures failures), waiting ${COOLDOWN_MINUTES}m"
                sleep $((COOLDOWN_MINUTES * 60))
                dev_failures=0
            fi
        fi

        # Wait for Dev to finish before launching QA (serial, not parallel)
        wait_for_agent dev

        # Launch QA
        if [ "$(check_health qa)" = "stopped" ]; then
            if [ $qa_failures -lt $MAX_CONSECUTIVE_FAILURES ]; then
                run_agent qa && qa_failures=0 || ((qa_failures++))
            else
                log "QA in cooldown ($qa_failures failures), waiting ${COOLDOWN_MINUTES}m"
                sleep $((COOLDOWN_MINUTES * 60))
                qa_failures=0
            fi
        fi

        wait_for_agent qa

        # Weekly review trigger
        if [ "$(date +%u)" = "$WEEKLY_REVIEW_DAY" ] && [ ! -f "$LOG_DIR/weekly-review-$(date +%Y%m%d).done" ]; then
            run_weekly_review
            touch "$LOG_DIR/weekly-review-$(date +%Y%m%d).done"
        fi

        # Sleep until next cycle
        log "Cycle complete. Sleeping ${CYCLE_INTERVAL_MIN}m..."
        sleep $((CYCLE_INTERVAL_MIN * 60))
    done
}
```

---

## 4. Interaction Protocol

### Dev → QA Communication (via GitHub Issues)

```
Dev completes fix → labels issue "status:done" → QA picks up on next cycle
QA verifies → labels "verified" (success) or removes "status:done" (failure)
QA finds new bug → creates issue with "from:qa" label → Dev picks up on next cycle
```

### Conflict Resolution Rules

| Situation | Resolution |
|-----------|-----------|
| Dev and QA disagree on severity | QA's severity assessment wins (conservative) |
| QA reports bug Dev thinks is "by design" | Dev comments rationale, Ace decides |
| Dev wants to defer issue, QA insists | Issue stays open, tagged "needs-discussion" |
| Both agents idle | Dev advances ROADMAP, QA does exploratory testing |
| CI red | Both agents stop, Dev fixes CI first |

### Shared State Protocol

```
agents/STATE.md          — Updated by Dev at end of each cycle
agents/dev/status.md     — Dev's current work, blockers, plans
agents/qa/status.md      — QA's current test focus, findings, plans
GitHub Issues             — Single source of truth for all work items
```

---

## 5. 24-Hour Cycle Design

```
Hour  Activity
────  ────────────────────────────────────────────
0:00  [Orchestrator] Daily reset: budget counter, log rotation
0:05  [Dev] Cycle 1: Triage → fix P0 bugs
1:00  [QA] Cycle 1: Verify Dev fixes, verify previous round
1:45  [Dev] Cycle 2: Continue P0/P1 bugs
2:30  [QA] Cycle 2: Exploratory testing on new apps
3:15  [Dev] Cycle 3: P2 bugs or enhancement work
4:00  [QA] Cycle 3: Edge case testing, performance testing
...   (continues every ~90 minutes, alternating Dev then QA)
...
21:00 [Dev] Cycle 14: Feature work or refactoring
21:45 [QA] Cycle 14: Noisy environment testing
22:30 [Dev] Cycle 15: Documentation updates, README review
23:15 [QA] Cycle 15: Daily summary report, quality assessment
23:45 [Orchestrator] Daily digest → Feishu notification
```

**Expected throughput per 24h:**
- Dev: 15 cycles × ~1 fix/feature each = 10-15 fixes or 2-3 features
- QA: 15 cycles × ~3-5 test scenarios each = 45-75 scenarios tested
- Issues closed: 8-12 per day
- New issues discovered: 3-5 per day

---

## 6. Self-Recovery Mechanisms

### Agent-Level Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Agent crashes | Orchestrator health check (PID gone) | Restart with fresh context |
| Agent stuck in loop | Timeout (>60 min per cycle) | Kill + restart + log incident |
| Git conflict | Push rejected | `git pull --rebase`, resolve, retry |
| CI fails | `gh run list` check | Stop features, fix CI, then resume |
| Compile machine down | SSH timeout | Try all IPs, notify Ace if all fail |
| API rate limit | 429 response | Exponential backoff (5min, 10min, 20min) |
| Budget exceeded | Budget guard check | Pause until midnight reset |

### System-Level Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Orchestrator crashes | systemd watchdog | Auto-restart via systemd |
| Network outage | ping check | Retry every 5 min, notify after 30 min |
| Disk full | df check in orchestrator | Alert Ace, pause agents |
| OpenClaw API down | Agent launch failure | Retry with backoff, notify after 3 failures |

---

## 7. Weekly Review Automation

Every Friday, a special review cycle runs:

```python
# Weekly review agent prompt
"""
You are the Naturo Weekly Reviewer. Produce a comprehensive review covering:

1. **Progress This Week**:
   - Issues closed (count + list)
   - PRs merged (count + list)
   - Features shipped
   - Bugs fixed

2. **Quality Metrics**:
   - Open bug count trend (this week vs last week)
   - CI pass rate
   - Test coverage delta
   - P0/P1 age (days open)

3. **Competitive Update**:
   - Check Peekaboo releases (any new features we should match?)
   - Check pywinauto/PyAutoGUI for relevant changes
   - Any new MCP automation tools appearing?

4. **Roadmap Adjustment**:
   - Are we on track for the current milestone?
   - Should any issues be reprioritized?
   - New issues to create based on observations?

5. **Growth Metrics** (post-launch):
   - GitHub stars this week
   - PyPI downloads this week
   - New issues from external users
   - Community contributions

6. **Next Week Plan**:
   - Top 5 priorities for Dev
   - Top 5 test focuses for QA
   - Any growth actions to trigger?

Output as: .work/reviews/YYYY-MM-DD-weekly-review.md
Create GitHub issues for any new action items.
Notify Ace via Feishu with summary.
"""
```

---

## 8. Growth Automation (QA Agent Extension)

### Post-Launch Monitoring

QA Agent gains growth responsibilities after the repo goes public:

```
Every 6 hours:
1. Check GitHub traffic (views, clones, referrers)
2. Check PyPI download stats
3. Monitor new issues from external users (label "from:community")
4. Check for new forks and PRs from contributors

Every week:
1. Search GitHub for new MCP automation tools (competitive intelligence)
2. Search Reddit/HN for naturo mentions
3. Check Peekaboo changelog for new features
4. Draft growth trigger assessment (see GROWTH.md)

On trigger:
1. Draft announcement post (Dev reviews before posting)
2. Prepare comparison data (naturo vs competitor)
3. Create "good first issue" candidates for new contributors
```

---

## 9. Implementation Plan

### Phase 1: Foundation (Week 1)
- [ ] Create `agents/orchestrator.py` (Python, not bash — more robust)
- [ ] Add `systemd` service file for orchestrator
- [ ] Implement budget guard with daily caps
- [ ] Implement health check and restart logic
- [ ] Add daily digest Feishu notification
- [ ] Test with 3 manual cycles

### Phase 2: Intelligence (Week 2)
- [ ] Add weekly review automation
- [ ] Add competitive monitoring (Peekaboo/pywinauto release tracking)
- [ ] Add diminishing-returns detection (if 3 cycles produce no issues/fixes, reduce frequency)
- [ ] Add cross-agent priority arbitration
- [ ] Add compile machine health monitoring

### Phase 3: Growth (Week 3, post-launch)
- [ ] Add GitHub traffic monitoring
- [ ] Add PyPI download tracking
- [ ] Add growth trigger detection
- [ ] Add community issue triage workflow
- [ ] Add contributor onboarding automation

### Phase 4: Optimization (Ongoing)
- [ ] Tune cycle frequency based on actual throughput data
- [ ] Add cost-per-issue metrics
- [ ] Add agent performance scoring (issues resolved per cycle)
- [ ] A/B test different agent prompts for effectiveness

---

## 10. Cost Estimation

### Per Cycle (estimated)
| Component | Tokens (est.) | Cost (est.) |
|-----------|--------------|-------------|
| Dev Agent context load | ~50K input | $0.50 |
| Dev Agent work output | ~10K output | $0.30 |
| QA Agent context load | ~30K input | $0.30 |
| QA Agent work output | ~5K output | $0.15 |
| **Total per cycle** | | **~$1.25** |

### Per Day (15 cycles)
- Agent API costs: ~$18.75/day
- GitHub Actions CI: ~$0 (free tier for public repos)
- Compile machine: ~$0 (existing hardware)
- **Total: ~$19/day, ~$570/month**

### Budget Controls
- Daily hard cap: $50 (allows for ~40 cycles)
- Weekly soft cap: $150 (alert at 80%)
- Monthly cap: $600 (pause and review if exceeded)
- Diminishing returns detector: if 5 consecutive cycles produce 0 issues/fixes, reduce to hourly

---

## 11. Success Metrics

### Efficiency Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Issues closed per week | 30+ | `gh issue list --state closed --since` |
| Bug mean time to fix | < 24 hours | Issue created → closed timestamp |
| QA verification turnaround | < 4 hours | status:done → verified timestamp |
| CI green rate | > 95% | `gh run list --status completed` |
| Agent uptime | > 95% | Orchestrator health logs |

### Quality Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| P0 bugs open | 0 | `gh issue list --label P0` |
| Test coverage | > 70% | pytest-cov report |
| Silent failure rate | 0% | QA screenshot validation |
| Regression rate | < 5% | QA full regression results |

### Growth Metrics (post-launch)
| Metric | Target (Month 1) | Target (Month 3) |
|--------|-------------------|-------------------|
| GitHub stars | 200+ | 500+ |
| PyPI downloads/month | 1,000+ | 5,000+ |
| External contributors | 3+ | 10+ |
| Community issues | 20+ | 50+ |

---

## Appendix: Quick Start

```bash
# 1. Install orchestrator as systemd service
sudo cp agents/naturo-orchestrator.service /etc/systemd/system/
sudo systemctl enable naturo-orchestrator
sudo systemctl start naturo-orchestrator

# 2. Monitor
journalctl -u naturo-orchestrator -f

# 3. Pause/resume
touch agents/PAUSE.md      # Pause all agents
rm agents/PAUSE.md         # Resume

# 4. View daily digest
cat .work/logs/daily-digest-$(date +%Y%m%d).md

# 5. View weekly review
cat .work/reviews/$(date +%Y-%m-%d)-weekly-review.md
```
