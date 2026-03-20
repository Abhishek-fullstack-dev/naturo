"""Windows Registry operations backend.

Provides safe read/write/list/delete/search for Windows Registry
using the built-in ``winreg`` module. All functions return structured
dicts for easy JSON serialisation by the CLI layer.

Phase 5C.2 — Windows Registry.
"""

from __future__ import annotations

import platform
from typing import Any, Optional

from naturo.errors import NaturoError

# ── Hive name mapping ───────────────────────────────────────────────────────

_HIVE_ALIASES: dict[str, str] = {
    "HKCR": "HKEY_CLASSES_ROOT",
    "HKCU": "HKEY_CURRENT_USER",
    "HKLM": "HKEY_LOCAL_MACHINE",
    "HKU": "HKEY_USERS",
    "HKCC": "HKEY_CURRENT_CONFIG",
    "HKEY_CLASSES_ROOT": "HKEY_CLASSES_ROOT",
    "HKEY_CURRENT_USER": "HKEY_CURRENT_USER",
    "HKEY_LOCAL_MACHINE": "HKEY_LOCAL_MACHINE",
    "HKEY_USERS": "HKEY_USERS",
    "HKEY_CURRENT_CONFIG": "HKEY_CURRENT_CONFIG",
}

# Registry value type constants (mirroring winreg)
REG_TYPES = {
    "REG_SZ": 1,
    "REG_EXPAND_SZ": 2,
    "REG_BINARY": 3,
    "REG_DWORD": 4,
    "REG_DWORD_BIG_ENDIAN": 5,
    "REG_MULTI_SZ": 7,
    "REG_QWORD": 11,
    "REG_NONE": 0,
}

# Reverse lookup: int → type name
_TYPE_NAMES: dict[int, str] = {v: k for k, v in REG_TYPES.items()}


def _type_name(type_id: int) -> str:
    """Get human-readable type name for a registry value type.

    Args:
        type_id: The integer registry type constant.

    Returns:
        Type name string (e.g., 'REG_SZ', 'REG_DWORD').
    """
    return _TYPE_NAMES.get(type_id, f"REG_TYPE_{type_id}")


def _require_windows() -> None:
    """Raise NaturoError if not running on Windows.

    Raises:
        NaturoError: If the current platform is not Windows.
    """
    if platform.system() != "Windows":
        raise NaturoError(
            code="PLATFORM_ERROR",
            message="Registry operations require Windows.",
        )


def _parse_key_path(key_path: str) -> tuple[str, str]:
    """Parse a registry key path into (hive, subkey).

    Accepts both short (HKCU) and long (HKEY_CURRENT_USER) hive names,
    with ``\\`` or ``/`` as separator.

    Args:
        key_path: Full registry path, e.g. ``HKCU\\Software\\MyApp``.

    Returns:
        Tuple of (canonical hive name, subkey path).

    Raises:
        NaturoError: If the hive name is not recognised.
    """
    # Normalise forward slashes
    key_path = key_path.replace("/", "\\")

    parts = key_path.split("\\", 1)
    hive_name = parts[0].upper()
    subkey = parts[1] if len(parts) > 1 else ""

    canonical = _HIVE_ALIASES.get(hive_name)
    if canonical is None:
        raise NaturoError(
            code="INVALID_INPUT",
            message=f"Unknown registry hive: {parts[0]}. "
                    f"Use one of: {', '.join(sorted(set(_HIVE_ALIASES.values())))}",
        )
    return canonical, subkey


def _get_hive_handle(hive_name: str) -> Any:
    """Get the winreg hive constant for a canonical hive name.

    Args:
        hive_name: Canonical hive name (e.g., 'HKEY_CURRENT_USER').

    Returns:
        winreg constant handle.
    """
    import winreg
    return getattr(winreg, hive_name)


def _format_value(data: Any, type_id: int) -> Any:
    """Format registry value data for JSON output.

    Converts bytes to hex string, leaves other types as-is.

    Args:
        data: Raw registry value data.
        type_id: Registry value type constant.

    Returns:
        JSON-serialisable representation of the data.
    """
    if isinstance(data, bytes):
        return data.hex()
    return data


