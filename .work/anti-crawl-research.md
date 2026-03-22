# 自然机器人反爬/反检测能力调研报告

> 调研日期: 2026-03-22
> 调研范围: Naturobot-Dev（23个 rpa-client 仓库 + naturo-sync + rpa-template-library）, Naturobot-Client（客户端引擎）, natagent-dev/natagent-serveragent（Agent 服务）, 本地项目

---

## 一、能力总览

| 类别 | 成熟度 | 关键项目 |
|------|--------|----------|
| 浏览器指纹伪装（Stealth JS 注入） | ★★★★ 生产可用 | biaopin, beijingjuntai, henjiuyiqian |
| 验证码处理（滑块/旋转/点选） | ★★★★★ 非常成熟 | naturo-sync/anti_crawl, biaopin, henjiuyiqian |
| 鼠标轨迹模拟 | ★★★★ 生产可用（两套算法） | biaopin（贝塞尔曲线）, henjiuyiqian（四段加速度） |
| Chrome 反检测参数 | ★★★★ 已统一整理 | naturo-sync/anti_crawl/browser |
| 登录态/Session 管理 | ★★★ 基本可用 | naturo-sync/anti_crawl/login |
| 请求频率控制 | ★★☆ 框架已有，待完善 | naturo-sync/anti_crawl/rate_limit |
| 浏览器指纹随机化（Canvas/WebGL） | ★☆☆ 仅框架定义 | naturo-sync/anti_crawl/browser/fingerprint.py |
| 多浏览器 Profile 管理 | ★★★ 基本可用 | NatureBrowser, naturo-sync/browser |
| 底层引擎能力（MinHook/Phys32） | ❌ 未找到 | Naturobot_Client_Engine（C++ 引擎，未发现反爬相关） |
| IP/代理管理 | ❌ 完全缺失 | 所有项目均未实现 |
| TLS/JA3 指纹 | ❌ 完全缺失 | — |

---

## 二、详细技术分析

### 2.1 浏览器指纹伪装（Stealth JS 注入）

**成熟度: ★★★★ — 已在生产环境跑了多个客户**

#### 出处
- `Naturobot-Dev/rpa-client-biaopin` → `src/crawlers/dy_data.py`, `src/crawlers/xhs_data.py`
- `Naturobot-Dev/rpa-client-beijingjuntai` → `聚光平台至企微智能表格.py`

#### 核心代码

通过 CDP `Page.addScriptToEvaluateOnNewDocument` 在每个新文档加载前注入反检测 JS：

```python
stealth_js = """
    // 1. 隐藏webdriver属性
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    delete navigator.__proto__.webdriver;

    // 2. 伪造chrome对象
    window.navigator.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};

    // 3. 修改permissions.query行为
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );

    // 4. 伪造plugins
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});

    // 5. 设置语言
    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});

    // 6. 伪造platform
    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});

    // 7. 修改硬件并发数（避免headless特征）
    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});

    // 8. 伪造deviceMemory
    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});

    // 9. Canvas 指纹扰动（修改像素防止追踪）
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        if (type === 'image/png' || type === undefined) {
            const context = this.getContext('2d');
            if (context) {
                const pixel = context.getImageData(0, 0, 1, 1);
                pixel.data[0] = pixel.data[0] ^ 1;
                context.putImageData(pixel, 0, 0);
            }
        }
        return origToDataURL.apply(this, arguments);
    };

    // 10. WebGL 渲染器信息伪装
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter.call(this, parameter);
    };
"""
page.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=stealth_js)
page.run_js(stealth_js)
```

**注入方式（DrissionPage）:**
```python
# 双重注入：CDP 新文档拦截 + 当前页面直接执行
page.run_cdp('Page.addScriptToEvaluateOnNewDocument', source=stealth_js)
page.run_js(stealth_js)
```

#### 覆盖的检测点（10项）
1. `navigator.webdriver` → 隐藏自动化标识
2. `window.chrome` → 伪造 Chrome 运行时对象
3. `navigator.permissions.query` → 修复权限查询行为
4. `navigator.plugins` → 伪造插件列表
5. `navigator.languages` → 设置中文语言
6. `navigator.platform` → 伪造 Win32 平台
7. `navigator.hardwareConcurrency` → 避免 headless 特征（设为 8）
8. `navigator.deviceMemory` → 伪造 8GB 内存
9. **Canvas 指纹** → XOR 像素扰动（每次产生不同指纹）
10. **WebGL 渲染器** → 伪装为 Intel Iris OpenGL Engine

