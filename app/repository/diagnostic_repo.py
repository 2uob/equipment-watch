from datetime import datetime
from app.schemas.diagnostic import DiagnosticItemIn, RuleResult

def now() -> str:
    """Current local time as ISO text (SQLite has no datetime type)."""
    return datetime.now().isoformat(timespec="seconds")

def add_equipment(conn, code: str, name: str, site: str) -> int:
    """Insert one equipment row and return its id."""
    cur = conn.execute(
        "INSERT INTO equipment (code, name, site) VALUES (?, ?, ?)",
        (code, name, site),
    )
    conn.commit()
    return cur.lastrowid

def save_run(conn, equipment_id: int, items: list[DiagnosticItemIn], result: RuleResult) -> int:
    """Save one diagnostic run and its items. Stores the result; does not judge."""
    cur = conn.execute(
        "INSERT INTO diagnostic_run (equipment_id, started_at, rule_verdict, rule_reason) "
        "VALUES (?, ?, ?, ?)",
        (equipment_id, now(), result.verdict, result.reason),
    )
    run_id = cur.lastrowid

    for item in items:
        conn.execute(
            "INSERT INTO diagnostic_item "
            "(run_id, seq, name, command, expected, observed, matched, rule_code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                item.seq,
                item.name,
                item.command,
                item.expected,
                item.observed,
                int(item.observed == item.expected),
                result.item_codes.get(item.seq),
            ),
        )

    conn.commit()
    return run_id