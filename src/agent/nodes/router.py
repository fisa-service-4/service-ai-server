from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL


_SYSTEM_PROMPT = """You are a financial assistant router.
Classify the user's message into one of these intents:
- ASSET: asset/spending analysis, financial advice, investment comparisons or recommendations (e.g. "삼성전자 살까 SK하이닉스 살까", "어떤 주식이 좋아?"), distribution settings, applying or confirming recommendations (적용, 설정 적용, 반영, 그대로 해줘)
- STOCK: clear buy/sell orders (e.g. "삼성전자 10주 매수해줘", "팔아줘") OR specific stock price inquiries (e.g. "삼성전자 현재가", "주가 얼마야", "시세 알려줘") OR holdings/portfolio queries (e.g. "보유종목", "내 주식 보여줘", "보유 현황", "어떤 주식 갖고 있어")
- TRANSFER: money transfers between accounts
- UNKNOWN: anything else

Respond with only one word: ASSET, STOCK, TRANSFER, or UNKNOWN."""


def router_node(state: ChatAgentState) -> dict:
    last_message = state["messages"][-1]["content"]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": last_message},
        ],
        temperature=0,
    )

    intent = (response.choices[0].message.content or "").strip().upper()
    if intent not in {"ASSET", "STOCK", "TRANSFER"}:
        intent = "UNKNOWN"

    return {"intent": intent}
