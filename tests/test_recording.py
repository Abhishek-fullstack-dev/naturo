"""Tests for the action recording and replay engine."""
import json
import os
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from naturo.recording import (
    ActionStep,
    Recording,
    generate_recording_id,
    save_recording,
    load_recording,
    list_recordings,
    delete_recording,
    replay_recording,
)
from naturo.cli.record_cmd import (
    record,
    _get_active_recording,
    _set_active_recording,
    record_action,
)
from naturo.cli import main


@pytest.fixture
def tmp_recordings_dir(tmp_path):
    """Provide a temporary recordings directory."""
    return tmp_path / "recordings"


@pytest.fixture
def sample_recording():
    """Create a sample recording for testing."""
    rec = Recording(
        name="Test Recording",
        recording_id="rec_20260321_020000",
        created_at="2026-03-21T02:00:00+00:00",
    )
    rec.add_step("click", {"x": 100, "y": 200, "button": "left"})
    rec.add_step("type", {"text": "hello", "wpm": 120})
    rec.add_step("press", {"key": "enter", "count": 1})
    return rec


class TestActionStep:
    """Tests for ActionStep dataclass."""

    def test_create_step(self):
        step = ActionStep(
            command="click",
            args={"x": 100, "y": 200},
            timestamp=1000.0,
            duration_ms=50.0,
        )
        assert step.command == "click"
        assert step.args == {"x": 100, "y": 200}
        assert step.timestamp == 1000.0
        assert step.duration_ms == 50.0

    def test_to_dict(self):
        step = ActionStep(command="press", args={"key": "enter"}, timestamp=1000.0)
        d = step.to_dict()
        assert d["command"] == "press"
        assert d["args"] == {"key": "enter"}
        assert d["timestamp"] == 1000.0
        assert d["duration_ms"] == 0.0

    def test_from_dict(self):
        data = {"command": "type", "args": {"text": "hi"}, "timestamp": 2000.0, "duration_ms": 100.0}
        step = ActionStep.from_dict(data)
        assert step.command == "type"
        assert step.args["text"] == "hi"
        assert step.duration_ms == 100.0

    def test_from_dict_missing_duration(self):
        data = {"command": "scroll", "args": {"direction": "down"}, "timestamp": 3000.0}
        step = ActionStep.from_dict(data)
        assert step.duration_ms == 0.0


class TestRecording:
    """Tests for Recording dataclass."""

    def test_create_recording(self):
        rec = Recording(
            name="My Recording",
            recording_id="rec_20260321_010000",
            created_at="2026-03-21T01:00:00+00:00",
        )
        assert rec.name == "My Recording"
        assert rec.steps == []
        assert rec.metadata == {}

    def test_add_step(self):
        rec = Recording(name="Test", recording_id="rec_test", created_at="2026-01-01T00:00:00Z")
        rec.add_step("click", {"x": 50, "y": 50})
        assert len(rec.steps) == 1
        assert rec.steps[0].command == "click"

    def test_to_dict(self, sample_recording):
        d = sample_recording.to_dict()
        assert d["name"] == "Test Recording"
        assert d["recording_id"] == "rec_20260321_020000"
        assert d["step_count"] == 3
        assert len(d["steps"]) == 3

    def test_from_dict(self, sample_recording):
        d = sample_recording.to_dict()
        rec2 = Recording.from_dict(d)
        assert rec2.name == sample_recording.name
        assert rec2.recording_id == sample_recording.recording_id
        assert len(rec2.steps) == len(sample_recording.steps)

    def test_total_duration_ms_empty(self):
        rec = Recording(name="Empty", recording_id="rec_empty", created_at="2026-01-01T00:00:00Z")
        assert rec.total_duration_ms() == 0

    def test_total_duration_ms_single_step(self):
        rec = Recording(name="Single", recording_id="rec_single", created_at="2026-01-01T00:00:00Z")
        rec.steps.append(ActionStep(command="click", args={}, timestamp=1000.0, duration_ms=50.0))
        assert rec.total_duration_ms() == 50.0