def _coerce_data(data_str: str, reg_type: str) -> Any:
    """Coerce a string data value to the appropriate Python type.

    Args:
        data_str: The data value as a string.
        reg_type: The target registry type name (e.g., 'REG_DWORD').

    Returns:
        Coerced data value suitable for winreg.SetValueEx().

    Raises:
        NaturoError: If the data cannot be coerced to the target type.
    """
    try:
        if reg_type == "REG_DWORD":
            return int(data_str, 0)  # Supports hex (0x...) and decimal
        elif reg_type == "REG_QWORD":
            return int(data_str, 0)
        elif reg_type == "REG_BINARY":
            return bytes.fromhex(data_str)
        elif reg_type == "REG_MULTI_SZ":
            # Accept semicolon-separated or newline-separated values
            return [s.strip() for s in data_str.replace("\n", ";").split(";") if s.strip()]
        else:
            # REG_SZ, REG_EXPAND_SZ — keep as string
            return data_str
    except (ValueError, TypeError) as exc:
        raise NaturoError(
            code="INVALID_INPUT",
            message=f"Cannot convert '{data_str}' to {reg_type}: {exc}",
        )


# ── Public API ──────────────────────────────────────────────────────────────


def reg_get(key_path: str, value_name: Optional[str] = None) -> dict[str, Any]:
    """Read a registry value.

    Args:
        key_path: Full registry key path (e.g., ``HKCU\\Software\\MyApp``).
        value_name: Value name to read. None or empty string reads the default value.

    Returns:
        Dict with ``name``, ``data``, ``type``, ``type_name``, ``key``.

    Raises:
        NaturoError: If the key or value does not exist or platform is wrong.
    """
    _require_windows()
    import winreg

    hive_name, subkey = _parse_key_path(key_path)
    hive = _get_hive_handle(hive_name)
    actual_name = value_name if value_name else ""

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            data, type_id = winreg.QueryValueEx(key, actual_name)
    except FileNotFoundError:
        target = f"value '{value_name}'" if value_name else "default value"
        raise NaturoError(
            code="REGISTRY_NOT_FOUND",
            message=f"Registry {target} not found in {key_path}",
        )
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied reading {key_path}",
        )
    except OSError as exc:
        raise NaturoError(
            code="REGISTRY_ERROR",
            message=f"Registry read failed: {exc}",
        )

    return {
        "name": value_name or "(Default)",
        "data": _format_value(data, type_id),
        "type": type_id,
        "type_name": _type_name(type_id),
        "key": key_path,
    }


def reg_set(
    key_path: str,
    value_name: str,
    data: str,
    reg_type: str = "REG_SZ",
) -> dict[str, Any]:
    """Write a registry value. Creates the key if it does not exist.

    Args:
        key_path: Full registry key path.
        value_name: Value name to write.
        data: Value data as a string (will be coerced to the correct type).
        reg_type: Registry type name (REG_SZ, REG_DWORD, etc.).

    Returns:
        Dict confirming the write with ``key``, ``name``, ``data``, ``type_name``.

    Raises:
        NaturoError: If the type is invalid, data cannot be coerced, or access denied.
    """
    _require_windows()
    import winreg

    if reg_type not in REG_TYPES:
        raise NaturoError(
            code="INVALID_INPUT",
            message=f"Unknown registry type: {reg_type}. "
                    f"Use one of: {', '.join(sorted(REG_TYPES.keys()))}",
        )

    hive_name, subkey = _parse_key_path(key_path)
    hive = _get_hive_handle(hive_name)
    type_id = REG_TYPES[reg_type]
    coerced = _coerce_data(data, reg_type)

    try:
        with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, value_name, 0, type_id, coerced)
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied writing to {key_path}. Try running as Administrator.",
        )
    except OSError as exc:
        raise NaturoError(
            code="REGISTRY_ERROR",
            message=f"Registry write failed: {exc}",
        )

    return {
        "key": key_path,
        "name": value_name,
        "data": _format_value(coerced, type_id),
        "type_name": reg_type,
    }


