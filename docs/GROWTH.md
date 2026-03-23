# Growth Strategy — Feature-Driven, Not Calendar-Driven

## Principle

Community outreach is tied to **feature milestones that create differentiation**, not release schedules. Push when we have something unique to show, not just because we shipped a version.

## Differentiation Triggers → Growth Actions

### Trigger 1: Cascading Recognition (#140) ships
**What's unique**: No other tool does multi-method UI recognition (UIA → CDP → AI vision fallback). WeChat/Feishu/Slack — naturo sees them all.

**Actions**:
- Demo video: "naturo sees what others can't" — side-by-side with PyAutoGUI/pywinauto on WeChat
- Post to r/Python, r/AutoHotkey, Hacker News
- Submit to awesome-python, awesome-automation lists
- Peekaboo collab pitch: "We're the Windows counterpart"

### Trigger 2: OpenClaw integration solid
**What's unique**: AI agents can automate any Windows app via `npx naturo mcp start`. Codex/Claude Code can see and click.

**Actions**:
- OpenClaw skill on ClawHub
- Demo: "Claude Code automates Excel via naturo" 
- Post to AI agent communities (OpenClaw Discord, Claude Discord, Codex forums)
- Blog: "How to give your AI agent eyes and hands on Windows"

### Trigger 3: CLI UX polished (v0.2.x complete)
**What's unique**: `naturo see → click e42 --see → type "hello" --on e5` — one coherent flow, not 5 different tools duct-taped together.

**Actions**:
- "Getting Started in 60 seconds" video
- Compare with Peekaboo UX (show parity/superiority on Windows)
- RPA/testing community outreach (UiPath/Playwright users looking for lighter alternatives)

### Trigger 4: Enterprise features (visual regression, recording)
**What's unique**: Open-source alternative to commercial RPA tools for Windows desktop testing.

**Actions**:
- Case study: "Automated regression testing for legacy Win32 apps"
- Conference talk proposal (PyCon / EuroPython)
- Enterprise community partnerships

## Anti-Patterns

- ❌ "We shipped v0.3.0, let's announce" — nobody cares about version numbers
- ❌ Generic "check out our tool" posts — no differentiation, gets ignored
- ❌ Premature outreach before core is solid — first impressions matter
- ✅ "Here's something you literally cannot do with any other tool" — this gets attention

## Platforms

| Platform | Audience | Content Style |
|----------|----------|---------------|
| Hacker News | Developers, early adopters | Technical deep-dive, "Show HN" |
| Reddit (r/Python, r/automation) | Python developers | Demo + comparison |
| LinkedIn | Enterprise, decision makers | Use case stories |
| Twitter/X | Developer community | Short demos, GIFs |
| OpenClaw Discord | AI agent builders | Integration guides |
| GitHub Discussions | Contributors | Architecture decisions, RFC |

## Contributor Funnel

1. **Attract**: Differentiated demo → "how does this work?"
2. **Onboard**: Good CONTRIBUTING.md, labeled "good first issue" 
3. **Retain**: Quick PR review, recognition, roadmap input
4. **Amplify**: Contributors become advocates
