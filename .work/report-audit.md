# QA Report Audit — Cross-Reference with GitHub Issues

**执行时间**: 2026-03-24  
**覆盖范围**: qa-round1, qa-round10 ~ qa-round18, qa-full-coverage-report, bugs.md, bugs-archive.md  
**GitHub Issues**: 全量 231 条（open + closed）

---

## 摘要统计

| 类别 | 数量 |
|------|------|
| QA 报告中发现的总 Bug/发现数 | ~85 |
| 已在 GitHub Issues 追踪 ✅ | ~68 |
| **未追踪 / 漏网之鱼 ❌** | **14** |
| 已关闭但实现不完整（需跟进）⚠️ | 2 |
| 建议/改进未入 Issues | 8 |

---

## ✅ 已正确追踪的问题（代表性举例）

这些在 QA 报告中出现，并有对应 GitHub Issue：

| Issue | 标题 | 状态 |
|-------|------|------|
| #230 | type command silent failure | OPEN P0 |
| #229 | Snapshot not persisted across CLI invocations | OPEN P0 |
| #228 | see returns shallow tree for Calculator (UWP) | OPEN P0 |
| #226 | type/click/press silent failure in schtasks | CLOSED |
| #223 | app list omits Calculator (UWP) | OPEN P1 |
| #222 | get cannot find elements after see | OPEN P0 |
| #221 | see fails on Chinese locale Calculator | OPEN P1 |
| #218 | Test CliRunner mixes stderr/stdout | CLOSED verified |
| #217 | DLL version out of sync | CLOSED verified |
| #208 | Auto-routing regression | CLOSED verified |
| #177 | --json flag doesn't propagate to subcommands | CLOSED verified |
| #166 | CLI parameter names not standardized | CLOSED verified |
| #155 | drag doesn't hold mouse button | CLOSED verified |
| #152 | capture saves all screenshots as capture.png | CLOSED verified |
| #149 | No fuzzy command matching | CLOSED verified |
| #145 | test_cli.py see fails in SSH | CLOSED verified |
| #144 | test_version.py encoding issue on Chinese Windows | CLOSED verified |
| #134 | 80+ tests fail on SSH/headless Windows | CLOSED |
| #133 | Version mismatch DLL/Python | CLOSED verified |
| #124 | find --actionable requires QUERY arg | CLOSED verified |
| #123 | press --json error format inconsistent | CLOSED verified |
| #121 | get --json error format inconsistent | CLOSED verified |
| #118 | get blocked: DLL missing export | CLOSED verified |
| #117 | get crashes: AttributeError typo | CLOSED verified |
| #115 | click returns exit 0 on failure | CLOSED verified |
| #114 | list apps returns NOT_IMPLEMENTED | CLOSED verified |
| #113 | SSH + RDP still gets System/COM error | CLOSED verified |
| #112 | find wildcard shell-expanded on Windows | CLOSED verified |
| #99 | Unified error handling for SSH/headless | CLOSED verified |
| #98 | app list should filter system processes | CLOSED verified |
| #31 | naturo open URL hangs | CLOSED verified |
| #25 | service list --state running returns 0 | CLOSED |
| #24 | Missing pyvda dependency | CLOSED verified |
| #23 | see element IDs can't be used with click | CLOSED verified |

---

## ❌ 未追踪的发现（漏网之鱼）

以下问题在 QA 报告中明确记录，但在 GitHub Issues 中**找不到对应的 issue**：

