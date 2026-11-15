# Co-authored with ChatGPT
"""Stage a NASA source for offline review; never admits it to the app corpus.

Run: python scripts/stage_research.py candidate.json [queue.jsonl]
Candidate JSON needs url, title, domain_id and topic_id.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.admission import stage_candidate
from backend.store import ResearchStore

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    queue = Path(sys.argv[2]) if len(sys.argv) == 3 else Path("work/research_review_queue.jsonl")
    candidate = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    with ResearchStore() as store:
        print(json.dumps(stage_candidate(candidate, queue, store), indent=2))
