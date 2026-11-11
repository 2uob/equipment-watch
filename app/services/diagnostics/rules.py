from app.schemas.diagnostic import DiagnosticItemIn, RuleResult

POLARITY_REVERSED = "POLARITY_REVERSED"
LR_SWAPPED = "LR_SWAPPED"

def flip(direction: str) -> str:
    """Swap left and right in a direction label (e.g. '우측 선회' -> '좌측 선회')."""
    return direction.replace("좌","#").replace("우","좌").replace("#","우")

def judge(items: list[DiagnosticItemIn]) -> RuleResult:
    """Judge motor wiring from 8 check items. Pure function: no DB, no HTTP."""
    by_seq = {item.seq: item for item in items}

    def ok(seq: int) -> bool:
        return by_seq[seq].observed == by_seq[seq].expected

    def flipped(seq: int) -> bool:
        return by_seq[seq].observed == flip(by_seq[seq].expected)

    mismatched = [item.seq for item in items if item.observed != item.expected]

    if not mismatched:
        return RuleResult("normal", "모든 항목이 기대 거동과 일치") 

    left_flipped = flipped(1) and flipped(2)
    right_flipped = flipped(3) and flipped(4) 
    left_ok = ok(1) and ok(2)
    right_ok = ok(3) and ok(4)

    if left_flipped and right_ok:
        return RuleResult("fault", "좌모터 단독 동작이 좌우 반대로 나옴 -> 좌모터 극성 반전",
                          {seq: POLARITY_REVERSED for seq in mismatched})
    if right_flipped and left_ok:
        return RuleResult("fault", "우모터 단독 동작이 좌우 반대로 나옴 -> 우모터 극성 반전",
                          {seq: POLARITY_REVERSED for seq in mismatched})
    if left_flipped and right_flipped and ok(5):
        return RuleResult("fault", "단독 4개가 모두 반대인데 통합 전진은 정상 -> 좌우 배선 교차",
                          {seq: LR_SWAPPED for seq in mismatched})
    if left_flipped and right_flipped and by_seq[5].observed == "후진":
        return RuleResult("fault", "단독 4개가 모두 반대이고 통합 전진이 후진 -> 양쪽 모터 극성 반전",
                          {seq: POLARITY_REVERSED for seq in mismatched})

    return RuleResult("unknown", f"알려진 패턴과 맞지 않음 (불일치 항목: {mismatched})")

