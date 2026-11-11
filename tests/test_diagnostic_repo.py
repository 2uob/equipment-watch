import sqlite3
import pytest

from app.models.db import SCHEMA_PATH
from app.repository.diagnostic_repo import add_equipment, save_run
from app.services.diagnostics.rules import judge
from tests.test_rules import make_items

def make_memory_db():
    """Create an empty in-memory DB with the real schema."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn

def test_save_run_stores_verdict_and_items():
    conn = make_memory_db()
    eq_id = add_equipment(conn, "BOT-01", "테스트봇", "테스트 현장")
    items = make_items({1: "좌측 선회", 2: "우측 선회"})
    result = judge(items)

    run_id = save_run(conn, eq_id, items, result)

    run = conn.execute(
        "SELECT rule_verdict, llm_status FROM diagnostic_run WHERE id = ?", (run_id,)
    ).fetchone()
    assert run == ("fault", "skipped")

    rows = conn.execute(
        "SELECT seq, matched, rule_code FROM diagnostic_item WHERE run_id = ? ORDER BY seq",
        (run_id,),
    ).fetchall()
    assert len(rows) == 8
    assert rows[0] == (1, 0, "POLARITY_REVERSED")
    assert rows[2] == (3, 1, None)

def test_save_run_rejects_unknown_equipment():
    conn = make_memory_db()
    items = make_items()
    with pytest.raises(sqlite3.IntegrityError):
        save_run(conn, 999, items, judge(items))