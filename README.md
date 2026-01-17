# LogSift

set -euo pipefail

# 1) Go to project folder (adjust if you're already there)
cd "LogSift"

# 2) Create + activate a fresh venv
rm -rf .venv
python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
source .venv/bin/activate

# 3) Install deps (incl dev deps for tests)
python -m pip install -U pip
python -m pip install -e ".[dev]"

# 4) Run tests
pytest

# 5) Verify CLI entrypoints
echo "== logsift help =="; logsift --help
echo "== log-analyzer help (compat) =="; log-analyzer --help

# 6) Demo: run summaries on sample logs
echo "== nginx sample =="; logsift summary --format nginx --file examples/nginx.sample.log --top 5
echo "== json sample =="; logsift summary --format json --file examples/json.sample.log --latency-field latency_ms

# 7) Demo: same using legacy entrypoint (optional)
echo "== nginx sample (legacy) =="; log-analyzer summary --format nginx --file examples/nginx.sample.log --top 5
echo "== json sample (legacy) =="; log-analyzer summary --format json --file examples/json.sample.log --latency-field latency_ms

echo "Done."
