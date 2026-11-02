"""SQLite translation memory, glossary overrides and job index."""
import hashlib
import sqlite3
import time

from . import config
from .textutil import norm_key

SCHEMA = """
CREATE TABLE IF NOT EXISTS tm (
  id INTEGER PRIMARY KEY,
  lang TEXT NOT NULL,
  src_hash TEXT NOT NULL,
  source TEXT NOT NULL,
  target TEXT NOT NULL,
  origin TEXT NOT NULL,
  created REAL NOT NULL,
  UNIQUE(lang, src_hash)
);
CREATE VIRTUAL TABLE IF NOT EXISTS tm_fts USING fts5(source, target, content='tm', content_rowid='id');
CREATE TRIGGER IF NOT EXISTS tm_ai AFTER INSERT ON tm BEGIN
  INSERT INTO tm_fts(rowid, source, target) VALUES (new.id, new.source, new.target);
END;
CREATE TRIGGER IF NOT EXISTS tm_ad AFTER DELETE ON tm BEGIN
  INSERT INTO tm_fts(tm_fts, rowid, source, target) VALUES ('delete', old.id, old.source, old.target);
END;
CREATE TABLE IF NOT EXISTS overrides (
  lang TEXT NOT NULL,
  en_key TEXT NOT NULL,
  en TEXT NOT NULL,
  target TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  created REAL NOT NULL,
  PRIMARY KEY (lang, en_key)
);
CREATE TABLE IF NOT EXISTS jobs (
  doc_id TEXT PRIMARY KEY,
  lang TEXT NOT NULL,
  source_path TEXT,
  output_path TEXT,
  segments INTEGER,
  created REAL NOT NULL
);
"""


def src_hash(text: str) -> str:
    return hashlib.sha1(norm_key(text).encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path=None):
        self.path = path or (config.HOME / "urim.sqlite")
        if str(self.path) != ":memory:":
            config.HOME.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    # ---- translation memory
    def tm_get(self, lang: str, source: str):
        r = self.db.execute("SELECT target, origin FROM tm WHERE lang=? AND src_hash=?",
                            (lang, src_hash(source))).fetchone()
        return (r["target"], r["origin"]) if r else None

    def tm_put(self, lang: str, source: str, target: str, origin: str, commit=True):
        h = src_hash(source)
        old = self.db.execute("SELECT id FROM tm WHERE lang=? AND src_hash=?", (lang, h)).fetchone()
        if old:
            self.db.execute("DELETE FROM tm WHERE id=?", (old["id"],))
        self.db.execute("INSERT INTO tm(lang, src_hash, source, target, origin, created) VALUES (?,?,?,?,?,?)",
                        (lang, h, norm_key(source), target, origin, time.time()))
        if commit:
            self.db.commit()

    def tm_search(self, query: str, lang=None, origin=None, limit=10):
        q = " ".join(f'"{w}"' for w in query.replace('"', " ").split())
        if not q:
            return []
        sql = ("SELECT tm.lang, tm.source, tm.target, tm.origin FROM tm_fts JOIN tm ON tm.id = tm_fts.rowid "
               "WHERE tm_fts MATCH ?")
        args = [q]
        if lang:
            sql += " AND tm.lang=?"
            args.append(lang)
        if origin:
            sql += " AND tm.origin=?"
            args.append(origin)
        sql += " ORDER BY rank LIMIT ?"
        args.append(limit)
        return [dict(r) for r in self.db.execute(sql, args)]

    def tm_stats(self):
        return {f'{r["lang"]}:{r["origin"]}': r["n"] for r in self.db.execute(
            "SELECT lang, origin, COUNT(*) n FROM tm GROUP BY lang, origin")}

    # ---- glossary overrides
    def overrides(self, lang: str):
        return [dict(r) for r in self.db.execute("SELECT en, target, note FROM overrides WHERE lang=?", (lang,))]

    def override_put(self, lang, en, target, note=""):
        from .textutil import fold
        self.db.execute("INSERT OR REPLACE INTO overrides(lang, en_key, en, target, note, created) VALUES (?,?,?,?,?,?)",
                        (lang, fold(en).strip(), en, target, note, time.time()))
        self.db.commit()

    def override_delete(self, lang, en) -> bool:
        from .textutil import fold
        n = self.db.execute("DELETE FROM overrides WHERE lang=? AND en_key=?", (lang, fold(en).strip())).rowcount
        self.db.commit()
        return bool(n)

    # ---- jobs
    def job_put(self, doc_id, lang, source_path, output_path, segments):
        self.db.execute("INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?)",
                        (doc_id, lang, source_path, output_path, segments, time.time()))
        self.db.commit()

    def job_get(self, doc_id):
        r = self.db.execute("SELECT * FROM jobs WHERE doc_id=?", (doc_id,)).fetchone()
        return dict(r) if r else None
