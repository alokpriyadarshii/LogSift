from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_NGINX_RE = re.compile(
    r'^(?P<remote>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<request>[^"]*)"\s+(?P<status>\d{3})\s+(?P<bytes>\S+)\s+"(?P<referer>[^"]*)"\s+"(?P<ua>[^"]*)"(?:\s+(?P<req_time>\S+))?'
)


@dataclass(slots=True)
class ParsedEvent:
    ts: Optional[datetime]
    path: str
    status: int
    latency_ms: Optional[float]


def parse_nginx_combined(line: str) -> ParsedEvent | None:
    m = _NGINX_RE.match(line.strip())
    if not m:
        return None

    ts: Optional[datetime] = None
    try:
        ts = datetime.strptime(m.group('time'), '%d/%b/%Y:%H:%M:%S %z')
    except Exception:  # noqa: BLE001
        ts = None

    request = m.group('request')
    # request like: GET /path HTTP/1.1
    parts = request.split()
    path = parts[1] if len(parts) >= 2 else "-"

    try:
        status = int(m.group('status'))
    except Exception:  # noqa: BLE001
        return None

    latency_ms: Optional[float] = None
    req_time = m.groupdict().get('req_time')
    if req_time:
        try:
            # nginx request_time is usually seconds (float)
            latency_ms = float(req_time) * 1000.0
        except Exception:  # noqa: BLE001
            latency_ms = None

    return ParsedEvent(ts=ts, path=path, status=status, latency_ms=latency_ms)


def _parse_iso(ts_val: Any) -> Optional[datetime]:
    if ts_val is None:
        return None
    if isinstance(ts_val, (int, float)):
        # epoch seconds or milliseconds
        ts_float = float(ts_val)
        if ts_float >= 1_000_000_000_000:
            ts_float /= 1000.0
        return datetime.fromtimestamp(ts_float, tz=timezone.utc)
    if not isinstance(ts_val, str):
        return None
    s = ts_val.strip()
        if s.isdigit():
        try:
            ts_float = float(s)
        except Exception:  # noqa: BLE001
            return None
        if ts_float >= 1_000_000_000_000:
            ts_float /= 1000.0
        return datetime.fromtimestamp(ts_float, tz=timezone.utc)
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    try:
        return datetime.fromisoformat(s)
    except Exception:  # noqa: BLE001
        return None


def parse_jsonl(line: str, *, path_field: str = "path", status_field: str = "status", latency_field: str = "latency_ms") -> ParsedEvent | None:
    try:
        obj = json.loads(line)
    except Exception:  # noqa: BLE001
        return None

    path = obj.get(path_field) or obj.get("url") or "-"
    try:
        status = int(obj.get(status_field))
    except Exception:  # noqa: BLE001
        return None

    ts = _parse_iso(obj.get("timestamp") or obj.get("ts") or obj.get("time"))

    latency_ms: Optional[float] = None
    if latency_field in obj and obj.get(latency_field) is not None:
        try:
            latency_ms = float(obj.get(latency_field))
        except Exception:  # noqa: BLE001
            latency_ms = None

    return ParsedEvent(ts=ts, path=str(path), status=status, latency_ms=latency_ms)
