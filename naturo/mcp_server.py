"""Naturo MCP Server — expose desktop automation as MCP tools.

Provides AI agents with structured access to Windows desktop automation:
capture, inspect, click, type, find elements, manage windows/apps.
"""
from __future__ import annotations

import functools
import json
import logging
import os
import sys
import base64
import traceback
from typing import Optional

from mcp.server.fastmcp import FastMCP

from naturo.backends.base import get_backend, Backend
from naturo.errors import NaturoError

logger = logging.getLogger(__name__)


def create_server(host: str = "localhost", port: int = 3100) -> FastMCP:
    """Create and configure the Naturo MCP server."""
    server = FastMCP(
        name="naturo",
        host=host,
        port=port,
        instructions=(
            "Naturo — Windows desktop automation engine. "
            "Use these tools to see, click, type, and automate Windows applications. "
            "Start with capture_screen or list_windows to understand the current state, "
            "then use find_element or see_ui_tree to locate UI elements, "
            "and interact with click, type_text, press_key, etc."
        ),
    )

    def _get_backend() -> Backend:
        """Get the platform backend, raising clear errors."""
        try:
            return get_backend()
        except RuntimeError as e:
            raise NaturoError(str(e))

    def _safe_tool(fn):
        """Decorator: wraps MCP tool handlers with try/except to return structured errors."""
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except NaturoError as e:
                error_info: dict = {"code": e.code, "message": str(e)}
                if e.suggested_action:
                    error_info["suggested_action"] = e.suggested_action
                if e.is_recoverable:
                    error_info["recoverable"] = True
                return {"success": False, "error": error_info}
            except Exception as e:
                logger.exception("Unhandled error in tool %s", fn.__name__)
                return {"success": False, "error": {"code": "INTERNAL_ERROR", "message": f"{type(e).__name__}: {e}"}}
        return wrapper

    # ── Capture ─────────────────────────────────

    @server.tool()
    @_safe_tool
    def capture_screen(
        output_path: str = "capture.png",
        screen_index: int = 0,
    ) -> dict:
        """Capture a screenshot of the entire screen.

        Args:
            output_path: Path to save the screenshot (PNG/JPG).
            screen_index: Monitor index (0 = primary).

        Returns:
            Dict with path, width, height, format, and base64-encoded image data.
        """
        backend = _get_backend()
        result = backend.capture_screen(screen_index=screen_index, output_path=output_path)
        response = {
            "success": True,
            "path": result.path,
            "width": result.width,
            "height": result.height,
            "format": result.format,
            "scale_factor": result.scale_factor,
            "dpi": result.dpi,
        }
        # Include base64 data for AI vision
        if os.path.exists(result.path):
            with open(result.path, "rb") as f:
                response["data_base64"] = base64.b64encode(f.read()).decode("ascii")
        return response

    @server.tool()
    @_safe_tool
    def capture_window(
        window_title: Optional[str] = None,
        output_path: str = "capture.png",
    ) -> dict:
        """Capture a screenshot of a specific window.

        Args:
            window_title: Window title to capture (partial match).
            output_path: Path to save the screenshot.

        Returns:
            Dict with path, width, height, format, scale_factor, dpi.
        """
        backend = _get_backend()
        result = backend.capture_window(window_title=window_title, output_path=output_path)
        response = {
            "success": True,
            "path": result.path,
            "width": result.width,
            "height": result.height,
            "format": result.format,
            "scale_factor": result.scale_factor,
            "dpi": result.dpi,
        }
        if os.path.exists(result.path):
            with open(result.path, "rb") as f:
                response["data_base64"] = base64.b64encode(f.read()).decode("ascii")
        return response

    # ── Monitor Enumeration ──────────────────────

    @server.tool()
    @_safe_tool
    def list_monitors() -> dict:
        """List all connected monitors/displays.

        Returns monitor index, name, resolution, position in virtual screen
        coordinates, DPI, scale factor, primary flag, and work area.

        Returns:
            Dict with success flag and list of monitors.
        """
        backend = _get_backend()
        monitors = backend.list_monitors()
        return {
            "success": True,
            "monitors": [
                {
                    "index": m.index,
                    "name": m.name,
                    "x": m.x, "y": m.y,
                    "width": m.width, "height": m.height,
                    "is_primary": m.is_primary,
                    "scale_factor": m.scale_factor,
                    "dpi": m.dpi,
                    "work_area": m.work_area,
                }
                for m in monitors
            ],
        }

    # ── Window Management ───────────────────────

    @server.tool()
    @_safe_tool
    def list_windows() -> dict:
        """List all visible windows on the desktop.

        Returns:
            Dict with success flag and list of windows (title, process, pid, bounds).
        """
        backend = _get_backend()
        windows = backend.list_windows()
        return {
            "success": True,
            "windows": [
                {
                    "handle": w.handle,
                    "title": w.title,
                    "process_name": w.process_name,
                    "pid": w.pid,
                    "x": w.x, "y": w.y,
                    "width": w.width, "height": w.height,
                    "is_visible": w.is_visible,
                    "is_minimized": w.is_minimized,
                }
                for w in windows
            ],
        }

    @server.tool()
    @_safe_tool
    def focus_window(
        title: Optional[str] = None,
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Bring a window to the foreground and give it focus.

        Args:
            title: Window title (partial match).
            app: Application/process name (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.focus_window(title=app or title, hwnd=hwnd)
        return {"success": True, "action": "focus"}

    @server.tool()
    @_safe_tool
    def window_close(
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
        force: bool = False,
    ) -> dict:
        """Close a window (graceful or forced).

        Args:
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.
            force: If True, forcefully terminate the owning process.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.close_window(title=app or title, hwnd=hwnd, force=force)
        return {"success": True, "action": "close"}

    @server.tool()
    @_safe_tool
    def window_minimize(
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Minimize a window.

        Args:
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.minimize_window(title=app or title, hwnd=hwnd)
        return {"success": True, "action": "minimize"}

    @server.tool()
    @_safe_tool
    def window_maximize(
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Maximize a window.

        Args:
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.maximize_window(title=app or title, hwnd=hwnd)
        return {"success": True, "action": "maximize"}

    @server.tool()
    @_safe_tool
    def window_restore(
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Restore a minimized or maximized window to normal state.

        Args:
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.restore_window(title=app or title, hwnd=hwnd)
        return {"success": True, "action": "restore"}

    @server.tool()
    @_safe_tool
    def window_move(
        x: int,
        y: int,
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Move a window to a position (keeps current size).

        Args:
            x: Target X coordinate.
            y: Target Y coordinate.
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.move_window(x=x, y=y, title=app or title, hwnd=hwnd)
        return {"success": True, "action": "move", "x": x, "y": y}

    @server.tool()
    @_safe_tool
    def window_resize(
        width: int,
        height: int,
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Resize a window (keeps current position).

        Args:
            width: Target width in pixels (must be >= 1).
            height: Target height in pixels (must be >= 1).
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        if width < 1 or height < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"width and height must be >= 1, got {width}x{height}"}}
        backend = _get_backend()
        backend.resize_window(width=width, height=height, title=app or title, hwnd=hwnd)
        return {"success": True, "action": "resize", "width": width, "height": height}

    @server.tool()
    @_safe_tool
    def window_set_bounds(
        x: int,
        y: int,
        width: int,
        height: int,
        app: Optional[str] = None,
        title: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Set window position and size in one call.

        Args:
            x: Target X coordinate.
            y: Target Y coordinate.
            width: Target width in pixels (must be >= 1).
            height: Target height in pixels (must be >= 1).
            app: Application/process name (partial match).
            title: Window title (partial match).
            hwnd: Direct window handle.

        Returns:
            Dict with success flag.
        """
        if width < 1 or height < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"width and height must be >= 1, got {width}x{height}"}}
        backend = _get_backend()
        backend.set_bounds(x=x, y=y, width=width, height=height, title=app or title, hwnd=hwnd)
        return {"success": True, "action": "set-bounds", "x": x, "y": y, "width": width, "height": height}

    @server.tool()
    @_safe_tool
    def app_hide(name: str) -> dict:
        """Hide (minimize) all windows of an application.

        Args:
            name: Application/process name (partial match).

        Returns:
            Dict with success flag and count of minimized windows.
        """
        backend = _get_backend()
        windows = backend.list_windows()
        name_lower = name.lower()
        matched = [w for w in windows if name_lower in w.process_name.lower() or name_lower in w.title.lower()]
        if not matched:
            from naturo.errors import AppNotFoundError
            raise AppNotFoundError(name)
        count = 0
        for w in matched:
            try:
                backend.minimize_window(hwnd=w.handle)
                count += 1
            except Exception:
                pass
        return {"success": True, "action": "hide", "app": name, "windows_minimized": count}

    @server.tool()
    @_safe_tool
    def app_unhide(name: str) -> dict:
        """Unhide (restore) all windows of an application.

        Args:
            name: Application/process name (partial match).

        Returns:
            Dict with success flag and count of restored windows.
        """
        backend = _get_backend()
        windows = backend.list_windows()
        name_lower = name.lower()
        matched = [w for w in windows if name_lower in w.process_name.lower() or name_lower in w.title.lower()]
        if not matched:
            from naturo.errors import AppNotFoundError
            raise AppNotFoundError(name)
        count = 0
        for w in matched:
            try:
                backend.restore_window(hwnd=w.handle)
                count += 1
            except Exception:
                pass
        return {"success": True, "action": "unhide", "app": name, "windows_restored": count}

    @server.tool()
    @_safe_tool
    def app_switch(name: str) -> dict:
        """Switch to (focus) the most recent window of an application.

        Args:
            name: Application/process name (partial match).

        Returns:
            Dict with success flag, window title and handle.
        """
        backend = _get_backend()
        windows = backend.list_windows()
        name_lower = name.lower()
        matched = [w for w in windows if name_lower in w.process_name.lower() or name_lower in w.title.lower()]
        if not matched:
            from naturo.errors import AppNotFoundError
            raise AppNotFoundError(name)
        target = matched[0]
        backend.focus_window(hwnd=target.handle)
        return {"success": True, "action": "switch", "app": name, "window_title": target.title, "handle": target.handle}

    # ── UI Inspection ───────────────────────────

    @server.tool()
    @_safe_tool
    def see_ui_tree(
        window_title: Optional[str] = None,
        depth: int = 3,
        accessibility_backend: str = "uia",
    ) -> dict:
        """Inspect the UI accessibility tree of a window.

        Returns the hierarchical tree of UI elements (buttons, text fields, etc.)
        with their roles, names, bounds, and properties.

        Args:
            window_title: Target window (partial match). None = foreground window.
            depth: How deep to traverse the tree (1-10).
            accessibility_backend: "uia" (default), "msaa" (for legacy apps like
                MFC, VB6, Delphi), "ia2" (for Firefox, Thunderbird, LibreOffice),
                "jab" (for Java/Swing/AWT), or "auto" (try UIA → IA2 → JAB → MSAA).

        Returns:
            Dict with the element tree structure.
        """
        if depth < 1 or depth > 10:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"depth must be between 1 and 10, got {depth}"}}
        if accessibility_backend not in ("uia", "msaa", "ia2", "jab", "auto"):
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"accessibility_backend must be uia, msaa, ia2, jab, or auto, got {accessibility_backend}"}}
        backend = _get_backend()
        tree = backend.get_element_tree(window_title=window_title, depth=depth,
                                        backend=accessibility_backend)
        if tree is None:
            return {"success": False, "error": {"code": "NO_WINDOW", "message": "No matching window found"}}

        def _serialize(el) -> dict:
            d = {
                "id": el.id,
                "role": el.role,
                "name": el.name,
                "value": el.value,
                "bounds": {"x": el.x, "y": el.y, "width": el.width, "height": el.height},
                "properties": el.properties,
            }
            if el.children:
                d["children"] = [_serialize(c) for c in el.children]
            return d

        return {"success": True, "tree": _serialize(tree)}

    @server.tool()
    @_safe_tool
    def find_element(
        selector: str,
        window_title: Optional[str] = None,
    ) -> dict:
        """Find a UI element by selector.

        Selector format: "Role:Name" (e.g. "Button:Save", "Edit:*search*").
        Supports fuzzy matching with wildcards.

        Args:
            selector: Element selector string.
            window_title: Target window (partial match).

        Returns:
            Dict with the found element's info or error.
        """
        backend = _get_backend()
        element = backend.find_element(selector=selector, window_title=window_title)
        if element is None:
            return {"success": False, "error": {"code": "ELEMENT_NOT_FOUND", "message": f"No element matching '{selector}'"}}
        return {
            "success": True,
            "element": {
                "id": element.id,
                "role": element.role,
                "name": element.name,
                "value": element.value,
                "bounds": {"x": element.x, "y": element.y, "width": element.width, "height": element.height},
                "properties": element.properties,
            },
        }

    # ── Input Actions ───────────────────────────

    @server.tool()
    @_safe_tool
    def click(
        x: Optional[int] = None,
        y: Optional[int] = None,
        element_id: Optional[str] = None,
        button: str = "left",
        double: bool = False,
        input_mode: str = "normal",
    ) -> dict:
        """Click at coordinates or on a UI element.

        Provide either (x, y) coordinates or an element_id from find_element/see_ui_tree.

        Args:
            x: X coordinate.
            y: Y coordinate.
            element_id: Element ID to click (from find_element).
            button: Mouse button — "left", "right", or "middle".
            double: Double-click if True.
            input_mode: Input method — "normal" (default) or "hardware" (Phys32, bypasses anti-cheat).

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.click(x=x, y=y, element_id=element_id, button=button, double=double,
                      input_mode=input_mode)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def type_text(
        text: str,
        wpm: int = 120,
        input_mode: str = "normal",
    ) -> dict:
        """Type text using keyboard input.

        Types the given text character by character, simulating human typing.

        Args:
            text: Text to type.
            wpm: Words per minute (typing speed).
            input_mode: Input method — "normal" (default) or "hardware" (Phys32 scan codes, bypasses anti-cheat).

        Returns:
            Dict with success flag.
        """
        if wpm < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"wpm must be >= 1, got {wpm}"}}
        backend = _get_backend()
        backend.type_text(text=text, wpm=wpm, input_mode=input_mode)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def press_key(key: str, count: int = 1, input_mode: str = "normal") -> dict:
        """Press a keyboard key.

        Args:
            key: Key name (e.g. "enter", "tab", "escape", "f1", "a").
            count: Number of times to press.
            input_mode: Input method — "normal" (default) or "hardware" (Phys32 scan codes).

        Returns:
            Dict with success flag.
        """
        if count < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"count must be >= 1, got {count}"}}
        backend = _get_backend()
        for _ in range(count):
            backend.press_key(key=key, input_mode=input_mode)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def hotkey(keys: list[str], input_mode: str = "normal") -> dict:
        """Press a keyboard shortcut (key combination).

        Args:
            keys: List of keys to press simultaneously (e.g. ["ctrl", "s"] for Ctrl+S).
            input_mode: Input method — "normal" (default) or "hardware" (Phys32 scan codes).

        Returns:
            Dict with success flag.
        """
        if not keys:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": "keys list must not be empty"}}
        backend = _get_backend()
        backend.hotkey(*keys, input_mode=input_mode)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def scroll(
        direction: str = "down",
        amount: int = 3,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> dict:
        """Scroll the mouse wheel.

        Args:
            direction: "up" or "down".
            amount: Number of scroll units.
            x: X coordinate to scroll at (optional).
            y: Y coordinate to scroll at (optional).

        Returns:
            Dict with success flag.
        """
        if amount < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"amount must be >= 1, got {amount}"}}
        backend = _get_backend()
        backend.scroll(direction=direction, amount=amount, x=x, y=y)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def drag(
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        duration_ms: int = 500,
        steps: int = 10,
    ) -> dict:
        """Drag from one point to another.

        Args:
            from_x: Start X coordinate.
            from_y: Start Y coordinate.
            to_x: End X coordinate.
            to_y: End Y coordinate.
            duration_ms: Duration in milliseconds.
            steps: Number of intermediate steps.

        Returns:
            Dict with success flag.
        """
        if steps < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"steps must be >= 1, got {steps}"}}
        if duration_ms < 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"duration_ms must be >= 0, got {duration_ms}"}}
        backend = _get_backend()
        backend.drag(from_x=from_x, from_y=from_y, to_x=to_x, to_y=to_y,
                     duration_ms=duration_ms, steps=steps)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def move_mouse(x: int, y: int) -> dict:
        """Move the mouse cursor to a position.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.move_mouse(x=x, y=y)
        return {"success": True}

    # ── Clipboard ───────────────────────────────

    @server.tool()
    @_safe_tool
    def clipboard_get() -> dict:
        """Get the current clipboard text content.

        Returns:
            Dict with success flag and clipboard text.
        """
        backend = _get_backend()
        text = backend.clipboard_get()
        return {"success": True, "text": text}

    @server.tool()
    @_safe_tool
    def clipboard_set(text: str) -> dict:
        """Set the clipboard text content.

        Args:
            text: Text to copy to clipboard.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.clipboard_set(text=text)
        return {"success": True}

    # ── Application Control ─────────────────────

    @server.tool()
    @_safe_tool
    def list_apps() -> dict:
        """List running applications.

        Returns:
            Dict with success flag and list of running applications.
        """
        backend = _get_backend()
        apps = backend.list_apps()
        return {"success": True, "apps": apps}

    @server.tool()
    @_safe_tool
    def launch_app(name: str) -> dict:
        """Launch an application by name.

        Args:
            name: Application name or executable path.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.launch_app(name=name)
        return {"success": True}

    @server.tool()
    @_safe_tool
    def quit_app(name: str, force: bool = False) -> dict:
        """Quit an application.

        Args:
            name: Application name.
            force: Force quit if True.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.quit_app(name=name, force=force)
        return {"success": True}

    # ── Menu ────────────────────────────────────

    @server.tool()
    @_safe_tool
    def menu_inspect(app: Optional[str] = None) -> dict:
        """Inspect the menu bar of an application.

        Returns the hierarchical menu structure with item names, shortcuts, and states.

        Args:
            app: Application name (optional, defaults to foreground app).

        Returns:
            Dict with success flag and menu items.
        """
        backend = _get_backend()
        items = backend.get_menu_items(window_title=app)

        def _serialize_menu(item) -> dict:
            d = {"name": item.name}
            if item.shortcut:
                d["shortcut"] = item.shortcut
            if hasattr(item, "enabled"):
                d["enabled"] = item.enabled
            if hasattr(item, "checked"):
                d["checked"] = item.checked
            if hasattr(item, "children") and item.children:
                d["children"] = [_serialize_menu(c) for c in item.children]
            return d

        return {
            "success": True,
            "menu_items": [_serialize_menu(m) for m in items],
        }

    # ── Wait ────────────────────────────────────

    @server.tool()
    @_safe_tool
    def wait_for_element(
        selector: str,
        timeout: float = 10.0,
        interval: float = 0.5,
        window_title: Optional[str] = None,
    ) -> dict:
        """Wait for a UI element to appear.

        Polls the UI tree until the element matching the selector is found or timeout.
        Essential for automation flows that need to wait for UI state changes.

        Args:
            selector: Element selector (e.g. "Button:Save", "Dialog:*").
            timeout: Maximum wait time in seconds (default 10).
            interval: Poll interval in seconds (default 0.5).
            window_title: Target window (partial match, optional).

        Returns:
            Dict with success, found element info, and wait_time.
        """
        if timeout < 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"timeout must be >= 0, got {timeout}"}}
        if interval <= 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"interval must be > 0, got {interval}"}}

        from naturo.wait import wait_for_element as _wait_element
        backend = _get_backend()
        result = _wait_element(
            selector=selector,
            timeout=timeout,
            poll_interval=interval,
            window_title=window_title,
            backend=backend,
        )
        if result.found and result.element:
            return {
                "success": True,
                "found": True,
                "wait_time": round(result.wait_time, 3),
                "element": {
                    "id": result.element.id,
                    "role": result.element.role,
                    "name": result.element.name,
                    "bounds": {
                        "x": result.element.x, "y": result.element.y,
                        "width": result.element.width, "height": result.element.height,
                    },
                },
            }
        return {
            "success": False,
            "found": False,
            "wait_time": round(result.wait_time, 3),
            "error": {"code": "TIMEOUT", "message": f"Element '{selector}' not found within {timeout}s"},
        }

    @server.tool()
    @_safe_tool
    def wait_for_window(
        title: str,
        timeout: float = 10.0,
        interval: float = 0.5,
    ) -> dict:
        """Wait for a window to appear.

        Polls until a window matching the title is found or timeout.

        Args:
            title: Window title to wait for (partial match).
            timeout: Maximum wait time in seconds (default 10).
            interval: Poll interval in seconds (default 0.5).

        Returns:
            Dict with success flag and wait_time.
        """
        if timeout < 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"timeout must be >= 0, got {timeout}"}}
        if interval <= 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"interval must be > 0, got {interval}"}}

        from naturo.wait import wait_for_window as _wait_window
        backend = _get_backend()
        result = _wait_window(
            title=title,
            timeout=timeout,
            poll_interval=interval,
            backend=backend,
        )
        if result.found:
            return {
                "success": True,
                "found": True,
                "wait_time": round(result.wait_time, 3),
            }
        return {
            "success": False,
            "found": False,
            "wait_time": round(result.wait_time, 3),
            "error": {"code": "TIMEOUT", "message": f"Window '{title}' not found within {timeout}s"},
        }

    @server.tool()
    @_safe_tool
    def wait_until_gone(
        selector: str,
        timeout: float = 10.0,
        interval: float = 0.5,
        window_title: Optional[str] = None,
    ) -> dict:
        """Wait for a UI element to disappear.

        Polls until the element matching the selector is no longer found, or timeout.
        Useful for waiting for loading dialogs or progress bars to vanish.

        Args:
            selector: Element selector to wait for disappearance.
            timeout: Maximum wait time in seconds (default 10).
            interval: Poll interval in seconds (default 0.5).
            window_title: Target window (partial match, optional).

        Returns:
            Dict with success flag and wait_time.
        """
        if timeout < 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"timeout must be >= 0, got {timeout}"}}
        if interval <= 0:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"interval must be > 0, got {interval}"}}

        from naturo.wait import wait_until_gone as _wait_gone
        backend = _get_backend()
        result = _wait_gone(
            selector=selector,
            timeout=timeout,
            poll_interval=interval,
            window_title=window_title,
            backend=backend,
        )
        if result.found:
            return {
                "success": True,
                "gone": True,
                "wait_time": round(result.wait_time, 3),
            }
        return {
            "success": False,
            "gone": False,
            "wait_time": round(result.wait_time, 3),
            "error": {"code": "TIMEOUT", "message": f"Element '{selector}' still present after {timeout}s"},
        }

    # ── Open ────────────────────────────────────

    @server.tool()
    @_safe_tool
    def open_uri(uri: str) -> dict:
        """Open a URL or file with the default application.

        Args:
            uri: URL (https://...) or file path to open.

        Returns:
            Dict with success flag.
        """
        backend = _get_backend()
        backend.open_uri(uri=uri)
        return {"success": True}

    # ── Snapshot ────────────────────────────────

    @server.tool()
    @_safe_tool
    def create_snapshot(
        window_title: Optional[str] = None,
        depth: int = 3,
    ) -> dict:
        """Create a snapshot of the current UI state (screenshot + element tree).

        Captures a screenshot and the UI accessibility tree, storing them together
        for later reference. Essential for AI workflows that need to track UI state
        changes over time.

        Args:
            window_title: Target window (partial match). None = foreground window.
            depth: How deep to traverse the UI tree (1-10, default 3).

        Returns:
            Dict with snapshot_id, screenshot_path (base64), and element tree summary.
        """
        if depth < 1 or depth > 10:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"depth must be between 1 and 10, got {depth}"}}

        from naturo.snapshot import SnapshotManager
        backend = _get_backend()
        manager = SnapshotManager()

        # Create snapshot and capture
        snapshot_id = manager.create_snapshot()

        # Capture screenshot
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name
        try:
            result = backend.capture_window(window_title=window_title, output_path=temp_path)
            manager.store_screenshot(snapshot_id, temp_path, metadata={
                "window_title": window_title or "foreground",
            })
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        # Capture UI tree
        tree = backend.get_element_tree(window_title=window_title, depth=depth)
        if tree:
            def _convert_elements(el, parent_id=None):
                from naturo.models.snapshot import UIElement
                elem = UIElement(
                    element_id=el.id,
                    role=el.role,
                    name=el.name,
                    value=el.value or "",
                    bounds=(el.x, el.y, el.width, el.height),
                    parent_id=parent_id,
                    children=[_convert_elements(c, el.id) for c in (el.children or [])],
                )
                return elem
            root_elem = _convert_elements(tree)
            manager.store_ui_tree(snapshot_id, root_elem)

        # Load the full snapshot
        snapshot = manager.get_snapshot(snapshot_id)

        response = {
            "success": True,
            "snapshot_id": snapshot_id,
            "screenshot_path": snapshot.screenshot_path,
            "element_count": sum(1 for _ in _iter_elements(tree)) if tree else 0,
        }

        # Include base64 if screenshot exists
        if snapshot.screenshot_path and os.path.exists(snapshot.screenshot_path):
            with open(snapshot.screenshot_path, "rb") as f:
                response["screenshot_base64"] = base64.b64encode(f.read()).decode("ascii")

        return response

    @server.tool()
    @_safe_tool
    def get_snapshot(snapshot_id: str) -> dict:
        """Retrieve a previously created snapshot.

        Args:
            snapshot_id: The snapshot ID returned by create_snapshot.

        Returns:
            Dict with snapshot details including UI tree and screenshot path.
        """
        from naturo.snapshot import SnapshotManager
        from naturo.models.snapshot import SnapshotNotFoundError

        manager = SnapshotManager()
        try:
            snapshot = manager.get_snapshot(snapshot_id)
        except SnapshotNotFoundError:
            return {"success": False, "error": {"code": "SNAPSHOT_NOT_FOUND", "message": f"Snapshot '{snapshot_id}' not found"}}

        response = {
            "success": True,
            "snapshot_id": snapshot.snapshot_id,
            "created_at": snapshot.created_at,
            "screenshot_path": snapshot.screenshot_path,
            "window_title": snapshot.window_title,
            "application_name": snapshot.application_name,
        }

        # Include element tree summary
        if snapshot.ui_tree:
            def _serialize(el) -> dict:
                d = {
                    "id": el.element_id,
                    "role": el.role,
                    "name": el.name,
                    "bounds": el.bounds,
                }
                if el.children:
                    d["children"] = [_serialize(c) for c in el.children]
                return d
            response["ui_tree"] = _serialize(snapshot.ui_tree)

        return response

    @server.tool()
    @_safe_tool
    def list_snapshots(limit: int = 10) -> dict:
        """List recent snapshots.

        Args:
            limit: Maximum number of snapshots to return (default 10).

        Returns:
            Dict with list of snapshot summaries.
        """
        if limit < 1:
            return {"success": False, "error": {"code": "INVALID_INPUT", "message": f"limit must be >= 1, got {limit}"}}

        from naturo.snapshot import SnapshotManager
        manager = SnapshotManager()
        snapshots = manager.list_snapshots(limit=limit)

        return {
            "success": True,
            "snapshots": [
                {
                    "snapshot_id": s.snapshot_id,
                    "created_at": s.created_at,
                    "window_title": s.window_title,
                    "application_name": s.application_name,
                    "is_valid": s.is_valid,
                }
                for s in snapshots
            ],
        }

    # ── AI Vision ────────────────────────────────

    @server.tool()
    @_safe_tool
    def describe_screen(
        window_title: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        prompt: Optional[str] = None,
        provider_name: str = "auto",
        max_tokens: int = 1024,
    ) -> dict:
        """Describe the current screen or a window using AI vision.

        Captures a screenshot and sends it to an AI model for analysis.
        Returns a natural language description of what's visible on screen.

        Args:
            window_title: Capture a specific window (optional).
            screenshot_path: Use an existing screenshot instead of capturing (optional).
            prompt: Custom analysis prompt (optional).
            provider_name: AI provider — 'auto', 'anthropic', 'openai', or 'ollama'.
            max_tokens: Maximum tokens in the AI response.

        Returns:
            Dict with success, description, model, tokens_used, and optional elements.
        """
        from naturo.vision import describe_screen as _describe_screen

        backend = _get_backend() if not screenshot_path else None
        result = _describe_screen(
            provider_name=provider_name,
            backend=backend,
            window_title=window_title,
            screenshot_path=screenshot_path,
            prompt=prompt,
            max_tokens=max_tokens,
        )

        response = {
            "success": True,
            "description": result.description,
            "model": result.model,
            "tokens_used": result.tokens_used,
        }
        if result.elements:
            response["elements"] = result.elements
        return response

    @server.tool()
    @_safe_tool
    def identify_element(
        element_description: str,
        window_title: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        provider_name: str = "auto",
        max_tokens: int = 512,
    ) -> dict:
        """Find a UI element by natural language description using AI vision.

        Captures a screenshot and asks the AI to locate the described element.
        Returns element bounds (approximate) and confidence.

        Args:
            element_description: What to find (e.g., "the Save button", "the search field").
            window_title: Capture a specific window (optional).
            screenshot_path: Use an existing screenshot (optional).
            provider_name: AI provider — 'auto', 'anthropic', 'openai', or 'ollama'.
            max_tokens: Maximum tokens in the AI response.

        Returns:
            Dict with success, description, elements (with bounds + confidence).
        """
        from naturo.vision import identify_element as _identify_element

        backend = _get_backend() if not screenshot_path else None
        result = _identify_element(
            element_description,
            provider_name=provider_name,
            backend=backend,
            window_title=window_title,
            screenshot_path=screenshot_path,
            max_tokens=max_tokens,
        )

        response = {
            "success": True,
            "description": result.description,
            "elements": result.elements,
            "model": result.model,
            "tokens_used": result.tokens_used,
        }
        return response

    @server.tool()
    @_safe_tool
    def ai_find_element(
        query: str,
        window_title: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        provider_name: str = "auto",
        refine_with_uia: bool = True,
        max_tokens: int = 512,
    ) -> dict:
        """Find a UI element using natural language and AI vision.

        Takes a screenshot and uses AI to locate the described element.
        Optionally refines against the UIA tree for precise element info.

        This is more powerful than find_element for natural language queries
        like "the submit button" or "the search bar at the top".

        Args:
            query: Natural language description (e.g., "the Save button").
            window_title: Target a specific window (optional).
            screenshot_path: Use an existing screenshot (optional).
            provider_name: AI provider — 'auto', 'anthropic', 'openai', or 'ollama'.
            refine_with_uia: Match AI result against UIA tree for precision.
            max_tokens: Maximum tokens in the AI response.

        Returns:
            Dict with found status, element info, confidence, and method.
        """
        from naturo.ai_find import ai_find_element as _ai_find

        result = _ai_find(
            query,
            provider_name=provider_name,
            window_title=window_title,
            screenshot_path=screenshot_path,
            refine_with_uia=refine_with_uia,
            max_tokens=max_tokens,
        )

        response: dict = {
            "success": result.found,
            "description": result.description,
            "confidence": result.confidence,
            "method": result.method,
            "model": result.model,
            "tokens_used": result.tokens_used,
        }
        if result.ai_bounds:
            response["ai_bounds"] = result.ai_bounds
        if result.element:
            response["element"] = result.element
        if not result.found:
            response["error"] = {
                "code": "ELEMENT_NOT_FOUND",
                "message": f"AI could not locate: {query}",
            }
        return response

    # ── Phase 4.5: Dialog Detection & Interaction ──────────────────────────

    @server.tool()
    @_safe_tool
    def dialog_detect(
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Detect active dialog windows (message boxes, file pickers, etc.).

        Scans for system dialogs and returns their type, title, message text,
        available buttons, and whether an input field is present. Essential for
        handling dialogs that block automation workflows.

        Args:
            app: Filter by owner application name (partial match).
            hwnd: Filter by specific dialog window handle.

        Returns:
            Dict with success, dialogs list, and count.
        """
        dialogs = backend.detect_dialogs(app=app, hwnd=hwnd)
        return {
            "success": True,
            "dialogs": [d.to_dict() for d in dialogs],
            "count": len(dialogs),
        }

    @server.tool()
    @_safe_tool
    def dialog_accept(
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Accept (confirm) the active dialog by clicking OK/Yes/Open/Save.

        Finds the first accept-type button and clicks it. Use when a dialog
        is blocking the workflow and you want to proceed.

        Args:
            app: Filter by owner application name.
            hwnd: Filter by specific dialog window handle.

        Returns:
            Dict with dialog title and button clicked.
        """
        from naturo.dialog import _ACCEPT_BUTTONS

        dialogs = backend.detect_dialogs(app=app, hwnd=hwnd)
        if not dialogs:
            return {
                "success": False,
                "error": {"code": "DIALOG_NOT_FOUND", "message": "No dialog detected"},
            }

        target = dialogs[0]
        if hwnd:
            target = next((d for d in dialogs if d.hwnd == hwnd), dialogs[0])

        for btn in target.buttons:
            if btn.name.lower() in _ACCEPT_BUTTONS or btn.is_default:
                backend.click(x=btn.x, y=btn.y)
                return {
                    "success": True,
                    "dialog_title": target.title,
                    "button_clicked": btn.name,
                    "dialog_hwnd": target.hwnd,
                }

        available = ", ".join(b.name for b in target.buttons)
        return {
            "success": False,
            "error": {
                "code": "ELEMENT_NOT_FOUND",
                "message": f"No accept button found. Available: [{available}]",
            },
        }

    @server.tool()
    @_safe_tool
    def dialog_dismiss(
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Dismiss (cancel) the active dialog by clicking Cancel/No/Close.

        Finds the first dismiss-type button and clicks it. Use when you want
        to cancel a dialog without proceeding.

        Args:
            app: Filter by owner application name.
            hwnd: Filter by specific dialog window handle.

        Returns:
            Dict with dialog title and button clicked.
        """
        from naturo.dialog import _DISMISS_BUTTONS

        dialogs = backend.detect_dialogs(app=app, hwnd=hwnd)
        if not dialogs:
            return {
                "success": False,
                "error": {"code": "DIALOG_NOT_FOUND", "message": "No dialog detected"},
            }

        target = dialogs[0]
        if hwnd:
            target = next((d for d in dialogs if d.hwnd == hwnd), dialogs[0])

        for btn in target.buttons:
            if btn.name.lower() in _DISMISS_BUTTONS or btn.is_cancel:
                backend.click(x=btn.x, y=btn.y)
                return {
                    "success": True,
                    "dialog_title": target.title,
                    "button_clicked": btn.name,
                    "dialog_hwnd": target.hwnd,
                }

        available = ", ".join(b.name for b in target.buttons)
        return {
            "success": False,
            "error": {
                "code": "ELEMENT_NOT_FOUND",
                "message": f"No dismiss button found. Available: [{available}]",
            },
        }

    @server.tool()
    @_safe_tool
    def dialog_click_button(
        button: str,
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Click a specific button in the active dialog by name.

        Supports exact and partial name matching (case-insensitive).
        Use 'dialog_detect' first to see available buttons.

        Args:
            button: Button text to click (e.g., "Save", "Don't Save", "Retry").
            app: Filter by owner application name.
            hwnd: Filter by specific dialog window handle.

        Returns:
            Dict with dialog title and button clicked.
        """
        result = backend.dialog_click_button(button=button, app=app, hwnd=hwnd)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def dialog_type(
        text: str,
        accept: bool = False,
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Type text into a dialog's input field.

        Finds the dialog's input/edit control, clears it, and types the text.
        With accept=True, also clicks the OK/Save button afterward.

        Args:
            text: Text to type in the input field.
            accept: Click the accept button after typing.
            app: Filter by owner application name.
            hwnd: Filter by specific dialog window handle.

        Returns:
            Dict with dialog title, text entered, and optional accept button.
        """
        result = backend.dialog_set_input(text=text, app=app, hwnd=hwnd)
        response = {"success": True, **result}

        if accept:
            from naturo.dialog import _ACCEPT_BUTTONS
            dialogs = backend.detect_dialogs(app=app, hwnd=hwnd)
            if dialogs:
                for btn in dialogs[0].buttons:
                    if btn.name.lower() in _ACCEPT_BUTTONS or btn.is_default:
                        backend.click(x=btn.x, y=btn.y)
                        response["accepted_with"] = btn.name
                        break

        return response

    # ── Taskbar (Phase 4.5.4) ─────────────────────────

    @server.tool()
    @_safe_tool
    def taskbar_list() -> dict:
        """List items on the Windows taskbar.

        Returns running applications and pinned shortcuts visible on the
        taskbar. Use this to discover what apps are available before clicking.

        Returns:
            Dict with success, items list (name, hwnd, is_active, is_pinned),
            and count.
        """
        items = backend.taskbar_list()
        return {"success": True, "items": items, "count": len(items)}

    @server.tool()
    @_safe_tool
    def taskbar_click(name: str) -> dict:
        """Click a taskbar item to activate its window.

        Finds a taskbar button matching the name (case-insensitive partial
        match) and clicks it to bring the application to the foreground.

        Args:
            name: Application name or window title (partial match).

        Returns:
            Dict with success, name of clicked item, and click coordinates.
        """
        result = backend.taskbar_click(name=name)
        return {"success": True, **result}

    # ── System Tray (Phase 4.5.5) ─────────────────────

    @server.tool()
    @_safe_tool
    def tray_list() -> dict:
        """List system tray (notification area) icons.

        Returns icons in the Windows notification area including both visible
        icons and those in the overflow panel. Use this to discover available
        tray icons before interacting with them.

        Returns:
            Dict with success, icons list (name, tooltip, is_visible), and count.
        """
        icons = backend.tray_list()
        return {"success": True, "icons": icons, "count": len(icons)}

    @server.tool()
    @_safe_tool
    def tray_click(
        name: str,
        button: str = "left",
        double_click: bool = False,
    ) -> dict:
        """Click a system tray icon.

        Finds a tray icon matching the name (case-insensitive partial match)
        and clicks it. Use button='right' for context menus, double_click=True
        to open the application.

        Args:
            name: Tray icon tooltip or name (partial match).
            button: Mouse button — 'left' or 'right'.
            double_click: Whether to double-click the icon.

        Returns:
            Dict with success, icon name, tooltip, button used, and coordinates.
        """
        result = backend.tray_click(name=name, button=button, double=double_click)
        return {"success": True, **result}

    # ── Virtual Desktop (Phase 5A.3) ─────────────────

    @server.tool()
    @_safe_tool
    def virtual_desktop_list() -> dict:
        """List all virtual desktops (Windows 10/11).

        Returns each desktop's index, name, whether it is current, and ID.
        Use this to discover available desktops before switching or moving
        windows.

        Returns:
            Dict with success, desktops list, and count.
        """
        desktops = backend.virtual_desktop_list()
        return {"success": True, "desktops": desktops, "count": len(desktops)}

    @server.tool()
    @_safe_tool
    def virtual_desktop_switch(index: int) -> dict:
        """Switch to a virtual desktop by index.

        Changes the active desktop. Use virtual_desktop_list to find
        valid indices.

        Args:
            index: Zero-based desktop index.

        Returns:
            Dict with success, switched desktop index and name.
        """
        result = backend.virtual_desktop_switch(index)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def virtual_desktop_create(name: Optional[str] = None) -> dict:
        """Create a new virtual desktop.

        Creates a new desktop and optionally assigns it a name.
        The new desktop is added at the end of the desktop list.

        Args:
            name: Optional name for the new desktop.

        Returns:
            Dict with success, new desktop index, name, and id.
        """
        result = backend.virtual_desktop_create(name=name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def virtual_desktop_close(index: Optional[int] = None) -> dict:
        """Close a virtual desktop.

        Without index, closes the current desktop. Cannot close the
        last remaining desktop. Windows on the closed desktop are moved
        to an adjacent desktop.

        Args:
            index: Zero-based desktop index. None = current desktop.

        Returns:
            Dict with success, closed desktop index and name.
        """
        result = backend.virtual_desktop_close(index=index)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def virtual_desktop_move_window(
        desktop_index: int,
        app: Optional[str] = None,
        hwnd: Optional[int] = None,
    ) -> dict:
        """Move a window to a different virtual desktop.

        Identifies the target window by app name or handle. If neither
        is provided, moves the foreground window.

        Args:
            desktop_index: Target desktop index (zero-based).
            app: Application name (partial match).
            hwnd: Window handle (integer).

        Returns:
            Dict with success, window handle, target desktop index and name.
        """
        result = backend.virtual_desktop_move_window(
            desktop_index=desktop_index,
            app=app,
            hwnd=hwnd,
        )
        return {"success": True, **result}

    # ── Chrome CDP Tools ──────────────────────────────────────

    @server.tool()
    @_safe_tool
    def chrome_list_tabs(
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """List open Chrome browser tabs via DevTools Protocol.

        Chrome must be started with --remote-debugging-port=9222.

        Args:
            host: DevTools host (default localhost).
            port: DevTools port (default 9222).

        Returns:
            Dict with success, tabs list, and count.
        """
        from naturo.cdp import CDPClient
        client = CDPClient(host=host, port=port)
        tabs = client.list_tabs()
        return {"success": True, "tabs": tabs, "count": len(tabs)}

    @server.tool()
    @_safe_tool
    def chrome_evaluate(
        expression: str,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Execute JavaScript in a Chrome tab.

        Chrome must be started with --remote-debugging-port=9222.

        Args:
            expression: JavaScript expression to evaluate.
            tab_id: Target tab ID (from chrome_list_tabs). If None, uses first tab.
            host: DevTools host (default localhost).
            port: DevTools port (default 9222).

        Returns:
            Dict with success and evaluation result.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            result = client.evaluate(expression)
            return {"success": True, "result": result}

    @server.tool()
    @_safe_tool
    def chrome_screenshot(
        tab_id: Optional[str] = None,
        format: str = "png",
        quality: int = 80,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Capture a screenshot of a Chrome tab.

        Uses Chrome's own rendering engine for pixel-perfect screenshots.
        Chrome must be started with --remote-debugging-port=9222.

        Args:
            tab_id: Target tab ID. If None, uses first tab.
            format: Image format — png or jpeg.
            quality: JPEG quality (1-100, ignored for PNG).
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success and base64-encoded screenshot data.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            data = client.screenshot(format=format, quality=quality)
            return {
                "success": True,
                "format": format,
                "data": base64.b64encode(data).decode("ascii"),
                "size": len(data),
            }

    @server.tool()
    @_safe_tool
    def chrome_navigate(
        url: str,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Navigate a Chrome tab to a URL.

        Chrome must be started with --remote-debugging-port=9222.

        Args:
            url: Target URL.
            tab_id: Target tab ID. If None, uses first tab.
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success, url, and frameId.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            result = client.navigate(url)
            return {"success": True, "url": url, "frameId": result.get("frameId", "")}

    @server.tool()
    @_safe_tool
    def chrome_click(
        selector: str,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Click a DOM element in Chrome by CSS selector.

        Scrolls the element into view and dispatches a click event.
        Chrome must be started with --remote-debugging-port=9222.

        Args:
            selector: CSS selector for the target element.
            tab_id: Target tab ID. If None, uses first tab.
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success and selector.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            client.click_element(selector)
            return {"success": True, "selector": selector}

    @server.tool()
    @_safe_tool
    def chrome_type(
        selector: str,
        text: str,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Type text into a form field in Chrome.

        Focuses the element, clears it, then types character by character.
        Chrome must be started with --remote-debugging-port=9222.

        Args:
            selector: CSS selector for the input element.
            text: Text to type.
            tab_id: Target tab ID. If None, uses first tab.
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success, selector, and typed text.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            client.type_text(selector, text)
            return {"success": True, "selector": selector, "text": text}

    @server.tool()
    @_safe_tool
    def chrome_get_text(
        selector: str,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Get the text content of a DOM element in Chrome.

        Args:
            selector: CSS selector.
            tab_id: Target tab ID. If None, uses first tab.
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success, selector, and text content.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            text = client.get_element_text(selector)
            return {"success": True, "selector": selector, "text": text}

    @server.tool()
    @_safe_tool
    def chrome_get_html(
        selector: Optional[str] = None,
        tab_id: Optional[str] = None,
        host: str = "localhost",
        port: int = 9222,
    ) -> dict:
        """Get HTML of a page or specific element in Chrome.

        Args:
            selector: CSS selector (omit for full page HTML).
            tab_id: Target tab ID. If None, uses first tab.
            host: DevTools host.
            port: DevTools port.

        Returns:
            Dict with success and html content.
        """
        from naturo.cdp import CDPClient
        with CDPClient(host=host, port=port) as client:
            client.connect(tab_id=tab_id)
            if selector:
                html = client.evaluate(
                    f"document.querySelector({json.dumps(selector)})?.outerHTML ?? ''"
                )
            else:
                html = client.get_page_html()
            return {"success": True, "html": html}

    # ── Electron/CEF Tools ─────────────────────────

    @server.tool()
    @_safe_tool
    def electron_detect(
        app_name: str,
    ) -> dict:
        """Detect if a running application is Electron/CEF-based.

        Checks for Electron characteristics like app.asar, renderer
        processes, and DevTools ports.

        Args:
            app_name: Application name (e.g., 'Slack', 'Discord', 'Code').

        Returns:
            Dict with is_electron, app_name, debug_port, main_pid, processes.
        """
        from naturo.electron import detect_electron_app
        result = detect_electron_app(app_name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def electron_list() -> dict:
        """List all running Electron/CEF applications.

        Scans known Electron apps (VS Code, Slack, Discord, etc.) and
        reports which are currently running with their debug port status.

        Returns:
            Dict with apps list and count.
        """
        from naturo.electron import list_electron_apps
        result = list_electron_apps()
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def electron_connect(
        app_name: str,
        port: Optional[int] = None,
    ) -> dict:
        """Connect to a running Electron app via Chrome DevTools Protocol.

        The app must be running with --remote-debugging-port enabled.
        If port is omitted, auto-detects from the running process.

        Args:
            app_name: Application name.
            port: CDP port (auto-detect if omitted).

        Returns:
            Dict with port, tabs list, and count.
        """
        from naturo.electron import connect_to_electron
        result = connect_to_electron(app_name, port=port)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def electron_launch(
        app_path: str,
        port: int = 9229,
    ) -> dict:
        """Launch an Electron app with remote debugging enabled.

        Starts the application with --remote-debugging-port so it can
        be controlled via CDP. Use port 9229 (default) to avoid
        conflicting with Chrome's default 9222.

        Args:
            app_path: Full path to the Electron app executable.
            port: DevTools port (default 9229).

        Returns:
            Dict with pid, port, app_path.
        """
        if port < 1 or port > 65535:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"port must be between 1 and 65535, got {port}",
                },
            }
        from naturo.electron import launch_with_debug
        result = launch_with_debug(app_path, port=port)
        return {"success": True, **result}

    # ── Registry tools ───────────────────────────────────────

    @server.tool()
    @_safe_tool
    def registry_get(
        key_path: str,
        value_name: Optional[str] = None,
    ) -> dict:
        """Read a Windows Registry value.

        Args:
            key_path: Full registry path (e.g. HKCU\\Software\\MyApp).
            value_name: Value name (default: (Default) value).

        Returns:
            Dict with name, data, type_name.
        """
        from naturo.registry import reg_get
        result = reg_get(key_path, value_name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def registry_set(
        key_path: str,
        value_name: str,
        data: str,
        reg_type: str = "REG_SZ",
    ) -> dict:
        """Write a Windows Registry value. Creates the key if needed.

        Args:
            key_path: Full registry path (e.g. HKCU\\Software\\MyApp).
            value_name: Value name to set.
            data: Value data.
            reg_type: Registry type (REG_SZ, REG_DWORD, REG_QWORD, REG_BINARY,
                      REG_EXPAND_SZ, REG_MULTI_SZ).

        Returns:
            Dict with key, name, data, type_name.
        """
        valid_types = {"REG_SZ", "REG_DWORD", "REG_QWORD", "REG_BINARY",
                       "REG_EXPAND_SZ", "REG_MULTI_SZ"}
        if reg_type not in valid_types:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"Invalid reg_type '{reg_type}'. Must be one of: {', '.join(sorted(valid_types))}",
                },
            }
        from naturo.registry import reg_set
        result = reg_set(key_path, value_name, data, reg_type)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def registry_list(key_path: str) -> dict:
        """List registry subkeys and values under a key.

        Args:
            key_path: Full registry path (e.g. HKCU\\Software).

        Returns:
            Dict with subkeys list and values list.
        """
        from naturo.registry import reg_list
        result = reg_list(key_path)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def registry_delete(
        key_path: str,
        value_name: Optional[str] = None,
        recursive: bool = False,
    ) -> dict:
        """Delete a registry key or value.

        Args:
            key_path: Full registry path.
            value_name: Delete specific value (omit to delete the key itself).
            recursive: Delete key recursively if it has subkeys.

        Returns:
            Dict with deleted type and details.
        """
        from naturo.registry import reg_delete
        result = reg_delete(key_path, value_name, recursive)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def registry_search(
        key_path: str,
        query: str,
        max_depth: int = 5,
        max_results: int = 50,
        search_keys: bool = True,
        search_values: bool = True,
        search_data: bool = False,
    ) -> dict:
        """Search registry keys, value names, or data.

        Args:
            key_path: Starting registry path.
            query: Search string (case-insensitive).
            max_depth: Maximum search depth (1-20, default 5).
            max_results: Maximum results to return (default 50).
            search_keys: Search key names.
            search_values: Search value names.
            search_data: Search value data.

        Returns:
            Dict with results list and truncated flag.
        """
        if not query.strip():
            return {
                "success": False,
                "error": {"code": "INVALID_INPUT", "message": "Search query cannot be empty"},
            }
        if max_depth < 1 or max_depth > 20:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"max_depth must be between 1 and 20, got {max_depth}",
                },
            }
        if max_results < 1:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"max_results must be >= 1, got {max_results}",
                },
            }
        from naturo.registry import reg_search
        result = reg_search(
            key_path, query,
            max_depth=max_depth, max_results=max_results,
            search_keys=search_keys, search_values=search_values, search_data=search_data,
        )
        return {"success": True, **result}

    # ── Service tools ────────────────────────────────────────

    @server.tool()
    @_safe_tool
    def service_list(state: str = "all") -> dict:
        """List Windows services.

        Args:
            state: Filter by state — 'running', 'stopped', or 'all' (default).

        Returns:
            Dict with services list and count.
        """
        valid_states = {"running", "stopped", "all"}
        if state not in valid_states:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"Invalid state '{state}'. Must be one of: {', '.join(sorted(valid_states))}",
                },
            }
        from naturo.service import service_list as _service_list
        result = _service_list(state)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def service_start(name: str) -> dict:
        """Start a Windows service.

        Args:
            name: Service short name (e.g. 'Spooler', 'wuauserv').

        Returns:
            Dict with service name and new state.
        """
        from naturo.service import service_start as _service_start
        result = _service_start(name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def service_stop(name: str) -> dict:
        """Stop a Windows service.

        Args:
            name: Service short name (e.g. 'Spooler', 'wuauserv').

        Returns:
            Dict with service name and new state.
        """
        from naturo.service import service_stop as _service_stop
        result = _service_stop(name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def service_restart(name: str) -> dict:
        """Restart a Windows service (stop then start).

        Args:
            name: Service short name (e.g. 'Spooler', 'wuauserv').

        Returns:
            Dict with service name and new state.
        """
        from naturo.service import service_restart as _service_restart
        result = _service_restart(name)
        return {"success": True, **result}

    @server.tool()
    @_safe_tool
    def service_status(name: str) -> dict:
        """Get detailed status of a Windows service.

        Args:
            name: Service short name (e.g. 'Spooler', 'wuauserv').

        Returns:
            Dict with state, PID, start type, binary path, dependencies.
        """
        from naturo.service import service_status as _service_status
        result = _service_status(name)
        return {"success": True, **result}

    return server


def _iter_elements(el):
    """Iterate over all elements in a tree."""
    if el is None:
        return
    yield el
    for c in (el.children or []):
        yield from _iter_elements(c)


def run_server(transport: str = "stdio", host: str = "localhost", port: int = 3100):
    """Run the MCP server with the specified transport."""
    server = create_server(host=host, port=port)
    server.run(transport=transport)
