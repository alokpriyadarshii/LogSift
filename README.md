# LogSift

LogSift is a lightweight streaming CLI tool for analyzing log files. It is designed to process logs line by line, so it can summarize large files without loading everything into memory.

It currently supports:
- **Nginx combined-style access logs** with optional `request_time`
- **JSON Lines (JSONL)** application logs

## Features

- Streaming log analysis for large files
- Auto-detection of log format (`json` vs `nginx`)
- Endpoint frequency summary
- HTTP status code distribution
- Time range detection from parsed events
- Latency percentiles (`p50`, `p95`, `p99`)
- Optional JSON export for automation and scripting
- Simple CLI with clean human-readable output

## Project Structure

```text
LogSift/
├── examples/
│   ├── json.sample.log
│   └── nginx.sample.log
├── src/log_analyzer_cli/
│   ├── analyzer.py
│   ├── cli.py
│   ├── parsers.py
│   └── quantile.py
├── tests/
│   ├── test_analyzer.py
│   └── test_quantile.py
├── pyproject.toml
└── README.md
```

## Requirements

- Python **3.11+**

## Installation

### Clone and install

```bash
git clone https://github.com/alokpriyadarshii/LogSift.git
cd LogSift
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

### Install with development dependencies

```bash
python -m pip install -e ".[dev]"
```

## CLI Usage

The package installs these commands:
- `logsift`
- `log-analyzer`

Main subcommand:

```bash
logsift summary --file <path-to-log-file>
```

### Options

```text
--file           Path to the log file
--format         auto | nginx | json
--top            Number of top endpoints to show
--latency-field  JSON field name to use for latency in milliseconds
--json-out       Write the computed summary to a JSON file
```

## Examples

### 1. Analyze an Nginx log

```bash
logsift summary --format nginx --file examples/nginx.sample.log --top 5
```

### 2. Analyze a JSONL log

```bash
logsift summary --format json --file examples/json.sample.log --latency-field latency_ms
```

### 3. Let LogSift auto-detect the format

```bash
logsift summary --format auto --file examples/json.sample.log
```

### 4. Save output as JSON

```bash
logsift summary \
  --format json \
  --file examples/json.sample.log \
  --json-out summary.json
```

## Example Output

```text
Lines: 3  Parsed: 3  Errors: 0
Time range: 2026-01-16T10:00:00+00:00  ->  2026-01-16T10:00:02+00:00
Latency (ms): count=3 p50=120.000 p95=250.000 p99=250.000

Top endpoints:
         2  /api/items
         1  /api/orders

Status codes:
         2  200
         1  500
```

## Supported Input Formats

### Nginx combined-style logs

Expected request line shape:

```text
127.0.0.1 - - [16/Jan/2026:10:00:00 +0000] "GET /api/items HTTP/1.1" 200 123 "-" "UA" 0.120
```

Notes:
- The parser extracts the request path and status code.
- If `request_time` is present, it is interpreted as **seconds** and converted to **milliseconds**.
- Timestamp parsing uses the Nginx date format.

### JSON Lines logs

Expected fields:
- Timestamp: one of `timestamp`, `ts`, or `time`
- Path: `path` or fallback `url`
- Status: `status`
- Latency: configurable, default is `latency_ms`

Example:

```json
{"timestamp":"2026-01-16T10:00:00+00:00","path":"/api/items","status":200,"latency_ms":120}
```

Timestamp handling supports:
- ISO 8601 timestamps
- Unix epoch seconds
- Unix epoch milliseconds

## How It Works

LogSift processes files as a stream and maintains counters and percentile estimators while reading lines.

It computes:
- Total lines seen
- Successfully parsed lines
- Parse error count
- Most frequent endpoints
- Status code counts
- Minimum and maximum timestamps
- Latency percentiles using the **P² streaming quantile algorithm**

This makes it suitable for large log files where storing all latency values in memory would be inefficient.

## Development

Run tests:

```bash
pytest
```

Show CLI help:

```bash
logsift --help
```

## Current Limitations

- Nginx parsing is tailored to a combined-style log line with an optional trailing request time.
- JSON logs assume one valid JSON object per line.
- The CLI currently provides a single `summary` workflow.
- Path field names for JSON logs are not configurable from the CLI.