#### 适用性评估
- **迁移难度: 低** — 纯 JS 注入，与 naturo 的 CDP 模块天然兼容
- **价值: 极高** — 通过抖音/小红书等平台的基础检测
- **改进空间**: 当前是静态伪装，应改为随机化（每个 session 不同的指纹组合）

---

### 2.2 验证码处理

**成熟度: ★★★★★ — 最成熟的能力，已在 naturo-sync 中模块化**

#### 出处
- `naturo-sync/src/anti_crawl/captcha/` — 统一模块（已从 14 个客户项目提取）
- `Naturobot-Dev/rpa-client-biaopin` → `dy_data.py` (Chaojiying_Client 类)
- `Naturobot-Dev/rpa-client-henjiuyiqian` → `抖音关键词_视频_评论.py`, `小红书品牌词.py`
- `Naturobot-Dev/rpa-client-beijingjuntai` → `专业号后台.py`

#### 支持的验证码类型

| 验证码类型 | 识别服务 | 平台 | 状态 |
|-----------|---------|------|------|
| 滑块验证码（缺口定位） | 超级鹰 (codetype=9101) | 抖音 | ✅ 生产可用 |
| 文字点选验证码 | 超级鹰 (codetype=9004) | 抖音 | ✅ 生产可用 |
| 旋转验证码 | 云码 (type=41114) | 小红书/抖音 | ✅ 生产可用 |
| 图形点选验证码 | 超级鹰 (codetype=9004) | 抖音 | ✅ 生产可用 |

#### 架构设计（naturo-sync 已模块化）

```
anti_crawl/captcha/
├── base.py                    # CaptchaSolver 抽象基类
├── xiaohongshu.py             # 小红书旋转验证码
├── douyin.py                  # 抖音多类型验证码（自动检测类型）
└── providers/
    ├── chaojiying.py          # 超级鹰（滑块/点选）
    └── yunma.py               # 云码（旋转）
```

#### 关键流程

**小红书旋转验证码:**
```
检测 red-captcha-rotate 元素 → 下载内圈/外圈图片 → Base64 编码
→ 云码 API 识别角度 → 角度转像素偏移 (x = angle * 250 / 314.685)
→ 四段加速度轨迹拖拽
```

**抖音滑块验证码:**
```
切换到 iframe → 截图背景 → 调整尺寸(340x212) → 超级鹰识别缺口位置
→ 计算偏移 (x = pic_str坐标 - 34) → 贝塞尔曲线轨迹拖拽
```

**抖音文字点选:**
```
截图验证码区域 → 超级鹰识别文字坐标 → 坐标转换为屏幕坐标
→ pyautogui 模拟点击 → 点击确认按钮
```

#### 适用性评估
- **迁移难度: 低** — naturo-sync 已经模块化，可直接集成
- **价值: 极高** — 验证码是最大的采集障碍
- **注意**: 依赖第三方打码服务（超级鹰/云码），有费用和可靠性问题

---

### 2.3 鼠标轨迹模拟

**成熟度: ★★★★ — 两套算法，biaopin 版本更先进**

#### 算法一：四段加速度模型（henjiuyiqian 原版）

**出处**: `naturo-sync/src/anti_crawl/trajectory/slider.py`（已提取）

```
阶段1 (0%~10%-20%):  启动加速  a = random(10, 15)
阶段2 (10%~65%-76%): 匀速前进  a = random(30, 40)
阶段3 (65%~84%-88%): 急减速    a = -70
阶段4 (84%~100%):    精确停靠  a = random(-25, -18)
```

回退策略:
- 超出 > 8px: `[-1, sub, -3, -1, -1, -1, -1]`
- 超出 2~8px: `[-1, -1, sub]`
- 超出 < 2px: 不回退

#### 算法二：三阶贝塞尔曲线（biaopin 进阶版）

**出处**: `Naturobot-Dev/rpa-client-biaopin` → `src/crawlers/dy_data.py`

