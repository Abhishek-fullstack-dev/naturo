"""Test CLI commands."""
from click.testing import CliRunner
from naturo.cli import main


def test_cli_version_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "naturo" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "capture" in result.output
    assert "list" in result.output
    assert "see" in result.output
    assert "click" in result.output
    assert "type" in result.output


def test_cli_capture_placeholder():
    runner = CliRunner()
    result = runner.invoke(main, ["capture"])
    assert result.exit_code == 0
    assert "Phase 1" in result.output


def test_cli_list_placeholder():
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0


def test_cli_see_placeholder():
    runner = CliRunner()
    result = runner.invoke(main, ["see"])
    assert result.exit_code == 0
