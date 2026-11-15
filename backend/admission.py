# Co-authored with ChatGPT
"""Local candidate staging only; this module cannot admit records to the corpus."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from .store import ResearchStore


def _candidate_id(url: str) -> str:
    return hashlib.sha256(url.rstrip("/").casefold().encode("utf-8")).hexdigest()


def _load_queue(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stage_candidate(candidate: dict, queue_path: Path, store: ResearchStore) -> dict:
    """Record a NASA URL for later human review, with no database mutation."""
    url = str(candidate.get("url", "")).strip()
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or not (
        parsed.hostname == "nasa.gov" or parsed.hostname.endswith(".nasa.gov")
    ) or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("candidate must use an official HTTPS NASA host")
    title = str(candidate.get("title", "")).strip()
    if not 5 <= len(title) <= 200:
        raise ValueError("candidate title must contain 5–200 characters")
    domain = candidate.get("domain_id")
    topic = candidate.get("topic_id")
    if domain not in {item["id"] for item in store.domains()} or not any(
        item["id"] == topic and item["domain_id"] == domain for item in store.topics()
    ):
        raise ValueError("candidate topic must belong to its research domain")
    if any(item["url"].rstrip("/").casefold() == url.rstrip("/").casefold()
           for item in store.sources(limit=100)):
        return {"status": "ALREADY_CATALOGUED", "url": url}
    identifier = _candidate_id(url)
    queue = _load_queue(queue_path)
    existing = next((item for item in queue if item["id"] == identifier), None)
    if existing:
        return existing
    record = {"id": identifier, "url": url, "title": title, "domain_id": domain,
              "topic_id": topic, "status": "PENDING_RIGHTS_AND_SCIENCE_REVIEW",
              "rights_status": "UNCONFIRMED", "requested_by": "local_research_request"}
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def reject_candidate(identifier: str, queue_path: Path, reason: str) -> dict:
    """Mark a staged candidate rejected; neither action touches the corpus."""
    queue = _load_queue(queue_path)
    if not 5 <= len(reason.strip()) <= 300:
        raise ValueError("rejection reason must contain 5–300 characters")
    record = next((item for item in queue if item["id"] == identifier), None)
    if record is None:
        raise ValueError("unknown staged candidate")
    record["status"] = "REJECTED"
    record["review_note"] = reason.strip()
    queue_path.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in queue) + "\n",
                          encoding="utf-8")
    return record
