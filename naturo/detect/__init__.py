"""Unified App Model — framework detection system.

Detects which UI frameworks a target application uses and which interaction
methods are available (CDP, UIA, MSAA, JAB, IA2, Vision). Provides a
recommended method based on priority and availability.

Usage:
    from naturo.detect import detect, DetectionResult

    result = detect(pid=1234, exe="notepad.exe")
    print(result.recommended)  # e.g., InteractionMethodType.UIA
    print(result.to_dict())    # JSON-serializable result
"""

from naturo.detect.cache import DetectionCache, get_cache
from naturo.detect.chain import detect, detect_for_hwnd
from naturo.detect.models import (
    DetectionResult,
    FrameworkInfo,
    FrameworkType,
    InteractionMethod,
    InteractionMethodType,
    ProbeStatus,
)

__all__ = [
    "detect",
    "detect_for_hwnd",
    "get_cache",
    "DetectionCache",
    "DetectionResult",
    "FrameworkInfo",
    "FrameworkType",
    "InteractionMethod",
    "InteractionMethodType",
    "ProbeStatus",
]
