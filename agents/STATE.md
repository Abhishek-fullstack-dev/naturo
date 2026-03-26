# Naturo Project Status

> Agents: read this on every startup.
> **Bug tracking**: GitHub Issues only → https://github.com/AcePeak/naturo/issues

## Current State

**v0.3.0 已发布** (PyPI + GitHub Release)。当前工作重心是 v0.3.1 和 v0.3.2。

## Active Milestones

### v0.3.1 — 当前最高优先级
- #405 P0 回归 bug: type/press 在 Win11 Notepad 失效
- #367 P0: Hybrid 逐节点混合识别引擎
- #312 P1: Win32+UIA 混合模式
- #382 P2: get --all 多元素返回
- #313 P2: highlight 全元素同时显示

### v0.3.2 — 下一步
- Unified Selector 引擎 (#102, #103, #104, #105)
- 稳定 ID 系统 (#361)
- Enterprise: Excel (#38), SAP (#39), MinHook (#40)
- 开源准备: README GIF (#47), CONTRIBUTING (#45), 公开 repo (#54)
- npm 发布 (#52), standalone exe (#43)

## 获取工作列表

```bash
# 当前应该做什么
gh issue list --milestone "v0.3.1" --state open --label bug     # 先修 bug
gh issue list --milestone "v0.3.1" --state open                 # 再做 enhancement
gh issue list --milestone "v0.3.2" --state open                 # v0.3.1 清完推这个
```

## Completed Releases

- v0.1.0 — Core features
- v0.1.1 — 67 bug fixes (PyPI published)
- v0.2.0 — Unified App Model + DPI
- v0.2.1 — Auto-routing + get command
- v0.3.0 — QA-tested release, 21 issues fixed (PyPI published)

## Agent Roles

- **Dev-Sirius**: Fix bugs, push features, maintain code quality. Bug 清完做 enhancement，milestone 清完推下一个。
- **QA-Mariana**: 跟着 Dev 进度测试，Dev 做到哪测到哪。阶段性全量回归。

## Rules

- Bug tracking: GitHub Issues (`gh issue list`, `gh issue create`)
- One bug = one commit, reference issue: `fixes #N`
- All issue comments must include Agent ID
- Code quality must survive public scrutiny
- Only operate within `~/Ace/naturo/`
- **v0.3.0 已发布，不要再看 v0.3.0 milestone**
