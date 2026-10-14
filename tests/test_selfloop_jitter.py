"""Regression test: /self_on N-M (range) picks a random delay that is always strictly
inside the range, never equal to either endpoint, and varies between cycles."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from self_tools import selfloop as sl


def _run():
    # fixed interval stays exact, unaffected (no jitter when a single value is given)
    cfg_fixed = {"interval": 90, "message": "x"}
    assert {sl._next_delay(cfg_fixed) for _ in range(50)} == {90}

    # ranged interval: 5m-7m == 300s-420s -> continuous (fractional-second) randomness,
    # not a limited/countable set of whole-second values
    cfg = {"lo": 300, "hi": 420, "message": "x"}
    samples = [sl._next_delay(cfg) for _ in range(5000)]
    assert all(isinstance(v, float) for v in samples)
    assert min(samples) > 300 and max(samples) < 420, (min(samples), max(samples))
    assert 300 not in samples and 420 not in samples
    assert len(set(samples)) > 4990, "should be essentially all-unique (continuous), not a small fixed set"

    # parser: range, fixed, reversed order, too-narrow rejected, garbage rejected
    assert sl._parse_interval_spec("5m-7m") == {"lo": 300, "hi": 420}
    assert sl._parse_interval_spec("10m") == {"fixed": 600}
    assert sl._parse_interval_spec("7m-5m") == {"lo": 300, "hi": 420}  # auto-sorted
    assert sl._parse_interval_spec("61s-62s") is None  # gap < MIN_RANGE_GAP
    assert sl._parse_interval_spec("garbage") is None

    print("selfloop jitter regression: OK")


if __name__ == "__main__":
    _run()
