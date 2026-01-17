from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import LogAnalyzer, as_dict


def _print_human(d: dict, top: int) -> None:
    print(f"Lines: {d['lines_total']}  Parsed: {d['lines_parsed']}  Errors: {d['parse_errors']}")

    tr = d.get("time_range") or {}
    print(f"Time range: {tr.get('min')}  ->  {tr.get('max')}")

    lat = d.get("latency_ms") or {}
    if lat.get("count", 0):
        print(
            "Latency (ms): "
            f"count={lat.get('count')} p50={lat.get('p50'):.3f} p95={lat.get('p95'):.3f} p99={lat.get('p99'):.3f}"
        )

    print("\nTop endpoints:")
    for path, cnt in (d.get("top_endpoints") or [])[:top]:
        print(f"  {cnt:>8}  {path}")

    print("\nStatus codes:")
    for code, cnt in (d.get("status_counts") or []):
        print(f"  {cnt:>8}  {code}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Streaming log analyzer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("summary", help="Print summary stats")
    s.add_argument("--file", required=True, help="Path to log file")
    s.add_argument("--format", default="auto", choices=["auto", "nginx", "json"])
    s.add_argument("--top", type=int, default=10)
    s.add_argument("--latency-field", default="latency_ms", help="JSON field to use as latency in ms")
    s.add_argument("--json-out", default=None, help="Write summary as JSON to this path")

    args = parser.parse_args()

    if args.cmd == "summary":
        analyzer = LogAnalyzer(fmt=args.format, latency_field=args.latency_field)
        analyzer.process_file(Path(args.file))
        res = analyzer.result(top=args.top)
        d = as_dict(res)
        _print_human(d, args.top)
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
