"""Test native bridge."""
import platform
import pytest
from naturo.bridge import NaturoCore


@pytest.mark.skipif(platform.system() != "Windows", reason="DLL only on Windows")
def test_load_core():
    core = NaturoCore()
    assert core is not None


@pytest.mark.skipif(platform.system() != "Windows", reason="DLL only on Windows")
def test_core_version():
    core = NaturoCore()
    ver = core.version()
    assert isinstance(ver, str)
    assert len(ver) > 0


@pytest.mark.skipif(platform.system() != "Windows", reason="DLL only on Windows")
def test_core_init_shutdown():
    core = NaturoCore()
    assert core.init() == 0
    assert core.shutdown() == 0


@pytest.mark.skipif(platform.system() != "Windows", reason="DLL only on Windows")
def test_core_double_init():
    core = NaturoCore()
    assert core.init() == 0
    assert core.init() == 0  # idempotent
    assert core.shutdown() == 0


def test_core_not_found_graceful():
    """On non-Windows, loading should fail with DependencyMissingError."""
    if platform.system() == "Windows":
        pytest.skip("Only test missing DLL on non-Windows")
    from naturo.errors import DependencyMissingError, ErrorCode
    with pytest.raises(DependencyMissingError) as exc_info:
        NaturoCore()
    assert exc_info.value.code == ErrorCode.DEPENDENCY_MISSING
    assert "naturo_core" in str(exc_info.value)
