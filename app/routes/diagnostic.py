from flask import Blueprint, jsonify, request

from app.models.db import get_connection
from app.repository.diagnostic_repo import save_llm, save_run
from app.schemas.diagnostic import DiagnosticItemIn
from app.services.diagnostics.llm_analyzer import analyze
from app.services.diagnostics.rules import judge

bp = Blueprint("diagnostic", __name__)

@bp.post("/diagnostics")
def run_diagnostic():
    """Receive 8 check items, judge, ask LLM if unknown, save, respond."""
    body = request.get_json()
    items = [DiagnosticItemIn(**raw) for raw in body["items"]]
    if len(items) != 8:
        return jsonify({"error": "점검 항목은 8개여야 합니다"}), 400

    rule = judge(items)
    llm = analyze(items, rule)

    conn = get_connection()
    run_id = save_run(conn, body["equipment_id"], items, rule)
    save_llm(conn, run_id, llm)
    conn.close()

    return jsonify({
        "run_id": run_id,
        "verdict": rule.verdict,
        "reason": rule.reason,
        "llm_status": llm.status,
        "llm_summary": llm.summary
    })