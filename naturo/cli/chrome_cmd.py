"""CLI commands for Chrome DevTools Protocol (CDP) browser automation.

Provides ``naturo chrome`` subcommands to interact with Chrome/Chromium/Edge
browsers via the DevTools Protocol.

Requires Chrome to be started with ``--remote-debugging-port=9222``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from naturo.cli.error_helpers import json_error


def _validate_port(port: int, as_json: bool) -> None:
    """Validate port is in 1-65535 range, exit with error if not.

    Args:
        port: Port number to validate.
        as_json: Whether to emit JSON error output.
    """
    if port < 1 or port > 65535:
        if as_json:
            click.echo(json_error("INVALID_INPUT",
                                  f"--port must be between 1 and 65535, got {port}"))
        else:
            click.echo(f"Error: --port must be between 1 and 65535, got {port}", err=True)
        sys.exit(1)


@click.group("chrome")
def chrome_group() -> None:
    """Chrome browser automation via DevTools Protocol (CDP).

    Requires Chrome to be started with --remote-debugging-port=9222.
    """
    pass


def _get_client(
    host: str = "localhost",
    port: int = 9222,
    timeout: float = 30.0,
) -> "CDPClient":
    """Create a CDPClient, importing lazily to avoid import-time errors."""
    from naturo.cdp import CDPClient
    return CDPClient(host=host, port=port, timeout=timeout)


@chrome_group.command("tabs")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_tabs(host: str, port: int, as_json: bool) -> None:
    """List open Chrome tabs."""
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        tabs = client.list_tabs()

        if as_json:
            click.echo(json.dumps({
                "success": True,
                "tabs": tabs,
                "count": len(tabs),
            }, indent=2))
        else:
            if not tabs:
                click.echo("No tabs found.")
                return
            for i, tab in enumerate(tabs):
                title = tab.get("title", "(untitled)")
                url = tab.get("url", "")
                tab_id = tab.get("id", "")
                click.echo(f"[{i}] {title}")
                click.echo(f"    URL: {url}")
                click.echo(f"    ID:  {tab_id}")

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("version")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_version(host: str, port: int, as_json: bool) -> None:
    """Show Chrome browser version info."""
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        info = client.get_version()

        if as_json:
            click.echo(json.dumps({"success": True, **info}, indent=2))
        else:
            for key, val in info.items():
                click.echo(f"{key}: {val}")

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("eval")
@click.argument("expression")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_eval(
    expression: str,
    tab: Optional[str],
    host: str,
    port: int,
    as_json: bool,
) -> None:
    """Evaluate JavaScript in a Chrome tab.

    Example: naturo chrome eval "document.title"
    """
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            result = client.evaluate(expression)

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "result": result,
                }, indent=2))
            else:
                click.echo(str(result) if result is not None else "(undefined)")
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("screenshot")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--path", "output_path", default=None, help="Output file path.")
@click.option("--format", "fmt", default="png", type=click.Choice(["png", "jpeg"]),
              help="Image format.")
@click.option("--quality", default=80, type=int, help="JPEG quality (1-100).")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_screenshot(
    tab: Optional[str],
    host: str,
    port: int,
    output_path: Optional[str],
    fmt: str,
    quality: int,
    as_json: bool,
) -> None:
    """Capture a screenshot of a Chrome tab.

    Uses Chrome's own rendering engine — pixel-perfect browser screenshots.
    """
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    if quality < 1 or quality > 100:
        if as_json:
            click.echo(json_error("INVALID_INPUT",
                                  f"--quality must be between 1 and 100, got {quality}"))
        else:
            click.echo(f"Error: --quality must be between 1 and 100, got {quality}", err=True)
        sys.exit(1)

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            data = client.screenshot(format=fmt, quality=quality)

            # Determine output path
            if output_path is None:
                ext = "jpg" if fmt == "jpeg" else "png"
                output_path = f"chrome_screenshot.{ext}"

            Path(output_path).write_bytes(data)

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "path": str(output_path),
                    "format": fmt,
                    "size": len(data),
                }, indent=2))
            else:
                click.echo(f"Screenshot saved: {output_path} ({len(data)} bytes)")
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("navigate")
@click.argument("url")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_navigate(
    url: str,
    tab: Optional[str],
    host: str,
    port: int,
    as_json: bool,
) -> None:
    """Navigate a Chrome tab to a URL.

    Example: naturo chrome navigate "https://example.com"
    """
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            result = client.navigate(url)

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "url": url,
                    "frameId": result.get("frameId", ""),
                }, indent=2))
            else:
                click.echo(f"Navigated to: {url}")
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("click")
@click.argument("selector")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_click(
    selector: str,
    tab: Optional[str],
    host: str,
    port: int,
    as_json: bool,
) -> None:
    """Click a DOM element by CSS selector.

    Example: naturo chrome click "button#submit"
    """
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            client.click_element(selector)

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "selector": selector,
                }, indent=2))
            else:
                click.echo(f"Clicked: {selector}")
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("type")
@click.argument("selector")
@click.argument("text")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_type_text(
    selector: str,
    text: str,
    tab: Optional[str],
    host: str,
    port: int,
    as_json: bool,
) -> None:
    """Type text into a DOM element.

    Example: naturo chrome type "input#search" "hello world"
    """
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            client.type_text(selector, text)

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "selector": selector,
                    "text": text,
                }, indent=2))
            else:
                click.echo(f"Typed into {selector}: {text}")
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("title")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_title(
    tab: Optional[str],
    host: str,
    port: int,
    as_json: bool,
) -> None:
    """Get the current page title."""
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            title = client.get_page_title()

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "title": title,
                }, indent=2))
            else:
                click.echo(title)
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@chrome_group.command("html")
@click.option("--tab", default=None, help="Tab ID to connect to.")
@click.option("--host", default="localhost", help="DevTools host.")
@click.option("--port", default=9222, type=int, help="DevTools port.")
@click.option("--selector", default=None, help="Get HTML of a specific element.")
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def chrome_html(
    tab: Optional[str],
    host: str,
    port: int,
    selector: Optional[str],
    as_json: bool,
) -> None:
    """Get page HTML or element HTML."""
    _validate_port(port, as_json)
    from naturo.cdp import CDPConnectionError, CDPError

    try:
        client = _get_client(host=host, port=port)
        client.connect(tab_id=tab)

        try:
            if selector:
                html = client.evaluate(
                    f"document.querySelector({json.dumps(selector)})?.outerHTML ?? ''"
                )
            else:
                html = client.get_page_html()

            if as_json:
                click.echo(json.dumps({
                    "success": True,
                    "html": html,
                }, indent=2))
            else:
                click.echo(html)
        finally:
            client.close()

    except CDPConnectionError as exc:
        if as_json:
            click.echo(json_error("CDP_CONNECTION_ERROR", str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except CDPError as exc:
        if as_json:
            click.echo(json_error(exc.code, str(exc)))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
