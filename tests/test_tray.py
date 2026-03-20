"""Tests for system tray interaction commands.

Phase 4.5.5: System Tray Interaction.

Tests the CLI commands for listing and clicking system tray icons.
Backend calls are mocked since tray interaction requires a Windows desktop session.
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
    """Mock backend with tray methods."""
    backend = MagicMock()
    backend.tray_list.return_value = []
    backend.tray_click.return_value = {
        "name": "Volume Mixer",
        "tooltip": "Speakers (Realtek Audio)",
        "button": "left",
        "double_click": False,
        "clicked_at": {"x": 1850, "y": 1060},
    }
    return backend


def _sample_icons():
    """Sample tray icons for testing."""
    return [
        {
            "name": "Volume Mixer",
            "tooltip": "Speakers (Realtek Audio) — 50%",
            "is_visible": True,
            "x": 1830,
            "y": 1045,
            "width": 24,
            "height": 24,
        },
        {
            "name": "Wi-Fi",
            "tooltip": "Connected — MyNetwork",
            "is_visible": True,
            "x": 1860,
            "y": 1045,
            "width": 24,
            "height": 24,
        },
        {
            "name": "Dropbox",
            "tooltip": "Dropbox — Up to date",
            "is_visible": False,
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        },
    ]


# ── CLI: tray list ─────────────────────────────


class TestTrayList:
    """Tests for 'naturo tray list'."""

    def test_list_empty(self, runner, mock_backend):
        """list with no icons shows message."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list"])
        assert result.exit_code == 0
        assert "No tray icons found" in result.output

    def test_list_empty_json(self, runner, mock_backend):
        """list --json with no icons returns empty array."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["icons"] == []
        assert data["count"] == 0

    def test_list_with_icons(self, runner, mock_backend):
        """list with icons shows names and tooltips."""
        mock_backend.tray_list.return_value = _sample_icons()
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list"])
        assert result.exit_code == 0
        assert "Volume Mixer" in result.output
        assert "Wi-Fi" in result.output
        assert "Dropbox" in result.output
        assert "[hidden]" in result.output  # Dropbox is hidden

    def test_list_with_icons_json(self, runner, mock_backend):
        """list --json returns all icons."""
        mock_backend.tray_list.return_value = _sample_icons()
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["count"] == 3
        assert data["icons"][0]["name"] == "Volume Mixer"
        assert data["icons"][0]["is_visible"] is True
        assert data["icons"][2]["is_visible"] is False

    def test_list_tooltip_display(self, runner, mock_backend):
        """list shows tooltip when different from name."""
        icons = [{"name": "Wi-Fi", "tooltip": "Connected — MyNetwork", "is_visible": True}]
        mock_backend.tray_list.return_value = icons
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list"])
        assert "Connected — MyNetwork" in result.output


# ── CLI: tray click ────────────────────────────


class TestTrayClick:
    """Tests for 'naturo tray click'."""

    def test_click_icon(self, runner, mock_backend):
        """click activates a tray icon."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "Volume"])
        assert result.exit_code == 0
        assert "Volume Mixer" in result.output
        mock_backend.tray_click.assert_called_once_with(
            name="Volume", button="left", double=False,
        )

    def test_click_icon_json(self, runner, mock_backend):
        """click --json returns structured result."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "Volume", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["name"] == "Volume Mixer"
        assert data["button"] == "left"

    def test_click_right(self, runner, mock_backend):
        """click --right sends right-click."""
        mock_backend.tray_click.return_value = {
            "name": "Wi-Fi",
            "tooltip": "Connected",
            "button": "right",
            "double_click": False,
            "clicked_at": {"x": 1860, "y": 1060},
        }
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "Wi-Fi", "--right"])
        assert result.exit_code == 0
        assert "Right-clicked" in result.output
        mock_backend.tray_click.assert_called_once_with(
            name="Wi-Fi", button="right", double=False,
        )

    def test_click_double(self, runner, mock_backend):
        """click --double sends double-click."""
        mock_backend.tray_click.return_value = {
            "name": "Dropbox",
            "tooltip": "Up to date",
            "button": "left",
            "double_click": True,
            "clicked_at": {"x": 1830, "y": 1060},
        }
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "Dropbox", "--double"])
        assert result.exit_code == 0
        assert "Double-clicked" in result.output
        mock_backend.tray_click.assert_called_once_with(
            name="Dropbox", button="left", double=True,
        )

    def test_click_empty_name(self, runner, mock_backend):
        """click with empty name returns error."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "   "])
        assert result.exit_code != 0

    def test_click_empty_name_json(self, runner, mock_backend):
        """click with empty name returns JSON error."""
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "   ", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_INPUT"

    def test_click_not_found(self, runner, mock_backend):
        """click with non-existent icon returns error."""
        from naturo.errors import NaturoError
        mock_backend.tray_click.side_effect = NaturoError(
            message="Tray icon not found: Nonexistent",
            code="TRAY_ICON_NOT_FOUND",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "click", "Nonexistent", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "TRAY_ICON_NOT_FOUND"


# ── CLI: tray help ─────────────────────────────


class TestTrayHelp:
    """Tests for tray command help output."""

    def test_tray_help(self, runner):
        """tray --help shows subcommands."""
        result = runner.invoke(main, ["tray", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "click" in result.output

    def test_list_help(self, runner):
        """tray list --help shows options."""
        result = runner.invoke(main, ["tray", "list", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output

    def test_click_help(self, runner):
        """tray click --help shows NAME and options."""
        result = runner.invoke(main, ["tray", "click", "--help"])
        assert result.exit_code == 0
        assert "NAME" in result.output
        assert "--right" in result.output
        assert "--double" in result.output


# ── Error handling ─────────────────────────────


class TestTrayErrors:
    """Tests for tray error handling."""

    def test_backend_error_json(self, runner, mock_backend):
        """Backend exception produces JSON error."""
        from naturo.errors import NaturoError
        mock_backend.tray_list.side_effect = NaturoError(
            message="COM error", code="UNKNOWN_ERROR",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False

    def test_backend_error_text(self, runner, mock_backend):
        """Backend exception produces text error."""
        from naturo.errors import NaturoError
        mock_backend.tray_list.side_effect = NaturoError(
            message="COM error", code="UNKNOWN_ERROR",
        )
        with patch("naturo.backends.base.get_backend", return_value=mock_backend):
            result = runner.invoke(main, ["tray", "list"])
        assert result.exit_code != 0
