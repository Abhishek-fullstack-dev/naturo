# Unified Selector System — Design Specification

**Status:** Draft  
**Version:** 0.1  
**Date:** 2026-03-22  
**Related Issues:** #23 (see→click broken), #29 (element ref caching)

---

## Background

### The Problem

Naturo's current `see` command outputs temporary element IDs (`e1`, `e2`, ...) that are ephemeral coordinate caches. These break when:

- The window moves or resizes
- Screen resolution or DPI changes
- The application re-renders its UI
- A different machine runs the same automation

This makes the `see → click` pipeline fragile and non-reproducible. Issue #23 documents this as a critical UX failure — users naturally try `see → click --id eN` and get 100% failure.

### Prior Art

**Naturobot Engine (Internal)**  
The original Naturobot RPA engine solved this by normalizing UIA, MSAA, and CDP element paths into a unified XML selector format. Elements were identified by semantic properties (role, name, automation ID) rather than coordinates, making selectors stable across sessions and machines.

**UiPath Selectors**  
UiPath uses XML-based selectors with attribute matching:
```xml
<wnd app='notepad.exe' cls='Notepad' title='*Untitled*' />
<wnd cls='Edit' />
```
Strengths: battle-tested, handles wildcards, supports partial matching.  
Weaknesses: verbose, tightly coupled to Windows UI framework internals, not AI-friendly.

**Playwright Locators**  
`page.getByRole('button', { name: 'Submit' })` — role-based, semantic, composable.  
Good model for AI-friendliness but web-only.

### Design Goals

1. **One format** covering desktop (UIA/MSAA/JAB/IA2) and browser (CDP/CSS/XPath)
2. **Semantic** — identifies elements by what they are, not where they are
3. **Cross-resolution, cross-machine** — works regardless of DPI, window position, or screen size
4. **AI agent friendly** — readable by humans, generatable by LLMs
5. **Incremental** — can coexist with the existing `eN` coordinate system during migration

---

## Selector Format Design

### Option A: URI-Style Selectors

```
app://notepad.exe/Window[@name="*Notepad"]/Button[@name="Save"]
app://notepad.exe/Edit[@automationid="txtContent"]
app://code.exe/Tree[@name="Explorer"]/TreeItem[@name="src"]
web://chrome/css:#submit-btn
web://chrome/xpath://button[text()="Login"]
web://edge/css:.modal-dialog >> button.confirm
```

**Structure:**
```
<scheme>://<app>/<node>[@attr="value"]/<node>[@attr="value"]/...
```

| Component | Description |
|-----------|-------------|
| `scheme` | `app` (desktop) or `web` (browser) |
| `app` | Process name or executable (e.g., `notepad.exe`, `chrome`) |
| `node` | UI role/control type (e.g., `Button`, `Edit`, `Window`) |
| `@attr` | Attribute filter: `name`, `automationid`, `cls`, `idx` |
| `*` | Wildcard in attribute values |

**Pros:**
- Compact, single-line, easy to paste and share
- Familiar URI syntax (developers already know it)
- Easy for AI to generate and parse
- Grep-friendly, works in CLI arguments
- Composable (chain nodes with `/`)

**Cons:**
- Escaping needed for special characters in names
- Less expressive for complex multi-attribute matching
- Nesting depth can make long selectors hard to read

### Option B: XML-Style Selectors

```xml
<selector app="notepad.exe" framework="uia">
  <node role="Window" name="*Notepad" />
  <node role="Button" name="Save" automationid="btnSave" />
</selector>
```

```xml
<selector app="chrome" framework="cdp">
  <node type="css" value="#submit-btn" />
</selector>
```

**Pros:**
- Rich attribute support (multiple attrs per node without escaping)
- Explicit framework hint
- Familiar to UiPath/Naturobot users
- Self-documenting structure

**Cons:**
- Verbose — multi-line for simple elements
- Painful as CLI arguments (quoting, escaping)
- AI models generate more errors with XML (closing tags, nesting)
- Harder to embed in JSON, log files, error messages

### Option C: Hybrid (Recommended)

**Use URI-style as the primary format** for CLI, API, and AI interactions.  
**Support XML-style as a storage/template format** for complex selectors and saved templates.

The system internally normalizes both to the same AST, so they are interchangeable:

