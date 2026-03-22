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
        """service_list with state='running' omits state= arg (sc.exe default = active)."""
        from naturo.service import service_list

        mock_run.return_value = MagicMock(
            returncode=0, stdout=SC_QUERY_RUNNING, stderr=""
        )
        result = service_list("running")
        assert result["count"] == 1
        args = mock_run.call_args[0][0]
        # BUG-013: sc.exe doesn't accept "state= active"; omitting state=
        # returns only running services by default.
        assert "state=" not in args

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


