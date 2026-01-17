from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional

from .parsers import ParsedEvent, parse_jsonl, parse_nginx_combined
from .quantile import P2Quantile

Format = Literal["auto", "nginx", "json"]


@dataclass
class AnalysisResult:
    lines_total: int
    lines_parsed: int
    parse_errors: int
    top_endpoints: list[tuple[str, int]]
    status_counts: list[tuple[str, int]]
    time_range: dict[str, Optional[str]]
    latency_ms: dict[str, Optional[float]]


class LogAnalyzer:
    def __init__(self, *, fmt: Format = "auto", latency_field: str = "latency_ms") -> None:
        self.fmt: Format = fmt
        self.latency_field = latency_field

        self.total = 0
        self.parsed = 0
        self.errors = 0

        self.endpoints: Counter[str] = Counter()
        self.statuses: Counter[str] = Counter()

        self._min_ts: Optional[datetime] = None
        self._max_ts: Optional[datetime] = None

        self._p50 = P2Quantile(0.50)
        self._p95 = P2Quantile(0.95)
        self._p99 = P2Quantile(0.99)
        self._latency_seen = 0

    def process_lines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.total += 1
            event = self._parse_line(line)
            if event is None:
                self.errors += 1
                continue

            self.parsed += 1
            self.endpoints[event.path] += 1
            self.statuses[str(event.status)] += 1

            if event.ts is not None:
                if self._min_ts is None or event.ts < self._min_ts:
                    self._min_ts = event.ts
                if self._max_ts is None or event.ts > self._max_ts:
                    self._max_ts = event.ts

            if event.latency_ms is not None:
                self._latency_seen += 1
                self._p50.add(event.latency_ms)
                self._p95.add(event.latency_ms)
                self._p99.add(event.latency_ms)

    def process_file(self, file: str | Path, *, encoding: str = "utf-8") -> None:
        path = Path(file)
        with path.open("r", encoding=encoding, errors="replace") as f:
            self.process_lines(f)

    def result(self, *, top: int = 10) -> AnalysisResult:
        return AnalysisResult(
            lines_total=self.total,
            lines_parsed=self.parsed,
            parse_errors=self.errors,
            top_endpoints=self.endpoints.most_common(top),
            status_counts=self.statuses.most_common(),
            time_range={
                "min": self._min_ts.isoformat() if self._min_ts else None,
                "max": self._max_ts.isoformat() if self._max_ts else None,
            },
            latency_ms={
                "count": self._latency_seen,
                "p50": self._p50.value(),
                "p95": self._p95.value(),
                "p99": self._p99.value(),
            })

    def _parse_line(self, line: str) -> ParsedEvent | None:
        # Auto-detect: JSON if line starts with '{' (after whitespace), else nginx.
        if self.fmt == "auto":
            s = line.lstrip()
            if s.startswith("{"):
                return parse_jsonl(line, latency_field=self.latency_field)
            return parse_nginx_combined(line)
        if self.fmt == "json":
            return parse_jsonl(line, latency_field=self.latency_field)
        return parse_nginx_combined(line)


def as_dict(res: AnalysisResult) -> Dict[str, Any]:
    return {
        "lines_total": res.lines_total,
        "lines_parsed": res.lines_parsed,
        "parse_errors": res.parse_errors,
        "top_endpoints": res.top_endpoints,
        "status_counts": res.status_counts,
        "time_range": res.time_range,
        "latency_ms": res.latency_ms,
    }