```python
# URI-style (primary — used in CLI, logs, AI output)
selector = 'app://notepad.exe/Button[@name="Save"]'

# XML-style (templates and saved selectors)
selector = '''
<selector app="notepad.exe" framework="uia">
  <node role="Button" name="Save" />
</selector>
'''

# Both resolve to the same internal representation
```

**Rationale:**
- URI is better for the 80% case: quick, single-line, AI-generatable
- XML is better for the 20% case: complex templates with many attributes, saved/shared selectors
- No need to force one format — parse both, normalize internally

---

## Format Specification

### URI Selector Grammar

```
selector     = scheme "://" app "/" path
scheme       = "app" | "web"
app          = process-name                    ; e.g., notepad.exe, chrome
path         = node ("/" node)*
node         = role ("[" attr-list "]")?
role         = identifier                      ; e.g., Button, Edit, Window, TreeItem
attr-list    = attr ("," attr)*
attr         = "@" attr-name "=" quoted-value
attr-name    = "name" | "automationid" | "cls" | "idx" | "value" | "type" | "state"
quoted-value = '"' escaped-string '"'
```

**Special attributes:**

| Attribute | Description | Example |
|-----------|-------------|---------|
| `@name` | Element name/label | `@name="Save"` |
| `@automationid` | UIA AutomationId | `@automationid="btnSave"` |
| `@cls` | Window class name | `@cls="Edit"` |
| `@idx` | Zero-based sibling index | `@idx="2"` (third matching sibling) |
| `@value` | Current value | `@value="Hello"` |
| `@type` | Framework-specific type | `@type="css"` (for web) |
| `@state` | Element state filter | `@state="enabled"` |

**Wildcards:**
- `*` matches any substring: `@name="*Notepad*"`
- `?` matches single character: `@name="Page ?"

**Web selectors:**
```
web://chrome/css[@value="#submit-btn"]
web://chrome/xpath[@value="//button[text()='Login']"]
web://edge/css[@value=".modal >> button.confirm"]
```

### XML Selector Schema

```xml
<selector app="string" framework="uia|msaa|jab|ia2|cdp|css">
  <node
    role="string"
    name="string"
    automationid="string"
    cls="string"
    idx="number"
    value="string"
    state="string"
  />
  <!-- Additional nodes for nested path -->
</selector>
```

### Resolution Rules

1. **Exact match first** — try all attributes as specified
2. **Relaxed match** — if exact fails, drop `idx`, try again
3. **Fuzzy match** — if relaxed fails, use name similarity (Levenshtein distance < 3)
4. **Framework fallback** — if specified framework fails, try others in priority order

Priority order: CDP → UIA → MSAA → JAB → IA2 → Vision (matches Unified App Model design)

---

## Core Components

### 1. SelectorBuilder

**Purpose:** Automatically generate selectors when `see` inspects UI elements.

**Behavior:**
- `see` outputs both `eN` IDs (for quick use) and selectors (for stable reuse)
- Selectors are generated from element properties discovered during inspection
- Builder picks the most discriminating attributes to create unique selectors

**Output example:**
```
[Button] "Save"  e5  →  app://notepad.exe/Window[@name="*Notepad"]/Button[@name="Save"]
[Edit]   ""      e6  →  app://notepad.exe/Window[@name="*Notepad"]/Edit[@automationid="txtContent"]
```

**Algorithm:**
1. Walk the UI tree from root to target element
2. At each level, select attributes that uniquely identify the node among siblings
3. Prefer: `automationid` > `name` > `cls` + `idx`
4. Skip intermediate nodes that don't add discrimination value
5. Validate: resolve the generated selector and verify it finds the same element

**Interface:**
```python
class SelectorBuilder:
    def build(self, element: UIElement, context: AppContext) -> str:
        """Generate a URI selector for the given element."""

    def build_xml(self, element: UIElement, context: AppContext) -> str:
        """Generate an XML selector for the given element."""

    def validate(self, selector: str, expected_element: UIElement) -> bool:
        """Verify that a selector resolves to the expected element."""
```

### 2. SelectorResolver

**Purpose:** Accept a selector string and locate the matching UI element(s).

**Behavior:**
- Parses both URI and XML formats
- Walks the UI tree matching each node in the selector path
- Returns matched element(s) with coordinates and properties

**Interface:**
```python
class SelectorResolver:
    def resolve(self, selector: str, timeout: float = 5.0) -> UIElement:
        """Find a single element matching the selector."""

    def resolve_all(self, selector: str) -> list[UIElement]:
        """Find all elements matching the selector."""

    def exists(self, selector: str) -> bool:
        """Check if a matching element exists."""

    def wait_for(self, selector: str, timeout: float = 30.0) -> UIElement:
        """Wait until a matching element appears."""