```python
def _generate_human_track(self, distance):
    """
    用贝塞尔曲线生成拟人轨迹点序列 [(dx, dy, duration), ...]
    特点：慢启动 → 中段加速 → 过冲 → 缓回
    """
    # 1. 过冲量：人几乎总会滑过头一点
    overshoot = random.uniform(8, 18)
    total_dist = distance + overshoot

    # 2. 贝塞尔曲线生成主路径（带Y轴漂移，因为人手不走直线）
    y_drift = random.uniform(-4, 6)
    p0 = (0, 0)
    p1 = (total_dist * random.uniform(0.25, 0.4), random.uniform(-3, 5))
    p2 = (total_dist * random.uniform(0.7, 0.85), y_drift + random.uniform(-2, 2))
    p3 = (total_dist, y_drift + random.uniform(-1, 1))

    # 3. 转换为增量 + 速度相关抖动 + 变速时间间隔
    # 4. 5% 概率插入微停顿（模拟犹豫）
    # 5. 回调修正（缓慢回退到精确位置）
    # 6. 末尾微颤（手指准备松开时的不稳定）
```

**拖拽执行的拟人细节：**
```python
# 1. 不精准对准滑块中心
driver.actions.move_to(slider, offset_x=random.randint(-3, 3), offset_y=random.randint(-2, 2))
# 2. 看到滑块后的反应时间
time.sleep(random.uniform(0.4, 1.0))
# 3. 按下前轻微延迟
driver.actions.hold(slider)
time.sleep(random.uniform(0.08, 0.25))
# 4. 贝塞尔曲线正向拖拽（带速度相关抖动）
# 5. 到达过冲位置后的微停（人意识到滑过了）
time.sleep(random.uniform(0.15, 0.4))
# 6. 回调修正
# 7. 末尾微颤（手指准备松开时的不稳定）
for _ in range(random.randint(2, 4)):
    driver.actions.move(offset_x=random.gauss(0, 0.4), ...)
```

#### 适用性评估
- **迁移难度: 低** — 纯 Python 算法，无外部依赖
- **价值: 高** — 贝塞尔曲线版本的拟人效果远优于简单轨迹
- **建议**: 优先集成 biaopin 的贝塞尔曲线版本，四段加速度作为降级方案

---

### 2.4 Chrome 反检测启动参数

**成熟度: ★★★★ — 已在 naturo-sync 中统一整理**

#### 出处
- `naturo-sync/src/anti_crawl/browser/chrome_options.py`
- 统计自 14 个客户项目中 255 次出现的 Chrome 参数

#### 参数分级体系

**核心反检测（必须启用）:**
```
--disable-blink-features=AutomationControlled  # 24次出现，最关键
```

**稳定性（推荐启用）:**
```
--hide-crash-restore-bubble       # 25次
--no-first-run                    # 12次
--no-sandbox                      # 14次（Windows 必须）
--disable-popup-blocking          # 11次
--remote-allow-origins=*          # 14次
--ignore-certificate-errors       # 9次
```

**性能优化（可选）:**
```
--disable-gpu                     # 13次
--disable-feature=VideoPlayback   # 21次
--disable-background-networking   # 8次
--disable-sync                    # 10次
```

**Chrome Preferences:**
```python
"credentials_enable_service": False     # 阻止"自动保存密码"
"download.prompt_for_download": False   # 阻止下载提示
```

#### 适用性评估
- **迁移难度: 极低** — naturo 已有 CDP 模块，参数直接复用
- **价值: 高** — `--disable-blink-features=AutomationControlled` 是基础中的基础

---

### 2.5 登录态/Session 管理

**成熟度: ★★★ — 基本可用，但方案较简单**

#### 出处
- `naturo-sync/src/anti_crawl/login/session_manager.py`
- `naturo-sync/src/browser/manager.py`（Chrome Profile 池管理）
- `NatureBrowser/src/services/profileManager.js`（Electron 多 Profile）

#### 当前方案
```
每个账号 → 独立的 Chrome user-data-dir → Cookie 持久化
  - 首次扫码登录，之后依赖 Cookie
  - 没有 Cookie 池、没有多账号轮换
  - Windows 桌面快捷方式(.lnk)传递 user-data-dir 参数
```

