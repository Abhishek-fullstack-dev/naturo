# NPM Distribution Design — `npx naturo mcp`

## 目标

让用户通过 `npm install naturo` 或 `npx naturo` 使用 naturo，**无需安装 Python**。

## 方案：Thin Wrapper + Platform Binary（推荐）

### 架构

```
npm package (naturo)          ~5KB
  └── postinstall script
        └── 检测 platform+arch
        └── 从 GitHub Releases 下载对应二进制
              ├── naturo-win-x64.exe     (~40-60MB)
              ├── naturo-linux-x64       (~40-60MB)
              └── naturo-macos-arm64     (~40-60MB)
```

### 用户体验

```bash
# 安装
npm install -g naturo
# 或一次性使用
npx naturo see
npx naturo mcp
```

### 先例

| 工具 | 方案 | 包体 |
|------|------|------|
| esbuild | npm thin wrapper + platform binary | ~9MB |
| turbo | npm thin wrapper + platform binary | ~20MB |
| playwright | npm + 按需下载浏览器 | ~2MB + browsers |
| prisma | npm + 按需下载 engine binary | ~5MB + engine |

### 实现步骤

#### Step 1: Standalone Binary (Nuitka)

使用 Nuitka 将 Python + naturo 编译为单文件可执行：

```bash
nuitka --standalone --onefile \
  --include-package=naturo \
  --include-data-files=naturo_core.dll=naturo_core.dll \
  --output-filename=naturo.exe \
  naturo/__main__.py
```

CI 矩阵：
- Windows x64 (windows-latest)
- Linux x64 (ubuntu-latest)  
- macOS arm64 (macos-latest)

产物上传到 GitHub Release assets。

#### Step 2: npm Package

```
packages/naturo-npm/
  ├── package.json
  ├── bin/naturo.js          # CLI entry point
  ├── install.js             # postinstall 下载脚本
  └── lib/
      └── platform.js        # platform detection + download logic
```

**package.json:**
```json
{
  "name": "naturo",
  "version": "0.3.0",
  "description": "Windows desktop automation for AI agents",
  "bin": { "naturo": "bin/naturo.js" },
  "scripts": { "postinstall": "node install.js" },
  "os": ["win32", "linux", "darwin"],
  "cpu": ["x64", "arm64"]
}
```

**bin/naturo.js:**
```javascript
#!/usr/bin/env node
const { execFileSync } = require('child_process');
const path = require('path');
const binary = path.join(__dirname, '..', 'bin', process.platform === 'win32' ? 'naturo.exe' : 'naturo');
execFileSync(binary, process.argv.slice(2), { stdio: 'inherit' });
```

**install.js:**
```javascript
// 1. 检测 platform + arch
// 2. 构造下载 URL: https://github.com/AcePeak/naturo/releases/download/vX.Y.Z/naturo-{platform}-{arch}{.exe}
// 3. 下载到 bin/
// 4. chmod +x (非 Windows)
```

#### Step 3: MCP 场景

```bash
# AI agent 配置
npx naturo mcp --transport stdio
# 或
npx naturo mcp --transport sse --port 8080
```

零配置启动 MCP server，这是 npm 包的核心价值场景。

### 备选方案（已排除）

#### ❌ 方案 B: npm 内嵌 Python Embedded

```
node_modules/naturo/
  python-3.12-embed/   (~15-40MB)
  naturo/              (Python 源码)
```

排除原因：
- 包体大（npm install 慢）
- Python Embedded 在 Linux/macOS 上不好用
- 更新 Python 源码要重新发 npm 包
- 权限和路径问题多

#### ❌ 方案 C: npm wrapper + 要求装 Python

排除原因：
- 用户体验差，回到"请先装 Python"
- Python 版本兼容问题转嫁给用户
- 违背"零依赖"目标

### 版本同步

- npm 版本号与 PyPI 版本号保持一致
- GitHub Release 同时包含：
  - PyPI package (自动)
  - npm package (手动或 CI)
  - Platform binaries (CI 编译)

### 大小优化

Nuitka 默认产物可能 60-100MB，优化手段：
- `--lto=yes` (Link-Time Optimization)
- 排除不需要的标准库模块
- UPX 压缩（可选，但可能触发杀毒误报）
- 目标：**<50MB per platform**

### 依赖矩阵

| 安装方式 | 需要 Python | 需要 Node | 需要编译器 |
|----------|:-----------:|:---------:|:----------:|
| `pip install naturo` | ✅ ≥3.10 | ❌ | ❌ |
| `npx naturo` | ❌ | ✅ ≥16 | ❌ |
| GitHub Release 下载 | ❌ | ❌ | ❌ |

### 时间线

- v0.4.0: Standalone binary (Nuitka CI) + GitHub Release
- v0.4.0: npm package + postinstall download
- v0.5.0: 优化包体大小，加 auto-update 机制
