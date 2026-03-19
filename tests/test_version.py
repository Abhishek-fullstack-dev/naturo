"""Test version consistency."""
from naturo.version import __version__


def test_version_is_string():
    assert isinstance(__version__, str)


def test_version_format():
    parts = __version__.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()


def test_version_matches_pyproject():
    import tomllib
    from pathlib import Path

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return  # skip in installed package
    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    assert data["project"]["version"] == __version__
