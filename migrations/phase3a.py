# Co-authored with ChatGPT
"""Create an independently auditable Phase 3A research catalogue.

The Phase 1 database is never modified. Run:
python migrations/phase3a.py INPUT_DB OUTPUT_DB
"""
import hashlib
import gzip
import re
import shutil
import sqlite3
import sys
from pathlib import Path

DOMAINS = {
    "combustion": "Microgravity combustion experiments",
    "detection": "Smoke detection and aerosol science",
    "background": "Scientific background and methods",
    "historical": "Historical spacecraft fire safety",
    "transfer": "NASA fire safety technology transfer",
    "engineering": "Engineering interpretation",
}
TOPICS = {
    "droplet": ("combustion", "Liquid droplet combustion"),
    "extinction": ("combustion", "Flame extinction"),
    "oxygen": ("combustion", "Oxygen concentration"),
    "pressure": ("combustion", "Atmospheric pressure"),
    "gas": ("combustion", "Gas composition"),
    "diameter": ("combustion", "Droplet diameter"),
    "burning_rate": ("combustion", "Burning-rate constant"),
    "burn_duration": ("combustion", "Burn duration"),
    "solid": ("combustion", "Solid material flammability"),
    "airflow": ("combustion", "Airflow and ventilation"),
    "flame_spread": ("combustion", "Flame spread"),
    "smoke": ("detection", "Smoke particles and aerosols"),
    "sensors": ("detection", "Fire detection instrumentation"),
    "methods": ("background", "Experimental methods"),
    "incident": ("historical", "Spacecraft fire incidents"),
    "technology": ("transfer", "Technology transfer"),
    "limitations": ("engineering", "Scientific limitations"),
}
SOURCE_CLASS = {
    1: ("background", "methods"),
    2: ("combustion", "droplet"),
    3: ("combustion", "solid"),
    4: ("combustion", "solid"),
    5: ("detection", "smoke"),
    6: ("combustion", "flame_spread"),
    7: ("combustion", "flame_spread"),
}
MEASUREMENT_TOPICS = {
    "pressure_mmhg": "pressure",
    "oxygen_mole_fraction": "oxygen",
    "nitrogen_mole_fraction": "gas",
    "carbon_dioxide_mole_fraction": "gas",
    "helium_mole_fraction": "gas",
    "initial_diameter_mm": "diameter",
    "visible_extinction_diameter_mm": "extinction",
    "burning_rate_mm2_s": "burning_rate",
    "burn_time_s": "burn_duration",
}
KEYWORDS = {
    "extinction": r"\bextinct(?:ion|uish(?:ed|ment)?)?\b",
    "oxygen": r"\boxygen\b|\bO2\b",
    "pressure": r"\bpressure\b",
    "gas": r"\bnitrogen\b|\bhelium\b|\bcarbon dioxide\b|\bCO2\b",
    "diameter": r"\bdiameter\b|\bdroplet size\b",
    "burning_rate": r"\bburning rate\b|\bburn rate\b",
    "burn_duration": r"\bburn time\b|\bburning time\b|\bduration\b",
    "airflow": r"\bairflow\b|\bflow velocity\b|\bventilation\b",
    "flame_spread": r"\bflame spread\b|\bflame propagation\b",
}
# This catalogue records discovery and rights status. Entries without admitted
# evidence remain catalogue-only; a URL never creates an experiment record.
# Fields: key, title, URL, identifier, domain, investigation, topic, verification,
# rights, source type.
WEB_SOURCES = [
    ("PSI-69", "Flame Extinguishment Experiment (FLEX)", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69", "10.60555/mbq8-0451", "combustion", "FLEX", "droplet", "VERIFIED_METADATA", "CC0-1.0", "INVESTIGATION"),
    ("PSI-25", "Burning and Suppression of Solids - II (BASS-II)", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-25", "10.60555/4qc4-de67", "combustion", "BASS-II", "solid", "VERIFIED_METADATA", "CC0-1.0", "INVESTIGATION"),
    ("PSI-98", "Spacecraft Fire Safety Experiment-I (Saffire-I)", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-98", "10.60555/0t15-1z43", "combustion", "SAFFIRE", "flame_spread", "VERIFIED_METADATA", "CC0-1.0", "INVESTIGATION"),
    ("PSI-99", "Saffire-II investigation", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-99", "PSI-99", "combustion", "SAFFIRE", "flame_spread", "IDENTIFIER_LINKED", "UNCONFIRMED", "INVESTIGATION"),
    ("PSI-100", "Saffire-III investigation", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-100", "PSI-100", "combustion", "SAFFIRE", "flame_spread", "IDENTIFIER_LINKED", "UNCONFIRMED", "INVESTIGATION"),
    ("PSI-101", "Smoke Aerosol Measurement Experiment-Reflight (SAME-R)", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-101", "10.60555/2np7-jv14", "detection", "SAME", "smoke", "VERIFIED_METADATA", "CC0-1.0", "INVESTIGATION"),
    ("PSI-107", "Smoke Point In Co-flow Experiment (SPICE)", "https://psi.nasa.gov/physci/repo/data/investigations/PSI-107", "10.60555/9kbh-e962", "combustion", "SPICE", "flame_spread", "VERIFIED_METADATA", "CC0-1.0", "INVESTIGATION"),
    ("NASA-COMBUSTION", "Combustion Science", "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/", "NASA web page", "background", None, "methods", "VERIFIED_PAGE", "REVIEW_REQUIRED", "BACKGROUND"),
    ("NASA-SCIENCECASTS", "The Power of Studying Combustion on the ISS", "https://www.youtube.com/watch?v=W1oXykoz9zg", "NASA ScienceCasts video", "background", None, "methods", "URL_LISTED", "UNCONFIRMED", "VIDEO"),
    ("NASA-GUIDE", "A Researcher's Guide to Combustion Science", "https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/", "NASA research guide", "background", None, "methods", "VERIFIED_PAGE", "REVIEW_REQUIRED", "BACKGROUND"),
    ("APOLLO-1", "Apollo 1 AS-204", "https://sma.nasa.gov/sma-disciplines/accllp/apollo-1", "Apollo 1", "historical", None, "incident", "VERIFIED_PAGE", "REVIEW_REQUIRED", "INCIDENT"),
    ("APOLLO-13", "Apollo 13", "https://sma.nasa.gov/sma-disciplines/accllp/apollo-13", "Apollo 13", "historical", None, "incident", "URL_LISTED", "REVIEW_REQUIRED", "INCIDENT"),
    ("MIR-1997", "25 Years Ago: Fire Aboard Space Station Mir", "https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/", "Mir 1997", "historical", None, "incident", "VERIFIED_PAGE", "REVIEW_REQUIRED", "INCIDENT"),
    ("SPINOFF-TANKS", "Fireman's Air Tanks", "https://spinoff.nasa.gov/node/9582", "NASA Spinoff 1976", "transfer", None, "technology", "VERIFIED_PAGE", "REVIEW_REQUIRED", "TECH_TRANSFER"),
    ("SPINOFF-DETECTOR", "Fire Detector", "https://spinoff.nasa.gov/node/9407", "NASA Spinoff 1978", "transfer", None, "technology", "VERIFIED_PAGE", "REVIEW_REQUIRED", "TECH_TRANSFER"),
    ("SPINOFF-ATTIRE", "New Technology for the Fire Attire", "https://spinoff.nasa.gov/node/9918", "NASA Spinoff 1982", "transfer", None, "technology", "VERIFIED_PAGE", "REVIEW_REQUIRED", "TECH_TRANSFER"),
]
# Paraphrases of CC0 investigation objectives only, not transcribed raw records.
CURATED_EVIDENCE = {
    "PSI-69": ("Objectives", "FLEX studies liquid-fuel droplet burning and extinction under varied ambient and suppressant conditions."),
    "PSI-25": ("Objectives", "BASS-II studies ignition, flame growth, spread and extinction of solid fuels in low-speed forced flows."),
    "PSI-98": ("Objectives", "Saffire-I examines larger-scale fire growth and material flammability in low gravity."),
    "PSI-101": ("Objectives", "SAME-R investigates smoke-particle size and its relationship to generation and transport conditions."),
    "PSI-107": ("Objectives", "SPICE studies smoke-point properties of non-buoyant jet diffusion flames under co-flow conditions."),
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def migrate(source: Path, destination: Path):
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to replace existing database: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = destination.with_name(destination.stem + "_pre3a_backup.db")
    if backup.exists():
        raise FileExistsError(f"Refusing to replace backup: {backup}")
    shutil.copy2(source, backup)
    assert digest(source) == digest(backup)
    shutil.copy2(source, destination)
    db = sqlite3.connect(destination)
    db.execute("PRAGMA foreign_keys=ON")
    try:
        with db:
            db.executescript("""
            CREATE TABLE research_domains(
                id TEXT PRIMARY KEY, label TEXT NOT NULL UNIQUE
            );
            CREATE TABLE research_topics(
                id TEXT PRIMARY KEY, domain_id TEXT NOT NULL REFERENCES research_domains(id),
                label TEXT NOT NULL UNIQUE
            );
            CREATE TABLE source_catalogue(
                key TEXT PRIMARY KEY, source_id INTEGER REFERENCES sources(id),
                title TEXT NOT NULL, publisher TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
                identifier TEXT, domain_id TEXT NOT NULL REFERENCES research_domains(id),
                investigation_id TEXT REFERENCES investigations(id),
                primary_topic_id TEXT NOT NULL REFERENCES research_topics(id),
                source_type TEXT NOT NULL, verification_status TEXT NOT NULL,
                rights_status TEXT NOT NULL, admission_status TEXT NOT NULL,
                checked_on TEXT NOT NULL
            );
            CREATE INDEX catalogue_scope ON source_catalogue(domain_id,investigation_id,primary_topic_id);
            CREATE TABLE passage_topics(
                passage_id INTEGER NOT NULL REFERENCES passages(id),
                topic_id TEXT NOT NULL REFERENCES research_topics(id),
                assignment_method TEXT NOT NULL,
                PRIMARY KEY(passage_id,topic_id)
            );
            CREATE INDEX passage_topic_scope ON passage_topics(topic_id,passage_id);
            CREATE TABLE measurement_topics(
                measurement_id INTEGER PRIMARY KEY REFERENCES measurements(id),
                topic_id TEXT NOT NULL REFERENCES research_topics(id)
            );
            CREATE INDEX measurement_topic_scope ON measurement_topics(topic_id,measurement_id);
            CREATE TABLE experiment_topics(
                experiment_id TEXT NOT NULL REFERENCES experiments(id),
                topic_id TEXT NOT NULL REFERENCES research_topics(id),
                PRIMARY KEY(experiment_id,topic_id)
            );
            CREATE INDEX experiment_topic_scope ON experiment_topics(topic_id,experiment_id);
            CREATE TABLE catalogue_evidence(
                id INTEGER PRIMARY KEY, catalogue_key TEXT NOT NULL REFERENCES source_catalogue(key),
                source_location TEXT NOT NULL, summary TEXT NOT NULL,
                evidence_kind TEXT NOT NULL CHECK(evidence_kind='PARAPHRASED_OBJECTIVE'),
                UNIQUE(catalogue_key,source_location)
            );
            CREATE TABLE investigation_coverage(
                investigation_id TEXT PRIMARY KEY REFERENCES investigations(id),
                admitted_experiments INTEGER NOT NULL,
                admitted_passages INTEGER NOT NULL,
                coverage_note TEXT NOT NULL
            );
            """)
            db.executemany("INSERT INTO research_domains VALUES (?,?)", DOMAINS.items())
            db.executemany("INSERT INTO research_topics VALUES (?,?,?)",
                           ((key, domain, label) for key, (domain, label) in TOPICS.items()))
            db.execute("INSERT INTO investigations(id,name,doi,psi_url) VALUES (?,?,?,?)",
                       ("SPICE", "SPICE", "10.60555/9kbh-e962", WEB_SOURCES[6][2]))
            for sid, title, url, status, rights, investigation in db.execute(
                "SELECT id,title,source_url,status,rights,investigation_id FROM sources"
            ).fetchall():
                domain, topic = SOURCE_CLASS[sid]
                db.execute(
                    "INSERT INTO source_catalogue VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (f"PDF-{sid}", sid, title, "NASA NTRS / supplied NASA PDF",
                     url, title, domain, investigation, topic, "PDF",
                     status, rights, "PASSAGES_ADMITTED" if sid in (2, 3) else "CATALOGUE_ONLY",
                     "2026-11-14"),
                )
            for key, title, url, identifier, domain, investigation, topic, verified, rights, kind in WEB_SOURCES:
                db.execute(
                    "INSERT INTO source_catalogue VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (key, None, title, "NASA" if "youtube.com" not in url else "NASA channel unverified",
                     url, identifier, domain, investigation, topic, kind, verified, rights,
                     "EVIDENCE_SUMMARY" if key in CURATED_EVIDENCE else "CATALOGUE_ONLY", "2026-11-14"),
                )
            for key, (location, summary) in CURATED_EVIDENCE.items():
                db.execute("INSERT INTO catalogue_evidence(catalogue_key,source_location,summary,evidence_kind) VALUES (?,?,?,'PARAPHRASED_OBJECTIVE')",
                           (key, location, summary))
            for passage_id, source_id, text in db.execute("SELECT id,source_id,text FROM passages"):
                domain, base_topic = SOURCE_CLASS[source_id]
                db.execute("INSERT INTO passage_topics VALUES (?,?,?)",
                           (passage_id, base_topic, "SOURCE_SCOPE"))
                for topic, pattern in KEYWORDS.items():
                    if TOPICS[topic][0] == domain and topic != base_topic and re.search(pattern, text, re.I):
                        db.execute("INSERT OR IGNORE INTO passage_topics VALUES (?,?,?)",
                                   (passage_id, topic, "KEYWORD_IN_TEXT"))
            for mid, experiment_id, variable in db.execute(
                "SELECT id,experiment_id,variable FROM measurements"
            ):
                topic = MEASUREMENT_TOPICS[variable]
                db.execute("INSERT INTO measurement_topics VALUES (?,?)", (mid, topic))
                db.execute("INSERT OR IGNORE INTO experiment_topics VALUES (?,?)",
                           (experiment_id, topic))
                db.execute("INSERT OR IGNORE INTO experiment_topics VALUES (?,?)",
                           (experiment_id, "droplet"))
            coverage_notes = {
                "FLEX": "Validated NASA report Table IX subset; original PSI telemetry not acquired.",
                "BASS-II": "Documentary PDF passages only; no validated numerical rows admitted.",
                "SAFFIRE": "Source references only; no validated numerical rows or passages admitted.",
                "SAME": "Source references only; no validated numerical rows or passages admitted.",
                "SPICE": "Verified PSI investigation metadata and objective summary only.",
            }
            for investigation, note in coverage_notes.items():
                experiments = db.execute(
                    "SELECT count(*) FROM experiments WHERE investigation_id=?", (investigation,)
                ).fetchone()[0]
                passages = db.execute(
                    "SELECT count(*) FROM passages p JOIN sources s ON s.id=p.source_id WHERE s.investigation_id=?",
                    (investigation,),
                ).fetchone()[0]
                db.execute("INSERT INTO investigation_coverage VALUES (?,?,?,?)",
                           (investigation, experiments, passages, note))
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert not db.execute("PRAGMA foreign_key_check").fetchall()
    finally:
        db.close()
    archive = destination.with_suffix(destination.suffix + ".gz")
    with destination.open("rb") as raw, archive.open("wb") as compressed:
        with gzip.GzipFile(filename="", fileobj=compressed, mode="wb", mtime=0, compresslevel=9) as stream:
            shutil.copyfileobj(raw, stream)
    print(f"Created {destination}; intact original backup {backup}; portable archive {archive}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python migrations/phase3a.py INPUT_DB OUTPUT_DB")
    migrate(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())