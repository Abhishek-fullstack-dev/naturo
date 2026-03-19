"""AI commands: agent, mcp."""
import click

# ── agent ───────────────────────────────────────


@click.command()
@click.argument("instruction")
@click.option("--app", help="Target application")
@click.option("--window-title", help="Target window")
@click.option("--model", help="AI model to use")
@click.option("--max-steps", type=int, default=10, help="Max automation steps")
@click.option("--dry-run", is_flag=True, help="Plan but don't execute")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def agent(instruction, app, window_title, model, max_steps, dry_run, json_output):
    """Execute a natural language automation instruction.

    Uses AI vision + UI automation to complete tasks described in plain language.

    Example: naturo agent "Open Chrome and search for weather"
    """
    click.echo("Not implemented yet — coming in Phase 4")


# ── mcp ─────────────────────────────────────────


@click.group()
def mcp():
    """MCP (Model Context Protocol) server operations."""
    pass


@mcp.command()
@click.option("--host", default="localhost", help="Bind host")
@click.option("--port", type=int, default=3100, help="Bind port")
@click.option("--transport", type=click.Choice(["stdio", "sse", "streamable-http"]),
              default="stdio", help="Transport protocol")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def start(host, port, transport, json_output):
    """Start the MCP server."""
    click.echo("Not implemented yet — coming in Phase 4")


@mcp.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def status(json_output):
    """Show MCP server status."""
    click.echo("Not implemented yet — coming in Phase 4")


@mcp.command()
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def stop(json_output):
    """Stop the MCP server."""
    click.echo("Not implemented yet — coming in Phase 4")