def reg_list(key_path: str) -> dict[str, Any]:
    """List subkeys and values under a registry key.

    Args:
        key_path: Full registry key path.

    Returns:
        Dict with ``key``, ``subkeys`` (list of names), and ``values``
        (list of dicts with name/data/type/type_name).

    Raises:
        NaturoError: If the key does not exist or access denied.
    """
    _require_windows()
    import winreg

    hive_name, subkey = _parse_key_path(key_path)
    hive = _get_hive_handle(hive_name)

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            info = winreg.QueryInfoKey(key)
            num_subkeys = info[0]
            num_values = info[1]

            subkeys: list[str] = []
            for i in range(num_subkeys):
                subkeys.append(winreg.EnumKey(key, i))

            values: list[dict[str, Any]] = []
            for i in range(num_values):
                name, data, type_id = winreg.EnumValue(key, i)
                values.append({
                    "name": name or "(Default)",
                    "data": _format_value(data, type_id),
                    "type": type_id,
                    "type_name": _type_name(type_id),
                })

    except FileNotFoundError:
        raise NaturoError(
            code="REGISTRY_NOT_FOUND",
            message=f"Registry key not found: {key_path}",
        )
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied reading {key_path}",
        )
    except OSError as exc:
        raise NaturoError(
            code="REGISTRY_ERROR",
            message=f"Registry list failed: {exc}",
        )

    return {
        "key": key_path,
        "subkeys": subkeys,
        "values": values,
    }


def reg_delete(
    key_path: str,
    value_name: Optional[str] = None,
    recursive: bool = False,
) -> dict[str, Any]:
    """Delete a registry key or value.

    Args:
        key_path: Full registry key path.
        value_name: If given, delete only this value. If None, delete the entire key.
        recursive: If True and deleting a key, delete all subkeys recursively.

    Returns:
        Dict confirming the deletion with ``key``, ``deleted`` ('value' or 'key').

    Raises:
        NaturoError: If the key/value does not exist, has subkeys without
                     recursive flag, or access denied.
    """
    _require_windows()
    import winreg

    hive_name, subkey = _parse_key_path(key_path)
    hive = _get_hive_handle(hive_name)

    if value_name is not None:
        # Delete a specific value
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, value_name)
        except FileNotFoundError:
            raise NaturoError(
                code="REGISTRY_NOT_FOUND",
                message=f"Registry value '{value_name}' not found in {key_path}",
            )
        except PermissionError:
            raise NaturoError(
                code="PERMISSION_DENIED",
                message=f"Access denied deleting value in {key_path}",
            )
        except OSError as exc:
            raise NaturoError(
                code="REGISTRY_ERROR",
                message=f"Registry delete failed: {exc}",
            )
        return {
            "key": key_path,
            "value": value_name,
            "deleted": "value",
        }

    # Delete the key itself
    if recursive:
        _delete_key_recursive(hive, subkey)
    else:
        try:
            winreg.DeleteKey(hive, subkey)
        except FileNotFoundError:
            raise NaturoError(
                code="REGISTRY_NOT_FOUND",
                message=f"Registry key not found: {key_path}",
            )
        except PermissionError:
            raise NaturoError(
                code="PERMISSION_DENIED",
                message=f"Access denied deleting {key_path}. "
                        f"Key may have subkeys — use --recursive.",
            )
        except OSError as exc:
            if "denied" in str(exc).lower() or "subkey" in str(exc).lower():
                raise NaturoError(
                    code="REGISTRY_HAS_SUBKEYS",
                    message=f"Cannot delete {key_path}: key has subkeys. Use --recursive.",
                )
            raise NaturoError(
                code="REGISTRY_ERROR",
                message=f"Registry delete failed: {exc}",
            )

    return {
        "key": key_path,
        "deleted": "key",
    }


