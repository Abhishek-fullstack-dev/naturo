# Naturo Continuous Dev/QA Agent System — 设计方案

## 1. 设计目标

打造一套 **24/7 自动运行** 的 Dev Agent + QA Agent 组合，以"合伙人思维"持续推进 naturo 项目：

- **Dev Agent**: 产品 + 技术视角，修 bug → 推 feature → 优化架构 → 推进 milestone
- **QA Agent**: 测试 + 运营视角，验证修复 → 发现新问题 → 用户体验审计 → 竞品对比
- **Orchestrator**: 调度 + 监控，控制成本，处理异常，协调两个 agent

**不依赖任何付费产品**（不用 openclaw），仅使用：
- Claude Code CLI (`claude -p`)
- macOS launchd / cron（Mac 调度）
- Windows Task Scheduler（Windows 编译机测试）
- GitHub Issues（协调中心）
- GitHub Actions（CI/CD）

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator (Mac)                        │
│                   launchd / cron                             │
│                                                             │
│  ┌─────────────────┐           ┌─────────────────┐         │
│  │   Dev Agent      │           │   QA Agent       │         │
│  │   claude -p      │           │   claude -p      │         │
│  │   每4小时一轮    │           │   每4小时一轮     │         │
│  │   错开2小时      │           │   (Dev后2小时)    │         │
│  └────────┬────────┘           └────────┬────────┘         │
│           │                             │                   │
│           ▼                             ▼                   │
│  ┌─────────────────────────────────────────────────┐       │
│  │           GitHub Issues (协调中心)                │       │
│  │  milestone + label = 任务分配                    │       │
│  │  status:done / verified = 状态流转               │       │
│  └─────────────────────────────────────────────────┘       │
│           │                             │                   │
│           ▼                             ▼                   │
│  ┌─────────────────┐           ┌─────────────────┐         │
│  │  GitHub Actions  │           │  Windows 编译机   │         │
│  │  CI/CD           │           │  桌面测试环境     │         │
│  └─────────────────┘           └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 运行节奏

```
时间轴 (UTC+8):
00:00  Dev Agent Round 1
02:00  QA Agent Round 1 (验证 Dev Round 1 的产出)
04:00  Dev Agent Round 2
06:00  QA Agent Round 2
...
22:00  Dev Agent Round 6
00:00  QA Agent Round 6 → 日报生成
```

- **每天 6 轮 Dev + 6 轮 QA = 12 轮**
- Dev 和 QA 错开 2 小时，形成"开发-验证"节拍
- 每轮 `--max-turns 30`，防止无限循环
- 每轮超时 45 分钟（`timeout 2700`）

---

## 3. 调度实现

### 3.1 Mac 上的 launchd 配置

