"""CLI commands for action recording and replay.

Provides record start/stop/list/show/play/delete commands
for recording and replaying user action sequences.
"""
from __future__ import annotations

import json as json_module
import sys
import time
from datetime import datetime, timezone

import click

from naturo.cli.error_helpers import json_error as _json_error_str
from naturo.recording import (
    Recording,
    generate_recording_id,
    save_recording,
    load_recording,
    list_recordings,
    delete_recording,
    replay_recording,
)


# Module-level active recording state
_active_recording: Recording | None = None


def _get_active_recording() -> Recording | None:
    """Get the currently active recording, if any.

    Returns:
        The active Recording instance, or None.
    """
    return _active_recording


def _set_active_recording(rec: Recording | None) -> None:
    """Set or clear the active recording.

    Args:
        rec: Recording instance to set as active, or None to clear.
    """
    global _active_recording
    _active_recording = rec


def record_action(command: str, args: dict, duration_ms: float = 0.0) -> None:
    """Record an action step if recording is active.

    Called by other CLI commands to record their actions.

    Args:
        command: The naturo command name (click, type, press, etc.).
        args: Command arguments as a dictionary.
        duration_ms: Execution duration in milliseconds.
    """
    rec = _get_active_recording()
    if rec is not None:
        rec.add_step(command, args, duration_ms)


@click.group()
def record():
    """Record and replay action sequences."""
    pass


