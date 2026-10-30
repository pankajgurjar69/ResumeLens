import json
import os
import sqlite3
from config import Config


def connect():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            filename TEXT NOT NULL,
            target TEXT NOT NULL,
            score INTEGER NOT NULL,
            matched TEXT NOT NULL,
            partial TEXT NOT NULL,
            missing TEXT NOT NULL,
            roadmap TEXT NOT NULL,
            projects TEXT NOT NULL,
            resources TEXT NOT NULL,
            owner_key TEXT NOT NULL DEFAULT 'legacy'
        )""")
        for name in ("resume_score", "review", "interview", "ai_status"):
            columns = {row[1] for row in conn.execute("PRAGMA table_info(analyses)").fetchall()}
            if name not in columns:
                col_type = "INTEGER NOT NULL DEFAULT 0" if name == "resume_score" else ("TEXT NOT NULL DEFAULT ''" if name == "ai_status" else "TEXT NOT NULL DEFAULT '{}'")
                conn.execute(f"ALTER TABLE analyses ADD COLUMN {name} {col_type}")
        conn.execute("""CREATE TABLE IF NOT EXISTS roadmap_progress (
            analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
            owner_key TEXT NOT NULL, task_key TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(analysis_id, owner_key, task_key)
        )""")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(analyses)").fetchall()}
        if "owner_key" not in columns:
            conn.execute("ALTER TABLE analyses ADD COLUMN owner_key TEXT NOT NULL DEFAULT 'legacy'")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analyses_owner ON analyses(owner_key, id DESC)")


def create_user(name, email, password_hash):
    with connect() as conn:
        cur = conn.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)", (name, email, password_hash))
        return cur.lastrowid


def get_user_by_email(email):
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=? COLLATE NOCASE", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id):
    with connect() as conn:
        row = conn.execute("SELECT id,name,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def save_analysis(owner_key, filename, target, score, matched, partial, missing, roadmap, projects, resources,
                  resume_score=0, review=None, interview=None, ai_status=""):
    with connect() as conn:
        cur = conn.execute("""INSERT INTO analyses(owner_key,filename,target,score,matched,partial,missing,roadmap,projects,resources,resume_score,review,interview,ai_status)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            owner_key, filename, target, score, json.dumps(matched), json.dumps(partial),
            json.dumps(missing), json.dumps(roadmap), json.dumps(projects), json.dumps(resources),
            resume_score, json.dumps(review or {}), json.dumps(interview or {}), ai_status
        ))
        return cur.lastrowid


def _decode(row):
    if not row:
        return None
    item = dict(row)
    for key in ("matched", "partial", "missing", "roadmap", "projects", "resources", "review", "interview"):
        item[key] = json.loads(item[key])
    return item


def get_analyses(owner_key):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM analyses WHERE owner_key=? ORDER BY id DESC", (owner_key,)).fetchall()
    return [_decode(row) for row in rows]


def get_analysis(analysis_id, owner_key):
    with connect() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id=? AND owner_key=?", (analysis_id, owner_key)).fetchone()
    return _decode(row)


def delete_analysis(analysis_id, owner_key):
    with connect() as conn:
        conn.execute("DELETE FROM analyses WHERE id=? AND owner_key=?", (analysis_id, owner_key))


def get_progress(analysis_id, owner_key):
    with connect() as conn:
        rows = conn.execute("SELECT task_key,completed FROM roadmap_progress WHERE analysis_id=? AND owner_key=?",
                            (analysis_id, owner_key)).fetchall()
    return {row["task_key"]: bool(row["completed"]) for row in rows}


def set_progress(analysis_id, owner_key, task_key, completed):
    with connect() as conn:
        conn.execute("""INSERT INTO roadmap_progress(analysis_id,owner_key,task_key,completed) VALUES(?,?,?,?)
            ON CONFLICT(analysis_id,owner_key,task_key) DO UPDATE SET completed=excluded.completed,updated_at=CURRENT_TIMESTAMP""",
                     (analysis_id, owner_key, task_key, int(completed)))
