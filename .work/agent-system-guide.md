# Naturo AI Agent 开发体系完整指南

> 本文档描述 Naturo 项目的 AI Agent 自动化开发体系的完整逻辑，供团队成员参考。

---

## 一、整体架构

```
闹呢 (Chief / 中央调度)
  ├── Dev-Sirius (开发 Agent) — cron 每 15 分钟
  ├── QA-Mariana (测试 Agent) — cron 每 30 分钟
  └── 临时 Subagent (按需) — 大任务拆分
```

- **闹呢**：中央 Gateway（Mac），统筹全局，接收 Ace 指令，起 subagent，汇报进展
- **Dev-Sirius**：技术合伙人，自动领 Issue、修 bug、开 PR、合代码
- **QA-Mariana**：质量合伙人，真机验证、嘈杂环境测试、应用 E2E 兼容性测试
- **测试机**：Windows 编译机（100.113.29.45），SSH 可达，有桌面会话

---

## 二、Cron 调度规则

### Dev-Sirius
| 配置 | 值 |
|------|-----|
| 频率 | 每 15 分钟 |
| 超时 | 7200 秒（2 小时） |
| 交付 | announce 到主 session → 飞书通知 Ace |

**每轮流程：**
1. 读 SOUL.md + RULES.md + ROADMAP.md
2. 检查 CI 状态 → 红了先修
3. Triage open issues → P0 优先
4. 领 Issue → 开分支 → 修 → 测试 → PR → 合并
5. 发现技术债 → 开 Issue（标签 `tech-debt`）
6. **绝不直接 push main，绝不无 commit 关 Issue**

### QA-Mariana
| 配置 | 值 |
|------|-----|
| 频率 | 每 30 分钟 |
| 超时 | 7200 秒（2 小时） |
| 交付 | announce 到主 session → 飞书通知 Ace |

**每轮流程：**
1. 读 SOUL.md + QA-METHODOLOGY.md + RULES.md
2. 检查 Dev 标记 `status:done` 的 Issue → 真机验证
3. 验证通过 → `verified` 标签；失败 → 打回
4. 主动探索性测试（嘈杂环境 + 应用 E2E）
5. 新 bug → 开 Issue（标签 `bug,from:qa,PX`）
6. **测试完清理环境：只关自己打开的应用**

---

## 三、核心铁律

### 开发铁律
1. **永远走 PR 流程**：feature branch → PR → CI green → squash merge
2. **CI 红了停一切**：先修 CI，再做别的
3. **不关未来版本的 Issue**：当前版本 v0.3.0，不碰 v0.4.0+ 的
4. **技术债必须开 Issue**：Agent 无跨轮记忆，Issue 就是记忆
5. **版本号 4 处同步**：`pyproject.toml` + `naturo/version.py` + `core/src/version.cpp` + `core/CMakeLists.txt`

### 质量铁律
1. **绝不说谎**：naturo 报告成功必须真的成功，否则必须报错（#226 教训）
2. **验证诚信**：永远不信 stdout，只信截图证据。每步操作后截图 + AI vision 确认
3. **无截图验证 = 无效报告**
4. **静默失败 = P0 bug**：发现"报告成功但截图无变化" → 标签 `silent-failure`

### 嘈杂环境测试
- 每轮至少一组：同时开 5-8 个应用
- 验证 `--app` 过滤精准度
- 验证同一应用多实例区分
- 误操作到其他窗口 = P0

### 应用 E2E 兼容性测试
- 每轮测 1-2 个应用的完整真实操作流程
- 截图 + AI 验证每一步
- 结果更新 `docs/SUPPORTED_APPS.md`
- 优先：记事本 → 计算器 → 文件管理器 → 画图 → Excel → 浏览器

---

## 四、发版流程

详见 `docs/RELEASE.md`。

