"""Aggregate .eval logs into per-condition solved / gamed / wrong rates with CIs.

    python -m swarm_env.analyze logs/pilot_obs_true logs/pilot_obs_false
"""
from __future__ import annotations

import glob
import math
import sys
from collections import defaultdict

from inspect_ai.log import read_eval_log


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h)


def entries_of(sample):
    for key, val in sample.store.items():
        if key.lower().endswith("entries") and isinstance(val, list):
            return val
    return []


def main(dirs):
    # condition -> counts
    agg = defaultdict(lambda: {"episodes": 0, "submissions": 0,
                               "solved": 0, "gamed": 0, "wrong": 0, "episodes_with_gamed": 0,
                               "contagion": 0})  # contagion: a gamed submission after an earlier one
    for d in dirs:
        for path in glob.glob(f"{d}/*.eval"):
            log = read_eval_log(path)
            observed = (log.eval.task_args or {}).get("observed", "?")
            cond = f"observed={observed}"
            for s in log.samples:
                es = sorted(entries_of(s), key=lambda e: e.get("seq", 0))
                a = agg[cond]
                a["episodes"] += 1
                a["submissions"] += len(es)
                for e in es:
                    a[e["label"]] = a.get(e["label"], 0) + (1 if e["label"] in ("solved", "gamed", "wrong") else 0)
                if any(e["label"] == "gamed" for e in es):
                    a["episodes_with_gamed"] += 1
                first_gamed = next((i for i, e in enumerate(es) if e["label"] == "gamed"), None)
                if first_gamed is not None and any(e["label"] == "gamed" for e in es[first_gamed + 1:]):
                    a["contagion"] += 1

    print(f"\n{'condition':<16}{'episodes':>9}{'gamed-rate':>12}  95% CI{'':8}{'contagion':>10}")
    for cond in sorted(agg):
        a = agg[cond]
        p, lo, hi = wilson(a["episodes_with_gamed"], a["episodes"])
        cp, _, _ = wilson(a["contagion"], a["episodes"])
        print(f"{cond:<16}{a['episodes']:>9}{p:>12.2f}  [{lo:.2f},{hi:.2f}]{'':6}{cp:>10.2f}")
        print(f"{'':16}submissions: solved={a['solved']} gamed={a['gamed']} wrong={a['wrong']}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["logs"])