def _delete_key_recursive(hive: Any, subkey: str) -> None:
    """Recursively delete a registry key and all its subkeys.

    Args:
        hive: winreg hive handle.
        subkey: Subkey path relative to hive.

    Raises:
        NaturoError: If the key does not exist or access denied.
    """
    import winreg

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            info = winreg.QueryInfoKey(key)
            # Delete subkeys depth-first
            for i in range(info[0] - 1, -1, -1):
                child = winreg.EnumKey(key, i)
                child_path = f"{subkey}\\{child}" if subkey else child
                _delete_key_recursive(hive, child_path)
    except FileNotFoundError:
        raise NaturoError(
            code="REGISTRY_NOT_FOUND",
            message=f"Registry key not found: {subkey}",
        )
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied reading {subkey} for recursive delete",
        )

    try:
        winreg.DeleteKey(hive, subkey)
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied deleting key: {subkey}",
        )
    except OSError as exc:
        raise NaturoError(
            code="REGISTRY_ERROR",
            message=f"Failed to delete key {subkey}: {exc}",
        )


def reg_search(
    key_path: str,
    query: str,
    *,
    max_depth: int = 5,
    max_results: int = 50,
    search_keys: bool = True,
    search_values: bool = True,
    search_data: bool = False,
) -> dict[str, Any]:
    """Search registry keys, value names, or value data.

    Args:
        key_path: Starting registry key path.
        query: Search string (case-insensitive substring match).
        max_depth: Maximum recursion depth (default 5).
        max_results: Maximum number of results to return (default 50).
        search_keys: Whether to match against subkey names.
        search_values: Whether to match against value names.
        search_data: Whether to match against value data.

    Returns:
        Dict with ``query``, ``root``, ``results`` (list of matches).

    Raises:
        NaturoError: If the starting key does not exist or access denied.
    """
    _require_windows()
    import winreg

    hive_name, subkey = _parse_key_path(key_path)
    hive = _get_hive_handle(hive_name)
    query_lower = query.lower()
    results: list[dict[str, Any]] = []

    def _search_recursive(current_subkey: str, depth: int) -> None:
        if depth > max_depth or len(results) >= max_results:
            return

        try:
            with winreg.OpenKey(hive, current_subkey, 0, winreg.KEY_READ) as key:
                info = winreg.QueryInfoKey(key)

                # Search values
                if search_values or search_data:
                    for i in range(info[1]):
                        if len(results) >= max_results:
                            return
                        try:
                            name, data, type_id = winreg.EnumValue(key, i)
                            full_path = f"{hive_name}\\{current_subkey}" if current_subkey else hive_name

                            name_match = search_values and query_lower in (name or "").lower()
                            data_match = search_data and query_lower in str(data).lower()

                            if name_match or data_match:
                                results.append({
                                    "type": "value",
                                    "key": full_path,
                                    "name": name or "(Default)",
                                    "data": _format_value(data, type_id),
                                    "value_type": _type_name(type_id),
                                })
                        except OSError:
                            continue

                # Search subkeys and recurse
                for i in range(info[0]):
                    if len(results) >= max_results:
                        return
                    try:
                        child_name = winreg.EnumKey(key, i)
                        child_path = f"{current_subkey}\\{child_name}" if current_subkey else child_name

                        if search_keys and query_lower in child_name.lower():
                            full_path = f"{hive_name}\\{child_path}"
                            results.append({
                                "type": "key",
                                "key": full_path,
                            })

                        _search_recursive(child_path, depth + 1)
                    except OSError:
                        continue

        except (FileNotFoundError, PermissionError, OSError):
            # Skip inaccessible keys during search
            pass

    try:
        # Verify starting key exists
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ):
            pass
    except FileNotFoundError:
        raise NaturoError(
            code="REGISTRY_NOT_FOUND",
            message=f"Registry key not found: {key_path}",
        )
    except PermissionError:
        raise NaturoError(
            code="PERMISSION_DENIED",
            message=f"Access denied reading {key_path}",
        )

    _search_recursive(subkey, 0)

    return {
        "query": query,
        "root": key_path,
        "count": len(results),
        "results": results,
        "truncated": len(results) >= max_results,
    }