```

**Integration points:**
- `click --selector "app://..."` — click by selector
- `type --selector "app://..." --text "hello"` — type into selector target
- `find --selector "app://..."` — find and return element info
- `wait --selector "app://..."` — wait for element to appear

### 3. SelectorCache

**Purpose:** Local storage for saving and reusing selectors.

**Storage:** `~/.naturo/selectors/`

**Structure:**
```
~/.naturo/selectors/
  notepad.json        # App-specific selectors
  chrome.json
  vscode.json
  _custom/            # User-saved selectors
    my-workflow.json
```

**Cache file format:**
```json
{
  "app": "notepad.exe",
  "version": "1.0",
  "selectors": {
    "save-button": {
      "selector": "app://notepad.exe/Window[@name=\"*Notepad\"]/Button[@name=\"Save\"]",
      "description": "Save button in main toolbar",
      "verified": "2026-03-20",
      "os_version": "Windows 11 22H2",
      "locale": "en-US"
    }
  }
}
```

**Interface:**
```python
class SelectorCache:
    def save(self, name: str, selector: str, app: str) -> None:
    def load(self, name: str, app: str) -> str | None:
    def list(self, app: str = None) -> list[dict]:
    def export(self, app: str, path: str) -> None:
    def import_file(self, path: str) -> int:  # returns count
