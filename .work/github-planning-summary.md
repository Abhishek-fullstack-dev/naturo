# GitHub Issues 全面规划完成报告

**执行时间**: 2026-03-22  
**执行者**: 闹呢 (subagent github-full-planning)

---

## 任务完成情况

### ✅ 1. Milestones 创建与更新

**已有 Milestones** (保留并更新描述):
- v0.2.0: Unified App Model — 自动检测应用框架并路由到最优交互通道
- v0.3.0: Enterprise Features — Excel COM、SAP GUI、MinHook、嵌入式 Python、独立可执行文件
- v0.4.0: Open Source Launch — 公开发布前的所有准备工作与发布执行

**新创建 Milestones**:
- v0.5.0: Linux Backend — X11 + Wayland 支持，全面跨平台覆盖
- v0.6.0: National OS + Enterprise Recording — UOS、Kylin 适配 + 企业级录制/回放引擎
- v1.0.0: Stable Release — API 稳定性保证、生态合作、社区发布

所有 milestone 描述已更新，包含：
- 版本核心目标
- 主要交付内容
- 交付标准 (Delivery criteria)

---

## ✅ 2. 详细 Issues 创建

### v0.2.0 (Unified App Model) — 9 个 issues

**ROADMAP 原有项目覆盖检查**:
- ✅ Framework detection chain (#26 已有)
- ✅ `naturo app inspect` (#27 已有)
- ✅ `naturo app inspect --all` (#32 新建)
- ✅ Per-PID detection cache (#33 新建)
- ✅ Auto-routing (#28 已有)
- ✅ `--method` override (#34 新建)
- ✅ `--quick` mode (#35 新建)
- ✅ MCP tools for app inspect (#36 新建)
- ✅ Integration tests (#37 新建)

**其他任务项**:
- #29 Element ref caching (已有，来自 bug fix)
- #30 Version bump script (已有)

**新建 issues**: #32, #33, #34, #35, #36, #37 (6 个)

---

### v0.3.0 (Enterprise Features) — 7 个 issues

**ROADMAP 项目完整覆盖**:
1. ✅ Excel COM automation (#38) — read/write cells, macros, charts
2. ✅ SAP GUI Scripting (#39) — 企业 ERP 自动化
3. ✅ MinHook injection (#40) — Win32 API 钩子
4. ✅ Embedded Python 3.12 runtime (#41) — ~40MB 嵌入式运行时
5. ✅ `naturo run my_script.py` (#42) — 执行用户脚本
6. ✅ Standalone executable (#43) — naturo.exe 独立可执行文件

**已有**: #21 (Naturobot engine-level RPA capabilities)

**新建 issues**: #38, #39, #40, #41, #42, #43 (6 个)

---

### v0.4.0 (Open Source Launch) — 14 个 issues (清理后)

**Pre-launch 准备** (7 个):
1. ✅ Branch protection (#44)
2. ✅ CONTRIBUTING.md + CODE_OF_CONDUCT.md (#45)
3. ✅ Issue/PR templates (#46)
4. ✅ README hero GIF (#47)
5. ✅ README badges (#49)
6. ✅ Code signing certificate (#50)
7. ✅ First PyPI release (#51)

**Distribution** (2 个):
8. ✅ npm package (#52)
9. ✅ OpenClaw skill (#53)

**Launch 执行** (5 个):
10. ✅ Flip repo to public (#54)
11. ✅ Multi-channel announcements (#55)
12. ✅ "How Naturo Works" blog post (#56)
13. ✅ Submit to awesome lists (#57)
14. ✅ Demo videos (#61)

**新建 issues**: #44-#61 (14 个，去重后保留 14 个有效)

---

### v0.5.0 (Linux Backend) — 6 个 issues (清理后)

**ROADMAP 项目完整覆盖**:
1. ✅ X11: xdotool + python-xlib (#66)
2. ✅ AT-SPI2 element inspection (#68)
3. ✅ Screenshot via Xlib / dbus portal (#74)
4. ✅ Wayland: ydotool + wlr protocols (#75)
5. ✅ CI: Ubuntu + xvfb UI tests (#77)
6. ✅ GNOME + KDE compatibility (#84)

**新建 issues**: #66, #68, #74, #75, #77, #84 (6 个)

---

### v0.6.0 (National OS + Enterprise Recording) — 5 个 issues (清理后)

**ROADMAP 项目完整覆盖**:
1. ✅ DDE (Deepin Desktop) compatibility (#87)
2. ✅ Kylin adapters (#88)
3. ✅ Self-hosted CI runner (#89)
4. ✅ Enterprise recording/playback engine (#90)
5. ✅ Enterprise visual regression testing (#91)

**新建 issues**: #87-#91 (5 个)

---

### v1.0.0 (Stable Release) — 5 个 issues (清理后)

**ROADMAP 项目完整覆盖**:
1. ✅ API stability guarantee (semver) (#92)
2. ✅ Peekaboo collaboration (#93)
3. ✅ OpenClaw recommended tool (#94)
4. ✅ Conference talk (PyCon/EuroPython) (#95)
5. ✅ RPA/testing community partnerships (#96)

**新建 issues**: #92-#96 (5 个)

---

## ✅ 3. Issue 质量标准执行

每个新建 issue 包含：
- ✅ **Description** — 清晰说明要做什么
- ✅ **Context** — 为什么要做，与产品目标的关系
- ✅ **Technical Approach** — 建议实现方式（文件/模块/API 设计）
- ✅ **Acceptance Criteria** — 明确完成标准（checklist 形式）
- ✅ **Dependencies** — 依赖其他 issue（用 #N 引用）
- ✅ **Deliverables** — 具体产出物列表
- ✅ **References** — 相关文档、竞品参考

**Labels 应用**:
- 所有 enhancement issues 都有 `enhancement` label
- Task issues 有 `task` label
- 文档类有 `documentation` label
- 每个 issue 都关联到正确的 milestone

---

## ✅ 4. Labels 创建

**新增状态 labels**:
```bash
✅ status:in-progress (fbca04) — Being worked on
✅ status:done (0e8a16) — Dev done, pending QA verification
✅ status:blocked (d73a4a) — Blocked by dependency or decision
```

**已有 labels 保留**:
- bug, enhancement, task, documentation
- P0, P1, P2, P3 (优先级)
- from:dev, from:qa, from:ace, from:external (来源)
- verified, needs-info, ux, docs

---

## ✅ 5. Dev/QA SOUL 更新

### Dev SOUL 新增内容:
1. **Issue 协作流程（铁律）**:
   - 开始工作: assign 自己 + 加 `status:in-progress` label
   - 完成开发: 移除 `status:in-progress` + 加 `status:done` + comment 通知 QA
   - 多 Dev 协作原则: 只 assign 自己，不碰别人的 issue

2. **Label 状态机**:
   ```
   无 status label → 待认领
   status:in-progress → 开发中
   status:blocked → 被阻塞（等依赖/决策）
   status:done → Dev 完成，等 QA 验证
   verified → QA 验证通过，可关闭
   ```

3. **铁律强调**: 
   - ⚠️ NEVER close an issue unless you have ACTUALLY fixed it with a commit that passes CI

### QA SOUL 新增内容:
1. **On Startup 检查**:
   ```bash
   gh issue list --label "status:done" --json number,title,labels \
     --jq '.[] | select(.labels | map(.name) | contains(["verified"]) | not) | "#\(.number) \(.title)"'
   ```

2. **验证流程**:
   - 验证通过: comment + add `verified` label
   - 验证失败: comment + remove `status:done` label

3. **验证优先级**: P0 > 当前 milestone > 其他

---

## ✅ 6. Git Commit & Push

**提交内容**:
```
commit edee168
Update Dev/QA SOULs with Issue-Driven workflow

- Dev: Add issue assignment protocol (assign self, status labels)
- Dev: Add multi-dev collaboration rules (never close others' issues)
- Dev: Clarify label state machine (in-progress → done → verified)
- QA: Enhance verification workflow with label-based filtering
- QA: Add verification priority guidance (P0 > milestone > others)
- Both: Ensure 'status:done' triggers QA verification cycle
```

Push 到 main 成功。

---

## 统计汇总

| Milestone | ROADMAP 项目数 | 已有 Issues | 新建 Issues | 总 Issues |
|-----------|---------------|------------|------------|----------|
| v0.2.0    | 9             | 3          | 6          | 9        |
| v0.3.0    | 6             | 1          | 6          | 7        |
| v0.4.0    | 14            | 0          | 14         | 14       |
| v0.5.0    | 6             | 0          | 6          | 6        |
| v0.6.0    | 5             | 0          | 5          | 5        |
| v1.0.0    | 5             | 0          | 5          | 5        |
| **总计**  | **45**        | **4**      | **42**     | **46**   |

**重复 issues 清理**: 20 个重复 issues 已关闭（都是 API 调用产生的重复提交）

---

## 下一步建议

### Dev Agent 下次启动时:
1. 运行 `gh issue list --state open --milestone "v0.2.0" --no-assignee` 查看待认领任务
2. 从 #26 (Framework detection chain) 开始，因为这是 v0.2.0 的基础
3. 每完成一个 issue，按新流程操作（assign → in-progress → done → 通知 QA）

### QA Agent 下次启动时:
1. 运行 `gh issue list --label "status:done"` 查看待验证任务
2. 优先验证 P0 issues
3. 验证通过后加 `verified` label，失败则移除 `status:done`

### 项目整体:
- 所有版本从 v0.2.0 到 v1.0.0 的路线图已完整映射到 GitHub Issues
- 每个 issue 都足够详细，外部 dev agent 可独立开发
- Labels 和 workflow 已就位，支持多人协作
- Dev/QA 流程已标准化，减少沟通成本

---

## 完成确认

✅ 所有任务完成:
1. ✅ Milestones 确认并创建 (v0.5.0, v0.6.0, v1.0.0)
2. ✅ Milestone 描述更新（所有 6 个）
3. ✅ ROADMAP 所有项目拆分成 issues (45 个项目 → 46 个 issues)
4. ✅ Issue 质量达标（每个都包含完整 8 要素）
5. ✅ Labels 创建（status:in-progress, status:done, status:blocked）
6. ✅ Dev/QA SOUL 更新并提交
7. ✅ Git commit & push

**仓库状态**: 所有改动已推送到 `main` 分支。
**Issue 链接**: https://github.com/AcePeak/naturo/issues
