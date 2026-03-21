# Dev Status

## 最新更新: 2026-03-21 13:54 CST

### 本轮工作
修复 3 个 Open bug（open 命令组）：

1. **BUG-065** 🟢 Fixed — `open ""` / `open "   "` 空目标校验
   - 入口处添加 `target.strip()` 检查，返回 INVALID_INPUT
   - commit: fce9954

2. **BUG-067** 🟢 Fixed — `open nonexistent_file.xyz` Windows 上挂起
   - 非 URL 目标先检查 `os.path.exists()`，不存在返回 FILE_NOT_FOUND
   - `subprocess.run` 添加 `timeout=15` 防无限阻塞
   - 修正 `start` 命令参数（加空 title 参数）
   - commit: deffa3e

3. **BUG-066** 🟢 Fixed — `open --app` 未实现但暴露
   - `hidden=True` 隐藏参数，保留向后兼容
   - commit: 3ca9089

### 测试
- 1480 passed, 306 skipped (macOS)
- 6 个新回归测试（TestOpenValidation）
- 已 SCP 到编译机

### Bug 状态
- 🔴 Open: 0
- 🟢 Fixed (待验证): 3 (BUG-065/066/067)
- ✅ Verified: 64

### 当前分支
main — 已 push
