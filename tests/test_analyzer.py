from __future__ import annotations

from log_analyzer_cli.analyzer import LogAnalyzer


def test_nginx_summary() -> None:
    lines = [
        '127.0.0.1 - - [16/Jan/2026:10:00:00 +0000] "GET /api/items HTTP/1.1" 200 123 "-" "UA" 0.120\n',
        '127.0.0.1 - - [16/Jan/2026:10:00:01 +0000] "GET /api/items HTTP/1.1" 200 456 "-" "UA" 0.080\n',
        '127.0.0.1 - - [16/Jan/2026:10:00:02 +0000] "POST /api/orders HTTP/1.1" 500 12 "-" "UA" 0.250\n',
    ]

    a = LogAnalyzer(fmt="nginx")
    a.process_lines(lines)
    res = a.result(top=10)

    assert res.lines_total == 3
    assert res.lines_parsed == 3
    assert res.parse_errors == 0
    assert ("/api/items", 2) in res.top_endpoints
    assert ("200", 2) in res.status_counts
    assert ("500", 1) in res.status_counts

    assert res.latency_ms["p50"] == 120.0
    assert res.latency_ms["p95"] == 250.0


def test_json_summary() -> None:
    lines = [
        '{"timestamp":"2026-01-16T10:00:00+00:00","path":"/a","status":200,"latency_ms":10}\n',
        '{"timestamp":"2026-01-16T10:00:01+00:00","path":"/b","status":404,"latency_ms":20}\n',
    ]
    a = LogAnalyzer(fmt="json")
    a.process_lines(lines)
    res = a.result(top=10)
    assert res.lines_parsed == 2
    assert ("/a", 1) in res.top_endpoints
    assert ("404", 1) in res.status_counts