class TestRecordingPersistence:
    """Tests for save/load/list/delete operations."""

    def test_save_and_load(self, sample_recording, tmp_recordings_dir):
        path = save_recording(sample_recording, directory=tmp_recordings_dir)
        assert path.exists()
        assert path.suffix == ".json"

        loaded = load_recording(sample_recording.recording_id, directory=tmp_recordings_dir)
        assert loaded.name == sample_recording.name
        assert len(loaded.steps) == 3

    def test_load_not_found(self, tmp_recordings_dir):
        with pytest.raises(FileNotFoundError, match="Recording not found"):
            load_recording("rec_nonexistent", directory=tmp_recordings_dir)

    def test_list_recordings_empty(self, tmp_recordings_dir):
        recs = list_recordings(directory=tmp_recordings_dir)
        assert recs == []

    def test_list_recordings(self, sample_recording, tmp_recordings_dir):
        save_recording(sample_recording, directory=tmp_recordings_dir)
        recs = list_recordings(directory=tmp_recordings_dir)
        assert len(recs) == 1
        assert recs[0]["recording_id"] == sample_recording.recording_id
        assert recs[0]["step_count"] == 3

    def test_delete_recording(self, sample_recording, tmp_recordings_dir):
        save_recording(sample_recording, directory=tmp_recordings_dir)
        assert delete_recording(sample_recording.recording_id, directory=tmp_recordings_dir)
        recs = list_recordings(directory=tmp_recordings_dir)
        assert len(recs) == 0

    def test_delete_not_found(self, tmp_recordings_dir):
        assert not delete_recording("rec_nonexistent", directory=tmp_recordings_dir)

    def test_generate_recording_id(self):
        rid = generate_recording_id()
        assert rid.startswith("rec_")
        assert len(rid) > 10


class TestReplay:
    """Tests for replay_recording."""

    def test_replay_dry_run(self, sample_recording):
        results = replay_recording(sample_recording, dry_run=True)
        assert len(results) == 3
        for r in results:
            assert r["status"] == "skipped"
            assert r["reason"] == "dry_run"

    def test_replay_empty_recording(self):
        rec = Recording(name="Empty", recording_id="rec_empty", created_at="2026-01-01T00:00:00Z")
        results = replay_recording(rec, dry_run=True)
        assert results == []

    def test_replay_invalid_speed(self, sample_recording):
        with pytest.raises(ValueError, match="Speed must be positive"):
            replay_recording(sample_recording, speed=0)
        with pytest.raises(ValueError, match="Speed must be positive"):
            replay_recording(sample_recording, speed=-1)

    def test_replay_callback(self, sample_recording):
        callback_calls = []

        def on_step(idx, step, result):
            callback_calls.append((idx, step.command, result["status"]))

        replay_recording(sample_recording, dry_run=True, step_callback=on_step)
        assert len(callback_calls) == 3
        assert callback_calls[0] == (0, "click", "skipped")
        assert callback_calls[1] == (1, "type", "skipped")
        assert callback_calls[2] == (2, "press", "skipped")

    @patch("naturo.backends.base.get_backend")
    def test_replay_executes_click(self, mock_get_backend, sample_recording):
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend
        # Only replay click (first step)
        rec = Recording(name="Click Only", recording_id="rec_click", created_at="2026-01-01T00:00:00Z")
        rec.steps = [sample_recording.steps[0]]

        results = replay_recording(rec)
        assert len(results) == 1
        assert results[0]["status"] == "success"
        mock_backend.click.assert_called_once()

    @patch("naturo.backends.base.get_backend")
    def test_replay_handles_error(self, mock_get_backend):
        mock_backend = MagicMock()
        mock_backend.click.side_effect = RuntimeError("Click failed")
        mock_get_backend.return_value = mock_backend

        rec = Recording(name="Error", recording_id="rec_err", created_at="2026-01-01T00:00:00Z")
        rec.add_step("click", {"x": 10, "y": 10, "button": "left"})

        results = replay_recording(rec)
        assert len(results) == 1
        assert results[0]["status"] == "error"
        assert "Click failed" in results[0]["error"]

    @patch("naturo.backends.base.get_backend")
    def test_replay_unknown_command(self, mock_get_backend):
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend

        rec = Recording(name="Unknown", recording_id="rec_unk", created_at="2026-01-01T00:00:00Z")
        rec.add_step("fly_to_moon", {"speed": "fast"})

        results = replay_recording(rec)
        assert results[0]["status"] == "error"
        assert "Unknown command" in results[0]["error"]