| # | 来源 | 问题描述 | 严重度建议 | 备注 |
|---|------|----------|-----------|------|
| U-01 | Round 18 | **Repo 里有 60+ PNG 截图文件已提交到 git**（~20MB 二进制）；存在 `fix/cleanup-screenshots` 分支但未合并，也没有对应 issue | P2 | 对开源项目形象有影响 |
| U-02 | Round 18 | **#142（Global --provider/--model flags）关闭但实现不完整**：flags 只加到了 `naturo find --ai`，`naturo --provider` 返回 "No such option"。Issue 闭了但功能没全做 | P1 | 需要新建跟进 issue 或重新打开 |
| U-03 | Round 10 | **MCP tools 缺少 try/except wrapper** (BUG-039)：backend 异常会泄漏 Python 内部错误给 AI agent，而非结构化错误信息 | P2 | 影响 AI agent 集成可靠性 |
| U-04 | Round 1 & Full | **`app find` 不支持中文名称搜索**：`naturo app find 飞书` 返回 Not found，但 `naturo app find Feishu` 能找到。违反设计原则 #3（中文 Windows 支持） | P2 | Round 1 Warning #2 记录 |
| U-05 | Round 1 & Full | **`app find --pid N` 静默忽略 NAME 参数**：`naturo app find dummy --pid 9408` 返回 PID 9408 的进程，NAME 被忽略无任何提示 | P2 | Round 1 Warning #1 |
| U-06 | Round Full (BUG-026) | **`menu-inspect --app nonexistent` 不区分"应用不存在"和"无菜单"**：两种情况都返回 "No menu items found"，无法区分。用户无法知道是应用没找到还是真的没有菜单 | P2 | 错误码不准确 |
| U-07 | Round Full (BUG-027) | **`menu-inspect` success=false 时 exit code 为 0**：JSON 里 `success: false` 但 exit code 不一致。可能已在后续统一 exit code 工作中修复，但没有具体 issue 追踪 | P2 | 需确认是否已修复 |
| U-08 | Round Full (BUG-022) | **`snapshot clean` 无参数时提示错误但 exit code 为 0**：应返回非零退出码 | P3 | 可能已在后续修复 |
| U-09 | Round Full (BUG-023) | **`learn nonexistent_topic` 静默 fallback 到概览，不报错**：应返回 "Unknown topic: xxx"。（注：`learn` 命令已在 command-audit 中标记为 REMOVE，若已删除则无需处理） | P3 | 需确认 `learn` 是否仍存在 |
| U-10 | Round 18 | **`electron list` 将 `naturo.exe` 自身误判为 Electron 应用**（false positive）：影响 `naturo electron list` 的可信度 | P2 | Round 18 Section 2 备注 |
| U-11 | Round 1 | **`capture live` 失败时 `.tmp.bmp` 临时文件残留**：应在 finally 块中清理。BUG-R1-008 中有记录 | P2 | 可能已修复但没有专项 issue |
| U-12 | Round 13 | **`press` 命令在无桌面时先返回 NO_DESKTOP_SESSION，无法校验无效 key 名**：`naturo press zzznotakey` 返回 NO_DESKTOP_SESSION 而非 INVALID_KEY。有桌面才能校验 key 名，逻辑顺序问题 | P3 | Round 13 Observation #2 |
| U-13 | Round 17 | **`wait` 不支持人类友好的时间格式**：`naturo wait 2s` 报错，用户期望 `2s`、`500ms` 等格式能工作 | P3 | Round 17 标记为 P3 recommendation |
| U-14 | Round 18 | **Compile machine GitHub HTTPS 访问不稳定**（多次 Round 报告 git pull 失败）：虽然是基础设施问题，但持续影响 QA 能力，建议文档化解决方案（git proxy 配置） | P2 | 运维问题，建议记录到 CONTRIBUTING 或 README |

---

## ⚠️ 已关闭但需跟进的问题

| Issue | 问题 | 建议行动 |
|-------|------|---------|
| #142 | Global --provider/--model flags：Issue 已关闭，但 Round 18 验证发现只在 `naturo find --ai` 实现，其他 AI-capable 命令无此 flag | 新建 follow-up issue："[BUG] #142 incomplete: --provider/--model only works on find, not globally" |
| #173 | Snapshot session isolation：Issue 已关闭，但 Round 18 的 Issues #229/#222 显示 snapshot 跨 CLI 调用持久化仍有问题 | 可能是新的 regression，#229 已在追踪但与 #173 关联应说明 |

---

## 📋 建议/改进未入 Issues（低优先级）

以下是 QA 报告中的建议性发现，不是 bug，但目前没有 GitHub issue 追踪：

