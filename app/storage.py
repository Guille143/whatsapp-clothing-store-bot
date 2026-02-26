import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("bot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            phone TEXT PRIMARY KEY,
            handoff INTEGER DEFAULT 0,
            updated_at TEXT
        )
        """)
        con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            direction TEXT,
            body TEXT,
            created_at TEXT
        )
        """)
        con.commit()

def set_handoff(phone: str, handoff: bool):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        INSERT INTO conversations(phone, handoff, updated_at)
        VALUES(?, ?, ?)
        ON CONFLICT(phone) DO UPDATE SET handoff=excluded.handoff, updated_at=excluded.updated_at
        """, (phone, 1 if handoff else 0, datetime.utcnow().isoformat()))
        con.commit()

def get_handoff(phone: str) -> bool:
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute("SELECT handoff FROM conversations WHERE phone=?", (phone,)).fetchone()
        return bool(row[0]) if row else False

def log_message(phone: str, direction: str, body: str):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO messages(phone, direction, body, created_at) VALUES(?,?,?,?)",
            (phone, direction, body, datetime.utcnow().isoformat())
        )
        con.commit()
