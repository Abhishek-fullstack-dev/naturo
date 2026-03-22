"""Data models for the Unified App Model detection system.

Defines the structures used to represent framework detection results,
interaction methods, and their capabilities.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FrameworkType(str, Enum):
    """Known UI framework types."""

    ELECTRON = "electron"
    CEF = "cef"
    CHROME = "chrome"
    WPF = "wpf"
    WINFORMS = "winforms"
    UWP = "uwp"
    WIN32 = "win32"
    QT = "qt"
    JAVA_SWING = "java_swing"
    JAVA_FX = "java_fx"
    GTK = "gtk"
    UNKNOWN = "unknown"


class InteractionMethodType(str, Enum):
    """Available interaction methods, ordered by general preference."""

    CDP = "cdp"
    UIA = "uia"
    MSAA = "msaa"
    JAB = "jab"
    IA2 = "ia2"
    VISION = "vision"


# Priority order: lower number = higher priority
METHOD_PRIORITY: Dict[InteractionMethodType, int] = {
    InteractionMethodType.CDP: 1,
    InteractionMethodType.UIA: 2,
    InteractionMethodType.MSAA: 3,
    InteractionMethodType.JAB: 4,
    InteractionMethodType.IA2: 5,
    InteractionMethodType.VISION: 6,
}


class ProbeStatus(str, Enum):
    """Status of a framework probe."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FALLBACK = "fallback"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class InteractionMethod:
    """An available interaction method for a target application.

    Attributes:
        method: The interaction method type.
        priority: Numeric priority (1 = highest).
        status: Whether this method is available/fallback/unavailable.
        capabilities: List of capabilities this method supports.
        metadata: Additional method-specific info (e.g., debug_port for CDP).
        confidence: How confident we are this method works (0.0-1.0).
    """

    method: InteractionMethodType
    priority: int
    status: ProbeStatus
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        result = {
            "method": self.method.value,
            "priority": self.priority,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "confidence": self.confidence,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class FrameworkInfo:
    """Detected framework information.

    Attributes:
        framework_type: The detected framework type.
        version: Framework version string if detectable.
        dll_signatures: DLLs that led to this detection.
    """

    framework_type: FrameworkType
    version: Optional[str] = None
    dll_signatures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        result = {
            "type": self.framework_type.value,
        }
        if self.version:
            result["version"] = self.version
        if self.dll_signatures:
            result["dll_signatures"] = self.dll_signatures
        return result


@dataclass
class DetectionResult:
    """Complete detection result for a target application.

    Attributes:
        pid: Process ID of the target.
        exe: Executable path.
        app_name: Application display name.
        frameworks: Detected frameworks (may be multiple).
        methods: Available interaction methods, sorted by priority.
        recommended: The recommended (best) interaction method.
        notes: Human-readable notes about the detection.
    """

    pid: int
    exe: str = ""
    app_name: str = ""
    frameworks: List[FrameworkInfo] = field(default_factory=list)
    methods: List[InteractionMethod] = field(default_factory=list)
    recommended: Optional[InteractionMethodType] = None
    notes: str = ""

    def best_method(self) -> Optional[InteractionMethod]:
        """Return the highest-priority available method.

        Returns:
            The best InteractionMethod, or None if no methods are available.
        """
        available = [
            m for m in self.methods
            if m.status in (ProbeStatus.AVAILABLE, ProbeStatus.FALLBACK)
        ]
        if not available:
            return None
        return min(available, key=lambda m: m.priority)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        best = self.best_method()
        return {
            "pid": self.pid,
            "exe": self.exe,
            "app": self.app_name,
            "framework": {
                "detected": [f.to_dict() for f in self.frameworks],
            },
            "interaction_methods": [m.to_dict() for m in self.methods],
            "recommended": best.method.value if best else None,
            "notes": self.notes,
        }
