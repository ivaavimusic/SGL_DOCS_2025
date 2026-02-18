#!/usr/bin/env python3
"""
Minimal AWAL helpers for x402-compute scripts.
"""

import json
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

DEFAULT_AWAL_PACKAGE = "awal@1.0.0"


def _build_awal_command(args: List[str]) -> List[str]:
    explicit_bin = os.getenv("AWAL_BIN", "").strip()
    if explicit_bin:
        return [explicit_bin, *args]

    local_awal = shutil.which("awal")
    if local_awal and os.getenv("AWAL_FORCE_NPX", "").strip() != "1":
        return [local_awal, *args]

    package = os.getenv("AWAL_PACKAGE", DEFAULT_AWAL_PACKAGE).strip() or DEFAULT_AWAL_PACKAGE
    return ["npx", "-y", package, *args]


def _run_awal(args: List[str], timeout: int = 180) -> Dict[str, Any]:
    cmd = _build_awal_command(args)
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "command": cmd,
    }


def _extract_json(text: str) -> Optional[Any]:
    raw = (text or "").strip()
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        pass

    lines = raw.splitlines()
    for i in range(len(lines) - 1, -1, -1):
        candidate = "\n".join(lines[i:]).strip()
        if not candidate or candidate[0] not in "[{":
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def _split_url(url: str) -> Tuple[str, str]:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL must include scheme and host (e.g. https://compute.x402layer.cc/compute/provision)")
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return base_url, path


def get_awal_evm_address(required: bool = True) -> Optional[str]:
    result = _run_awal(["address"])
    combined = f"{result['stdout']}\n{result['stderr']}"
    match = re.search(r"0x[a-fA-F0-9]{40}", combined)
    if match:
        return match.group(0)

    if required:
        if result["ok"]:
            raise ValueError("Could not parse wallet address from AWAL output")
        raise ValueError((result["stderr"] or result["stdout"] or "AWAL address failed").strip())
    return None


def _build_pay_args(
    base_url: str,
    path: str,
    method: str,
    data: Optional[Dict[str, Any]],
    query: Optional[Dict[str, Any]],
    headers: Optional[Dict[str, Any]],
    max_amount: Optional[int],
    short_flags: bool,
) -> List[str]:
    args: List[str] = ["pay", base_url, path]

    if method and method.upper() != "GET":
        args += (["-X", method.upper()] if short_flags else ["--method", method.upper()])
    if data is not None:
        payload = json.dumps(data, separators=(",", ":"))
        args += (["-d", payload] if short_flags else ["--data", payload])
    if query is not None:
        payload = json.dumps(query, separators=(",", ":"))
        args += (["-q", payload] if short_flags else ["--query", payload])
    if headers is not None:
        payload = json.dumps(headers, separators=(",", ":"))
        args += (["-h", payload] if short_flags else ["--headers", payload])
    if max_amount is not None:
        args += ["--max-amount", str(max_amount)]

    return args


def awal_pay_url(
    url: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    query: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None,
    max_amount: Optional[int] = None,
) -> Dict[str, Any]:
    base_url, path = _split_url(url)

    attempts = [
        _build_pay_args(base_url, path, method, data, query, headers, max_amount, short_flags=True),
        _build_pay_args(base_url, path, method, data, query, headers, max_amount, short_flags=False),
    ]

    last_result: Optional[Dict[str, Any]] = None
    for args in attempts:
        result = _run_awal(args)
        last_result = result
        parsed = _extract_json(result["stdout"])
        if result["ok"]:
            if isinstance(parsed, dict):
                return parsed
            if parsed is not None:
                return {"result": parsed}
            output = (result["stdout"] or "").strip()
            return {"success": True, "output": output}

        stderr = (result["stderr"] or "").lower()
        if "unknown option" not in stderr and "unknown command" not in stderr:
            break

    if not last_result:
        return {"error": "AWAL invocation failed before execution"}
    err = (last_result["stderr"] or last_result["stdout"] or f"AWAL command failed ({last_result['code']})").strip()
    return {"error": err, "output": (last_result["stdout"] or "").strip()}
