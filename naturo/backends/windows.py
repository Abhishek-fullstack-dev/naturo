"""Windows backend — powered by naturo_core.dll (C++ engine)."""
from naturo.backends.base import Backend, WindowInfo, ElementInfo, CaptureResult
from typing import Optional


class WindowsBackend(Backend):
    """Windows automation via naturo_core.dll.

    Uses UIAutomation, MSAA, and native Windows APIs through the C++ core.
    Supports advanced input modes: normal (SendInput), hardware (Phys32), hook (MinHook).
    """

    def __init__(self):
        # DLL will be loaded when methods are called
        self._core = None

    @property
    def platform_name(self) -> str:
        return "windows"

    @property
    def capabilities(self) -> dict:
        return {
            "platform": "windows",
            "input_modes": ["normal", "hardware", "hook"],
            "accessibility": ["uia", "msaa", "ia2"],
            "extensions": ["excel", "java", "sap", "registry", "service"],
        }

    # All methods raise NotImplementedError for now — Phase 1+ will implement
    def capture_screen(self, screen_index=0, output_path="capture.png") -> CaptureResult:
        raise NotImplementedError("Coming in Phase 1")

    def capture_window(self, window_title=None, hwnd=None, output_path="capture.png") -> CaptureResult:
        raise NotImplementedError("Coming in Phase 1")

    def list_windows(self) -> list[WindowInfo]:
        raise NotImplementedError("Coming in Phase 1")

    def focus_window(self, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 1")

    def close_window(self, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def minimize_window(self, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def maximize_window(self, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def move_window(self, x=0, y=0, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def resize_window(self, width=800, height=600, title=None, hwnd=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def find_element(self, selector="", window_title=None) -> Optional[ElementInfo]:
        raise NotImplementedError("Coming in Phase 1")

    def get_element_tree(self, window_title=None, depth=3) -> Optional[ElementInfo]:
        raise NotImplementedError("Coming in Phase 1")

    def click(self, x=None, y=None, element_id=None, button="left", double=False, input_mode="normal") -> None:
        raise NotImplementedError("Coming in Phase 2")

    def type_text(self, text="", delay_ms=5, profile="human", wpm=120, input_mode="normal") -> None:
        raise NotImplementedError("Coming in Phase 2")

    def press_key(self, key="", input_mode="normal") -> None:
        raise NotImplementedError("Coming in Phase 2")

    def hotkey(self, *keys, hold_duration_ms=50) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def scroll(self, direction="down", amount=3, x=None, y=None, smooth=False) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def drag(self, from_x=0, from_y=0, to_x=0, to_y=0, duration_ms=500, steps=10) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def move_mouse(self, x=0, y=0) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def clipboard_get(self) -> str:
        raise NotImplementedError("Coming in Phase 2")

    def clipboard_set(self, text="") -> None:
        raise NotImplementedError("Coming in Phase 2")

    def list_apps(self) -> list[dict]:
        raise NotImplementedError("Coming in Phase 2")

    def launch_app(self, name="") -> None:
        raise NotImplementedError("Coming in Phase 2")

    def quit_app(self, name="", force=False) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def menu_list(self, app=None) -> list[dict]:
        raise NotImplementedError("Coming in Phase 2")

    def menu_click(self, path="", app=None) -> None:
        raise NotImplementedError("Coming in Phase 2")

    def open_uri(self, uri="") -> None:
        raise NotImplementedError("Coming in Phase 2")
