# Co-authored with ChatGPT
"""Apply the reviewed Phase 4D documentary admission manifest to a copy.

Run: python migrations/phase4d.py INPUT.db.gz OUTPUT.db.gz
The input is never modified; the output must not exist.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research" / "phase4d_admissions.json"
CORE_TABLES = ("sources", "experiments", "measurements", "passages")


def row_hash(db: sqlite3.Connection, table: str) -> str:
    digest = hashlib.sha256()
    for row in db.execute(f"SELECT * FROM {table} ORDER BY rowid"):
        digest.update(repr(tuple(row)).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def migrate(source: Path, destination: Path) -> dict:
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to replace existing archive: {destination}")
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    db = sqlite3.connect(":memory:")
    db.deserialize(gzip.decompress(source.read_bytes()))
    db.execute("PRAGMA foreign_keys=ON")
    before = {table: row_hash(db, table) for table in CORE_TABLES}
    try:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS documentary_evidence(
            id INTEGER PRIMARY KEY,
            source_key TEXT NOT NULL REFERENCES source_catalogue(key),
            source_location TEXT NOT NULL,
            summary TEXT NOT NULL,
            topic_id TEXT NOT NULL REFERENCES research_topics(id),
            rights_basis TEXT NOT NULL,
            rights_guidance_url TEXT NOT NULL,
            verification_status TEXT NOT NULL CHECK(verification_status='SOURCE_CHECKED'),
            review_method TEXT NOT NULL CHECK(review_method='MANUAL_SOURCE_COMPARISON_BY_AGENT'),
            checked_on TEXT NOT NULL,
            summary_sha256 TEXT NOT NULL UNIQUE,
            UNIQUE(source_key,source_location)
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS documentary_evidence_fts USING fts5(
            summary, content='documentary_evidence', content_rowid='id'
        );
        CREATE TRIGGER IF NOT EXISTS documentary_evidence_insert AFTER INSERT ON documentary_evidence BEGIN
            INSERT INTO documentary_evidence_fts(rowid,summary) VALUES(new.id,new.summary);
        END;
        CREATE TABLE IF NOT EXISTS corpus_versions(
            version TEXT PRIMARY KEY,
            checked_on TEXT NOT NULL,
            manifest_sha256 TEXT NOT NULL,
            admitted_notes INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS admission_audit(
            id INTEGER PRIMARY KEY,
            version TEXT NOT NULL REFERENCES corpus_versions(version),
            source_key TEXT NOT NULL REFERENCES source_catalogue(key),
            summary_sha256 TEXT NOT NULL UNIQUE,
            decision TEXT NOT NULL CHECK(decision='ADMITTED_CURATED'),
            checked_on TEXT NOT NULL
        );
        """)
        with db:
            for candidate in manifest["catalogue_only"]:
                if candidate["domain_id"] != db.execute(
                    "SELECT domain_id FROM research_topics WHERE id=?", (candidate["topic_id"],)
                ).fetchone()[0]:
                    raise ValueError("catalogue candidate topic/domain mismatch")
                db.execute("""INSERT OR IGNORE INTO source_catalogue
                    (key,source_id,title,publisher,url,identifier,domain_id,investigation_id,
                     primary_topic_id,source_type,verification_status,rights_status,
                     admission_status,checked_on)
                    VALUES (?,NULL,?,'NASA',?,?,?,NULL,? ,?,'VERIFIED_PAGE','REVIEW_REQUIRED',
                            'CATALOGUE_ONLY',?)""",
                    (candidate["key"], candidate["title"], candidate["url"],
                     candidate["identifier"], candidate["domain_id"], candidate["topic_id"],
                     candidate["source_type"], manifest["checked_on"]))
                row = db.execute("SELECT url,admission_status FROM source_catalogue WHERE key=?",
                                 (candidate["key"],)).fetchone()
                if row != (candidate["url"], "CATALOGUE_ONLY"):
                    raise ValueError(f"catalogue key conflict: {candidate['key']}")

            notes = manifest["notes"]
            version = manifest["version"]
            manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
            existing_version = db.execute("SELECT manifest_sha256 FROM corpus_versions WHERE version=?",
                                          (version,)).fetchone()
            if existing_version and existing_version[0] != manifest_hash:
                raise ValueError("corpus version already exists with a different manifest")
            db.execute("INSERT OR IGNORE INTO corpus_versions VALUES (?,?,?,?)",
                       (version, manifest["checked_on"], manifest_hash, len(notes)))

            for note in notes:
                source_row = db.execute("SELECT url,domain_id,source_type FROM source_catalogue WHERE key=?",
                                        (note["source_key"],)).fetchone()
                if source_row is None or not source_row[0].startswith(("https://www.nasa.gov/",
                                                                       "https://sma.nasa.gov/",
                                                                       "https://spinoff.nasa.gov/")):
                    raise ValueError(f"source is not a reviewed official NASA page: {note['source_key']}")
                topic_domain = db.execute("SELECT domain_id FROM research_topics WHERE id=?",
                                          (note["topic_id"],)).fetchone()
                if topic_domain is None or topic_domain[0] != source_row[1]:
                    raise ValueError(f"topic/domain mismatch: {note['source_key']}")
                if not 30 <= len(note["summary"]) <= 600 or "<" in note["summary"]:
                    raise ValueError("invalid factual paraphrase")
                digest = hashlib.sha256(note["summary"].encode("utf-8")).hexdigest()
                db.execute("""UPDATE source_catalogue SET verification_status='VERIFIED_PAGE',
                    rights_status=?,admission_status='DOCUMENTARY_ADMITTED',checked_on=?
                    WHERE key=?""", (manifest["rights_basis"], manifest["checked_on"], note["source_key"]))
                db.execute("""INSERT OR IGNORE INTO documentary_evidence
                    (source_key,source_location,summary,topic_id,rights_basis,rights_guidance_url,
                     verification_status,review_method,checked_on,summary_sha256)
                    VALUES (?,?,?,?,?,?,'SOURCE_CHECKED','MANUAL_SOURCE_COMPARISON_BY_AGENT',?,?)""",
                    (note["source_key"], note["location"], note["summary"], note["topic_id"],
                     manifest["rights_basis"], manifest["rights_guidance_url"],
                     manifest["checked_on"], digest))
                row = db.execute("""SELECT summary_sha256 FROM documentary_evidence
                    WHERE source_key=? AND source_location=?""",
                    (note["source_key"], note["location"])).fetchone()
                if row != (digest,):
                    raise ValueError(f"duplicate location conflict: {note['source_key']}")
                db.execute("""INSERT OR IGNORE INTO admission_audit
                    (version,source_key,summary_sha256,decision,checked_on)
                    VALUES (?,?,?,'ADMITTED_CURATED',?)""",
                    (version, note["source_key"], digest, manifest["checked_on"]))

        after = {table: row_hash(db, table) for table in CORE_TABLES}
        if before != after:
            raise ValueError("original scientific tables changed")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("database integrity check failed")
        count = db.execute("SELECT count(*) FROM documentary_evidence").fetchone()[0]
        fts = db.execute("SELECT count(*) FROM documentary_evidence_fts").fetchone()[0]
        if count != len(notes) or fts != count:
            raise ValueError("documentary evidence or FTS count mismatch")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(gzip.compress(db.serialize(), compresslevel=9, mtime=0))
        return {"version": manifest["version"], "notes": count, "core_hashes": after,
                "archive_sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(json.dumps(migrate(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))
