#!/usr/bin/env python3
"""
Naturo Agent Orchestrator

Manages continuous Dev/QA agent cycles with health checks, budget guards,
cooldowns, and weekly review triggers. Designed for 24/7 unattended operation.

Usage:
    python agents/orchestrator.py                  # Run continuously
    python agents/orchestrator.py --once            # Run one cycle then exit
    python agents/orchestrator.py --role dev        # Run only Dev agent
    python agents/orchestrator.py --role qa         # Run only QA agent
    python agents/orchestrator.py --dry-run         # Show what would run
"""

import argparse
import datetime
import json
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NATURO_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = NATURO_DIR / ".work" / "logs"
BUDGET_FILE = NATURO_DIR / ".work" / "agent-budget.json"
PAUSE_FILE = NATURO_DIR / "agents" / "PAUSE.md"
STATE_FILE = NATURO_DIR / "agents" / "STATE.md"

CYCLE_INTERVAL_SECONDS = 30 * 60        # 30 minutes between cycles
AGENT_TIMEOUT_SECONDS = 60 * 60         # 60 minute hard timeout per agent
DAILY_BUDGET_USD = 50.0                 # Daily API cost cap
MAX_CONSECUTIVE_FAILURES = 3            # Failures before cooldown
COOLDOWN_SECONDS = 60 * 60             # 1 hour cooldown
WEEKLY_REVIEW_DAY = 4                   # Friday (0=Monday in Python)
DIMINISHING_RETURNS_THRESHOLD = 5       # Consecutive no-op cycles before slowdown
SLOWDOWN_INTERVAL_SECONDS = 60 * 60     # 1 hour between cycles when slowed


@dataclass
class AgentState:
    """Tracks an agent's operational state across cycles."""
    name: str
    consecutive_failures: int = 0
    consecutive_no_ops: int = 0
    last_run: Optional[datetime.datetime] = None
    last_success: Optional[datetime.datetime] = None
    cooldown_until: Optional[datetime.datetime] = None
    total_cycles: int = 0
    total_issues_touched: int = 0


@dataclass
class OrchestratorState:
    """Global orchestrator state."""
    dev: AgentState = field(default_factory=lambda: AgentState(name="dev"))
    qa: AgentState = field(default_factory=lambda: AgentState(name="qa"))
    daily_spend: float = 0.0
    budget_date: str = ""
    cycle_count: int = 0
    slowed_down: bool = False


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logging to file and stdout."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"orchestrator-{datetime.date.today().isoformat()}.log"

    logger = logging.getLogger("orchestrator")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


log = setup_logging()


# ---------------------------------------------------------------------------
# Budget Management
# ---------------------------------------------------------------------------

def load_budget() -> dict:
    """Load daily budget tracking data."""
    if not BUDGET_FILE.exists():
        return {"date": datetime.date.today().isoformat(), "spent": 0.0}
    try:
        with open(BUDGET_FILE) as f:
            data = json.load(f)
        if data.get("date") != datetime.date.today().isoformat():
            return {"date": datetime.date.today().isoformat(), "spent": 0.0}
        return data
    except (json.JSONDecodeError, KeyError):
        return {"date": datetime.date.today().isoformat(), "spent": 0.0}


def save_budget(data: dict) -> None:
    """Persist budget tracking data."""
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BUDGET_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_budget() -> bool:
    """Return True if within daily budget."""
    data = load_budget()
    if data["spent"] >= DAILY_BUDGET_USD:
        log.warning("Daily budget exceeded: $%.2f / $%.2f",
                     data["spent"], DAILY_BUDGET_USD)
        return False
    return True


def record_spend(amount: float) -> None:
    """Record API spend for the current day."""
    data = load_budget()
    data["spent"] = data.get("spent", 0) + amount
    save_budget(data)
    log.info("Recorded spend: $%.2f (daily total: $%.2f)", amount, data["spent"])


# ---------------------------------------------------------------------------
# Pause Control
# ---------------------------------------------------------------------------

