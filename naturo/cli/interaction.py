"""Interaction commands: click, type, press, hotkey, scroll, drag, move, paste."""
import click

# ── click ───────────────────────────────────────


@click.command("click")
@click.argument("query", required=False)
@click.option("--on", "on_text", help="Text/element to click on")
@click.option("--id", "element_id", help="Automation element ID")
@click.option("--coords", nargs=2, type=int, help="X Y coordinates")
@click.option("--double", is_flag=True, help="Double-click")
@click.option("--right", is_flag=True, help="Right-click")
@click.option("--app", help="Application name")
@click.option("--pid", type=int, help="Process ID")
@click.option("--window-title", help="Window title pattern")
@click.option("--window-id", "--hwnd", "window_id", type=int, help="Window handle (HWND)")
@click.option("--wait-for", type=float, help="Wait for element (seconds)")
@click.option(
    "--input-mode",
    type=click.Choice(["normal", "hardware", "hook"]),
    default="normal",
    help="Input method: normal (SendInput), hardware (Phys32 driver), hook (MinHook injection)",
)
@click.option("--process-name", help="Filter by process name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def click_cmd(query, on_text, element_id, coords, double, right, app, pid,
              window_title, window_id, wait_for, input_mode, process_name,
              json_output):
    """Click on a UI element, text, or coordinates.

    QUERY is optional text to find and click on. Use --on, --id, or --coords
    for alternative targeting.

    Input modes (Windows-specific):
      normal   — SendInput API (default, works for most apps)
      hardware — Phys32 driver (bypasses software input filtering)
      hook     — MinHook injection (for protected/game apps)
    """
    click.echo("Not implemented yet — coming in Phase 2")


# ── type ────────────────────────────────────────


@click.command("type")
@click.argument("text", required=False)
@click.option("--delay", type=float, help="Delay between keystrokes (ms)")
@click.option(
    "--profile",
    type=click.Choice(["human", "linear"]),
    default="linear",
    help="Typing profile: human (variable delay), linear (constant delay)",
)
@click.option("--wpm", type=int, help="Words per minute (for human profile)")
@click.option("--return", "press_return", is_flag=True, help="Press Return after typing")
@click.option("--tab", "tab_count", type=int, help="Press Tab N times after typing")
@click.option("--escape", is_flag=True, help="Press Escape after typing")
@click.option("--delete", is_flag=True, help="Delete existing text first")
@click.option("--clear", is_flag=True, help="Select all + delete before typing")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option(
    "--input-mode",
    type=click.Choice(["normal", "hardware", "hook"]),
    default="normal",
    help="Input method: normal (SendInput), hardware (Phys32), hook (MinHook)",
)
@click.option("--process-name", help="Filter by process name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def type_cmd(text, delay, profile, wpm, press_return, tab_count, escape,
             delete, clear, app, window_title, hwnd, input_mode,
             process_name, json_output):
    """Type text with configurable speed and profile.

    TEXT is the string to type. Supports human-like variable-speed typing
    and Windows-specific input modes.
    """
    click.echo("Not implemented yet — coming in Phase 2")


# ── press ───────────────────────────────────────


@click.command()
@click.argument("key")
@click.option("--count", "-n", type=int, default=1, help="Number of times to press")
@click.option("--delay", type=float, help="Delay between presses (ms)")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option(
    "--input-mode",
    type=click.Choice(["normal", "hardware", "hook"]),
    default="normal",
    help="Input method",
)
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def press(key, count, delay, app, window_title, hwnd, input_mode, json_output):
    """Press a single key or key sequence.

    KEY can be a key name (enter, tab, escape, f1, etc.) or a character.
    """
    click.echo("Not implemented yet — coming in Phase 2")


# ── hotkey ──────────────────────────────────────


@click.command()
@click.argument("keys", required=False)
@click.option("--keys", "keys_option", multiple=True, help="Key names (repeatable)")
@click.option("--hold-duration", type=float, help="Hold duration in ms")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option(
    "--input-mode",
    type=click.Choice(["normal", "hardware", "hook"]),
    default="normal",
    help="Input method",
)
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def hotkey(keys, keys_option, hold_duration, app, window_title, hwnd,
           input_mode, json_output):
    """Press a hotkey combination.

    KEYS as a string like "ctrl+c" or "alt+f4". Or use --keys for each key.
    """
    click.echo("Not implemented yet — coming in Phase 2")


# ── scroll ──────────────────────────────────────


@click.command()
@click.option(
    "--direction", "-d",
    type=click.Choice(["up", "down", "left", "right"]),
    default="down",
    help="Scroll direction",
)
@click.option("--amount", "-a", type=int, default=3, help="Scroll amount (lines/clicks)")
@click.option("--on", "on_text", help="Element to scroll on")
@click.option("--smooth", is_flag=True, help="Smooth scrolling")
@click.option("--delay", type=float, help="Delay between scroll steps (ms)")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def scroll(direction, amount, on_text, smooth, delay, app, window_title,
           hwnd, json_output):
    """Scroll in a direction."""
    click.echo("Not implemented yet — coming in Phase 2")


# ── drag ────────────────────────────────────────


@click.command()
@click.option("--from", "from_text", help="Source element text")
@click.option("--from-coords", nargs=2, type=int, help="Source X Y coordinates")
@click.option("--to", "to_text", help="Destination element text")
@click.option("--to-coords", nargs=2, type=int, help="Destination X Y coordinates")
@click.option("--duration", type=float, default=0.5, help="Drag duration (seconds)")
@click.option("--steps", type=int, default=10, help="Interpolation steps")
@click.option("--modifiers", multiple=True, help="Modifier keys to hold (ctrl, shift, alt)")
@click.option(
    "--profile",
    type=click.Choice(["linear", "ease-in-out"]),
    default="linear",
    help="Motion profile",
)
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def drag(from_text, from_coords, to_text, to_coords, duration, steps,
         modifiers, profile, app, window_title, hwnd, json_output):
    """Drag from one element/position to another."""
    click.echo("Not implemented yet — coming in Phase 2")


# ── move ────────────────────────────────────────


@click.command()
@click.option("--to", "to_text", help="Target element text")
@click.option("--coords", nargs=2, type=int, help="Target X Y coordinates")
@click.option("--id", "element_id", help="Target element automation ID")
@click.option("--duration", type=float, default=0.0, help="Move duration (seconds)")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def move(to_text, coords, element_id, duration, app, window_title, hwnd,
         json_output):
    """Move the mouse cursor to a target element or coordinates."""
    click.echo("Not implemented yet — coming in Phase 2")


# ── paste ───────────────────────────────────────


@click.command()
@click.argument("text", required=False)
@click.option("--file", "file_path", type=click.Path(exists=True), help="File to paste from")
@click.option("--restore", is_flag=True, default=True, help="Restore clipboard after paste")
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def paste(text, file_path, restore, app, window_title, hwnd, json_output):
    """Set clipboard content and paste (Ctrl+V), then restore clipboard.

    TEXT is the string to paste. Or use --file to read from a file.
    """
    click.echo("Not implemented yet — coming in Phase 2")
