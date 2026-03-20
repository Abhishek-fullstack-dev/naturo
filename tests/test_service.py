"""Tests for Windows Service management (Phase 5C.3).

Tests the service backend and CLI commands using mocked subprocess calls.
"""

from __future__ import annotations

import json
import platform
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from naturo.cli import main


# ── Sample sc.exe output fixtures ─────────────────────────────────────────

SC_QUERY_RUNNING = """\
SERVICE_NAME: Spooler
DISPLAY_NAME: Print Spooler
        TYPE               : 110  WIN32_OWN_PROCESS  (interactive)
        STATE              : 4  RUNNING
                                (STOPPABLE, NOT_PAUSABLE, ACCEPTS_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x0
        PID                : 1234
        FLAGS              :
"""

SC_QUERY_STOPPED = """\
SERVICE_NAME: wuauserv
DISPLAY_NAME: Windows Update
        TYPE               : 20  WIN32_SHARE_PROCESS
        STATE              : 1  STOPPED
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x0
"""

SC_QUERY_MULTI = SC_QUERY_RUNNING + "\n" + SC_QUERY_STOPPED

SC_QC_OUTPUT = """\
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: Spooler
        TYPE               : 110  WIN32_OWN_PROCESS  (interactive)
        START_TYPE         : 2   AUTO_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : C:\\Windows\\System32\\spoolsv.exe
        LOAD_ORDER_GROUP   : SpoolerGroup
        TAG                : 0
        DISPLAY_NAME       : Print Spooler
        DEPENDENCIES       : RPCSS/http
        SERVICE_START_NAME : LocalSystem
"""

SC_QUERY_NOT_FOUND = """\
[SC] EnumQueryServicesStatus:OpenService FAILED 1060:

The specified service does not exist as an installed service.
"""


# ── Backend tests ─────────────────────────────────────────────────────────


