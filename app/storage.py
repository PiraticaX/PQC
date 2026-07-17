import sqlite3
from pathlib import Path
from threading import Lock

DB_PATH = Path(__import__("os").environ.get("QSHIELD_DB_PATH", str(Path(__file__).with_name("qshield.db"))))
_lock = Lock()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, url TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id INTEGER NOT NULL, status TEXT NOT NULL, readiness INTEGER, result_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(asset_id) REFERENCES assets(id))")


def list_assets():
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute("SELECT id,name,url,status,created_at FROM assets ORDER BY id DESC")]


def add_asset(name: str, url: str):
    with _lock, sqlite3.connect(DB_PATH) as db:
        cur = db.execute("INSERT INTO assets(name,url) VALUES(?,?)", (name, url))
        return {"id": cur.lastrowid, "name": name, "url": url, "status": "pending"}


def get_asset(asset_id: int):
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT id,name,url,status,created_at FROM assets WHERE id=?", (asset_id,)).fetchone()
        return dict(row) if row else None


def set_asset_status(asset_id: int, status: str):
    with _lock, sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE assets SET status=? WHERE id=?", (status, asset_id))


def save_scan(asset_id: int, status: str, readiness: int | None, result_json: str):
    with _lock, sqlite3.connect(DB_PATH) as db:
        cur = db.execute("INSERT INTO scans(asset_id,status,readiness,result_json) VALUES(?,?,?,?)", (asset_id, status, readiness, result_json))
        return cur.lastrowid


def latest_scan(asset_id: int):
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT id,asset_id,status,readiness,result_json,created_at FROM scans WHERE asset_id=? ORDER BY id DESC LIMIT 1", (asset_id,)).fetchone()
        return dict(row) if row else None
