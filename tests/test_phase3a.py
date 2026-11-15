# Co-authored with ChatGPT
"""Scientific-preservation checks for the Phase 3A catalogue migration."""
import sqlite3
import unittest
import gzip
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "flame_research.db"


class Phase3AAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DB.exists():
            cls.db = sqlite3.connect(DB)
        else:
            cls.db = sqlite3.connect(":memory:")
            with gzip.open(DB.with_suffix(".db.gz"), "rb") as compressed:
                cls.db.deserialize(compressed.read())
        cls.db.execute("PRAGMA foreign_keys=ON")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def count(self, table):
        return self.db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]

    def test_original_corpus_is_intact(self):
        self.assertEqual(self.count("experiments"), 273)
        self.assertEqual(self.count("measurements"), 2457)
        self.assertEqual(self.count("passages"), 329)
        self.assertEqual(self.count("passages_fts"), 329)
        self.assertEqual(
            self.db.execute("SELECT DISTINCT data_origin,validation_status FROM experiments").fetchall(),
            [("NASA_REPORT_EXTRACTED", "VALIDATED")],
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM measurements WHERE classification='UNAVAILABLE' AND numeric_value IS NULL").fetchone()[0],
            108,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM measurements WHERE classification='UNAVAILABLE' AND numeric_value IS NOT NULL").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.execute("SELECT DISTINCT original_unit FROM measurements WHERE variable='burning_rate_mm2_s'").fetchone()[0],
            "mm²/s",
        )

    def test_integrity_and_source_links(self):
        self.assertEqual(self.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(self.count("source_catalogue"), 25)
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM source_catalogue WHERE source_id IS NOT NULL").fetchone()[0],
            7,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM catalogue_evidence").fetchone()[0],
            5,
        )
        self.assertEqual(
            self.db.execute("SELECT investigation_id,admitted_experiments,admitted_passages FROM investigation_coverage ORDER BY investigation_id").fetchall(),
            [("BASS-II", 0, 20), ("FLEX", 273, 309), ("SAFFIRE", 0, 0), ("SAME", 0, 0), ("SPICE", 0, 0)],
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM catalogue_evidence e JOIN source_catalogue c ON c.key=e.catalogue_key WHERE c.rights_status='CC0-1.0' AND c.verification_status='VERIFIED_METADATA'").fetchone()[0],
            5,
        )

    def test_retrieval_scope_and_topic_coverage(self):
        self.assertEqual(
            self.db.execute("SELECT count(DISTINCT passage_id) FROM passage_topics").fetchone()[0],
            329,
        )
        self.assertEqual(self.count("measurement_topics"), 2457)
        self.assertEqual(
            self.db.execute("SELECT count(DISTINCT experiment_id) FROM experiment_topics").fetchone()[0],
            273,
        )
        self.assertGreater(
            self.db.execute("SELECT count(*) FROM passages_fts WHERE passages_fts MATCH 'combustion'").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM passage_topics pt JOIN passages p ON p.id=pt.passage_id WHERE pt.topic_id='smoke'").fetchone()[0],
            0,
        )
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM source_catalogue WHERE key='PSI-101' AND domain_id='detection'").fetchone()[0],
            1,
        )


if __name__ == "__main__":
    unittest.main()