@record.command()
@click.option("--name", "-n", default=None, help="Recording name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def start(name, json_output):
    """Start recording actions.

    All subsequent naturo commands (click, type, press, etc.) will be
    recorded until 'naturo record stop' is called.

    Examples:
        naturo record start --name "Login flow"
        naturo record start
    """
    if _get_active_recording() is not None:
        msg = "A recording is already in progress. Stop it first with 'naturo record stop'."
        if json_output:
            click.echo(_json_error_str("RECORDING_ACTIVE", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)

    rec_id = generate_recording_id()
    rec_name = name or f"Recording {rec_id}"
    now = datetime.now(timezone.utc).isoformat()

    rec = Recording(
        name=rec_name,
        recording_id=rec_id,
        created_at=now,
    )
    _set_active_recording(rec)

    if json_output:
        click.echo(json_module.dumps({
            "success": True,
            "recording_id": rec_id,
            "name": rec_name,
            "message": "Recording started",
        }))
    else:
        click.echo(f"Recording started: {rec_name} ({rec_id})")
        click.echo("Run naturo commands to record actions, then 'naturo record stop' to save.")


@record.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def stop(json_output):
    """Stop recording and save the action sequence.

    Saves all recorded actions to a JSON file in ~/.naturo/recordings/.

    Examples:
        naturo record stop
        naturo record stop --json
    """
    rec = _get_active_recording()
    if rec is None:
        msg = "No recording in progress. Start one with 'naturo record start'."
        if json_output:
            click.echo(_json_error_str("NO_RECORDING", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)

    filepath = save_recording(rec)
    step_count = len(rec.steps)
    _set_active_recording(None)

    if json_output:
        click.echo(json_module.dumps({
            "success": True,
            "recording_id": rec.recording_id,
            "name": rec.name,
            "step_count": step_count,
            "path": str(filepath),
            "message": "Recording saved",
        }))
    else:
        click.echo(f"Recording saved: {rec.name}")
        click.echo(f"  ID: {rec.recording_id}")
        click.echo(f"  Steps: {step_count}")
        click.echo(f"  File: {filepath}")


@record.command("list")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def list_cmd(json_output):
    """List all saved recordings.

    Shows recording ID, name, creation date, and step count.

    Examples:
        naturo record list
        naturo record list --json
    """
    try:
        recs = list_recordings()
    except Exception as e:
        if json_output:
            click.echo(_json_error_str("UNKNOWN_ERROR", str(e)))
            sys.exit(1)
        else:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)

    if json_output:
        click.echo(json_module.dumps({
            "success": True,
            "recordings": recs,
        }))
    else:
        if not recs:
            click.echo("No recordings found.")
        else:
            for r in recs:
                click.echo(
                    f"  {r['recording_id']}  {r['name']}  "
                    f"({r['step_count']} steps)  {r['created_at']}"
                )


@record.command()
@click.argument("recording_id")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def show(recording_id, json_output):
    """Show details of a specific recording.

    Displays all recorded steps with their commands and arguments.

    Args:
        recording_id: The recording ID to show (e.g., rec_20260321_020000).

    Examples:
        naturo record show rec_20260321_020000
        naturo record show rec_20260321_020000 --json
    """
    try:
        rec = load_recording(recording_id)
    except FileNotFoundError:
        msg = f"Recording not found: {recording_id}"
        if json_output:
            click.echo(_json_error_str("NOT_FOUND", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)

    if json_output:
        click.echo(json_module.dumps({
            "success": True,
            **rec.to_dict(),
        }))
    else:
        click.echo(f"Recording: {rec.name}")
        click.echo(f"  ID: {rec.recording_id}")
        click.echo(f"  Created: {rec.created_at}")
        click.echo(f"  Steps: {len(rec.steps)}")
        duration = rec.total_duration_ms()
        if duration > 0:
            click.echo(f"  Duration: {duration / 1000:.1f}s")
        click.echo()
        for i, step in enumerate(rec.steps):
            args_str = ", ".join(f"{k}={v!r}" for k, v in step.args.items())
            click.echo(f"  {i + 1}. {step.command}({args_str})")


@record.command()
@click.argument("recording_id")
@click.option("--speed", "-s", type=float, default=1.0,
              help="Playback speed multiplier (default: 1.0)")
@click.option("--dry-run", is_flag=True, help="Print actions without executing")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def play(recording_id, speed, dry_run, json_output):
    """Replay a recorded action sequence.

    Executes all recorded steps with their original timing,
    adjusted by the speed multiplier.

    Args:
        recording_id: The recording ID to replay.

    Examples:
        naturo record play rec_20260321_020000
        naturo record play rec_20260321_020000 --speed 2.0
        naturo record play rec_20260321_020000 --dry-run
    """
    # Validate speed
    if speed <= 0:
        msg = f"--speed must be > 0, got {speed}"
        if json_output:
            click.echo(_json_error_str("INVALID_INPUT", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)

    # Load recording
    try:
        rec = load_recording(recording_id)
    except FileNotFoundError:
        msg = f"Recording not found: {recording_id}"
        if json_output:
            click.echo(_json_error_str("NOT_FOUND", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)

    if not rec.steps:
        msg = "Recording has no steps to replay."
        if json_output:
            click.echo(json_module.dumps({
                "success": True,
                "recording_id": recording_id,
                "steps_played": 0,
                "message": msg,
            }))
        else:
            click.echo(msg)
        return

    if not json_output and not dry_run:
        click.echo(f"Replaying: {rec.name} ({len(rec.steps)} steps, speed={speed}x)")

    def on_step(idx, step, result):
        """Callback for each replayed step."""
        if not json_output:
            status_icon = "✓" if result["status"] == "success" else "✗" if result["status"] == "error" else "⊘"
            args_str = ", ".join(f"{k}={v!r}" for k, v in step.args.items())
            msg_line = f"  {status_icon} {idx + 1}. {step.command}({args_str})"
            if result.get("error"):
                msg_line += f"  — {result['error']}"
            click.echo(msg_line)

    try:
        results = replay_recording(
            rec,
            speed=speed,
            dry_run=dry_run,
            step_callback=on_step if not json_output else None,
        )
    except Exception as e:
        if json_output:
            click.echo(_json_error_str("REPLAY_ERROR", str(e)))
            sys.exit(1)
        else:
            click.echo(f"Error during replay: {e}", err=True)
            sys.exit(1)

    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")

    if json_output:
        click.echo(json_module.dumps({
            "success": error_count == 0,
            "recording_id": recording_id,
            "steps_played": len(results),
            "steps_succeeded": success_count,
            "steps_failed": error_count,
            "results": results,
        }))
        if error_count > 0:
            sys.exit(1)
    else:
        click.echo(f"\nReplay complete: {success_count} succeeded, {error_count} failed")


@record.command()
@click.argument("recording_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def delete(recording_id, yes, json_output):
    """Delete a saved recording.

    Args:
        recording_id: The recording ID to delete.

    Examples:
        naturo record delete rec_20260321_020000
        naturo record delete rec_20260321_020000 --yes
    """
    if not yes and not json_output:
        if not click.confirm(f"Delete recording {recording_id}?"):
            click.echo("Cancelled.")
            return

    deleted = delete_recording(recording_id)
    if deleted:
        if json_output:
            click.echo(json_module.dumps({
                "success": True,
                "recording_id": recording_id,
                "message": "Recording deleted",
            }))
        else:
            click.echo(f"Deleted: {recording_id}")
    else:
        msg = f"Recording not found: {recording_id}"
        if json_output:
            click.echo(_json_error_str("NOT_FOUND", msg))
            sys.exit(1)
        else:
            click.echo(f"Error: {msg}", err=True)
            sys.exit(1)