class TestRecordActionHook:
    """Tests for the record_action hook in interaction commands."""

    def setup_method(self):
        """Clear any active recording before each test."""
        _set_active_recording(None)

    def test_record_action_no_active_recording(self):
        """record_action should be a no-op when no recording is active."""
        record_action("click", {"x": 100, "y": 200})
        assert _get_active_recording() is None

    def test_record_action_with_active_recording(self):
        """record_action should add a step when recording is active."""
        rec = Recording(name="Test", recording_id="rec_test", created_at="2026-01-01T00:00:00Z")
        _set_active_recording(rec)
        record_action("click", {"x": 100, "y": 200})
        assert len(rec.steps) == 1
        assert rec.steps[0].command == "click"
        _set_active_recording(None)


class TestRecordCLI:
    """Tests for record CLI commands."""

    def test_record_start(self):
        runner = CliRunner()
        result = runner.invoke(main, ["record", "start", "--name", "My Test", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["name"] == "My Test"
        assert "recording_id" in data
        # Clean up
        _set_active_recording(None)

    def test_record_start_already_active(self):
        _set_active_recording(
            Recording(name="Existing", recording_id="rec_existing", created_at="2026-01-01T00:00:00Z")
        )
        runner = CliRunner()
        result = runner.invoke(main, ["record", "start", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "RECORDING_ACTIVE"
        _set_active_recording(None)

    def test_record_stop_no_active(self):
        runner = CliRunner()
        result = runner.invoke(main, ["record", "stop", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["success"] is False
        assert data["error"]["code"] == "NO_RECORDING"

    def test_record_list_empty(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.list_recordings", return_value=[]):
            result = runner.invoke(main, ["record", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["recordings"] == []

    def test_record_show_not_found(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", side_effect=FileNotFoundError("Recording not found: rec_x")):
            result = runner.invoke(main, ["record", "show", "rec_x", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["error"]["code"] == "NOT_FOUND"

    def test_record_show_success(self, sample_recording):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", return_value=sample_recording):
            result = runner.invoke(main, ["record", "show", "rec_20260321_020000", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["step_count"] == 3

    def test_record_play_dry_run(self, sample_recording):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", return_value=sample_recording):
            result = runner.invoke(main, ["record", "play", "rec_20260321_020000", "--dry-run", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["steps_played"] == 3

    def test_record_play_invalid_speed(self):
        runner = CliRunner()
        result = runner.invoke(main, ["record", "play", "rec_x", "--speed", "0", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["error"]["code"] == "INVALID_INPUT"

    def test_record_play_not_found(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", side_effect=FileNotFoundError("Recording not found: rec_x")):
            result = runner.invoke(main, ["record", "play", "rec_x", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["error"]["code"] == "NOT_FOUND"

    def test_record_delete_not_found(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.delete_recording", return_value=False):
            result = runner.invoke(main, ["record", "delete", "rec_x", "--yes", "--json"])
        assert result.exit_code != 0
        data = json.loads(result.output)
        assert data["error"]["code"] == "NOT_FOUND"

    def test_record_delete_success(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.delete_recording", return_value=True):
            result = runner.invoke(main, ["record", "delete", "rec_x", "--yes", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

    def test_record_play_empty_recording(self):
        empty_rec = Recording(name="Empty", recording_id="rec_empty", created_at="2026-01-01T00:00:00Z")
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", return_value=empty_rec):
            result = runner.invoke(main, ["record", "play", "rec_empty", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["steps_played"] == 0


class TestRecordPlainText:
    """Tests for record CLI plain-text output."""

    def test_record_start_plain(self):
        runner = CliRunner()
        result = runner.invoke(main, ["record", "start", "--name", "Plain Test"])
        assert result.exit_code == 0
        assert "Recording started" in result.output
        assert "Plain Test" in result.output
        _set_active_recording(None)

    def test_record_list_no_recordings(self):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.list_recordings", return_value=[]):
            result = runner.invoke(main, ["record", "list"])
        assert result.exit_code == 0
        assert "No recordings found" in result.output

    def test_record_show_plain(self, sample_recording):
        runner = CliRunner()
        with patch("naturo.cli.record_cmd.load_recording", return_value=sample_recording):
            result = runner.invoke(main, ["record", "show", "rec_20260321_020000"])
        assert result.exit_code == 0
        assert "Test Recording" in result.output
        assert "click" in result.output
        assert "type" in result.output
        assert "press" in result.output
