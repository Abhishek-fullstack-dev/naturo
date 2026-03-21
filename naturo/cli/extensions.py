"""Windows-specific extensions: excel, java, sap, registry, service, electron."""
import json as json_module
import sys

import click


def _not_implemented(name: str, phase: str, json_output: bool) -> None:
    """Emit a NOT_IMPLEMENTED error with correct exit code.

    Args:
        name: Command name for the error message.
        phase: Phase identifier (e.g., '5C.1').
        json_output: Whether to emit JSON output.
    """
    msg = f"{name} is not implemented yet — coming in Phase {phase}"
    if json_output:
        click.echo(json_module.dumps({
            "success": False,
            "error": {"code": "NOT_IMPLEMENTED", "message": msg},
        }))
    else:
        click.echo(f"Error: {msg}", err=True)
    sys.exit(1)


# ── excel ───────────────────────────────────────


@click.group(hidden=True)
def excel():
    """Excel COM automation (Windows-specific).

    Automate Excel workbooks via COM interface — read/write cells, run macros,
    list sheets, and inspect used ranges.

    Requires Microsoft Excel and pywin32 (pip install pywin32).
    """
    pass


@excel.command("open")
@click.argument("path", type=click.Path())
@click.option("--visible", is_flag=True, help="Show Excel window")
@click.option("--read-only", is_flag=True, help="Open in read-only mode")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def excel_open_cmd(path, visible, read_only, json_output):
    """Open an Excel workbook and show its info.

    PATH is the workbook file (.xlsx, .xls, .xlsm).

    Examples:

      naturo excel open report.xlsx

      naturo excel open "C:\\Data\\sales.xlsx" --visible --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.excel import excel_open
        result = excel_open(path, visible=visible, read_only=read_only)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Opened: {result['path']}")
        click.echo(f"Sheets ({result['sheet_count']}): {', '.join(result['sheets'])}")
        click.echo(f"Active: {result['active_sheet']}")


@excel.command()
@click.argument("path", type=click.Path())
@click.argument("cell")
@click.option("--sheet", help="Sheet name (default: active sheet)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def read(path, cell, sheet, json_output):
    """Read a cell or range value from a workbook.

    PATH is the workbook file. CELL is a cell reference (A1) or range (A1:C10).

    Examples:

      naturo excel read report.xlsx A1

      naturo excel read data.xlsx "A1:D100" --sheet "Sales" --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.excel import excel_read
        result = excel_read(path, cell, sheet=sheet)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        value = result["value"]
        if isinstance(value, list):
            # Range result — format as table
            for row in value:
                click.echo("\t".join(str(c) if c is not None else "" for c in row))
        else:
            click.echo(f"{result['cell']} ({result['sheet']}): {value}")


@excel.command()
@click.argument("path", type=click.Path())
@click.argument("cell")
@click.argument("value")
@click.option("--sheet", help="Sheet name (default: active sheet)")
@click.option("--create", is_flag=True, help="Create workbook if it doesn't exist")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def write(path, cell, value, sheet, create, json_output):
    """Write a value to a cell in a workbook.

    PATH is the workbook file. CELL is the target cell (e.g., A1).
    VALUE is the data to write.

    Examples:

      naturo excel write report.xlsx A1 "Hello World"

      naturo excel write data.xlsx B2 42 --sheet "Numbers" --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    # Try to convert numeric values
    write_value: Any = value
    try:
        write_value = int(value)
    except ValueError:
        try:
            write_value = float(value)
        except ValueError:
            pass

    try:
        from naturo.excel import excel_write
        result = excel_write(path, cell, write_value, sheet=sheet, create=create)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Wrote to {result['cell']} ({result['sheet']}): {write_value}")


@excel.command("list-sheets")
@click.argument("path", type=click.Path())
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def list_sheets(path, json_output):
    """List all sheets in a workbook.

    Examples:

      naturo excel list-sheets report.xlsx

      naturo excel list-sheets data.xlsx --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.excel import excel_list_sheets
        result = excel_list_sheets(path)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Workbook: {result['path']}")
        for i, name in enumerate(result["sheets"], 1):
            active = " (active)" if name == result["active_sheet"] else ""
            click.echo(f"  {i}. {name}{active}")


