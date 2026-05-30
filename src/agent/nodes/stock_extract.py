import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_SYSTEM_PROMPT = """사용자의 메시지에서 주식 관련 의도를 파악하세요.

is_inquiry 판단 기준:
- true: 현재가/시세/가격만 물어보는 경우 ("현재가 알려줘", "얼마야", "시세 조회")
- false: 매수/매도/주문 의도가 있는 경우 ("사줘", "팔아줘", "매수해줘", "매도해줘", "주문해줘")

다음 JSON 형식으로만 응답하세요. 마크다운 없이 순수 JSON만 출력하세요:
{
  "is_inquiry": true 또는 false,
  "code": "종목코드 (없으면 null)",
  "name": "종목명 (없으면 null)",
  "quantity": 수량 숫자 (없으면 null),
  "order_type": "BUY 또는 SELL (없으면 null)",
  "price_type": "MARKET 또는 LIMIT (없으면 null)",
  "price": 지정가 숫자 (없으면 null),
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}

예시1: "삼성전자 현재가 알려줘" → is_inquiry: true, missing: [], question: null
예시2: "삼성전자 10주 매수해줘" → is_inquiry: false, order_type: "BUY", quantity: 10
예시3: "삼성전자 1주 시장가로 사줘" → is_inquiry: false, order_type: "BUY", price_type: "MARKET", quantity: 1"""


def stock_extract_node(state: ChatAgentState) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            *state["messages"],
        ],
        temperature=0,
    )

    try:
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        extracted = {"is_inquiry": False, "missing": ["파싱 오류"], "question": "다시 말씀해 주시겠어요?"}

    stock_info = {
        "is_inquiry": extracted.get("is_inquiry", False),
        "code": extracted.get("code"),
        "name": extracted.get("name"),
        "quantity": extracted.get("quantity"),
        "order_type": extracted.get("order_type"),
        "price_type": extracted.get("price_type"),
        "price": extracted.get("price"),
    }

    question = extracted.get("question")
    info_complete = extracted.get("is_inquiry", False) or (not extracted.get("missing") and question is None)

    updated_messages = state["messages"]
    if question:
        updated_messages = state["messages"] + [{"role": "assistant", "content": question}]

    return {
        "stock_info": stock_info,
        "info_complete": info_complete,
        "messages": updated_messages,
    }
