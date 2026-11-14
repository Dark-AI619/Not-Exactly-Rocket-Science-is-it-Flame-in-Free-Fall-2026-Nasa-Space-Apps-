# Co-authored with ChatGPT
"""Assistant and Solution Lab share bounded generation and deterministic fallback."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

from backend import GroqResult, ResearchStore, research_turn, retrieve_evidence


class MockAdapter:
    def __init__(self, text=None, *, configured=True, status="ok", limit=2):
        self.settings = SimpleNamespace(configured=configured, session_request_limit=limit)
        self.text = text
        self.status = status
        self.complete = Mock(side_effect=self._complete)

    def _complete(self, messages):
        return GroqResult("model" if self.status == "ok" else "evidence_only",
                          self.text if self.status == "ok" else None,
                          self.status, "mock-model", 1.0, 1)


def test_chat_turn_keeps_scope_history_and_source_citations():
    answer = json.dumps({"claims": [{"text": "FLEX Test 054 used Methanol and ended in Extinction.",
                                      "citations": ["E1"]}]})
    adapter = MockAdapter(answer)
    with ResearchStore() as store:
        packet = retrieve_evidence(store, "What happened in FLEX Test 054?", investigation_id="FLEX")
    result, used = research_turn(packet, adapter, 0, history=("Earlier FLEX question",))
    assert used == 1 and result.mode == "model"
    assert result.claims[0].endswith("[E1]")
    assert result.citations[0]["experiment_id"].endswith("054")
    prompt = json.loads(adapter.complete.call_args.args[0][1]["content"])
    assert prompt["prior_questions"] == ["Earlier FLEX question"]
    assert {e["investigation"] for e in prompt["evidence"]} == {"FLEX"}


def test_session_limit_and_provider_failure_keep_verified_packet():
    with ResearchStore() as store:
        packet = retrieve_evidence(store, "What is flame extinction in FLEX?")
    adapter = MockAdapter(status="rate_limited", limit=1)
    failed, used = research_turn(packet, adapter, 0)
    assert failed.status == "rate_limited" and failed.evidence_packet is packet and used == 1
    limited, used = research_turn(packet, adapter, used)
    assert limited.status == "session_limit" and limited.evidence_packet is packet and used == 1
    assert adapter.complete.call_count == 1


def test_missing_key_and_missing_evidence_do_not_spend_request():
    with ResearchStore() as store:
        flex = retrieve_evidence(store, "What is flame extinction in FLEX?")
        mir = retrieve_evidence(store, "What happened during the Mir station fire?")
    adapter = MockAdapter(configured=False)
    no_key, used = research_turn(flex, adapter, 0)
    assert no_key.status == "missing_key" and used == 0
    missing, used = research_turn(mir, MockAdapter(), 0)
    assert missing.status == "missing_evidence" and used == 0
    adapter.complete.assert_not_called()
