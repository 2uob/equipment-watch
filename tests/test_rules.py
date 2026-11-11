from app.schemas.diagnostic import DiagnosticItemIn
from app.services.diagnostics.rules import judge, flip, POLARITY_REVERSED, LR_SWAPPED

EXPECTED = {
    1: "우측 선회",
    2: "좌측 선회",
    3: "좌측 선회",
    4: "우측 선회",
    5: "직진",
    6: "후진",
    7: "제자리 좌회전",
    8: "제자리 우회전"
}

def make_items(changes=None):
    """Build 8 items; obeserved equals expected unless overridden in changes."""
    changes = changes or {}
    items = []
    for seq, expected in EXPECTED.items():
        observed = changes.get(seq, expected)
        items.append(DiagnosticItemIn(seq, f"item{seq}", "", expected, observed))
    return items

def test_flip_swaps_left_and_right():
    assert flip("우측 선회") == "좌측 선회"
    assert flip("제자리 좌회전") == "제자리 우회전"
    assert flip("직진") =="직진"

def test_all_match_is_normal():
    result = judge(make_items())
    assert result.verdict == "normal"
    assert result.item_codes == {}

def test_left_polarity_reversed():
    result = judge(make_items({1: "좌측 선회", 2: "우측 선회"}))
    assert result.verdict == "fault"
    assert "좌모터 극성 반전" in result.reason
    assert result.item_codes == {1: POLARITY_REVERSED, 2: POLARITY_REVERSED}

def test_right_polarity_reversed():
    result = judge(make_items({3: "우측 선회", 4: "좌측 선회"}))
    assert result.verdict  == "fault"
    assert "우모터 극성 반전" in result.reason
    assert result.item_codes == {3: POLARITY_REVERSED, 4: POLARITY_REVERSED}

def test_lr_swapped_when_combined_forward_is_ok():
    changes = {1: "좌측 선회", 2: "우측 선회", 3: "우측 선회", 4: "좌측 선회"}
    result = judge(make_items(changes))
    assert result.verdict == "fault"
    assert "좌우 배선 교차" in result.reason
    assert set(result.item_codes.values()) == {LR_SWAPPED}

def test_both_polarity_when_combined_forward_is_backward():
    changes = {1: "좌측 선회", 2: "우측 선회", 3: "우측 선회", 4: "좌측 선회", 5: "후진"}
    result = judge(make_items(changes))
    assert result.verdict == "fault"
    assert "양쪽 모터 극성 반전" in result.reason
    assert result.item_codes == {1: POLARITY_REVERSED, 2: POLARITY_REVERSED,
                                  3: POLARITY_REVERSED, 4: POLARITY_REVERSED, 
                                  5: POLARITY_REVERSED}

def test_unknown_pattern_goes_to_llm():
    result = judge(make_items({5: "좌측 쏠림"}))
    assert result.verdict == "unknown"
    assert result.item_codes == {}