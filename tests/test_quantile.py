from __future__ import annotations

from log_analyzer_cli.quantile import P2Quantile


def test_p2_quantile_reasonable() -> None:
    q = P2Quantile(0.95)
    for i in range(1, 101):
        q.add(float(i))
    est = q.value()
    assert est is not None
    # For a smooth sequence 1..100, p95 should be near 95
    assert 92 <= est <= 98
