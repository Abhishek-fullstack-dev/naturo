"""Bridge to naturo_core native library via ctypes."""
import ctypes
import os
import platform
import sys
from pathlib import Path


class NaturoCore:
    """Wrapper around naturo_core.dll/.so native library."""

    def __init__(self, lib_path: str | None = None):
        self._lib = self._load(lib_path)
        # Set up function signatures
        self._lib.naturo_version.restype = ctypes.c_char_p
        self._lib.naturo_version.argtypes = []
        self._lib.naturo_init.restype = ctypes.c_int
        self._lib.naturo_init.argtypes = []
        self._lib.naturo_shutdown.restype = ctypes.c_int
        self._lib.naturo_shutdown.argtypes = []

    def _load(self, lib_path: str | None) -> ctypes.CDLL:
        if lib_path:
            return ctypes.CDLL(lib_path)

        # Search order:
        # 1. NATURO_CORE_PATH env var
        # 2. Package bin/ directory (bundled in wheel)
        # 3. Current directory
        # 4. System PATH

        env_path = os.environ.get("NATURO_CORE_PATH")
        if env_path and os.path.exists(env_path):
            return ctypes.CDLL(env_path)

        system = platform.system()
        if system == "Windows":
            lib_name = "naturo_core.dll"
        elif system == "Linux":
            lib_name = "libnaturo_core.so"
        elif system == "Darwin":
            lib_name = "libnaturo_core.dylib"
        else:
            raise OSError(f"Unsupported platform: {system}")

        # Check package bin/ directory
        pkg_dir = Path(__file__).parent / "bin"
        pkg_lib = pkg_dir / lib_name
        if pkg_lib.exists():
            return ctypes.CDLL(str(pkg_lib))

        # Check current directory
        cwd_lib = Path.cwd() / lib_name
        if cwd_lib.exists():
            return ctypes.CDLL(str(cwd_lib))

        # Fall back to system search
        try:
            return ctypes.CDLL(lib_name)
        except OSError:
            raise FileNotFoundError(
                f"Cannot find {lib_name}. Set NATURO_CORE_PATH or install the native library.\n"
                f"Searched: {env_path}, {pkg_lib}, {cwd_lib}, system PATH"
            )

    def version(self) -> str:
        return self._lib.naturo_version().decode("utf-8")

    def init(self) -> int:
        return self._lib.naturo_init()

    def shutdown(self) -> int:
        return self._lib.naturo_shutdown()
