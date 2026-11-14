# Co-authored with ChatGPT
"""Bounded, category-routed retrieval of admitted research evidence."""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Protocol

from .store import ResearchError, ResearchStore


class OptionalLLMProvider(Protocol):
    """Future opt-in generator; no provider is configured or invoked in Phase 3."""

    def draft(self, question: str, evidence_packet: dict) -> str: ...


ALIASES = {
    "FLEX": (r"\bflex(?:[\s-]?1)?\b", r"flame extinguishment experiment"),
    "BASS-II": (r"\bbass[\s-]?(?:ii|2)\b", r"burning and suppression of solids"),
    "SAFFIRE": (r"\bsaffire(?:[\s-]?(?:i|ii|iii|1|2|3))?\b", r"spacecraft fire safety experiment"),
    "SAME": (r"\bsame[\s-]?r\b", r"smoke aerosol measurement"),
    "SPICE": (r"\bspice\b", r"smoke point in co.flow"),
}
TOPIC_ALIASES = {
    "oxygen": (r"\boxygen\b", r"\bo2\b", r"oxidizer"),
    "extinction": (r"extinguish", r"extinction", r"quench"),
    "burning_rate": (r"burn(?:ing)?[\s-]?rate", r"\bk[\s-]?constant\b"),
    "burn_duration": (r"burn[\s-]?(?:time|duration)", r"how long.*burn"),
    "diameter": (r"diameter", r"droplet size"),
    "pressure": (r"pressure", r"\bmmhg\b"),
    "gas": (r"atmospher", r"gas composition", r"nitrogen", r"helium", r"carbon dioxide"),
    "airflow": (r"airflow", r"ventilat", r"flow speed"),
    "flame_spread": (r"flame spread", r"propagat"),
    "solid": (r"solid material", r"flammab", r"fabric"),
    "smoke": (r"smoke", r"aerosol", r"particle"),
    "sensors": (r"sensor", r"detector", r"instrument"),
    "methods": (r"apparatus", r"method", r"diagnostic"),
    "incident": (r"\bmir\b", r"apollo", r"incident", r"station fire"),
    "technology": (r"spinoff", r"technology transfer", r"fireman"),
    "limitations": (r"limit", r"uncertain", r"caveat"),
}
TOPIC_TERMS = {
    "oxygen": "oxygen", "extinction": "extinction", "burning_rate": "burning",
    "burn_duration": "burn", "diameter": "droplet", "pressure": "pressure",
    "gas": "ambient", "airflow": "flow", "flame_spread": "flame",
    "solid": "material", "smoke": "smoke", "sensors": "sensor",
    "methods": "experiment",
}
RELATED = {
    "oxygen": ("gas", "extinction"), "extinction": ("oxygen", "droplet"),
    "burning_rate": ("droplet", "burn_duration"), "burn_duration": ("burning_rate", "droplet"),
    "diameter": ("droplet", "burn_duration"), "smoke": ("sensors",),
    "sensors": ("smoke",), "airflow": ("solid", "flame_spread"),
}
STOPWORDS = {"what", "which", "where", "when", "does", "about", "show", "tell", "during",
             "the", "and", "with", "from", "have", "there", "were", "their", "these", "those",
             "into", "that", "this", "research", "evidence", "effect", "affect", "compare",
             "versus", "between", "data", "source", "measurements", "experiment", "test"}


@lru_cache(maxsize=128)
def route_question(question: str) -> dict:
    if not question.strip() or len(question) > 600:
        raise ResearchError("question must contain 1–600 characters")
    text = question.casefold()
    investigations = tuple(key for key, patterns in ALIASES.items()
                           if any(re.search(pattern, text) for pattern in patterns))
    if re.search(r"\bSAME\b", question) and "SAME" not in investigations:
        investigations += ("SAME",)
    topics = tuple(key for key, patterns in TOPIC_ALIASES.items()
                   if any(re.search(pattern, text) for pattern in patterns))
    if re.search(r"\bmir\b|apollo|station fire", text):
        domain = "historical"
    elif re.search(r"technology transfer|spinoff|fireman", text):
        domain = "transfer"
    elif "SAME" in investigations or any(t in topics for t in ("smoke", "sensors")):
        domain = "detection"
    elif any(t in topics for t in ("methods", "limitations")) and not investigations:
        domain = "background"
    else:
        domain = "combustion"
    if re.search(r"\b(compare|versus|vs\.?|difference)\b", text) or len(investigations) > 1:
        intent = "comparison"
    elif re.search(r"\b(design|solution|prevent|suppress|hazard)\b", text):
        intent = "engineering"
    elif re.search(r"\b(measur\w*|value\w*|number\w*|test[\s-]*\d+|rate\w*|duration)\b", text):
        intent = "measurement"
    else:
        intent = "research"
    match = re.search(r"\b(?:flex[\s–-]*(?:test[\s–-]*)?|test[\s–-]*)0*(\d{1,3})\b", text)
    test_number = int(match.group(1)) if match else None
    return {"intent": intent, "domain": domain, "investigations": investigations,
            "topics": topics, "test_number": test_number}


