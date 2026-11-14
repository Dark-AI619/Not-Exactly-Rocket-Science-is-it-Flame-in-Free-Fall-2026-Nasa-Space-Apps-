# Co-authored with ChatGPT
"""Descriptive, source-traceable comparisons of admitted FLEX measurements."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .store import ResearchError, ResearchStore, VARIABLE_UNITS


@dataclass(frozen=True)
class Comparison:
    rows: pd.DataFrame
    plotted: pd.DataFrame
    x_variable: str
    y_variable: str
    x_unit: str
    y_unit: str
    missing_x: int
    missing_y: int
    missing_either: int
    fuels: tuple[str, ...]
    oxygen_span: tuple[float, float] | None
    pressure_span: tuple[float, float] | None


def _span(series: pd.Series) -> tuple[float, float] | None:
    values = series.to_numpy(dtype=float)
    finite = values[np.isfinite(values)]
    return (float(np.min(finite)), float(np.max(finite))) if finite.size else None


def build_comparison(
    store: ResearchStore, x_variable: str, y_variable: str, *,
    fuel: str | None = None, oxygen_range: tuple[float, float] | None = None,
    pressure_range: tuple[float, float] | None = None,
    experiment_ids: list[str] | None = None,
) -> Comparison:
    """Join original reported values; retain missing cells and provenance.

    No imputation, unit conversion, or statistical inference is performed.
    """
    if x_variable not in VARIABLE_UNITS or y_variable not in VARIABLE_UNITS:
        raise ResearchError("comparison variable is not admitted")
    if x_variable == y_variable:
        raise ResearchError("choose two different measurements")
    if experiment_ids is not None and len(experiment_ids) != len(set(experiment_ids)):
        raise ResearchError("duplicate experiment selection")

    kwargs = {"investigation_id": "FLEX", "fuel": fuel, "limit": 500}
    if oxygen_range is not None:
        kwargs.update(oxygen_min=oxygen_range[0], oxygen_max=oxygen_range[1])
    if pressure_range is not None:
        kwargs.update(pressure_min=pressure_range[0], pressure_max=pressure_range[1])
    base = pd.DataFrame.from_records(store.experiments(**kwargs))
    if base.empty:
        empty = pd.DataFrame()
        return Comparison(empty, empty, x_variable, y_variable,
                          VARIABLE_UNITS[x_variable], VARIABLE_UNITS[y_variable],
                          0, 0, 0, (), None, None)
    if experiment_ids is not None:
        unknown = set(experiment_ids) - set(base["id"])
        if unknown:
            raise ResearchError("selected experiments are outside the filtered FLEX scope")
        base = base[base["id"].isin(experiment_ids)].copy()
    if base.empty:
        empty = pd.DataFrame()
        return Comparison(empty, empty, x_variable, y_variable,
                          VARIABLE_UNITS[x_variable], VARIABLE_UNITS[y_variable],
                          0, 0, 0, (), None, None)

    keep = ["id", "original_test_id", "fuel", "test_end", "oxygen_mole_fraction",
            "pressure_mmhg", "data_origin", "source_title", "source_url", "source_rights"]
    rows = base[keep].rename(columns={"id": "experiment_id"})
    for prefix, variable in (("x", x_variable), ("y", y_variable)):
        frame = store.measurement_frame(variable)
        frame = frame[["experiment_id", "numeric_value", "original_value", "original_unit",
                       "classification", "uncertainty", "page"]]
        frame = frame.rename(columns={column: f"{prefix}_{column}" for column in frame
                                      if column != "experiment_id"})
        rows = rows.merge(frame, on="experiment_id", how="left", validate="one_to_one")
        if rows[f"{prefix}_original_unit"].isna().any() or set(rows[f"{prefix}_original_unit"]) != {VARIABLE_UNITS[variable]}:
            raise ResearchError(f"missing or inconsistent original unit for {variable}")

    missing_x = int(rows["x_numeric_value"].isna().sum())
    missing_y = int(rows["y_numeric_value"].isna().sum())
    plotted = rows.dropna(subset=["x_numeric_value", "y_numeric_value"]).copy()
    return Comparison(
        rows=rows, plotted=plotted, x_variable=x_variable, y_variable=y_variable,
        x_unit=VARIABLE_UNITS[x_variable], y_unit=VARIABLE_UNITS[y_variable],
        missing_x=missing_x, missing_y=missing_y,
        missing_either=len(rows) - len(plotted),
        fuels=tuple(sorted(rows["fuel"].dropna().unique())),
        oxygen_span=_span(rows["oxygen_mole_fraction"]),
        pressure_span=_span(rows["pressure_mmhg"]),
    )