#### NatureBrowser 的增强
- Electron 架构的多 Profile 管理
- 基于 domain 的账号映射（记住每个网站用哪个 Profile）
- 多 tab 管理

#### 适用性评估
- **迁移难度: 中** — Profile 管理逻辑可复用，但 Cookie 池需要新建
- **价值: 中高** — 登录态管理是自动化的基础，但还不够强（缺少 Cookie 池、多账号轮换）

---

### 2.6 请求频率控制

**成熟度: ★★☆ — naturo-sync 有框架，但原始项目都只用 sleep**

#### 出处
- `naturo-sync/src/anti_crawl/rate_limit/limiter.py`

#### 当前状态
所有 14 个客户项目的频率控制方式:
```python
# 固定延迟（最常见）
time.sleep(3)

# 随机延迟（较少使用）
time.sleep(random.uniform(2, 5))

# HTTP 请求自动重试
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, connect=5, read=5)
```

#### naturo-sync 新增的 RateLimiter
```python
limiter = RateLimiter(platform="xiaohongshu")
for item in items:
    limiter.wait()           # 随机化延迟
    try:
        result = fetch(item)
        limiter.record_success()  # 逐步恢复速度
    except RateLimitError:
        limiter.record_failure()  # 指数退避
```

**各平台默认配置：**
| 平台 | 最小延迟 | 最大延迟 | 退避倍率 | 最大退避 |
|------|---------|---------|---------|---------|
| 小红书 | 2.0s | 5.0s | 2x | 60s |
| 抖音 | 1.5s | 4.0s | 2x | 60s |
| B站 | 1.0s | 3.0s | 1.5x | 30s |
| 美团 | 2.0s | 5.0s | 2x | 120s |

#### 适用性评估
- **迁移难度: 极低** — 纯逻辑代码
- **价值: 中** — 比 sleep 好，但仍是基础方案（缺乏基于响应头分析的智能限流）

---

### 2.7 浏览器指纹随机化

**成熟度: ★☆☆ — 仅框架定义，未实现**

#### 出处
- `naturo-sync/src/anti_crawl/browser/fingerprint.py`

#### 当前状态
- 定义了 `FingerprintRandomizer` 类
- 内置 UA 池（5 个 Chrome UA）和屏幕分辨率池（5 种）
- `apply_to_page()` 方法直接 `raise NotImplementedError`
- 注释标注为 "Phase 3 规划"

#### 适用性评估
- **迁移难度: 中** — 需要新实现，但 stealth JS 已有 Canvas/WebGL 的基础
- **价值: 高** — 高频采集场景下指纹随机化是刚需
- **建议**: 将 stealth JS 中的 Canvas/WebGL 伪装与 FingerprintRandomizer 合并，实现每 session 随机化

---

### 2.8 多浏览器 Profile 管理

**成熟度: ★★★**

#### 出处
- `natagent-serveragent/NatureBrowser` — Electron 多 Profile 浏览器
- `naturo-sync/src/browser/manager.py` — Python Profile 池

#### NatureBrowser 特性
- 基于 Electron 的多 Profile 管理
- 域名-账号映射（自动记住哪个网站用哪个 Profile）
- 独立的 session partition per profile
- Tab 管理

#### naturo-sync BrowserManager 特性
- 跨平台 Chrome 检测（Windows/macOS/Linux）
- Profile 创建/列表/清理
- 登录状态检测

#### 适用性评估
- **迁移难度: 中** — 概念可复用，但 naturo 是 Windows RPA 工具，架构不同
- **价值: 中** — naturo 当前以单机单浏览器为主，多 Profile 在规模化场景才需要

---

### 2.9 Natagent VNC Sandbox

**出处**: `natagent-dev/Natagent-VNC-SandBox`

#### 架构
- Docker + K8s 部署
- 提供远程桌面环境，可运行浏览器
- 用于 Agent 隔离执行

#### 适用性评估
- **迁移难度: 高** — 完整的基础设施方案，与 naturo 单机 RPA 架构差异大
- **价值: 中** — 云端 RPA 才需要，naturo 当前是客户端 RPA

---

## 三、完全缺失的能力