def is_paused() -> bool:
    """Check if agents are paused via PAUSE.md flag file."""
    if PAUSE_FILE.exists():
        log.info("PAUSED — %s exists", PAUSE_FILE)
        return True
    return False


# ---------------------------------------------------------------------------
# Agent Execution
# ---------------------------------------------------------------------------

def build_agent_prompt(role: str) -> str:
    """Build the full context prompt for an agent cycle."""
    state = STATE_FILE.read_text(encoding="utf-8") if STATE_FILE.exists() else "No state file."
    rules_file = NATURO_DIR / "agents" / "RULES.md"
    rules = rules_file.read_text(encoding="utf-8") if rules_file.exists() else ""
    soul_file = NATURO_DIR / "agents" / role / "SOUL.md"
    soul = soul_file.read_text(encoding="utf-8") if soul_file.exists() else ""
    roadmap_file = NATURO_DIR / "docs" / "ROADMAP.md"
    roadmap = roadmap_file.read_text(encoding="utf-8") if roadmap_file.exists() else ""

    return f"""You are Naturo's {role.upper()} Agent. Read the context below, then autonomously
determine what to do and start working. Follow your SOUL document precisely.

## Project State
{state}

## Rules
{rules}

## Your Role ({role})
{soul}

## Roadmap
{roadmap}

---

Start working now. When finished, update agents/{role}/status.md with what you did,
what you plan next, and any blockers. Then update agents/STATE.md if milestones changed.
"""


def run_agent(role: str, dry_run: bool = False) -> bool:
    """Launch an agent via Claude Code CLI and wait for completion.

    Returns True on success, False on failure.
    """
    log.info("=== Starting %s agent cycle ===", role.upper())

    prompt = build_agent_prompt(role)

    if dry_run:
        log.info("[DRY RUN] Would launch %s agent with %d char prompt", role, len(prompt))
        return True

    # Try Claude Code CLI first, fall back to openclaw
    cmd = None
    if _command_exists("claude"):
        cmd = [
            "claude", "--print",
            "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,Agent",
            "-p", prompt,
        ]
    elif _command_exists("openclaw"):
        cmd = ["openclaw", "agent", "--message", prompt]
    else:
        log.error("Neither 'claude' nor 'openclaw' CLI found. Cannot run agent.")
        return False

    log_file = LOG_DIR / f"{role}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

    try:
        with open(log_file, "w", encoding="utf-8") as lf:
            proc = subprocess.run(
                cmd,
                cwd=str(NATURO_DIR),
                stdout=lf,
                stderr=subprocess.STDOUT,
                timeout=AGENT_TIMEOUT_SECONDS,
                text=True,
            )

        if proc.returncode == 0:
            log.info("%s agent completed successfully (log: %s)", role.upper(), log_file.name)
            return True
        else:
            log.warning("%s agent exited with code %d (log: %s)",
                        role.upper(), proc.returncode, log_file.name)
            return False

    except subprocess.TimeoutExpired:
        log.error("%s agent timed out after %d seconds", role.upper(), AGENT_TIMEOUT_SECONDS)
        return False
    except Exception as e:
        log.error("%s agent failed: %s", role.upper(), e)
        return False


