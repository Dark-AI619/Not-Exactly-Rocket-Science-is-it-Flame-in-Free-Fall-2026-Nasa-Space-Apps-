# Co-authored with ChatGPT
"""Scientific bounds and source-admission checks for the schematic model."""
import math

import pytest

from backend import DropletModel, ResearchStore, compatible_report_inputs


def test_d_squared_equation_units_end_and_monotonic_profile():
    model = DropletModel(3.0, 0.5)  # mm and mm²/s
    assert model.ideal_zero_time_s == pytest.approx(18.0)
    assert model.diameter_mm(0) == pytest.approx(3.0)
    assert model.diameter_mm(8) == pytest.approx(math.sqrt(5.0))
    assert model.diameter_mm(18) == pytest.approx(0.0)
    assert model.diameter_mm(30) == 0.0  # Never take a square root of negative D².
    profile = model.profile()
    assert len(profile) == 121 and profile[0] == (0.0, 3.0)
    assert profile[-1][1] == pytest.approx(0.0)
    assert all(a[1] >= b[1] for a, b in zip(profile, profile[1:]))


@pytest.mark.parametrize("diameter,rate", [(0, .4), (3, 0), (-1, .4), (3, -1),
                                            (math.nan, .4), (3, math.inf), (True, .4), (21, .4)])
def test_invalid_model_parameters_rejected(diameter, rate):
    with pytest.raises(ValueError):
        DropletModel(diameter, rate)


@pytest.mark.parametrize("elapsed", [-1, math.nan, math.inf, True, "2"])
def test_invalid_time_rejected(elapsed):
    with pytest.raises(ValueError):
        DropletModel(3, .4).diameter_mm(elapsed)


def test_compatible_flex_inputs_preserve_original_cells_and_provenance():
    with ResearchStore() as store:
        row = store.experiments(test_query="054")[0]
        source = compatible_report_inputs(store.experiment(row["id"]))
    assert source is not None and source.original_test_id.endswith("054")
    assert source.initial_diameter_mm == 3.56
    assert source.burning_rate_mm2_s == .41
    assert (source.diameter_original, source.rate_original) == ("3.56", ".41")
    assert (source.diameter_classification, source.rate_classification) == ("MEASURED", "DERIVED")
    assert (source.diameter_pdf_page, source.rate_pdf_page) == (27, 27)
    assert source.reported_burn_duration == "29" and source.reported_outcome == "Extinction"
    assert source.source_url == "https://ntrs.nasa.gov/citations/20150023456"
    assert DropletModel(source.initial_diameter_mm, source.burning_rate_mm2_s).ideal_zero_time_s == pytest.approx(30.91121951)


def test_missing_or_unverified_source_cells_do_not_load_as_model_inputs():
    with ResearchStore() as store:
        experiment_id = store.db.execute(
            "SELECT experiment_id FROM measurements WHERE variable='burning_rate_mm2_s' AND classification='UNAVAILABLE' LIMIT 1"
        ).fetchone()[0]
        candidate = store.experiment(experiment_id)
    assert compatible_report_inputs(candidate) is None
    altered = dict(candidate, validation_status="PENDING")
    assert compatible_report_inputs(altered) is None
    altered = dict(candidate, data_origin="PSI_RAW_TELEMETRY")
    assert compatible_report_inputs(altered) is None


def test_source_units_must_match_without_conversion():
    with ResearchStore() as store:
        row = store.experiments(test_query="054")[0]
        experiment = store.experiment(row["id"])
    changed = dict(experiment, measurements=[dict(cell, original_unit="cm") if cell["variable"] == "initial_diameter_mm"
                                            else cell for cell in experiment["measurements"]])
    assert compatible_report_inputs(changed) is None
    approximate = dict(experiment, measurements=[dict(cell, original_value="~3.56")
                                                 if cell["variable"] == "initial_diameter_mm" else cell
                                                 for cell in experiment["measurements"]])
    assert compatible_report_inputs(approximate) is None
