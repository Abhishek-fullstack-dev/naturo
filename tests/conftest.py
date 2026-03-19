import pytest
import platform


def pytest_configure(config):
    """Register custom markers."""
    pass  # markers defined in pyproject.toml


@pytest.fixture
def is_windows():
    return platform.system() == "Windows"


@pytest.fixture
def skip_if_not_windows():
    if platform.system() != "Windows":
        pytest.skip("Windows-only test")
