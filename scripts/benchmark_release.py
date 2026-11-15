# Co-authored with ChatGPT
"""Small local release benchmark; no network, credentials, or private prompts."""
from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend import ResearchStore, RestrictedSQL, build_comparison, retrieve_evidence


def median_ms(task, repeats=10):
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        task()
        timings.append((time.perf_counter() - start) * 1000)
    return round(statistics.median(timings), 2)


def main():
    tracemalloc.start()
    load = median_ms(lambda: ResearchStore().close())
    with ResearchStore() as store:
        flex = median_ms(lambda: retrieve_evidence(store, "FLEX flame extinction"))
        history = median_ms(lambda: retrieve_evidence(store, "What happened in the Mir fire?"))
        fts = median_ms(lambda: store.passages("flame extinction", limit=10))
        sql = median_ms(lambda: RestrictedSQL(store).execute(
            "SELECT fuel, COUNT(*) AS n FROM experiment_records GROUP BY fuel"))

        def chart():
            comparison = build_comparison(store, "initial_diameter_mm", "burn_time_s")
            px.scatter(comparison.plotted, x="x_numeric_value", y="y_numeric_value", color="fuel")
            return len(comparison.plotted)

        chart_rows = chart()
        chart_ms = median_ms(chart, repeats=5)
    _, peak = tracemalloc.get_traced_memory()
    print(json.dumps({"median_ms": {"sqlite_load": load, "flex_retrieval": flex,
                                    "historical_retrieval": history, "fts_search": fts,
                                    "restricted_sql": sql, "chart_processing": chart_ms},
                      "chart_rows": chart_rows, "peak_python_mb": round(peak / 1048576, 2)},
                     indent=2))


if __name__ == "__main__":
    main()
