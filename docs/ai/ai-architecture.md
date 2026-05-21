# AI Architecture

## 전체 호출 구조
```
Front(Next.js)
↓
Backend(Spring Boot)   ← AI 요청은 무조건 백엔드 통해서만
↓
AI Server(FastAPI)
↓
분석: Python Pipeline → LLM 직접 호출
챗봇: LangGraph Agent
```

---

## AI 서버 두 가지 역할

### 1. 분석 파이프라인 (배치)
```
Python Pipeline → LLM 직접 호출
주간/월간 분석 데이터 생성 → 분석 DB 저장
```

### 2. 챗봇 (LangGraph Agent)
```
사용자 요청 처리
분석 DB 데이터 활용
금융 액션 실행 (이체/주문)
```

---

## LLM 연동 방식
```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',  # 배포 시 vLLM URL로 변경
    api_key='ollama',
)
```

```
개발: Ollama  → base_url=http://localhost:11434/v1
배포: vLLM    → base_url=http://localhost:8000/v1
코드 변경 없이 base_url만 수정하면 전환 가능
```

---

## 모델
| 용도 | 모델 |
| --- | --- |
| LLM | Qwen3-8B (Ollama) |
| 임베딩 | BGE-M3 (로컬) |
| STT | faster-whisper |
| TTS | Kokoro |