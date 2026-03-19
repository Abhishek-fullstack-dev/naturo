"""Windows-specific extensions: excel, java, sap, registry, service."""
import click

# ── excel ───────────────────────────────────────


@click.group()
def excel():
    """Excel COM automation (Windows-specific).

    Automate Excel workbooks via COM interface — read/write cells, run macros, etc.
    """
    pass


@excel.command()
@click.argument("path", type=click.Path())
@click.option("--visible", is_flag=True, help="Show Excel window")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def open_workbook(path, visible, json_output):
    """Open an Excel workbook."""
    click.echo("Not implemented yet — coming in Phase 5")


@excel.command()
@click.argument("cell")
@click.option("--sheet", help="Sheet name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def read(cell, sheet, json_output):
    """Read a cell or range value."""
    click.echo("Not implemented yet — coming in Phase 5")


@excel.command()
@click.argument("cell")
@click.argument("value")
@click.option("--sheet", help="Sheet name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def write(cell, value, sheet, json_output):
    """Write a value to a cell or range."""
    click.echo("Not implemented yet — coming in Phase 5")


@excel.command()
@click.argument("macro_name")
@click.option("--args", multiple=True, help="Macro arguments")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def run_macro(macro_name, args, json_output):
    """Run a VBA macro."""
    click.echo("Not implemented yet — coming in Phase 5")


# ── java ────────────────────────────────────────


@click.group()
def java():
    """Java application automation via Java Access Bridge (Windows-specific).

    Automate Java Swing/AWT applications using the Java Access Bridge API.
    """
    pass


@java.command(name="list")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def java_list(json_output):
    """List Java applications with Access Bridge enabled."""
    click.echo("Not implemented yet — coming in Phase 5")


@java.command()
@click.option("--pid", type=int, help="Java process ID")
@click.option("--title", help="Window title")
@click.option("--depth", type=int, default=5, help="Tree depth")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def tree(pid, title, depth, json_output):
    """Inspect Java UI element tree."""
    click.echo("Not implemented yet — coming in Phase 5")


@java.command(name="click")
@click.argument("query")
@click.option("--pid", type=int, help="Java process ID")
@click.option("--title", help="Window title")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def java_click(query, pid, title, json_output):
    """Click a Java UI element."""
    click.echo("Not implemented yet — coming in Phase 5")


# ── sap ─────────────────────────────────────────


@click.group()
def sap():
    """SAP GUI Scripting automation (Windows-specific).

    Automate SAP GUI for Windows using the SAP Scripting API.
    """
    pass


@sap.command(name="list")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def sap_list(json_output):
    """List SAP GUI sessions."""
    click.echo("Not implemented yet — coming in Phase 5")


@sap.command()
@click.argument("transaction")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def run(transaction, session, json_output):
    """Run a SAP transaction code."""
    click.echo("Not implemented yet — coming in Phase 5")


@sap.command(name="get")
@click.argument("field_id")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def sap_get(field_id, session, json_output):
    """Get a SAP GUI field value."""
    click.echo("Not implemented yet — coming in Phase 5")


@sap.command(name="set")
@click.argument("field_id")
@click.argument("value")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def sap_set(field_id, value, session, json_output):
    """Set a SAP GUI field value."""
    click.echo("Not implemented yet — coming in Phase 5")


# ── registry ────────────────────────────────────


@click.group()
def registry():
    """Windows Registry operations (Windows-specific).

    Read, write, and manage Windows Registry keys and values.
    """
    pass


@registry.command(name="get")
@click.argument("key_path")
@click.option("--value", "-v", "value_name", help="Value name (default: (Default))")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def reg_get(key_path, value_name, json_output):
    """Read a registry value."""
    click.echo("Not implemented yet — coming in Phase 5")


@registry.command(name="set")
@click.argument("key_path")
@click.option("--value", "-v", "value_name", required=True, help="Value name")
@click.option("--data", "-d", required=True, help="Value data")
@click.option("--type", "-t", "reg_type",
              type=click.Choice(["REG_SZ", "REG_DWORD", "REG_QWORD", "REG_BINARY",
                                 "REG_EXPAND_SZ", "REG_MULTI_SZ"]),
              default="REG_SZ", help="Registry value type")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def reg_set(key_path, value_name, data, reg_type, json_output):
    """Write a registry value."""
    click.echo("Not implemented yet — coming in Phase 5")


@registry.command(name="list")
@click.argument("key_path")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def reg_list(key_path, json_output):
    """List registry subkeys and values."""
    click.echo("Not implemented yet — coming in Phase 5")


@registry.command()
@click.argument("key_path")
@click.option("--value", "-v", "value_name", help="Delete specific value (omit to delete key)")
@click.option("--recursive", "-r", is_flag=True, help="Delete key recursively")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def delete(key_path, value_name, recursive, json_output):
    """Delete a registry key or value."""
    click.echo("Not implemented yet — coming in Phase 5")


# ── service ─────────────────────────────────────


@click.group()
def service():
    """Windows Service management (Windows-specific).

    Start, stop, and query Windows services.
    """
    pass


@service.command(name="list")
@click.option("--state", type=click.Choice(["running", "stopped", "all"]),
              default="all", help="Filter by state")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_list(state, json_output):
    """List Windows services."""
    click.echo("Not implemented yet — coming in Phase 5")


@service.command(name="start")
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_start(name, json_output):
    """Start a Windows service."""
    click.echo("Not implemented yet — coming in Phase 5")


@service.command(name="stop")
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_stop(name, json_output):
    """Stop a Windows service."""
    click.echo("Not implemented yet — coming in Phase 5")


@service.command()
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def restart(name, json_output):
    """Restart a Windows service."""
    click.echo("Not implemented yet — coming in Phase 5")


@service.command()
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def status(name, json_output):
    """Get status of a Windows service."""
    click.echo("Not implemented yet — coming in Phase 5")