### 3.1 IP/代理管理 ❌
**所有项目都没有代理池/IP 轮换**。这是当前最大的短板：
- 被封 IP 后没有自动切换机制
- 没有代理服务集成（如 SmartProxy、Bright Data 等）
- 没有 IP 质量检测

### 3.2 TLS/JA3 指纹 ❌
- 没有 JA3 指纹定制
- 没有 TLS ClientHello 修改
- 现代反爬系统（Cloudflare、DataDome）高度依赖 TLS 指纹

### 3.3 底层引擎能力 ❌
- `Naturobot_Client_Engine`（C++ 引擎）未发现 MinHook/Phys32 等反爬相关代码
- 引擎主要是 UI 自动化（Accessibility/MSAA），不涉及网络层反检测
- 没有发现硬件键盘模拟（Phys32）

### 3.4 Cloudflare/DataDome 绕过 ❌
- 没有专门的 WAF 绕过方案
- 依赖 stealth JS + 真实浏览器环境隐式绕过
- 没有 challenge 页面自动处理

---

## 四、能力迁移到 naturo 的评估

### 优先级矩阵

| 能力 | 迁移难度 | 价值 | 优先级 |
|------|---------|------|--------|
| Stealth JS 注入 | 低 | 极高 | 🔴 P0 — 立即集成 |
| Chrome 反检测参数 | 极低 | 高 | 🔴 P0 — 立即集成 |
| 验证码处理框架 | 低 | 极高 | 🟠 P1 — 第二批 |
| 贝塞尔曲线轨迹 | 低 | 高 | 🟠 P1 — 第二批 |
| 四段加速度轨迹 | 极低 | 中高 | 🟠 P1 — 降级方案 |
| 频率控制 | 极低 | 中 | 🟡 P2 — 第三批 |
| 登录态管理 | 中 | 中高 | 🟡 P2 — 第三批 |
| 指纹随机化 | 中 | 高 | 🟡 P2 — 与 Stealth JS 合并 |
| IP/代理管理 | 高（需新建） | 极高 | 🔵 P3 — 规划中 |
| TLS/JA3 指纹 | 高（需新建） | 高 | 🔵 P3 — 规划中 |

### P0 集成方案（建议）

naturo 已有 `naturo/cdp.py` CDP Client，直接扩展：

```python
# naturo/anti_detect.py (新增)
class AntiDetect:
    """反检测模块 — 从 14 个 RPA 客户项目提炼"""
    
    STEALTH_JS = """..."""  # 从 biaopin 提取的完整 stealth JS
    
    CHROME_ARGS = {
        "minimal": ["--disable-blink-features=AutomationControlled"],
        "standard": [...],  # 从 chrome_options.py 复用
        "full": [...],
    }
    
    def inject_stealth(self, cdp_client):
        """注入反检测脚本"""
        cdp_client.send("Page.addScriptToEvaluateOnNewDocument", source=self.STEALTH_JS)
    
    def get_chrome_args(self, level="standard"):
        """获取 Chrome 启动参数"""
        return self.CHROME_ARGS[level]
```

---

## 五、总结

### 已有能力的核心价值

1. **Stealth JS 10 项检测点覆盖** — 实战验证，通过小红书/抖音检测
2. **三种验证码类型全覆盖** — 滑块/旋转/点选，两个打码服务
3. **两套拟人轨迹算法** — 四段加速度（简单可靠）+ 贝塞尔曲线（高拟真）
4. **统一模块化架构** — naturo-sync 已做好抽象，可直接复用

### 最大短板

1. **没有代理/IP 管理** — 规模化采集的致命缺陷
2. **没有 TLS 指纹定制** — 高防网站（Cloudflare 等）无法绕过
3. **指纹随机化未实现** — 同一机器多次采集会被关联
4. **客户端引擎 C++ 层没有反爬能力** — 期待的 MinHook/Phys32 不存在

### 建议路线

```
Phase 1 (1-2 周): 集成 Stealth JS + Chrome Args → naturo anti_detect 模块
Phase 2 (2-3 周): 集成验证码框架 + 贝塞尔曲线轨迹
Phase 3 (3-4 周): 实现指纹随机化 + 频率控制
Phase 4 (需规划): IP/代理池 + TLS 指纹（这是新能力，非迁移）
```
