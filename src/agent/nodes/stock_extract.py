import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_SYSTEM_PROMPT = """사용자의 메시지에서 주식 주문 정보를 추출하세요.
다음 JSON 형식으로만 응답하세요:
{
  "code": "종목코드 (없으면 null)",
  "name": "종목명 (없으면 null)",
  "quantity": 수량 (없으면 null),
  "order_type": "BUY 또는 SELL (없으면 null)",
  "price_type": "MARKET 또는 LIMIT (없으면 null)",
  "price": 지정가 (없으면 null),
  "missing": ["부족한 정보 목록"],
  "question": "사용자에게 물어볼 내용 (정보가 충분하면 null)"
}"""


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
        extracted = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        extracted = {"missing": ["파싱 오류"], "question": "다시 말씀해 주시겠어요?"}

    stock_info = {
        "code": extracted.get("code"),
        "name": extracted.get("name"),
        "quantity": extracted.get("quantity"),
        "order_type": extracted.get("order_type"),
        "price_type": extracted.get("price_type"),
        "price": extracted.get("price"),
    }

    question = extracted.get("question")
    info_complete = not extracted.get("missing") and question is None

    updated_messages = state["messages"]
    if question:
        updated_messages = state["messages"] + [{"role": "assistant", "content": question}]

    return {
        "stock_info": stock_info,
        "info_complete": info_complete,
        "messages": updated_messages,
    }
