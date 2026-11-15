# Co-authored with ChatGPT
"""Controlled documentary admission, source isolation, and local review staging."""
import hashlib
import json

import pytest

from backend import GroqResult, ResearchError, ResearchStore, retrieve_evidence, validate_database
from backend.admission import reject_candidate, stage_candidate
from backend.grounded import grounded_from_packet
from backend.store import DEFAULT_ARCHIVE
from migrations.phase4d import migrate, row_hash


EXPECTED_CORE = {
    "sources": "117f9768efae40a02bff085bbfad8d5aee41d5c5c75b1829c4e86c6ccd4cded7",
    "experiments": "c27a04c8584d53bfd025e9e95cecb9d12a46cb95ac10adaee458a855d605cbf0",
    "measurements": "e116af0dc09f04d69bcc6cfebf4364fb28f38f1e3623124717d58f2673d8b62a",
    "passages": "c4fc9c747ce59223feec01a9f09da49a299e65167e53607307bcc399aeb0ce52",
}


def test_original_science_is_unchanged_and_new_sources_have_provenance():
    with ResearchStore() as store:
        audit = validate_database(store)
        assert (audit["experiments"], audit["measurements"], audit["passages"]) == (273, 2457, 329)
        assert audit["documentary_notes"] == 10 and audit["sources"] == 25
        assert {table: row_hash(store.db, table) for table in EXPECTED_CORE} == EXPECTED_CORE
        notes = store.documentary_notes(domain_id="historical")
        assert len(notes) == 5
        assert all(note["source_url"].startswith("https://") and note["source_location"]
                   and note["rights_basis"] == "NASA_WEB_FACT_PARAPHRASE_ONLY"
                   and note["rights_guidance_url"].startswith("https://www.nasa.gov/")
                   for note in notes)
        assert len(store.documentary_notes("Mir", domain_id="historical")) == 2
        assert store.documentary_notes("Mir", domain_id="combustion") == []


def test_routing_admits_mir_but_never_invents_other_incident_or_experiment():
    with ResearchStore() as store:
        mir = retrieve_evidence(store, "What happened during the Mir station fire?")
        apollo = retrieve_evidence(store, "What happened in Apollo 1?")
        missing = retrieve_evidence(store, "What happened during the 1978 Cosmos station fire?")
        flex = retrieve_evidence(store, "What happened in FLEX Test 054?")
        transfer = retrieve_evidence(store, "What was the NASA Fire Detector spinoff?")
        with pytest.raises(ResearchError, match="historical incidents"):
            retrieve_evidence(store, "What happened in the Mir fire?", investigation_id="FLEX")
    assert mir["supported"] and {item["source_key"] for item in mir["items"]} == {"MIR-1997"}
    assert all(item["kind"] == "documentary_note" for item in mir["items"])
    assert apollo["supported"] and {item["source_key"] for item in apollo["items"]} == {"APOLLO-1"}
    assert not missing["supported"] and not any(i["kind"] == "experiment" for i in missing["items"])
    assert flex["supported"] and all(item["source_key"] != "MIR-1997" for item in flex["items"])
    assert transfer["supported"] and {item["source_key"] for item in transfer["items"]} == {"SPINOFF-DETECTOR"}


def test_mir_grounded_claim_cites_actual_historical_page():
    class Adapter:
        settings = type("Settings", (), {"configured": True})()

        def complete(self, _messages):
            raw = json.dumps({"claims": [{"text": "The Kvant-1 module fire ignited on 24 February 1997.",
                                          "citations": ["E1"]}]})
            return GroqResult("model", raw, "ok", "mock", 1.0, 1)

    with ResearchStore() as store:
        packet = retrieve_evidence(store, "What happened during the Mir station fire?")
    result = grounded_from_packet(packet, Adapter())
    assert result.mode == "model" and result.citations[0]["source_key"] == "MIR-1997"
    assert result.citations[0]["source_url"].endswith("fire-aboard-space-station-mir/")


def test_catalogue_only_and_rejected_candidates_remain_excluded(tmp_path):
    queue = tmp_path / "review.jsonl"
    candidate = {"url": "https://science.nasa.gov/research/proposed-source/",
                 "title": "Proposed research source", "domain_id": "combustion", "topic_id": "droplet"}
    with ResearchStore() as store:
        staged = stage_candidate(candidate, queue, store)
        assert staged["status"] == "PENDING_RIGHTS_AND_SCIENCE_REVIEW"
        assert stage_candidate(candidate, queue, store) == staged
        assert stage_candidate({**candidate, "url": store.source("MIR-1997")["url"]}, queue, store)["status"] == "ALREADY_CATALOGUED"
        with pytest.raises(ValueError, match="official HTTPS NASA host"):
            stage_candidate({**candidate, "url": "https://example.org/claim"}, queue, store)
        rejected = reject_candidate(staged["id"], queue, "Source identity remains unverified")
        assert rejected["status"] == "REJECTED"
        assert store.db.execute("SELECT count(*) FROM source_catalogue WHERE url=?", (candidate["url"],)).fetchone()[0] == 0
        assert all(store.source(key)["admission_status"] == "CATALOGUE_ONLY"
                   and store.documentary_notes(source_key=key) == []
                   for key in ("NASA-ACME", "NASA-FLEX-2", "PDF-4"))


def test_migration_is_idempotent_and_does_not_duplicate_admissions(tmp_path):
    destination = tmp_path / "repeat.db.gz"
    result = migrate(DEFAULT_ARCHIVE, destination)
    assert result["notes"] == 10
    assert result["core_hashes"] == EXPECTED_CORE
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == hashlib.sha256(DEFAULT_ARCHIVE.read_bytes()).hexdigest()
    with ResearchStore(destination) as store:
        assert store.db.execute("SELECT count(*) FROM admission_audit").fetchone()[0] == 10
        assert store.db.execute("SELECT count(*) FROM corpus_versions").fetchone()[0] == 1
