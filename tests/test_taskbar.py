"""Tests for taskbar interaction commands.

Phase 4.5.4: Taskbar Interaction.

Tests the CLI commands for listing and clicking taskbar items.
Backend calls are mocked since taskbar interaction requires a Windows desktop session.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from naturo.cli import main


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_backend():
    """Mock backend with taskbar methods."""
    backend = MagicMock()
    backend.taskbar_list.return_value = []
    backend.taskbar_click.return_value = {
        "name": "Chrome",
        "clicked_at": {"x": 200, "y": 1060},
    }
    return backend


def _sample_items():
    """Sample taskbar items for testing."""
    return [
        {
            "name": "Google Chrome",
            "hwnd": 12345,
            "is_active": True,
            "is_pinned": True,
            "x": 150,
            "y": 1040,
            "width": 50,
            "height": 40,
        },
        {
            "name": "Notepad",
            "hwnd": 67890,
            "is_active": False,
            "is_pinned": False,
            "x": 210,
            "y": 1040,
            "width": 50,
            "height": 40,
        },
    ]


# ── CLI: taskbar list ──────────────────────────


class TestTaskbarList:
    """Tests for 'naturo taskbar list'."""

    def test_list_empty(self, runner, mock_backend):
        """list with no items shows message."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list"])
        assert result.exit_code == 0
        assert "No taskbar items found" in result.output

    def test_list_empty_json(self, runner, mock_backend):
        """list --json with no items returns empty array."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["items"] == []
        assert data["count"] == 0

    def test_list_with_items(self, runner, mock_backend):
        """list with items shows names and states."""
        mock_backend.taskbar_list.return_value = _sample_items()
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list"])
        assert result.exit_code == 0
        assert "Google Chrome" in result.output
        assert "Notepad" in result.output
        assert "[active]" in result.output

    def test_list_with_items_json(self, runner, mock_backend):
        """list --json returns all items."""
        mock_backend.taskbar_list.return_value = _sample_items()
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["count"] == 2
        assert data["items"][0]["name"] == "Google Chrome"
        assert data["items"][0]["is_active"] is True
        assert data["items"][1]["name"] == "Notepad"


# ── CLI: taskbar click ─────────────────────────


class TestTaskbarClick:
    """Tests for 'naturo taskbar click'."""

    def test_click_item(self, runner, mock_backend):
        """click activates a taskbar item."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "click", "Chrome"])
        assert result.exit_code == 0
        assert "Chrome" in result.output
        mock_backend.taskbar_click.assert_called_once_with(name="Chrome")

    def test_click_item_json(self, runner, mock_backend):
        """click --json returns structured result."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "click", "Chrome", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["name"] == "Chrome"

    def test_click_empty_name(self, runner, mock_backend):
        """click with empty name returns error."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "click", "   "])
        assert result.exit_code != 0

    def test_click_empty_name_json(self, runner, mock_backend):
        """click with empty name returns JSON error."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "click", "   ", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_INPUT"

    def test_click_not_found(self, runner, mock_backend):
        """click with non-existent item returns error."""
        from naturo.errors import NaturoError
        mock_backend.taskbar_click.side_effect = NaturoError(
            message="Taskbar item not found: Nonexistent",
            code="TASKBAR_ITEM_NOT_FOUND",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "click", "Nonexistent", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "TASKBAR_ITEM_NOT_FOUND"


# ── CLI: taskbar help ──────────────────────────


class TestTaskbarHelp:
    """Tests for taskbar command help output."""

    def test_taskbar_help(self, runner):
        """taskbar --help shows subcommands."""
        result = runner.invoke(main, ["taskbar", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "click" in result.output

    def test_list_help(self, runner):
        """taskbar list --help shows options."""
        result = runner.invoke(main, ["taskbar", "list", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output

    def test_click_help(self, runner):
        """taskbar click --help shows NAME argument."""
        result = runner.invoke(main, ["taskbar", "click", "--help"])
        assert result.exit_code == 0
        assert "NAME" in result.output


# ── Error handling ─────────────────────────────


class TestTaskbarErrors:
    """Tests for taskbar error handling."""

    def test_backend_error_json(self, runner, mock_backend):
        """Backend exception produces JSON error."""
        from naturo.errors import NaturoError
        mock_backend.taskbar_list.side_effect = NaturoError(
            message="COM error", code="UNKNOWN_ERROR",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False

    def test_backend_error_text(self, runner, mock_backend):
        """Backend exception produces text error."""
        from naturo.errors import NaturoError
        mock_backend.taskbar_list.side_effect = NaturoError(
            message="COM error", code="UNKNOWN_ERROR",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["taskbar", "list"])
        assert result.exit_code != 0