def _command_exists(name: str) -> bool:
    """Check if a command exists on PATH."""
    try:
        subprocess.run(["which", name], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# ---------------------------------------------------------------------------
# Weekly Review
# ---------------------------------------------------------------------------

def should_run_weekly_review() -> bool:
    """Check if it's time for the weekly review."""
    today = datetime.date.today()
    if today.weekday() != WEEKLY_REVIEW_DAY:
        return False

    marker = LOG_DIR / f"weekly-review-{today.isoformat()}.done"
    return not marker.exists()


def run_weekly_review(dry_run: bool = False) -> None:
    """Trigger the weekly review agent."""
    log.info("=== Running Weekly Review ===")

    today = datetime.date.today()
    marker = LOG_DIR / f"weekly-review-{today.isoformat()}.done"

    prompt = f"""You are the Naturo Weekly Reviewer. Today is {today.isoformat()}.

Produce a comprehensive weekly review covering:

1. **Progress This Week**: Issues closed, PRs merged, features shipped, bugs fixed.
   Use `gh issue list --state closed --since {(today - datetime.timedelta(days=7)).isoformat()}T00:00:00Z`
   and `gh pr list --state closed` to gather data.

2. **Quality Metrics**: Open bug count, CI pass rate, P0/P1 age.

3. **Roadmap Assessment**: Are we on track? Should priorities change?

4. **Growth Metrics**: GitHub stars, PyPI downloads (if public), community activity.

5. **Next Week Plan**: Top 5 priorities for Dev, top 5 for QA.

6. **New Issues**: Create GitHub issues for any new action items you identify.

Output the review to: .work/reviews/{today.isoformat()}-weekly-review.md
"""

    if dry_run:
        log.info("[DRY RUN] Would run weekly review")
    else:
        success = run_agent("review", dry_run=False)
        if success:
            marker.touch()
            log.info("Weekly review completed")
        else:
            log.warning("Weekly review failed")


# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def run_cycle(state: OrchestratorState, roles: list[str], dry_run: bool = False) -> None:
    """Run one orchestrator cycle: Dev then QA."""
    state.cycle_count += 1
    log.info("━━━ Cycle %d starting ━━━", state.cycle_count)

    if is_paused():
        return

    if not check_budget():
        log.warning("Budget exceeded, skipping cycle")
        return

    now = datetime.datetime.now()

    for role in roles:
        agent = getattr(state, role, None)
        if agent is None:
            continue

        # Check cooldown
        if agent.cooldown_until and now < agent.cooldown_until:
            remaining = (agent.cooldown_until - now).total_seconds() / 60
            log.info("%s in cooldown for %.0f more minutes", role.upper(), remaining)
            continue

        # Run agent
        agent.last_run = now
        agent.total_cycles += 1
        success = run_agent(role, dry_run=dry_run)

        if success:
            agent.consecutive_failures = 0
            agent.last_success = now
            # Estimate spend (~$1.25 per agent cycle)
            record_spend(1.25)
        else:
            agent.consecutive_failures += 1
            if agent.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                agent.cooldown_until = now + datetime.timedelta(seconds=COOLDOWN_SECONDS)
                log.warning("%s entering cooldown until %s (%d consecutive failures)",
                            role.upper(), agent.cooldown_until.strftime("%H:%M"),
                            agent.consecutive_failures)

    # Weekly review
    if should_run_weekly_review():
        run_weekly_review(dry_run=dry_run)

    log.info("━━━ Cycle %d complete ━━━", state.cycle_count)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Naturo Agent Orchestrator")
    parser.add_argument("--once", action="store_true", help="Run one cycle then exit")
    parser.add_argument("--role", choices=["dev", "qa"], help="Run only this role")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run")
    args = parser.parse_args()

    roles = [args.role] if args.role else ["dev", "qa"]
    state = OrchestratorState()

    # Graceful shutdown
    def handle_signal(signum, frame):
        log.info("Received signal %d, shutting down gracefully...", signum)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("Naturo Orchestrator starting (roles=%s, once=%s, dry_run=%s)",
             roles, args.once, args.dry_run)

    if args.once:
        run_cycle(state, roles, dry_run=args.dry_run)
        return

    # Continuous loop
    while True:
        try:
            run_cycle(state, roles, dry_run=args.dry_run)

            # Adaptive interval based on diminishing returns
            interval = SLOWDOWN_INTERVAL_SECONDS if state.slowed_down else CYCLE_INTERVAL_SECONDS
            log.info("Next cycle in %d minutes", interval // 60)
            time.sleep(interval)

        except KeyboardInterrupt:
            log.info("Interrupted, shutting down...")
            break
        except Exception as e:
            log.error("Unexpected error in main loop: %s", e, exc_info=True)
            log.info("Recovering in 5 minutes...")
            time.sleep(300)


if __name__ == "__main__":
    main()
