import sqlite3
from pathlib import Path

DB_PATH = Path("equipment.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = get_connection()
    conn.executescript(sql)
    conn.close()