@excel.command("run-macro")
@click.argument("path", type=click.Path())
@click.argument("macro_name")
@click.option("--arg", "macro_args", multiple=True, help="Macro argument (repeatable)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def run_macro(path, macro_name, macro_args, json_output):
    """Run a VBA macro in a workbook.

    PATH is the workbook file (.xlsm). MACRO_NAME is the macro to run.

    Examples:

      naturo excel run-macro report.xlsm "Module1.FormatReport"

      naturo excel run-macro data.xlsm "UpdateData" --arg "2024" --arg "Q1" --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.excel import excel_run_macro
        result = excel_run_macro(path, macro_name, args=list(macro_args) or None)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Macro '{result['macro']}' executed.")
        if result.get("result") is not None:
            click.echo(f"Result: {result['result']}")


@excel.command("info")
@click.argument("path", type=click.Path())
@click.option("--sheet", help="Sheet name (default: active sheet)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def excel_info(path, sheet, json_output):
    """Get used range info for a worksheet.

    Shows the dimensions of the data area in the sheet.

    Examples:

      naturo excel info report.xlsx

      naturo excel info data.xlsx --sheet "Sales" --json
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.excel import excel_get_range_info
        result = excel_get_range_info(path, sheet=sheet)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="EXCEL_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"Sheet: {result['sheet']}")
        click.echo(f"Used range: {result['used_range']}")
        click.echo(f"Rows: {result['rows']}, Columns: {result['columns']}")


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
    _not_implemented("java list", "5B.3", json_output)


@java.command()
@click.option("--pid", type=int, help="Java process ID")
@click.option("--title", help="Window title")
@click.option("--depth", type=int, default=5, help="Tree depth")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def tree(pid, title, depth, json_output):
    """Inspect Java UI element tree."""
    _not_implemented("java tree", "5B.3", json_output)


@java.command(name="click")
@click.argument("query")
@click.option("--pid", type=int, help="Java process ID")
@click.option("--title", help="Window title")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def java_click(query, pid, title, json_output):
    """Click a Java UI element."""
    _not_implemented("java click", "5B.3", json_output)


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
    _not_implemented("sap list", "5B.4", json_output)


@sap.command()
@click.argument("transaction")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def run(transaction, session, json_output):
    """Run a SAP transaction code."""
    _not_implemented("sap run", "5B.4", json_output)


@sap.command(name="get")
@click.argument("field_id")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def sap_get(field_id, session, json_output):
    """Get a SAP GUI field value."""
    _not_implemented("sap get", "5B.4", json_output)


@sap.command(name="set")
@click.argument("field_id")
@click.argument("value")
@click.option("--session", type=int, default=0, help="Session index")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def sap_set(field_id, value, session, json_output):
    """Set a SAP GUI field value."""
    _not_implemented("sap set", "5B.4", json_output)


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


# ── electron ────────────────────────────────────


@click.group()
def electron():
    """Electron/CEF application support (Windows-specific).

    Detect and automate Electron-based apps (VS Code, Slack, Discord, etc.)
    via Chrome DevTools Protocol.
    """
    pass


@electron.command(name="detect")
@click.argument("app_name")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def electron_detect(app_name, json_output):
    """Detect if an application is Electron-based.

    APP_NAME is the application name (e.g., 'Slack', 'Discord', 'Code').
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.electron import detect_electron_app
        result = detect_electron_app(app_name)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="ELECTRON_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        if result["is_electron"]:
            click.echo(f"  {result['app_name']}: Electron app ✓")
            if result["debug_port"]:
                click.echo(f"  Debug port: {result['debug_port']}")
            else:
                click.echo("  Not running with remote debugging.")
            click.echo(f"  Main PID: {result.get('main_pid', 'N/A')}")
            click.echo(f"  Processes: {len(result['processes'])}")
        else:
            click.echo(
                f"  '{app_name}' is not detected as an Electron application"
                " (not running or not Electron-based)."
            )


@electron.command(name="list")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def electron_list(json_output):
    """List all running Electron applications."""
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.electron import list_electron_apps
        result = list_electron_apps()
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="ELECTRON_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        apps = result["apps"]
        if not apps:
            click.echo("No Electron applications detected.")
        else:
            for app in apps:
                debug = f" (CDP port {app['debug_port']})" if app.get("debug_port") else ""
                click.echo(f"  {app['app_name']:<30} PID {app['pid']}{debug}")
            click.echo(f"\n{result['count']} Electron app(s)")


@electron.command(name="connect")
@click.argument("app_name")
@click.option("--port", "-p", type=int, default=None,
              help="CDP port (auto-detect if omitted)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def electron_connect(app_name, port, json_output):
    """Connect to an Electron app via DevTools Protocol.

    Requires the app to be running with --remote-debugging-port.
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    try:
        from naturo.electron import connect_to_electron
        result = connect_to_electron(app_name, port=port)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="ELECTRON_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"  Connected to {app_name} on port {result['port']}")
        click.echo(f"  {result['count']} tab(s) available:")
        for tab in result.get("tabs", []):
            title = tab.get("title", "Untitled")
            url = tab.get("url", "")
            click.echo(f"    - {title} ({url})")


@electron.command(name="launch")
@click.argument("app_path")
@click.option("--port", "-p", type=int, default=9229,
              help="CDP debug port (default 9229)")
@click.option("--json", "-j", "json_output", is_flag=True, help="JSON output")
def electron_launch(app_path, port, json_output):
    """Launch an Electron app with remote debugging enabled.

    APP_PATH is the full path to the Electron application executable.
    """
    import json as json_module
    from naturo.cli.error_helpers import emit_exception_error

    if port < 1 or port > 65535:
        import sys
        if json_output:
            click.echo(json_module.dumps({
                "success": False,
                "error": {
                    "code": "INVALID_INPUT",
                    "message": f"--port must be between 1 and 65535, got {port}",
                },
            }))
        else:
            click.echo(
                f"Error: --port must be between 1 and 65535, got {port}",
                err=True,
            )
        sys.exit(1)

    try:
        from naturo.electron import launch_with_debug
        result = launch_with_debug(app_path, port=port)
    except Exception as exc:
        emit_exception_error(exc, json_output, fallback_code="ELECTRON_ERROR")
        return

    if json_output:
        click.echo(json_module.dumps({"success": True, **result}))
    else:
        click.echo(f"  Launched {app_path}")
        click.echo(f"  PID: {result['pid']}")
        click.echo(f"  Debug port: {result['port']}")
        click.echo(f"  Connect with: naturo chrome tabs --port {result['port']}")
