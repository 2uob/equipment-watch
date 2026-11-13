import json
import time
import urllib.request

from app.schemas.diagnostic import DiagnosticItemIn, LlmResult, RuleResult

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"
TIMEOUT_SEC = 60

def build_prompt(items: list[DiagnosticItemIn]) -> str:
    """Build the prompt from mismatched items only."""
    lines = []
    for item in items:
        if item.observed != item.expected:
            lines.append(f"- {item.seq}번 {item.name}: 기대 '{item.expected}', 실제 '{item.observed}'")
    return (
        "좌우 두 개의 구동 모터를 가진 장비의 운행 전 점검 결과입니다.\n"
        "기대와 다르게 나온 항목은 다음과 같습니다.\n"
        + "\n".join(lines)
        + "\n나머지 항목은 모두 기대와 같았습니다.\n"
        "가능한 원인을 세 문장 이내로 추정하고, 먼저 확인할 것을 한 가지 제안해 주세요. "
        "제목이나 목록 없이 평문으로 답해주세요."
    )

def call_ollama(prompt: str) -> str:
    """Send one prompt to local Ollama and return the reply text."""
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "1h",
        "options": {"num_predict": 200},
    }).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        return json.loads(resp.read())["response"]

def analyze(items: list[DiagnosticItemIn], rule: RuleResult, call=call_ollama) -> LlmResult:
    """Ask the LLM only for unknown verdicts. Never raises; never changes the verdict."""
    if rule.verdict != "unknown":
        return LlmResult("skipped")

    start = time.monotonic()
    prompt = build_prompt(items)
    try:
        text = call(prompt)
        status = "ok"
    except TimeoutError:
        text, status = None, "timeout"
    except Exception:
        text, status = None, "failed"
    elapsed_ms = int((time.monotonic() - start) * 1000)

    return LlmResult(status, text, MODEL, elapsed_ms)