# Agent 协作规则

## 共享状态
- **项目状态**: `agents/STATE.md` — 只读参考，由闹呢维护
- **Bug 跟踪**: **GitHub Issues** (https://github.com/AcePeak/naturo/issues) — 所有 bug 通过 `gh issue create` 创建和跟踪
- **历史记录**: `.work/bugs.md` — 仅保留历史记录，不再更新
- **外部测试**: `.work/external-test/round-*.md` — 外部测试员写入，Dev/QA 读取

## 角色边界
- **Dev**: 修 bug、写代码、跑 CI。不做测试决策。
- **QA**: 发现 bug、验证修复、质量评估。不改代码。
- **External Tester**: 用户视角测试，写报告。不改代码，不改 bugs.md。
- **闹呢**: 统筹协调、对外沟通、最终决策。

## 外部测试报告处理流程

### QA 职责
每轮启动时，检查 `.work/external-test/` 是否有新的 round 报告：
1. **读取**新的 external test round 报告
2. **评估**每个 ISSUE-E*：
   - 是否已在 GitHub Issues 中（去重）
   - 严重度是否合理（可调整）
   - 是否能复现
3. **转化**为 GitHub Issue：
   - 新问题 → `gh issue create --label "bug,P0,from:external"` 创建 issue
   - 重复问题 → `gh issue comment` 在已有 issue 补充外部视角
   - 不认同的 → 写理由，保留在报告中不删
4. **回写**处理状态到 round 报告末尾：
   ```
   ## 🔄 QA 处理记录
   - ISSUE-E001 → 转为 GitHub Issue #XX (P0)
   - ISSUE-E002 → 已有 Issue #YY，补充外部视角
   - ISSUE-E003 → 不认同，理由：...
   ```
5. **验证修复**后：`gh issue comment` 添加验证结果 + `gh label add verified`

### Dev 职责
- 从 GitHub Issues 获取待修 bug：`gh issue list --label bug --label P0`
- 修完后 `gh issue comment` 说明修复 + commit message 关联 `fixes #N`
- 来源标注 `from:external` 的 bug 优先级可能更高（因为是真实用户视角）

## 通用规则
1. 只操作 `~/Ace/naturo/` 目录
2. 一个 bug = 一个 commit，commit message 关联 issue：`fix: [BUG-XXX] 简述 (fixes #N)`
3. 代码质量要经得起全世界 review
4. README.md 每次功能进展后同步更新
5. 版本号变更需要同步 Python + DLL
6. Bug 跟踪使用 GitHub Issues，不再使用 `.work/bugs.md`
