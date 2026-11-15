# Co-authored with ChatGPT
"""Representative end-to-end scientific questions for Phase 3 readiness."""
from backend import ResearchStore, retrieve_evidence, validate_database


def test_five_representative_questions_keep_evidence_and_limits_distinct():
    questions = [
        "What is flame extinction in FLEX?",
        "What measurements are available for FLEX Test 054?",
        "What happened during the Mir station fire?",
        "Compare BASS-II and FLEX burning rates.",
        "Show evidence of oxygen concentration affecting FLEX experimental outcomes.",
    ]
    with ResearchStore() as store:
        audit = validate_database(store)
        packets = [retrieve_evidence(store, question) for question in questions]

    assert audit["status"] == "VALIDATED_SUBSET"
    assert (audit["experiments"], audit["measurements"], audit["passages"]) == (273, 2457, 329)

    extinction, test, mir, cross, oxygen = packets
    assert extinction["scopes"] == ["FLEX"]
    assert any(item["kind"] == "passage" and item["source_key"] == "PDF-2"
               and item["location"].startswith("PDF page ") for item in extinction["items"])

    record = next(item for item in test["items"] if item["kind"] == "experiment")
    assert record["experiment_id"].endswith("054")
    assert len(record["measurements"]) == 9
    assert all(measure["original_value"] is not None and measure["original_unit"]
               for measure in record["measurements"])

    assert mir["route"]["domain"] == "historical" and mir["supported"]
    assert all(item["kind"] == "documentary_note" and item["investigation_id"] is None
               for item in mir["items"])
    assert {item["source_key"] for item in mir["items"]} == {"MIR-1997"}
    assert not any(item["kind"] == "experiment" for item in mir["items"])

    assert set(cross["scopes"]) == {"FLEX", "BASS-II"}
    assert any("numerical rate comparison is unavailable" in notice for notice in cross["notices"])
    assert not any(item["kind"] == "experiment" and item["investigation_id"] == "BASS-II"
                   for item in cross["items"])

    examples = [item for item in oxygen["items"] if item["kind"] == "experiment"]
    assert len(examples) == 3
    oxygen_tokens = [next(float(m["original_value"]) for m in item["measurements"]
                          if m["variable"] == "oxygen_mole_fraction") for item in examples]
    assert oxygen_tokens == [0.12, 0.2, 0.34]
    assert all(item["source_identifier"] == "NASA/TP-2015-216046" and
               item["verification_status"] == "VALIDATED" for item in examples)
    assert any("do not establish a causal effect" in notice for notice in oxygen["notices"])

    for packet in packets:
        assert len(packet["items"]) <= 15
        assert all(item["source_title"] and item["source_identifier"] and item["location"]
                   and item["verification_status"] and item["source_url"].startswith("https://")
                   for item in packet["items"])