```

### 4. SelectorTemplate

**Purpose:** Built-in selector templates for common Windows applications.

These are shipped with naturo and maintained by the project. They provide ready-to-use selectors for the most common automation targets.

**Top 20 applications:**

| # | Application | Process | Key Elements |
|---|-------------|---------|-------------|
| 1 | Notepad | notepad.exe | Menu, Edit area, Status bar |
| 2 | Chrome | chrome.exe | Address bar, Tabs, Page content (CDP) |
| 3 | Firefox | firefox.exe | Address bar, Tabs, Page content (IA2/CDP) |
| 4 | Edge | msedge.exe | Address bar, Tabs, Page content (CDP) |
| 5 | File Explorer | explorer.exe | Navigation pane, File list, Address bar |
| 6 | VS Code | code.exe | Explorer, Editor tabs, Terminal, Command palette |
| 7 | Word | winword.exe | Ribbon, Document area, Status bar |
| 8 | Excel | excel.exe | Ribbon, Cell grid, Formula bar, Sheet tabs |
| 9 | PowerPoint | powerpnt.exe | Ribbon, Slide panel, Notes area |
| 10 | Calculator | calc.exe / calculatorapp.exe | Number pad, Display, Mode buttons |
| 11 | Settings | systemsettings.exe | Navigation, Search, Setting controls |
| 12 | Task Manager | taskmgr.exe | Process list, Tabs, Performance graphs |
| 13 | Windows Terminal | windowsterminal.exe | Tab bar, Terminal pane |
| 14 | Outlook | outlook.exe / olk.exe | Mail list, Reading pane, Compose |
| 15 | Teams | ms-teams.exe | Chat list, Message input, Call controls |
| 16 | CMD | cmd.exe | Console output area |
| 17 | Paint | mspaint.exe | Canvas, Tool palette, Color picker |
| 18 | Snipping Tool | snippingtool.exe | Capture buttons, Mode selector |
| 19 | Control Panel | control.exe | Category links, Setting items |
| 20 | Registry Editor | regedit.exe | Tree view, Value list |

**Template format:**
```json
{
  "app": "notepad.exe",
  "display_name": "Notepad",
  "framework": "uia",
  "os_versions": ["Windows 10", "Windows 11"],
  "locales": ["en-US"],
  "elements": {
    "menu-file": "app://notepad.exe/Window[@name=\"*Notepad\"]/MenuBar/MenuItem[@name=\"File\"]",
    "edit-area": "app://notepad.exe/Window[@name=\"*Notepad\"]/Edit",
    "save-button": "app://notepad.exe/Window[@name=\"*Notepad\"]/MenuBar/MenuItem[@name=\"File\"]/MenuItem[@name=\"Save\"]",
    "status-bar": "app://notepad.exe/Window[@name=\"*Notepad\"]/StatusBar"
  }
}
```

---

## Implementation Roadmap

### v0.2.0 — Foundation (Current)

- **Element ref caching** (#29): Quick fix for `eN` → coordinates cache with TTL. Solves the immediate UX crisis (#23).
- **This design doc**: Unified Selector format specification. Establishes the target architecture.

The v0.2.0 caching is a **temporary bridge** — it makes `see → click` work today while we build the proper selector system.

### v0.3.0 — Selector Engine

- Implement `SelectorBuilder` and `SelectorResolver`
- `see` outputs selectors alongside `eN` IDs
- `click --selector`, `type --selector`, `find --selector` accept unified selectors
- Built-in selector templates for Top 20 Windows apps
- Selector validation (build → resolve round-trip check)

### v0.4.0 — User Selector Management

- `naturo selector save <name>` — save a selector from the last `see` output
- `naturo selector load <name>` — use a saved selector
- `naturo selector list [--app <app>]` — list saved selectors
- `naturo selector export <file>` — export for sharing
- `naturo selector import <file>` — import from file

### v1.0.0+ — Community Registry (Future)

A npm/pip-like service where users publish and share verified selectors.

---

## Community Selector Registry — Evaluation

### Vision

Users automate Notepad, Chrome, SAP, etc. Instead of everyone building selectors from scratch, a community registry lets people share verified, tested selectors:

```bash
naturo selector install notepad          # official template
naturo selector install @user/sap-gui    # community package
naturo selector publish my-custom-app    # share your own
```

### Advantages

- **Reduced duplication** — common apps get solved once
- **Quality through usage** — popular selectors get battle-tested
- **Faster onboarding** — new users get working automation immediately
- **Ecosystem growth** — community contributions accelerate coverage

### Challenges

1. **Environment variance** — Selectors depend on OS version, locale (en-US vs zh-CN), DPI, app version. A selector for Notepad on Windows 11 en-US may not work on Windows 10 zh-CN.
2. **Maintenance burden** — Apps update their UI. Who updates the selectors?
3. **Cold start** — Registry is useless without content; content requires users.
4. **Trust** — Malicious selectors could target wrong elements (security risk in enterprise).
5. **Versioning** — Need selector versions tied to app versions.

### Conclusion

**Not yet.** The registry is a v1.0.0+ goal, blocked on user base.

**Realistic progression:**
1. **v0.3.0**: Ship built-in templates for Top 20 apps (maintained by naturo team)
2. **v0.4.0**: Let users save/export/import selectors locally
3. **v0.5.0+**: Gauge demand — if users are sharing selector files manually, that's the signal
4. **v1.0.0**: If demand exists, build the registry

**First step:** Official, team-maintained selector library for common Windows applications. This proves the format works and builds the muscle for template creation.

---

## Migration Strategy

### Phase 1: Coexistence (v0.2.0)

`eN` refs continue working via coordinate cache. Selectors are designed but not yet implemented.

### Phase 2: Dual Output (v0.3.0)

`see` outputs both `eN` and selectors. Users can use either:
```bash
naturo click --id e5              # coordinate cache (fast, fragile)
naturo click --selector "app://notepad.exe/Button[@name='Save']"  # selector (slower, stable)
```

### Phase 3: Selector-First (v0.4.0+)

Selectors become the recommended approach. `eN` refs remain for quick interactive use. Documentation and tutorials lead with selectors.

---

## Open Questions

1. **Selector shorthand** — Should we support `Button:Save` as shorthand for `app://<current-app>/Button[@name="Save"]`? Reduces typing for interactive use.
2. **Framework hints** — Should selectors include framework hints (`framework="uia"`) or always auto-detect? Auto-detect is simpler but slower.
3. **Regex support** — Should `@name` support regex beyond `*` wildcards? Power vs complexity tradeoff.
4. **Cross-locale** — How to handle apps with localized UI? `@name="Save"` won't work on a Chinese system where it's `@name="保存"`. Possible solution: `@automationid` is locale-independent.

---

## References

- [#23 — see element IDs cannot be used with click](https://github.com/anthropic-ace/naturo/issues/23)
- [#29 — Element ref caching system](https://github.com/anthropic-ace/naturo/issues/29)
- [Unified App Model Design](UNIFIED_APP_MODEL.md)
- [UiPath Selectors Documentation](https://docs.uipath.com/studio/docs/about-selectors)
- [Playwright Locators](https://playwright.dev/docs/locators)
