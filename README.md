# equipment-watch

## 한 줄 설명
- 운행 전 모터 점검 결과를 규칙으로 판정하고 규칙에 안 맞는 경우만 로컬 LLM이 원인을 추정하는 진단 서비스

## 개요 
- 기존 사내에서 운영하던 시스템의 구조만 가져와 처음부터 다시 작성한 축소판
- 원본 코드는 전 직장 소유로 공개할 수 없어 새로 작성
- 데이터는 전부 합성이며 실제 장비, 사이트, 임계값과 무관

## 왜 만들었나
- 설비 이상 알림이 없어 직접 사이트 확인하며 이상 값을 판정해야 했음
- 규모 16대, 운행 시간 10시간 내에서 수시로 확인
- 감시는 총 15종, 현장 불편 사항을 반영해 알림을 구성함
- 운행 후 모터 이상이 발견되는 경우가 발생

## 무엇을 하나
- 모터 진단 1개 구현, 감시 2종(임계 초과, 통신 두절)과 알림 억제는 테이블과 설계까지

## 구조
```
app/
- routes/            요청만 받고 응답만 돌려줌
- services/          판정 로직
    - diagnostics/   규칙 판정+LLM 해석
    - monitors/      감시 모듈 2종
- repository/        DB 접근
- schemas/           DTO 
- models/            테이블 정의
tests/
```

## 설계 판단
- 패턴이 명확한 항목은 규칙으로 판정하고 LLM은 규칙에 걸리지 않는 조합에만 활용
- 현장 데이터를 외부로 보낼 수 없어 로컬 모델 사용
- 규칙 판정과 LLM 해석을 다른 칸에 저장하고, LLM이 실패해도 판정은 남음
- services는 DB를 모르게 해서 테스트에 DB가 필요 없음

## 실행 방법
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -v          # 테스트 9개. Ollama 없이 돌아감

python run.py      # 서버 실행 (localhost:5000)
```

다른 터미널에서 장비 1대를 등록한 뒤 요청을 보냅니다.
```bash
python -c "from app.models.db import get_connection; from app.repository.diagnostic_repo import add_equipment; c = get_connection(); print(add_equipment(c, 'BOT-01', '데모 장비', '데모 현장'))"
curl -s -X POST localhost:5000/diagnostics -H "Content-Type: application/json" -d @samples/left_polarity.json
curl -s -X POST localhost:5000/diagnostics -H "Content-Type: application/json" -d @samples/combined_drift.json
```

LLM 해석은 로컬 Ollama(`gemma3:4b`)를 씁니다. Ollama가 없으면 `llm_status`가 `failed`로 기록되고 판정은 그대로 나옵니다.