def _search_terms(question: str, topics: tuple[str, ...]) -> list[str]:
    terms = [TOPIC_TERMS[t] for t in topics if t in TOPIC_TERMS]
    words = re.findall(r"[a-z]{4,}", question.casefold())
    terms.extend(word for word in words if word not in STOPWORDS
                 and not any(re.search(p, word) for patterns in ALIASES.values() for p in patterns))
    return list(dict.fromkeys(terms))[:3]


def _source_map(store: ResearchStore) -> dict[str, dict]:
    return {item["url"]: item for item in store.sources(limit=100)}


def retrieve_evidence(
    store: ResearchStore, question: str, *, domain_id: str | None = None,
    investigation_id: str | None = None, topic_id: str | None = None,
) -> dict:
    """Return a small citation-ready packet; no model or external API is called."""
    route = route_question(question).copy()
    domains = {row["id"] for row in store.domains()}
    topics_available = {row["id"]: row["domain_id"] for row in store.topics()}
    investigations_available = {row["id"] for row in store.investigations()}
    if domain_id is not None and domain_id not in domains:
        raise ResearchError("unknown research domain")
    if investigation_id is not None and investigation_id not in investigations_available:
        raise ResearchError("unknown investigation")
    if topic_id is not None and topic_id not in topics_available:
        raise ResearchError("unknown topic")
    if investigation_id is not None:
        route["investigations"] = (investigation_id,)
    if domain_id is not None:
        route["domain"] = domain_id
    elif investigation_id == "SAME":
        route["domain"] = "detection"
    if topic_id is not None:
        route["topics"] = (topic_id,)
        if domain_id is None and investigation_id is None:
            route["domain"] = topics_available[topic_id]
    if domain_id and topic_id and topics_available[topic_id] != domain_id:
        raise ResearchError("topic does not belong to selected domain")

    scopes = list(route["investigations"])
    if not scopes and route["domain"] in ("combustion", "detection"):
        scopes = [row["id"] for row in store.investigations(route["domain"])
                  if row["admitted_passages"] or row["admitted_experiments"]][:3]
    sources_by_url = _source_map(store)
    items: list[dict] = []
    notices: list[str] = []
    expansions: list[str] = []
    terms = _search_terms(question, route["topics"])
    primary_topic = topic_id or next((t for t in route["topics"] if t in topics_available), None)

    for investigation in scopes:
        coverage = store.coverage(investigation)
        if coverage["admitted_experiments"] == 0:
            notices.append(f"{investigation}: no validated numerical experiment rows are admitted.")
        if investigation == "FLEX" and route["test_number"] is not None:
            suffix = f'{route["test_number"]:03d}'
            matching = [row for row in store.experiments(investigation_id="FLEX", test_query=suffix, limit=20)
                        if row["original_test_id"].endswith(suffix)]
            if matching:
                experiment = store.experiment(matching[0]["id"])
                provenance = store.provenance(experiment["id"])
                items.append({"kind": "experiment", "investigation_id": "FLEX",
                              "source_title": provenance["source_title"], "source_identifier": "NASA/TP-2015-216046",
                              "source_url": provenance["source_url"], "source_key": "PDF-2",
                              "verification_status": provenance["validation_status"],
                              "location": f'Appendix A, Table IX; PDF page {provenance["first_pdf_page"]}',
                              "experiment_id": experiment["original_test_id"],
                              "text": f'{experiment["fuel"]}; reported outcome {experiment["test_end"]}; date {experiment["test_date"]}.',
                              "measurements": [{"variable": m["variable"], "original_value": m["original_value"],
                                                "original_unit": m["original_unit"], "classification": m["classification"],
                                                "uncertainty": m["uncertainty"], "page": m["page"]}
                                               for m in experiment["measurements"]]})
            else:
                notices.append(f'FLEX test {suffix}: no validated record is present in the admitted subset.')

        if coverage["admitted_passages"] and not (investigation == "FLEX" and route["test_number"] is not None and not route["topics"]):
            hits = []
            # Two topic words at most; fall back one term at a time within this investigation.
            candidates = [" ".join(terms[:2])] if terms else []
            candidates.extend(terms)
            for phrase in dict.fromkeys(candidates):
                if not phrase:
                    continue
                hits = store.passages(phrase, investigation_id=investigation,
                                      topic_id=primary_topic, limit=3)
                if hits:
                    break
            if not hits and primary_topic and topic_id is None:
                for related in RELATED.get(primary_topic, ()):
                    hits = store.passages(TOPIC_TERMS.get(related, related),
                                          investigation_id=investigation, topic_id=related, limit=3)
                    if hits:
                        expansions.append(f"{investigation}: expanded from {primary_topic} to related topic {related}.")
                        break
            if not hits and terms:
                hits = store.passages(terms[0], investigation_id=investigation, limit=3)
                if hits and primary_topic:
                    expansions.append(f"{investigation}: broadened from topic {primary_topic} to the investigation's verified passages.")
            for hit in hits:
                source = sources_by_url.get(hit["source_url"], {})
                items.append({"kind": "passage", "investigation_id": investigation,
                              "source_title": hit["source_title"], "source_identifier": source.get("identifier") or hit["source_title"],
                              "source_url": hit["source_url"], "source_key": source.get("key"),
                              "verification_status": source.get("verification_status", "VERIFIED"),
                              "location": f'PDF page {hit["page"]}', "experiment_id": None,
                              "text": hit["excerpt"], "measurements": []})
            if not hits:
                notices.append(f"{investigation}: no admitted PDF passage matched this topic and question.")

        # Objective summaries are admitted separately from full document passages.
        for source in store.sources(investigation_id=investigation, admitted_only=True):
            if source["admission_status"] != "EVIDENCE_SUMMARY" or source["rights_status"] != "CC0-1.0":
                continue
            for evidence in store.source_evidence(source["key"])[:1]:
                items.append({"kind": "objective_summary", "investigation_id": investigation,
                              "source_title": source["title"], "source_identifier": source["identifier"] or source["key"],
                              "source_url": source["url"], "source_key": source["key"],
                              "verification_status": source["verification_status"],
                              "location": evidence["source_location"], "experiment_id": None,
                              "text": evidence["summary"], "measurements": []})

    if not scopes or not items:
        # Catalogue pointers support discovery, never factual answers on their own.
        candidates = store.sources(domain_id=route["domain"], limit=30)
        query_words = [w for w in re.findall(r"[a-z0-9]+", question.casefold())
                       if len(w) >= 3 and w not in STOPWORDS]
        pointers = [s for s in candidates if any(w in (s["title"] + " " + s["key"]).casefold()
                                                    for w in query_words)]
        if not pointers and not scopes:
            pointers = candidates[:3]
        for source in pointers[:3]:
            if source["admission_status"] == "CATALOGUE_ONLY":
                items.append({"kind": "source_pointer", "investigation_id": source["investigation_id"],
                              "source_title": source["title"], "source_identifier": source["identifier"] or source["key"],
                              "source_url": source["url"], "source_key": source["key"],
                              "verification_status": source["verification_status"],
                              "location": "Source catalogue only", "experiment_id": None,
                              "text": "No admitted source passage or numerical record is available for a factual summary.",
                              "measurements": []})
    admitted = [item for item in items if item["kind"] != "source_pointer"]
    exact_test_missing = route["test_number"] is not None and not any(item["kind"] == "experiment" for item in items)
    if not admitted or exact_test_missing:
        notices.append("The current approved corpus cannot support a factual answer to this question.")
    return {"question": question, "route": route, "scopes": scopes, "items": items[:15],
            "notices": list(dict.fromkeys(notices)), "expansions": expansions,
            "mode": "deterministic_evidence_summary", "supported": bool(admitted) and not exact_test_missing}
