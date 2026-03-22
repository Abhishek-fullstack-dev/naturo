# Agent 协作规则

## 共享状态
- **项目状态**: `agents/STATE.md` — 只读参考，由闹呢维护
- **Bug 跟踪**: `.work/bugs.md` — Dev 修改状态，QA 添加/验证
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
   - 是否已在 bugs.md 中（去重）
   - 严重度是否合理（可调整）
   - 是否能复现
3. **转化**为 bugs.md 条目：
   - 新问题 → 添加到 bugs.md，注明来源 `[External Test Round N]`
   - 重复问题 → 在已有条目补充外部视角
   - 不认同的 → 写理由，保留在报告中不删
4. **回写**处理状态到 round 报告末尾：
   ```
   ## 🔄 QA 处理记录
   - ISSUE-E001 → 转为 BUG-075 (P0)
   - ISSUE-E002 → 已有 BUG-073，补充外部视角
   - ISSUE-E003 → 不认同，理由：...
   ```

### Dev 职责
- 正常按 bugs.md 优先级修 bug，无需关心来源
- 来源标注 `[External Test]` 的 bug 优先级可能更高（因为是真实用户视角）

## 通用规则
1. 只操作 `~/Ace/naturo/` 目录
2. 一个 bug = 一个 commit
3. 代码质量要经得起全世界 review
4. README.md 每次功能进展后同步更新
5. 版本号变更需要同步 Python + DLL