class TestServiceBackend:
    """Tests for naturo.service module."""

    @pytest.mark.skipif(platform.system() == "Windows", reason="Tests mock for non-Windows")
    def test_require_windows_raises_on_non_windows(self):
        """Service functions raise PLATFORM_ERROR on non-Windows."""
        from naturo.errors import NaturoError
        from naturo.service import _require_windows

        with pytest.raises(NaturoError, match="Service operations require Windows"):
            _require_windows()

    def test_parse_sc_query_output_running(self):
        """Parses running service from sc query output."""
        from naturo.service import _parse_sc_query_output

        services = _parse_sc_query_output(SC_QUERY_RUNNING)
        assert len(services) == 1
        svc = services[0]
        assert svc["name"] == "Spooler"
        assert svc["display_name"] == "Print Spooler"
        assert svc["state"] == "running"
        assert svc["pid"] == 1234

    def test_parse_sc_query_output_stopped(self):
        """Parses stopped service from sc query output."""
        from naturo.service import _parse_sc_query_output

        services = _parse_sc_query_output(SC_QUERY_STOPPED)
        assert len(services) == 1
        svc = services[0]
        assert svc["name"] == "wuauserv"
        assert svc["state"] == "stopped"

    def test_parse_sc_query_output_multiple(self):
        """Parses multiple services from sc query output."""
        from naturo.service import _parse_sc_query_output

        services = _parse_sc_query_output(SC_QUERY_MULTI)
        assert len(services) == 2
        assert services[0]["name"] == "Spooler"
        assert services[1]["name"] == "wuauserv"

    def test_parse_sc_query_output_empty(self):
        """Parses empty output gracefully."""
        from naturo.service import _parse_sc_query_output

        services = _parse_sc_query_output("")
        assert services == []

    def test_parse_sc_qc_output(self):
        """Parses sc qc config output."""
        from naturo.service import _parse_sc_qc_output

        config = _parse_sc_qc_output(SC_QC_OUTPUT)
        assert config["name"] == "Spooler"
        assert config["display_name"] == "Print Spooler"
        assert config["start_type"] == "auto_start"
        assert "spoolsv.exe" in config["binary_path"]
        assert config["run_as"] == "LocalSystem"
        assert "RPCSS" in config["dependencies"]

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_list_all(self, mock_run, mock_platform):
        """service_list returns all services."""
        from naturo.service import service_list

        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_MULTI, stderr=""
        )
        result = service_list("all")
        assert result["count"] == 2
        assert len(result["services"]) == 2
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "all" in args

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_list_running(self, mock_run, mock_platform):
        """service_list with state='running' passes 'active' to sc."""
        from naturo.service import service_list

        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_RUNNING, stderr=""
        )
        result = service_list("running")
        assert result["count"] == 1
        args = mock_run.call_args[0][0]
        assert "active" in args

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_status_found(self, mock_run, mock_platform):
        """service_status returns detailed info for existing service."""
        from naturo.service import service_status

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
        ]
        result = service_status("Spooler")
        assert result["name"] == "Spooler"
        assert result["state"] == "running"
        assert result["pid"] == 1234
        assert result["start_type"] == "auto_start"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_status_not_found(self, mock_run, mock_platform):
        """service_status raises SERVICE_NOT_FOUND for unknown service."""
        from naturo.errors import NaturoError
        from naturo.service import service_status

        mock_run.return_value = MagicMock(
            returncode=1, stdout=SC_QUERY_NOT_FOUND, stderr=""
        )
        with pytest.raises(NaturoError, match="Service not found"):
            service_status("nonexistent_svc")

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_status_empty_name(self, mock_run, mock_platform):
        """service_status rejects empty name."""
        from naturo.errors import NaturoError
        from naturo.service import service_status

        with pytest.raises(NaturoError, match="cannot be empty"):
            service_status("")

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_start_success(self, mock_run, mock_platform):
        """service_start succeeds for stopped service."""
        from naturo.service import service_start

        mock_run.side_effect = [
            # service_status: queryex
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            # service_status: qc
            MagicMock(returncode=0, stdout="", stderr=""),
            # net start
            MagicMock(returncode=0, stdout="Service started successfully", stderr=""),
        ]
        result = service_start("wuauserv")
        assert result["action"] == "start"
        assert result["state"] == "running"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_start_already_running(self, mock_run, mock_platform):
        """service_start raises error if already running."""
        from naturo.errors import NaturoError
        from naturo.service import service_start

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
        ]
        with pytest.raises(NaturoError, match="already running"):
            service_start("Spooler")

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_stop_success(self, mock_run, mock_platform):
        """service_stop succeeds for running service."""
        from naturo.service import service_stop

        mock_run.side_effect = [
            # service_status: queryex
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            # service_status: qc
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
            # net stop
            MagicMock(returncode=0, stdout="Service stopped successfully", stderr=""),
        ]
        result = service_stop("Spooler")
        assert result["action"] == "stop"
        assert result["state"] == "stopped"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_stop_already_stopped(self, mock_run, mock_platform):
        """service_stop raises error if already stopped."""
        from naturo.errors import NaturoError
        from naturo.service import service_stop

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        with pytest.raises(NaturoError, match="already stopped"):
            service_stop("wuauserv")

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_restart_from_running(self, mock_run, mock_platform):
        """service_restart stops and starts a running service."""
        from naturo.service import service_restart

        mock_run.side_effect = [
            # service_status: queryex
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            # service_status: qc
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
            # net stop
            MagicMock(returncode=0, stdout="", stderr=""),
            # net start
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        result = service_restart("Spooler")
        assert result["action"] == "restart"
        assert result["state"] == "running"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_restart_from_stopped(self, mock_run, mock_platform):
        """service_restart just starts a stopped service."""
        from naturo.service import service_restart

        mock_run.side_effect = [
            # service_status: queryex
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            # service_status: qc
            MagicMock(returncode=0, stdout="", stderr=""),
            # net start
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        result = service_restart("wuauserv")
        assert result["action"] == "restart"
        assert result["state"] == "running"


# ── CLI tests ─────────────────────────────────────────────────────────────


class TestServiceCLI:
    """Tests for service CLI commands."""

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_list_json(self, mock_run, mock_platform):
        """naturo service list --json outputs valid JSON."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_MULTI, stderr=""
        )
        runner = CliRunner()
        result = runner.invoke(main, ["service", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["services"]) == 2

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_list_text(self, mock_run, mock_platform):
        """naturo service list shows formatted text output."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_MULTI, stderr=""
        )
        runner = CliRunner()
        result = runner.invoke(main, ["service", "list"])
        assert result.exit_code == 0
        assert "Spooler" in result.output
        assert "wuauserv" in result.output
        assert "2 service(s)" in result.output

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_list_running(self, mock_run, mock_platform):
        """naturo service list --state running filters."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_RUNNING, stderr=""
        )
        runner = CliRunner()
        result = runner.invoke(main, ["service", "list", "--state", "running", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_status_json(self, mock_run, mock_platform):
        """naturo service status --json returns service details."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "status", "Spooler", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["state"] == "running"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_status_text(self, mock_run, mock_platform):
        """naturo service status shows human-readable output."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "status", "Spooler"])
        assert result.exit_code == 0
        assert "Spooler" in result.output
        assert "running" in result.output

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_status_not_found_json(self, mock_run, mock_platform):
        """naturo service status --json returns SERVICE_NOT_FOUND error."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout=SC_QUERY_NOT_FOUND, stderr=""
        )
        runner = CliRunner()
        result = runner.invoke(main, ["service", "status", "nonexistent_svc", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "SERVICE_NOT_FOUND"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_start_json(self, mock_run, mock_platform):
        """naturo service start --json returns success."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="Service started", stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "start", "wuauserv", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["action"] == "start"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_start_already_running_json(self, mock_run, mock_platform):
        """naturo service start --json returns error if already running."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "start", "Spooler", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "SERVICE_ALREADY_RUNNING"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_stop_json(self, mock_run, mock_platform):
        """naturo service stop --json returns success."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
            MagicMock(returncode=0, stdout="Service stopped", stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "stop", "Spooler", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["action"] == "stop"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_stop_already_stopped_json(self, mock_run, mock_platform):
        """naturo service stop --json returns error if already stopped."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "stop", "wuauserv", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "SERVICE_ALREADY_STOPPED"

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_cli_service_restart_json(self, mock_run, mock_platform):
        """naturo service restart --json returns success."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ]
        runner = CliRunner()
        result = runner.invoke(main, ["service", "restart", "Spooler", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["action"] == "restart"

    def test_cli_service_platform_error_json(self):
        """naturo service on non-Windows returns PLATFORM_ERROR."""
        if platform.system() == "Windows":
            pytest.skip("Only on non-Windows")
        runner = CliRunner()
        result = runner.invoke(main, ["service", "list", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "PLATFORM_ERROR"

    def test_cli_service_status_platform_error_text(self):
        """naturo service status on non-Windows shows text error."""
        if platform.system() == "Windows":
            pytest.skip("Only on non-Windows")
        runner = CliRunner()
        result = runner.invoke(main, ["service", "status", "Spooler"])
        assert result.exit_code != 0

    def test_cli_service_help(self):
        """naturo service --help shows available commands."""
        runner = CliRunner()
        result = runner.invoke(main, ["service", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "start" in result.output
        assert "stop" in result.output
        assert "restart" in result.output
        assert "status" in result.output


# ── Edge cases ────────────────────────────────────────────────────────────


class TestServiceEdgeCases:
    """Edge case tests for service operations."""

    def test_parse_sc_query_partial_output(self):
        """Handles partial/malformed sc output gracefully."""
        from naturo.service import _parse_sc_query_output

        partial = "SERVICE_NAME: partial_svc\n"
        services = _parse_sc_query_output(partial)
        assert len(services) == 1
        assert services[0]["name"] == "partial_svc"

    def test_parse_sc_query_no_pid(self):
        """Handles service without PID field."""
        from naturo.service import _parse_sc_query_output

        no_pid = """\
SERVICE_NAME: test_svc
DISPLAY_NAME: Test Service
        STATE              : 1  STOPPED
"""
        services = _parse_sc_query_output(no_pid)
        assert len(services) == 1
        assert "pid" not in services[0]

    def test_parse_sc_qc_empty_dependencies(self):
        """Handles service with no dependencies."""
        from naturo.service import _parse_sc_qc_output

        output = """\
SERVICE_NAME: test_svc
        START_TYPE         : 3   DEMAND_START
        DEPENDENCIES       : 
        SERVICE_START_NAME : LocalSystem
"""
        config = _parse_sc_qc_output(output)
        assert config["start_type"] == "demand_start"
        assert config["dependencies"] == []

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_list_empty(self, mock_run, mock_platform):
        """service_list handles no services matching filter."""
        from naturo.service import service_list

        mock_run.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        result = service_list("stopped")
        assert result["count"] == 0
        assert result["services"] == []

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_start_net_failure(self, mock_run, mock_platform):
        """service_start handles net start failure."""
        from naturo.errors import NaturoError
        from naturo.service import service_start

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_STOPPED, stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=2, stdout="", stderr="Access is denied."),
        ]
        with pytest.raises(NaturoError, match="Failed to start"):
            service_start("wuauserv")

    @patch("naturo.service.platform.system", return_value="Windows")
    @patch("naturo.service.subprocess.run")
    def test_service_stop_net_failure(self, mock_run, mock_platform):
        """service_stop handles net stop failure."""
        from naturo.errors import NaturoError
        from naturo.service import service_stop

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=SC_QUERY_RUNNING, stderr=""),
            MagicMock(returncode=0, stdout=SC_QC_OUTPUT, stderr=""),
            MagicMock(returncode=2, stdout="", stderr="Access is denied."),
        ]
        with pytest.raises(NaturoError, match="Failed to stop"):
            service_stop("Spooler")