**Dev Agent** (`~/Library/LaunchAgents/com.naturo.dev-agent.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.naturo.dev-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ~/naturo && bash agents/orchestrator/run-dev.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>14400</integer> <!-- 每4小时 = 14400秒 -->
    <key>StandardOutPath</key>
    <string>/tmp/naturo-dev-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/naturo-dev-agent.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
```

**QA Agent** — 同结构，`run-qa.sh`，通过脚本内 sleep 错开 2 小时。

### 3.2 备选：cron 配置

```cron
# Dev Agent: 每天 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
0 0,4,8,12,16,20 * * * cd ~/naturo && bash agents/orchestrator/run-dev.sh >> /tmp/naturo-dev.log 2>&1

# QA Agent: 每天 02:00, 06:00, 10:00, 14:00, 18:00, 22:00
0 2,6,10,14,18,22 * * * cd ~/naturo && bash agents/orchestrator/run-qa.sh >> /tmp/naturo-qa.log 2>&1

# Weekly Review: 每周一 09:00
0 9 * * 1 cd ~/naturo && bash agents/orchestrator/run-review.sh >> /tmp/naturo-review.log 2>&1
```

### 3.3 备选：Windows Task Scheduler（编译机）

```powershell
schtasks /create /tn "NaturoDevAgent" /tr "bash -c 'cd /c/Users/Naturobot/naturo && bash agents/orchestrator/run-dev.sh'" /sc HOURLY /mo 4 /st 00:00
schtasks /create /tn "NaturoQAAgent" /tr "bash -c 'cd /c/Users/Naturobot/naturo && bash agents/orchestrator/run-qa.sh'" /sc HOURLY /mo 4 /st 02:00
```

---

## 4. Agent 脚本设计

### 4.1 config.sh — 共享配置

```bash
#!/bin/bash
# agents/orchestrator/config.sh — 所有 agent 共享的配置

export NATURO_DIR="${NATURO_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
export LOG_DIR="$NATURO_DIR/.work/logs"
export MAX_DAILY_ROUNDS=6           # 每日每角色最多轮数
export MAX_TURNS_PER_ROUND=30       # 每轮最多 claude 交互次数
export ROUND_TIMEOUT=2700           # 每轮超时（秒）= 45 分钟
export MIN_OUTPUT_SIZE=1024         # 上一轮产出低于此值则节流（字节）
export WEEKEND_DIVISOR=2            # 周末轮数 = MAX_DAILY_ROUNDS / 2

# 周末检测
DOW=$(date +%u)  # 1=Mon, 7=Sun
if [ "$DOW" -ge 6 ]; then
    export MAX_DAILY_ROUNDS=$((MAX_DAILY_ROUNDS / WEEKEND_DIVISOR))
fi

mkdir -p "$LOG_DIR"
```

### 4.2 run-dev.sh — Dev Agent 入口

```bash
#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/config.sh"

ROLE="dev"
LOCK_FILE="/tmp/naturo-${ROLE}-agent.lock"
ROUND_FILE="$LOG_DIR/${ROLE}-round-$(date +%Y%m%d-%H%M).md"

# ===== 防止并发运行 =====
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "[$(date)] $ROLE agent already running (PID $pid), skipping"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# ===== PAUSE 检查 =====
if [ -f "$NATURO_DIR/agents/PAUSE.md" ]; then
    echo "[$(date)] PAUSED — see agents/PAUSE.md"
    exit 0
fi

# ===== 成本控制：每日轮数上限 =====
today=$(date +%Y%m%d)
today_rounds=$(ls "$LOG_DIR"/${ROLE}-round-${today}-*.md 2>/dev/null | wc -l || echo 0)
if [ "$today_rounds" -ge "$MAX_DAILY_ROUNDS" ]; then
    echo "[$(date)] Daily limit reached ($MAX_DAILY_ROUNDS rounds). Skipping."
    exit 0
fi

# ===== 智能节流：上一轮产出过少则跳过 =====
last_round=$(ls -t "$LOG_DIR"/${ROLE}-round-*.md 2>/dev/null | head -1 || true)
if [ -n "$last_round" ] && [ -f "$last_round" ]; then
    last_size=$(wc -c < "$last_round")
    if [ "$last_size" -lt "$MIN_OUTPUT_SIZE" ]; then
        echo "[$(date)] Last round had minimal output (${last_size}B). Cooling down."
        exit 0
    fi
fi

# ===== 拉取最新代码 =====
cd "$NATURO_DIR"
git pull origin main --rebase 2>/dev/null || true

# ===== 构建 prompt =====
STATE=$(cat agents/STATE.md 2>/dev/null || echo "无")
SOUL=$(cat agents/dev/SOUL.md 2>/dev/null || echo "无")

PROMPT="你是 Naturo 的 Dev Agent (Dev-Sirius)。你是技术合伙人。

## 项目状态
$STATE

## 你的职责（完整版在 agents/dev/SOUL.md，请先读取）
读取以下文件获取完整上下文：
- agents/STATE.md（当前状态）
- agents/RULES.md（协作规则）
- agents/dev/SOUL.md（你的完整职责）
- docs/ROADMAP.md（路线图）

## 本轮任务
1. 读取上述文件，理解全局
2. 检查 CI 状态: gh run list --limit 3 —— CI 红了先修 CI
3. 查看 GitHub Issues，按优先级处理:
   gh issue list --state open --label bug
   gh issue list --state open --limit 20
4. 修 bug 或推进 feature，每个改动走 PR + CI
5. 完成后更新 agents/STATE.md
6. 轮末输出总结：完成了什么、下一轮建议、风险预警

记住：你不只是修 bug 的人，你是推动产品向前走的人。
Bug 清完了就推 enhancement，enhancement 清完了就推下一个 milestone。"

# ===== 运行 =====
echo "[$(date)] Starting Dev Agent round $((today_rounds + 1))/$MAX_DAILY_ROUNDS..."

timeout "$ROUND_TIMEOUT" claude -p "$PROMPT" \
    --allowedTools "Read,Edit,Write,Bash,Glob,Grep,Agent" \
    --max-turns "$MAX_TURNS_PER_ROUND" \
    > "$ROUND_FILE" 2>&1

exit_code=$?
echo "[$(date)] Dev Agent round complete (exit=$exit_code). Output: $ROUND_FILE"

# ===== 失败告警 =====
if [ $exit_code -ne 0 ] && [ $exit_code -ne 124 ]; then
    echo "[ALERT] Dev Agent failed with exit code $exit_code"
fi
```

### 4.3 run-qa.sh — QA Agent 入口

```bash
#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/config.sh"

ROLE="qa"
LOCK_FILE="/tmp/naturo-${ROLE}-agent.lock"
ROUND_FILE="$LOG_DIR/${ROLE}-round-$(date +%Y%m%d-%H%M).md"

# ===== 并发 / PAUSE / 成本控制 / 节流 =====
# （同 run-dev.sh 的逻辑，此处省略，实际实现时完整复制）
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "[$(date)] $ROLE agent already running, skipping"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

if [ -f "$NATURO_DIR/agents/PAUSE.md" ]; then exit 0; fi

today=$(date +%Y%m%d)
today_rounds=$(ls "$LOG_DIR"/${ROLE}-round-${today}-*.md 2>/dev/null | wc -l || echo 0)
if [ "$today_rounds" -ge "$MAX_DAILY_ROUNDS" ]; then exit 0; fi

cd "$NATURO_DIR"
git pull origin main --rebase 2>/dev/null || true

# ===== 构建 prompt =====
PROMPT="你是 Naturo 的 QA Agent (QA-Mariana)。你是质量合伙人。

## 本轮任务
读取以下文件获取完整上下文：
- agents/STATE.md（当前状态）
- agents/RULES.md（协作规则）
- agents/qa/SOUL.md（你的完整职责）
- agents/qa/QA-METHODOLOGY.md（测试方法论）
- agents/qa/ACE-TESTING-LESSONS.md（历史教训）

然后执行：

1. 检查 status:done issues → 验证 Dev 的修复
   gh issue list --label 'status:done' --json number,title
2. 在编译机上运行完整测试:
   sshpass -p 'compile@123' ssh Naturobot@100.113.29.45 \\
     'cd C:\\Users\\Naturobot\\naturo && git pull && pytest -v --timeout=30 -x --tb=short'
3. 做至少 1 个应用的 E2E 测试（在编译机上）
4. 发现问题 → gh issue create --label 'bug,from:qa' --milestone 'v0.3.1'
5. 验证通过 → gh issue comment + gh issue edit --add-label verified
6. 轮末输出：质量评估 + Top 3 改进建议 + 风险预警

记住：永远不要相信 naturo 的文字输出，只相信截图证据。"

echo "[$(date)] Starting QA Agent round $((today_rounds + 1))/$MAX_DAILY_ROUNDS..."

timeout "$ROUND_TIMEOUT" claude -p "$PROMPT" \
    --allowedTools "Read,Bash,Glob,Grep,Agent" \
    --max-turns "$MAX_TURNS_PER_ROUND" \
    > "$ROUND_FILE" 2>&1 || true

echo "[$(date)] QA Agent round complete. Output: $ROUND_FILE"
```

### 4.4 run-review.sh — 周报 Agent

```bash
#!/bin/bash
set -euo pipefail
source "$(dirname "$0")/config.sh"

cd "$NATURO_DIR"
git pull origin main --rebase 2>/dev/null || true

PROMPT="你是 Naturo 项目的周度 Review Agent。

读取以下文件获取上下文：
- agents/STATE.md
- docs/ROADMAP.md
- .work/reviews/ 目录下的历史 review（如有）
- .work/logs/ 目录下本周的 agent 日志

请完成完整的周度评审，将报告写入 .work/reviews/$(date +%Y-%m-%d)-weekly-review.md：

1. 本周进展：合并了哪些 PR，关闭了哪些 issue
2. 架构评估：代码健康度，技术债
3. Issue 积压分析：分类统计，优先级分布
4. CI/CD 状态
5. 社区指标：stars, forks
6. Top 10 优先事项（下周）
7. 风险登记表
8. 对 Dev/QA Agent 效率的改进建议

完成后 git add + commit + push 到 main。"

timeout 3600 claude -p "$PROMPT" \
    --allowedTools "Read,Edit,Write,Bash,Glob,Grep,Agent" \
    --max-turns 40 \
    > "$LOG_DIR/review-$(date +%Y%m%d).log" 2>&1 || true
```

---

## 5. 协调机制

### 5.1 GitHub Issues 状态机

两个 Agent 不直接通信，通过 label 协调：

```
[新 Issue]
    ↓
Dev 认领: status:in-progress
    ↓
Dev 完成: status:done + comment "Fixed in commit xxx"
    ↓
QA 验证 ──→ 通过: +verified label → 可关闭
         └→ 失败: 移除 status:done, comment 说明原因 → Dev 继续
```

### 5.2 agents/STATE.md 共享上下文

每轮结束 Agent 更新 STATE.md，下一轮启动读取。
冲突通过 `git pull --rebase` 自动解决。

### 5.3 冲突避免

| 规则 | 说明 |
|------|------|
| Dev 只改代码 | QA 只读代码 + 测试 |
| Dev 用 PR 提交 | QA 用 issue comment |
| 锁文件 | 防止同角色并发 |
| 错开调度 | Dev 和 QA 间隔 2 小时 |

---

## 6. 成本控制

| 参数 | 值 | 说明 |
|------|-----|------|
| 每轮 max-turns | 30 | 防止无限循环 |
| 每轮超时 | 45 分钟 | 防止卡死 |
| 每日轮数上限 | 6（周末 3） | 控制每日成本 |
| 智能节流 | 上轮产出 < 1KB 则跳过 | 避免空转 |
| PAUSE 机制 | `touch agents/PAUSE.md` | 一键暂停所有 agent |

### 预估成本

按 Claude Opus 4 定价（$15/MTok input, $75/MTok output）粗估：
- 每轮约 30K input + 10K output tokens ≈ $1.2
- 每天 12 轮 ≈ $14.4
- 每月 ≈ $430（含周末减半）

如需降低成本：
- 改为每 6 小时一轮（4 轮/天）→ ~$290/月
- 使用 Sonnet 模型（1/5 价格）→ ~$86/月
- 工作日才跑（5 天/周）→ ~$310/月

---

## 7. 健康监控

### 7.1 日报

```bash
# agents/orchestrator/daily-summary.sh — 每天 23:00 运行
today=$(date +%Y%m%d)
echo "=== $(date +%Y-%m-%d) Agent Summary ==="
echo "Dev rounds: $(ls .work/logs/dev-round-${today}-*.md 2>/dev/null | wc -l)"
echo "QA rounds:  $(ls .work/logs/qa-round-${today}-*.md 2>/dev/null | wc -l)"
echo "Issues closed today: $(gh issue list --state closed --json closedAt --jq '[.[] | select(.closedAt | startswith("'$(date +%Y-%m-%d)'"))] | length')"
echo "PRs merged today: $(gh pr list --state merged --json mergedAt --jq '[.[] | select(.mergedAt | startswith("'$(date +%Y-%m-%d)'"))] | length')"
```

### 7.2 异常告警

Agent 脚本失败时自动创建 GitHub Issue：

```bash
if [ $exit_code -ne 0 ] && [ $exit_code -ne 124 ]; then
    gh issue create \
      --title "[ALERT] $ROLE Agent failed at $(date +%H:%M)" \
      --label "ops" \
      --body "Exit code: $exit_code. Log: $ROUND_FILE"
fi
```

---

## 8. 一键安装

### install-mac.sh

```bash
#!/bin/bash
set -euo pipefail
NATURO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# 验证前置条件
command -v claude >/dev/null || { echo "❌ claude CLI not found"; exit 1; }
command -v gh >/dev/null || { echo "❌ gh CLI not found"; exit 1; }

# 生成 launchd plist 文件
for role in dev qa; do
    cat > ~/Library/LaunchAgents/com.naturo.${role}-agent.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.naturo.${role}-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd ${NATURO_DIR} && bash agents/orchestrator/run-${role}.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>14400</integer>
    <key>StandardOutPath</key>
    <string>/tmp/naturo-${role}-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/naturo-${role}-agent.err</string>
</dict>
</plist>
EOF
    launchctl load ~/Library/LaunchAgents/com.naturo.${role}-agent.plist
    echo "✅ ${role} agent scheduled (every 4h)"
done

echo ""
echo "查看状态: launchctl list | grep naturo"
echo "暂停所有: touch ${NATURO_DIR}/agents/PAUSE.md"
echo "恢复:     rm ${NATURO_DIR}/agents/PAUSE.md"
echo "卸载:     bash ${NATURO_DIR}/agents/orchestrator/uninstall-mac.sh"
```

### uninstall-mac.sh

```bash
#!/bin/bash
for role in dev qa; do
    launchctl unload ~/Library/LaunchAgents/com.naturo.${role}-agent.plist 2>/dev/null
    rm -f ~/Library/LaunchAgents/com.naturo.${role}-agent.plist
    echo "✅ ${role} agent uninstalled"
done
```

---

## 9. 演进路径

| Phase | 时间 | 内容 |
|-------|------|------|
| **Phase 1** | 立即 | 实现基础脚本，Mac launchd 调度，本地验证 |
| **Phase 2** | 1-2 周 | 添加智能节流、日报、告警、Windows 支持 |
| **Phase 3** | 1 月 | Agent SDK 替代 CLI，Dashboard，成本追踪 |
| **Phase 4** | 远期 | 开源为独立框架，支持自定义角色 |

---

## 10. 与 Claude Code /schedule 的关系

如果后续 Claude Code 的 `/schedule` 功能可用（当前连接问题），可以考虑：
- **替代 launchd/cron**：直接用 `/schedule` 设置定时任务
- **优势**：不需要本地机器一直开着，云端运行
- **劣势**：可能无法 SSH 到编译机（网络隔离）

建议：**先用 launchd/cron 落地 Phase 1**，`/schedule` 可用后评估迁移。

---

## 11. 前置条件清单

```bash
# 在 Mac 上运行以下命令验证
claude --version                    # Claude CLI 已安装
gh auth status                      # GitHub CLI 已认证
ls ~/naturo/agents/STATE.md         # 仓库已 clone
ssh -o ConnectTimeout=5 \
  Naturobot@100.113.29.45 "echo ok" # 编译机可达（QA 需要）
```
