"""Naturo CLI — Windows desktop automation."""
import click
from naturo.version import __version__


@click.group()
@click.version_option(__version__, prog_name="naturo")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
@click.pass_context
def main(ctx, json_output, verbose):
    """Naturo — Windows desktop automation engine.

    See, click, type, automate. Built for AI agents.
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["verbose"] = verbose


@main.command()
def version():
    """Show version info including native core."""
    from naturo.bridge import NaturoCore
    click.echo(f"naturo {__version__}")
    try:
        core = NaturoCore()
        click.echo(f"naturo_core.dll {core.version()}")
    except Exception as e:
        click.echo(f"naturo_core.dll not available ({e})")


# Placeholder commands — will be implemented in later phases
@main.command()
@click.option("--window", "-w", help="Window title pattern")
@click.option("--screen", "-s", type=int, help="Screen index")
@click.option("--output", "-o", default="capture.png", help="Output file")
def capture(window, screen, output):
    """Capture screenshot of screen or window."""
    click.echo("Not implemented yet — coming in Phase 1")


@main.command(name="list")
@click.option("--type", "-t", "list_type", default="windows", type=click.Choice(["windows", "processes"]))
def list_cmd(list_type):
    """List windows or processes."""
    click.echo("Not implemented yet — coming in Phase 1")


@main.command()
@click.option("--window", "-w", help="Window title pattern")
@click.option("--depth", "-d", type=int, default=3, help="Tree depth")
def see(window, depth):
    """Inspect UI element tree."""
    click.echo("Not implemented yet — coming in Phase 1")


@main.command()
@click.argument("target")
def click_cmd(target):
    """Click on element or coordinates."""
    click.echo("Not implemented yet — coming in Phase 2")


# Register click_cmd as 'click' command
main.add_command(click_cmd, "click")


@main.command(name="type")
@click.argument("text")
def type_cmd(text):
    """Type text."""
    click.echo("Not implemented yet — coming in Phase 2")


@main.command()
@click.argument("keys")
def press(keys):
    """Press key combination."""
    click.echo("Not implemented yet — coming in Phase 2")


@main.command()
@click.argument("selector")
def find(selector):
    """Find UI element by selector."""
    click.echo("Not implemented yet — coming in Phase 2")


if __name__ == "__main__":
    main()
