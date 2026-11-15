# Co-authored with ChatGPT
"""Limited D-squared droplet regression model, separate from research records."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DropletModel:
    initial_diameter_mm: float
    burning_rate_mm2_s: float

    def __post_init__(self) -> None:
        d0 = self.initial_diameter_mm
        k = self.burning_rate_mm2_s
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool)
                   and math.isfinite(value) for value in (d0, k)):
            raise ValueError("model inputs must be finite numbers")
        if not 0 < d0 <= 20 or not 0 < k <= 10:
            raise ValueError("model inputs must be positive and within the supported droplet range")

    @property
    def ideal_zero_time_s(self) -> float:
        """Time at which this idealized regression reaches D=0; not flame extinction."""
        return self.initial_diameter_mm ** 2 / self.burning_rate_mm2_s

    def diameter_mm(self, elapsed_s: float) -> float:
        if (isinstance(elapsed_s, bool) or not isinstance(elapsed_s, (int, float))
                or not math.isfinite(elapsed_s) or elapsed_s < 0):
            raise ValueError("elapsed time must be finite and nonnegative")
        remaining_mm2 = self.initial_diameter_mm ** 2 - self.burning_rate_mm2_s * elapsed_s
        return math.sqrt(max(0.0, remaining_mm2))

    def profile(self, samples: int = 121) -> list[tuple[float, float]]:
        if isinstance(samples, bool) or not isinstance(samples, int) or not 2 <= samples <= 1001:
            raise ValueError("samples must be an integer from 2 to 1001")
        end = self.ideal_zero_time_s
        return [(t, self.diameter_mm(t)) for t in
                (end * index / (samples - 1) for index in range(samples))]


@dataclass(frozen=True)
class ReportInputs:
    experiment_id: str
    original_test_id: str
    initial_diameter_mm: float
    burning_rate_mm2_s: float
    diameter_original: str
    rate_original: str
    diameter_classification: str
    rate_classification: str
    diameter_pdf_page: int
    rate_pdf_page: int
    reported_burn_duration: str | None
    reported_outcome: str
    source_url: str


def compatible_report_inputs(experiment: dict) -> ReportInputs | None:
    """Admit only validated FLEX Table IX cells with the required units and values."""
    if (experiment.get("investigation_id") != "FLEX"
            or experiment.get("validation_status") != "VALIDATED"
            or experiment.get("data_origin") != "NASA_REPORT_EXTRACTED"):
        return None
    cells = {cell["variable"]: cell for cell in experiment["measurements"]}
    diameter = cells.get("initial_diameter_mm")
    rate = cells.get("burning_rate_mm2_s")
    if not diameter or not rate:
        return None
    for cell, unit in ((diameter, "mm"), (rate, "mm²/s")):
        value = cell["numeric_value"]
        if (cell["original_unit"] != unit or cell["classification"] not in {"MEASURED", "DERIVED"}
                or isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value <= 0):
            return None
        try:
            printed = float(cell["original_value"])
        except (TypeError, ValueError):
            return None  # Approximate or nonnumeric printed tokens need separate review.
        if not math.isfinite(printed) or not math.isclose(printed, value, rel_tol=1e-9, abs_tol=1e-12):
            return None
    try:
        DropletModel(diameter["numeric_value"], rate["numeric_value"])
    except ValueError:
        return None
    duration = cells.get("burn_time_s")
    return ReportInputs(
        experiment_id=experiment["id"], original_test_id=experiment["original_test_id"],
        initial_diameter_mm=diameter["numeric_value"], burning_rate_mm2_s=rate["numeric_value"],
        diameter_original=diameter["original_value"], rate_original=rate["original_value"],
        diameter_classification=diameter["classification"], rate_classification=rate["classification"],
        diameter_pdf_page=diameter["page"], rate_pdf_page=rate["page"],
        reported_burn_duration=duration["original_value"] if duration and duration["classification"] != "UNAVAILABLE" else None,
        reported_outcome=experiment["test_end"], source_url=experiment["source_url"],
    )
