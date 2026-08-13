#!/usr/bin/env python3
"""Microbenchmark for the data pipeline (split_data.py + validate.py).

Usage: python3 site/_data/bench.py [runs]

Measures wall-clock time per process, including interpreter startup, because
that is how the pipeline is actually run. Keep this stable and re-run it after
editing either script to confirm gains and catch regressions.
"""

import statistics
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def time_cmd(args):
    t0 = time.perf_counter()
    result = subprocess.run(args, cwd=BASE, capture_output=True, text=True)
    dt = time.perf_counter() - t0
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        sys.exit(result.returncode)
    return dt


def run(label, args):
    times = [time_cmd(args) for _ in range(RUNS)]
    print(
        f"{label}: n={RUNS} "
        f"mean={statistics.mean(times) * 1000:.1f}ms "
        f"median={statistics.median(times) * 1000:.1f}ms "
        f"min={min(times) * 1000:.1f}ms "
        f"max={max(times) * 1000:.1f}ms"
    )


run("split_data", [sys.executable, "split_data.py"])
run("validate   ", [sys.executable, "validate.py"])