| 来源 | 建议 | 建议优先级 |
|------|------|-----------|
| Round 1 | 统一退出码语义规范文档（find nonexistent=1, 参数错误=2, 内部错误=3+）| P3 |
| Round 16 | `capture` 是命令组时，`naturo capture --json` 报 "No such option" 而非引导到 `capture live` | P3 |
| Round 13 | `type ""` 的错误信息说 "required" 而非 "cannot be empty"，细节不准确 | P3 |
| Round 18 | RDP/desktop session testing 的系统性方案（目前 QA 高度依赖 SSH，无法测试鼠标操作）| P2 |
| Round 10 | `test_process.py` 5 个 mock 问题 + `launch_app` 缺少测试覆盖（BUG-040）| P2 |
| Round 12 | Windows shell quoting 系统性问题（不只是 `find *`，所有接受自由文本的参数都可能在 cmd/PS 中出问题）| P2 |
| Round 16 | Compile machine git proxy 配置方案需文档化，避免每次 GFW 问题都要重新摸索 | P3 |
| Round 18 | `naturo.exe` 在 electron list 的 false positive，可能需要排除规则 | P2 |

---

## 推荐行动

### 立即创建（高价值未追踪 Bug）

```bash
cd ~/Ace/naturo

# U-01: Repo PNG cleanup
gh issue create --title "[CLEANUP] 60+ screenshot PNG files committed to repo root — add to .gitignore and remove from history" \
  --label "task,P2" --body "Found in QA Round 18: 60+ naturo-screen-*.png files are committed to the repo root (~20MB binary in git history). Branch fix/cleanup-screenshots exists but was never merged and has no corresponding issue."

# U-02: #142 incomplete 
gh issue create --title "[BUG] #142 incomplete: --provider/--model flags only work on 'find', not globally" \
  --label "bug,P1,from:qa" --body "Issue #142 was closed as done, but QA Round 18 verification shows flags are only implemented on 'naturo find --ai'. Running 'naturo --provider openai' returns 'No such option'."

# U-03: MCP try/except
gh issue create --title "[BUG] MCP tools missing try/except wrapper — Python exceptions leak to AI agents" \
  --label "bug,P2,from:qa" --body "QA Round 10 (BUG-039): MCP tool handlers lack try/except. Backend exceptions propagate as raw Python errors instead of structured error responses. Affects all 26+ MCP tools."

# U-04: Chinese app name
gh issue create --title "[BUG] app find does not match Chinese app names — violates Chinese Windows design principle" \
  --label "bug,P2,from:qa" --body "naturo app find 飞书 returns Not found, but naturo app find Feishu works. Chinese Windows users cannot search apps by their displayed Chinese names."

# U-05: app find --pid ignores NAME
gh issue create --title "[BUG] app find --pid N silently ignores NAME argument — confusing behavior" \
  --label "bug,P2,from:qa" --body "naturo app find dummy --pid 9408 returns the process for PID 9408, silently ignoring 'dummy'. Should either error on conflict or document that --pid takes precedence."

# U-10: electron false positive
gh issue create --title "[BUG] electron list reports naturo.exe itself as an Electron app — false positive" \
  --label "bug,P2,from:qa" --body "QA Round 18: naturo electron list incorrectly identifies naturo.exe as an Electron application. Needs exclusion rule or better Electron detection heuristics."
```

### 需要确认状态（可能已修复但无 issue）

- **U-06/U-07**: `menu-inspect` error handling — 检查当前代码是否已修复
- **U-08**: `snapshot clean` no-args exit code — 检查当前行为
- **U-11**: `capture live` temp file cleanup — 检查是否有 finally 块

### 可以关闭/标记为 wontfix

- **U-09**: `learn nonexistent_topic` — 如 `learn` 命令已按 command-audit 从产品中移除，则无需处理
- **U-12/U-13/U-14**: P3 items — 可以创建低优先级 issue 备忘，或先放入 backlog

---

## 覆盖质量评估

### 追踪完整度：较好，但有盲区

**强项**：
- 所有 P0 bugs 都有 GitHub Issues ✅
- 大多数 P1 bugs 有追踪 ✅
- 质量稳定下降后新 bug 都及时记录 ✅
- Closed issues 基本都有 `verified` 标签 ✅

**弱项**：
- 早期 QA 报告（Round 1 warnings、Full Coverage BUG-022/023/026/027）的"次级问题"没有全部转入 GitHub ❌
- Round 10 的 MCP-specific bugs 没有独立 issues ❌
- 技术债务（repo hygiene、git proxy 文档）完全没追踪 ❌
- 部分 issue 关闭后发现实现不完整，没有 follow-up issue ❌

**总体评价**：产品层面的核心 bug 追踪完整度约 **85%**，"软性"建议和技术债务追踪完整度约 **40%**。