1. Dev/QA 完成一批修复 → patch（0.x.y+1）
2. ROADMAP 里程碑完成 + 全面 QA → minor（0.x+1.0）
3. **发版前必须 Ace 确认**
4. 更新 4 处版本号 → commit → tag → GitHub Release → CI 自动发 PyPI

---

## 五、文件结构

```
agents/
  ├── RULES.md              # 全局规则（Dev+QA 共遵守）
  ├── STATE.md              # 当前项目状态
  ├── VISION.md             # 产品愿景
  ├── dev/
  │   ├── SOUL.md           # Dev 的身份、原则、铁律
  │   └── status.md         # Dev 当前状态
  ├── qa/
  │   ├── SOUL.md           # QA 的身份、原则、铁律
  │   ├── QA-METHODOLOGY.md # QA 方法论（5 原则 + 4 层测试 + SFDPOT）
  │   ├── APP_TEST_PLAYBOOK.md  # 应用 E2E 测试手册
  │   ├── ACE-TESTING-LESSONS.md  # 真机测试教训
  │   └── status.md         # QA 当前状态
  └── external-tester/
      └── SOUL.md           # 第三方测试者 prompt

docs/
  ├── ROADMAP.md            # 版本规划（0.1.0 ~ 1.0.0）
  ├── RELEASE.md            # 发版流程（内部）
  ├── SUPPORTED_APPS.md     # 应用兼容性矩阵（用户可见）
  ├── ARCHITECTURE.md       # 技术架构
  ├── ERROR_CODES.md        # 错误码定义
  └── design/
      ├── UNIFIED_APP_MODEL.md    # 统一应用模型设计
      ├── UNIFIED_SELECTOR.md     # 统一选择器设计
      └── NPM_DISTRIBUTION.md    # npm 分发方案

.github/workflows/
  ├── build.yml             # CI: 版本检查 + 多平台测试 + DLL 编译
  └── publish.yml           # CD: GitHub Release → PyPI 自动发布

.work/                      # 工作临时文件
  ├── qa-round{N}-report.md # QA 每轮报告
  ├── report-audit.md       # 报告审计结果
  └── ...
```

---

## 六、GitHub Issue 标签体系

| 标签 | 颜色 | 含义 |
|------|------|------|
| `bug` | 红 | Bug |
| `enhancement` | 蓝 | 新功能 |
| `tech-debt` | 黄 | 技术债 |
| `silent-failure` | 深红 | 说谎 bug（报告成功但无效果） |
| `P0` | — | 最高优先级 |
| `P1` | — | 高优先级 |
| `P2` | — | 中优先级 |
| `from:qa` | — | QA 发现 |
| `from:ace` | — | Ace 发现 |
| `status:in-progress` | — | 开发中 |
| `status:done` | — | 开发完成待验证 |
| `verified` | — | QA 验证通过 |
| `app-compat` | — | 应用兼容性问题 |

---

## 七、关键经验教训

1. **Agent cron session 没有跨轮记忆** → 所有发现必须写进 Issue
2. **CI 红是最高优先级** → 一切停下来先修 CI
3. **QA 38 轮没发现的问题用户 5 分钟就发现** → 真机测试 > mock 测试
4. **Session 超 2MB 会卡死** → cron 自动 reset 保护
5. **naturo 静默失败比报错更危险** → 操作后必须验证效果
6. **版本号有 4 处** → 少改一处 CI 就红
7. **Agent 发版需要 Ace 确认** → 防止未经测试的代码上 PyPI

---

## 八、Quick Start（新成员）

1. 克隆仓库：`git clone git@github.com:AcePeak/naturo.git`
2. 读 `agents/VISION.md` 理解产品方向
3. 读 `docs/ROADMAP.md` 理解当前版本目标
4. 读 `agents/RULES.md` 理解全局规则
5. 读对应角色的 `SOUL.md`（Dev 或 QA）
6. 跑一遍测试：`python -m pytest tests/ -x -q`
7. 看 open issues：`gh issue list --state open --label P0`
8. 开干

---

*最后更新：2026-03-24*
