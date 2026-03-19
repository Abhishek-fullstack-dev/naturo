"""Core commands: capture, list, see, learn, tools."""
import click

# ── capture ─────────────────────────────────────


@click.group()
def capture():
    """Capture screenshots, video, or watch for changes."""
    pass


@capture.command()
@click.option("--app", help="Application name to capture")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--screen", "-s", type=int, help="Screen/monitor index")
@click.option("--path", "-p", default="capture.png", help="Output file path")
@click.option("--format", "fmt", type=click.Choice(["png", "jpg", "bmp"]), default="png", help="Image format")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def live(app, window_title, hwnd, screen, path, fmt, json_output):
    """Capture a live screenshot."""
    click.echo("Not implemented yet — coming in Phase 1")


@capture.command()
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--screen", "-s", type=int, help="Screen/monitor index")
@click.option("--duration", "-d", type=float, default=5.0, help="Duration in seconds")
@click.option("--fps", type=int, default=30, help="Frames per second")
@click.option("--path", "-p", default="capture.mp4", help="Output file path")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def video(app, window_title, hwnd, screen, duration, fps, path, json_output):
    """Record video of screen or window."""
    click.echo("Not implemented yet — coming in Phase 3")


@capture.command()
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--interval", type=float, default=1.0, help="Check interval in seconds")
@click.option("--timeout", type=float, help="Max watch time in seconds")
@click.option("--path", "-p", help="Output directory")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def watch(app, window_title, hwnd, interval, timeout, path, json_output):
    """Watch for screen changes and capture on change."""
    click.echo("Not implemented yet — coming in Phase 3")


# ── list ────────────────────────────────────────


@click.group("list")
def list_cmd():
    """List apps, windows, screens, or permissions."""
    pass


@list_cmd.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def apps(json_output):
    """List running applications."""
    click.echo("Not implemented yet — coming in Phase 1")


@list_cmd.command()
@click.option("--app", help="Filter by application name")
@click.option("--process-name", help="Filter by process name")
@click.option("--pid", type=int, help="Filter by process ID")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def windows(app, process_name, pid, json_output):
    """List open windows."""
    click.echo("Not implemented yet — coming in Phase 1")


@list_cmd.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def screens(json_output):
    """List connected screens/monitors."""
    click.echo("Not implemented yet — coming in Phase 1")


@list_cmd.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def permissions(json_output):
    """List automation permissions status (UIAccess, admin, etc.)."""
    click.echo("Not implemented yet — coming in Phase 1")


# ── see ─────────────────────────────────────────


@click.command()
@click.option("--app", help="Application name")
@click.option("--window-title", help="Window title pattern")
@click.option("--hwnd", type=int, help="Window handle (HWND)")
@click.option("--pid", type=int, help="Process ID")
@click.option(
    "--mode",
    type=click.Choice(["full", "interactive", "fast"]),
    default="full",
    help="Analysis mode: full (all elements), interactive (clickable only), fast (quick scan)",
)
@click.option("--path", "-p", help="Save screenshot to path")
@click.option("--annotate", is_flag=True, help="Annotate screenshot with element labels")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def see(app, window_title, hwnd, pid, mode, path, annotate, json_output):
    """Capture screenshot and analyze UI elements.

    Combines screen capture with UI tree inspection.
    """
    click.echo("Not implemented yet — coming in Phase 1")


# ── learn ───────────────────────────────────────


@click.command()
@click.argument("topic", required=False)
def learn(topic):
    """Show usage guide and tutorials.

    Without TOPIC, shows an overview. With TOPIC, shows detailed help.
    """
    topics = {
        "capture": "Capture screenshots, video, or watch for changes.",
        "interaction": "Click, type, press, hotkey, scroll, drag, move, paste.",
        "system": "App, window, menu, clipboard, dialog, open.",
        "windows": "Windows-specific: taskbar, tray, desktop, registry, service.",
        "extensions": "Enterprise: excel, java, sap automation.",
        "ai": "AI agent and MCP server integration.",
    }
    if topic and topic in topics:
        click.echo(f"\n  {topic}: {topics[topic]}\n")
    else:
        click.echo("\nNaturo — Windows desktop automation engine\n")
        click.echo("Available topics:")
        for t, desc in topics.items():
            click.echo(f"  {t:15s} {desc}")
        click.echo("\nRun: naturo learn <topic> for details.")


# ── tools ───────────────────────────────────────


@click.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def tools(json_output):
    """List available automation tools and backends.

    Shows which native backends are available (UIA, MSAA, Java Bridge, etc.).
    """
    click.echo("Not implemented yet — coming in Phase 1")
