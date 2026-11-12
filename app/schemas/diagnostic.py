from dataclasses import dataclass, field

@dataclass
class DiagnosticItemIn:
    seq: int
    name: str
    command: str
    expected: str
    observed: str

@dataclass
class RuleResult:
    verdict: str   # normal/fault/unknown
    reason: str
    item_codes: dict = field(default_factory=dict) # {seq:rule_code}

@dataclass
class LlmResult:
    status: str # ok/failed/timeout/skipped
    summary: str | None = None
    model: str | None = None
    elapsed_ms: int | None = None