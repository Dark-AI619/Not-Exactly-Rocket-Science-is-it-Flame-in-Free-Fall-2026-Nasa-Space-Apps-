# Co-authored with ChatGPT
"""Scientific checks for the Phase 3D descriptive comparison service."""
import pytest

from backend import ResearchError, ResearchStore, build_comparison


@pytest.fixture
def store():
    with ResearchStore() as research:
        yield research


def test_comparison_preserves_missing_pairs_and_original_units(store):
    result = build_comparison(store, "initial_diameter_mm", "burn_time_s")
    assert len(result.rows) == 273
    assert len(result.plotted) == 260
    assert (result.missing_x, result.missing_y, result.missing_either) == (11, 6, 13)
    assert result.x_unit == "mm" and result.y_unit == "s"
    assert set(result.rows["data_origin"]) == {"NASA_REPORT_EXTRACTED"}
    assert result.rows.loc[result.rows["x_numeric_value"].isna(), "x_classification"].eq("UNAVAILABLE").all()
    assert result.plotted[["x_numeric_value", "y_numeric_value"]].notna().all().all()


def test_selected_test_retains_source_values_and_page(store):
    test = store.experiments(test_query="130")[0]
    result = build_comparison(store, "initial_diameter_mm", "burn_time_s",
                              experiment_ids=[test["id"]])
    row = result.rows.iloc[0]
    assert row["x_original_value"] == "2.91" and row["x_numeric_value"] == pytest.approx(2.91)
    assert row["y_original_value"] == ".6" and row["y_numeric_value"] == pytest.approx(0.6)
    assert row["x_page"] == row["y_page"] == 29
    assert row["source_title"] == "20150023456.pdf"
    assert row["source_url"] == "https://ntrs.nasa.gov/citations/20150023456"


def test_conditions_and_selection_are_scoped_to_admitted_flex(store):
    result = build_comparison(store, "pressure_mmhg", "burning_rate_mm2_s",
                              fuel="Heptane", oxygen_range=(0.17, 0.21))
    assert result.rows["fuel"].eq("Heptane").all()
    assert result.rows["oxygen_mole_fraction"].between(0.17, 0.21).all()
    assert result.y_unit == "mm²/s"
    assert result.missing_y > 0
    assert set(result.rows["y_classification"]) <= {"DERIVED", "UNAVAILABLE"}
    with pytest.raises(ResearchError, match="outside the filtered FLEX scope"):
        build_comparison(store, "pressure_mmhg", "burn_time_s",
                         fuel="Heptane", experiment_ids=[store.experiments(fuel="Methanol")[0]["id"]])
    with pytest.raises(ResearchError, match="different measurements"):
        build_comparison(store, "burn_time_s", "burn_time_s")
