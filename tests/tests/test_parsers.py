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
