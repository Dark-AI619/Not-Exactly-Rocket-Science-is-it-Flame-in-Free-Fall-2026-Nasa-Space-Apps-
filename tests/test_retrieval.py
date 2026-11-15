# Co-authored with ChatGPT
"""Evidence routing, citation and absence checks for deterministic retrieval."""
import pytest

from backend import ResearchError, ResearchStore, retrieve_evidence, route_question


@pytest.fixture
def store():
    with ResearchStore() as research:
        yield research


def test_router_understands_aliases_and_topics():
    route = route_question("How does O2 affect quenching in the Flame Extinguishment Experiment?")
    assert route["investigations"] == ("FLEX",)
    assert route["domain"] == "combustion"
    assert {"oxygen", "extinction"} <= set(route["topics"])
    assert route_question("What measurements are available for FLEX Test 054?")["test_number"] == 54
    assert route_question("BASS 2 solid material airflow")["investigations"] == ("BASS-II",)
    assert route_question("SAME-R aerosol detector")["domain"] == "detection"
    with pytest.raises(ResearchError):
        route_question(" ")


def test_flex_passages_are_bounded_and_cited(store):
    packet = retrieve_evidence(store, "What is flame extinction in FLEX?")
    passages = [item for item in packet["items"] if item["kind"] == "passage"]
    assert packet["supported"] and 1 <= len(passages) <= 3
    assert all(item["investigation_id"] == "FLEX" for item in passages)
    assert all(item["source_title"] == "20150023456.pdf" for item in passages)
    assert all(item["location"].startswith("PDF page ") and item["source_url"] for item in passages)
    assert len(packet["items"]) <= 15


def test_exact_flex_test_preserves_original_measurements(store):
    packet = retrieve_evidence(store, "What measurements are available for FLEX Test 054?")
    experiments = [item for item in packet["items"] if item["kind"] == "experiment"]
    assert len(experiments) == 1
    item = experiments[0]
    assert item["experiment_id"].endswith("054")
    assert item["source_identifier"] == "NASA/TP-2015-216046"
    assert item["location"].startswith("Appendix A, Table IX; PDF page ")
    assert len(item["measurements"]) == 9
    assert all(m["original_unit"] and m["page"] for m in item["measurements"])
    assert not any(item["kind"] == "passage" for item in packet["items"])
    missing = retrieve_evidence(store, "What measurements are available for FLEX Test 999?")
    assert not missing["supported"]
    assert not any(item["kind"] == "experiment" for item in missing["items"])
    assert any("no validated record" in note for note in missing["notices"])


def test_mir_historical_answer_uses_only_admitted_documentary_notes(store):
    packet = retrieve_evidence(store, "What happened during the Mir station fire?")
    assert packet["route"]["domain"] == "historical"
    assert packet["supported"]
    assert any(item["source_key"] == "MIR-1997" for item in packet["items"])
    assert all(item["kind"] == "documentary_note" for item in packet["items"])
    assert not any(item["kind"] == "experiment" for item in packet["items"])
    missing = retrieve_evidence(store, "What happened during the 1978 Cosmos station fire?")
    assert not missing["supported"]


def test_cross_investigation_evidence_remains_separate(store):
    packet = retrieve_evidence(store, "Compare BASS-II and FLEX burning rates.")
    assert packet["route"]["intent"] == "comparison"
    assert set(packet["scopes"]) == {"FLEX", "BASS-II"}
    passages = [item for item in packet["items"] if item["kind"] == "passage"]
    assert {item["investigation_id"] for item in passages} == {"FLEX", "BASS-II"}
    assert any("BASS-II: no validated numerical" in note for note in packet["notices"])
    assert not any(item["kind"] == "experiment" and item["investigation_id"] == "BASS-II"
                   for item in packet["items"])


def test_explicit_scope_does_not_fall_back_across_investigations(store):
    packet = retrieve_evidence(store, "oxygen concentration", investigation_id="BASS-II")
    assert packet["scopes"] == ["BASS-II"]
    assert all(item["investigation_id"] == "BASS-II" for item in packet["items"])
    with pytest.raises(ResearchError, match="unknown topic"):
        retrieve_evidence(store, "oxygen", topic_id="invented")
