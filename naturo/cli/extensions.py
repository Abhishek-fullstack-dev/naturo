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
    Supports HKCU, HKLM, HKCR, HKU, HKCC hives with both short and long names.
    """
    pass


@registry.command(name="get")
@click.argument("key_path")
@click.option("--value", "-v", "value_name", default=None, help="Value name (default: (Default))")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def reg_get(key_path, value_name, json_output):
    """Read a registry value.

    KEY_PATH is the full registry path, e.g. HKCU\\Software\\MyApp.
    """
    import json as json_module
    import sys
    from naturo.cli.error_helpers import emit_error, emit_exception_error

    try:
        from naturo.registry import reg_get as _reg_get
        result = _reg_get(key_path, value_name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="REGISTRY_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"{result['name']}: {result['data']} ({result['type_name']})")


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
    """Write a registry value. Creates the key if it does not exist.

    KEY_PATH is the full registry path, e.g. HKCU\\Software\\MyApp.
    """
    import json as json_module
    import sys
    from naturo.cli.error_helpers import emit_error, emit_exception_error

    try:
        from naturo.registry import reg_set as _reg_set
        result = _reg_set(key_path, value_name, data, reg_type)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="REGISTRY_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Set {result['name']} = {result['data']} ({result['type_name']}) in {result['key']}")


@registry.command(name="list")
@click.argument("key_path")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def reg_list(key_path, json_output):
    """List registry subkeys and values.

    KEY_PATH is the full registry path, e.g. HKCU\\Software.
    """
    import json as json_module
    import sys
    from naturo.cli.error_helpers import emit_error, emit_exception_error

    try:
        from naturo.registry import reg_list as _reg_list
        result = _reg_list(key_path)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="REGISTRY_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        if result["subkeys"]:
            click.echo("Subkeys:")
            for sk in result["subkeys"]:
                click.echo(f"  {sk}")
        if result["values"]:
            click.echo("Values:")
            for v in result["values"]:
                click.echo(f"  {v['name']}: {v['data']} ({v['type_name']})")
        if not result["subkeys"] and not result["values"]:
            click.echo(f"(empty key: {key_path})")


@registry.command()
@click.argument("key_path")
@click.option("--value", "-v", "value_name", default=None, help="Delete specific value (omit to delete key)")
@click.option("--recursive", "-r", is_flag=True, help="Delete key recursively")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def delete(key_path, value_name, recursive, json_output):
    """Delete a registry key or value.

    KEY_PATH is the full registry path. Use --value to delete a specific value,
    or omit to delete the entire key (requires --recursive if subkeys exist).
    """
    import json as json_module
    import sys
    from naturo.cli.error_helpers import emit_error, emit_exception_error

    try:
        from naturo.registry import reg_delete as _reg_delete
        result = _reg_delete(key_path, value_name, recursive)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="REGISTRY_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        if result["deleted"] == "value":
            click.echo(f"Deleted value '{result['value']}' from {result['key']}")
        else:
            click.echo(f"Deleted key {result['key']}")


@registry.command()
@click.argument("key_path")
@click.argument("query")
@click.option("--depth", type=int, default=5, help="Maximum search depth (default: 5)")
@click.option("--max-results", type=int, default=50, help="Maximum results (default: 50)")
@click.option("--keys/--no-keys", default=True, help="Search key names")
@click.option("--values/--no-values", default=True, help="Search value names")
@click.option("--data/--no-data", default=False, help="Search value data")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def search(key_path, query, depth, max_results, keys, values, data, json_output):
    """Search registry keys, value names, or data.

    KEY_PATH is the starting path, QUERY is the search string (case-insensitive).
    """
    import json as json_module
    import sys
    from naturo.cli.error_helpers import emit_error, emit_exception_error

    if depth < 1 or depth > 20:
        emit_error("INVALID_INPUT", f"--depth must be between 1 and 20, got {depth}", json_output)
        return
    if max_results < 1:
        emit_error("INVALID_INPUT", f"--max-results must be >= 1, got {max_results}", json_output)
        return
    if not query.strip():
        emit_error("INVALID_INPUT", "Search query cannot be empty", json_output)
        return

    try:
        from naturo.registry import reg_search as _reg_search
        result = _reg_search(
            key_path, query,
            max_depth=depth, max_results=max_results,
            search_keys=keys, search_values=values, search_data=data,
        )
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="REGISTRY_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        if not result["results"]:
            click.echo(f"No results for '{query}' in {key_path}")
        else:
            for r in result["results"]:
                if r["type"] == "key":
                    click.echo(f"[KEY] {r['key']}")
                else:
                    click.echo(f"[VAL] {r['key']}\\{r['name']} = {r['data']} ({r['value_type']})")
            if result["truncated"]:
                click.echo(f"(truncated at {max_results} results)")


# ── service ─────────────────────────────────────


@click.group()
def service():
    """Windows Service management (Windows-specific).

    Start, stop, query, and restart Windows services.
    """
    pass


@service.command(name="list")
@click.option("--state", type=click.Choice(["running", "stopped", "all"]),
              default="all", help="Filter by state")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_list(state, json_output):
    """List Windows services.

    Filter by state: running, stopped, or all (default).
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.service import service_list as _service_list
        result = _service_list(state)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="SERVICE_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        services = result["services"]
        if not services:
            click.echo(f"No {state} services found.")
        else:
            for svc in services:
                state_str = svc.get("state", "unknown")
                pid = svc.get("pid", "")
                pid_str = f" (PID {pid})" if pid else ""
                click.echo(f"  {svc['name']:<40} {state_str:<12}{pid_str}")
            click.echo(f"\n{result['count']} service(s)")


@service.command(name="start")
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_start(name, json_output):
    """Start a Windows service.

    NAME is the service short name (e.g., 'Spooler', 'wuauserv').
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.service import service_start as _service_start
        result = _service_start(name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="SERVICE_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Service '{result['name']}' started.")


@service.command(name="stop")
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def svc_stop(name, json_output):
    """Stop a Windows service.

    NAME is the service short name (e.g., 'Spooler', 'wuauserv').
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.service import service_stop as _service_stop
        result = _service_stop(name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="SERVICE_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Service '{result['name']}' stopped.")


@service.command()
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def restart(name, json_output):
    """Restart a Windows service (stop then start).

    NAME is the service short name (e.g., 'Spooler', 'wuauserv').
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.service import service_restart as _service_restart
        result = _service_restart(name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="SERVICE_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Service '{result['name']}' restarted.")


@service.command()
@click.argument("name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def status(name, json_output):
    """Get detailed status of a Windows service.

    NAME is the service short name (e.g., 'Spooler', 'wuauserv').
    Shows state, PID, start type, binary path, and dependencies.
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.service import service_status as _service_status
        result = _service_status(name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="SERVICE_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Service: {result.get('name', name)}")
        if "display_name" in result:
            click.echo(f"  Display Name: {result['display_name']}")
        click.echo(f"  State: {result.get('state', 'unknown')}")
        if "pid" in result:
            click.echo(f"  PID: {result['pid']}")
        if "start_type" in result:
            click.echo(f"  Start Type: {result['start_type']}")
        if "binary_path" in result:
            click.echo(f"  Binary Path: {result['binary_path']}")
        if "run_as" in result:
            click.echo(f"  Run As: {result['run_as']}")
        if result.get("dependencies"):
            click.echo(f"  Dependencies: {', '.join(result['dependencies'])}")
