from __future__ import annotations

from datetime import datetime, timezone

from log_analyzer_cli.parsers import parse_jsonl


def test_parse_jsonl_epoch_seconds() -> None:
    line = '{"timestamp": 1700000000, "path":"/", "status":200}\n'
    event = parse_jsonl(line)
    assert event is not None
    assert event.ts == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_parse_jsonl_epoch_milliseconds() -> None:
    line = '{"timestamp": 1700000000000, "path":"/", "status":200}\n'
    event = parse_jsonl(line)
    assert event is not None
    assert event.ts == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_parse_jsonl_epoch_string() -> None:
    line = '{"timestamp": "1700000000", "path":"/", "status":200}\n'
    event = parse_jsonl(line)
    assert event is not None
    assert event.ts == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_parse_jsonl_epoch_decimal_string() -> None:
    line = '{"timestamp": "1700000000.5", "path":"/", "status":200}\n'
    event = parse_jsonl(line)
    assert event is not None
    assert event.ts == datetime.fromtimestamp(1700000000.5, tz=timezone.utc)


def test_parse_jsonl_naive_iso_assumed_utc() -> None:
    line = '{"timestamp": "2026-01-16T10:00:00", "path":"/", "status":200}\n'
    event = parse_jsonl(line)
    assert event is not None
    assert event.ts == datetime(2026, 1, 16, 10, 0, 0, tzinfo=timezone.utc)
