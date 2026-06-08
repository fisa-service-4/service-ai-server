import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_SYSTEM_PROMPT = """사용자의 메시지에서 주식 관련 의도를 파악하세요.

is_holdings 판단 기준:
- true: 보유종목/보유주식 목록을 물어보는 경우 ("보유종목 뭐야", "내 주식 보여줘", "보유 현황")
- false: 그 외 모든 경우

is_inquiry 판단 기준:
- true: 현재가/시세/가격/정보만 물어보는 경우 ("현재가 알려줘", "얼마야", "시세 조회", "어때", "주가 보여줘")
- false: 매수/매도/주문 의도가 있는 경우

has_order_intent 판단 기준 (명시적 실행 의도):
- true: 사용자가 직접 주문 실행 의사를 밝힌 경우만
  ("매수해줘", "매도해줘", "팔아줘", "사줘", "팔아", "사", "주문해줘", "주문할게", "주문할래", "살게", "살래", "매수할게", "매수할래", "매도할게", "매도할래")
- false: 그 외 모든 경우 (정보만 묻거나, 종목/수량만 언급)

다음 JSON 형식으로만 응답하세요. 마크다운 없이 순수 JSON만 출력하세요:
{
  "is_holdings": true 또는 false,
  "is_inquiry": true 또는 false,
  "has_order_intent": true 또는 false,
  "code": "종목코드 (없으면 null)",
  "name": "종목명 (없으면 null)",
  "quantity": 수량 숫자 (없으면 null),
  "order_type": "BUY 또는 SELL (없으면 null)",
  "price_type": "MARKET 또는 LIMIT (없으면 null)",
  "price": 지정가 숫자 (없으면 null),
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}

예시1: "삼성전자 현재가 알려줘" → is_inquiry: true, has_order_intent: false
예시2: "삼성전자 10주 매수해줘" → is_inquiry: false, has_order_intent: true, order_type: "BUY", quantity: 10
예시3: "내 보유종목 뭐야" → is_holdings: true, has_order_intent: false
예시4: "삼성전자 10주" → is_inquiry: false, has_order_intent: false, missing: ["order_type", "price_type"], question: "매수/매도 중 어떤 주문을 원하시나요?"
예시5: "주문할게" → has_order_intent: true"""


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
        raw = (response.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw.strip())
    except (json.JSONDecodeError, IndexError):
        extracted = {"is_inquiry": False, "missing": ["파싱 오류"], "question": "다시 말씀해 주시겠어요?"}

    prev_stock_info = state.get("stock_info") or {}
    has_order_intent = extracted.get("has_order_intent", False)
    stock_info = {
        "is_holdings": extracted.get("is_holdings", False),
        "is_inquiry": extracted.get("is_inquiry", False),
        "has_order_intent": has_order_intent,
        "code": extracted.get("code") or prev_stock_info.get("code"),
        "name": extracted.get("name") or prev_stock_info.get("name"),
        "quantity": extracted.get("quantity") or prev_stock_info.get("quantity"),
        "order_type": extracted.get("order_type") or prev_stock_info.get("order_type"),
        "price_type": extracted.get("price_type") or prev_stock_info.get("price_type"),
        "price": extracted.get("price") or prev_stock_info.get("price"),
    }

    question = extracted.get("question")
    fields_ok = not extracted.get("missing") and question is None
    # 주문 실행은 명시적 의도가 있고 필드가 모두 채워진 경우만
    info_complete = extracted.get("is_inquiry", False) or (has_order_intent and fields_ok)

    updated_messages = state["messages"]
    if question:
        updated_messages = state["messages"] + [{"role": "assistant", "content": question}]
    elif fields_ok and not has_order_intent and not extracted.get("is_inquiry") and not extracted.get("is_holdings"):
        # 정보는 다 있지만 명시적 주문 의도가 없으면 확인 요청
        order_type = stock_info.get("order_type", "BUY")
        action = "매수" if order_type == "BUY" else "매도"
        confirm_msg = f"주문을 진행할까요? 진행하시려면 \"{action}할게\" 또는 \"주문할래\"라고 말씀해 주세요."
        updated_messages = state["messages"] + [{"role": "assistant", "content": confirm_msg}]

    return {
        "stock_info": stock_info,
        "info_complete": info_complete,
        "messages": updated_messages,
    }
