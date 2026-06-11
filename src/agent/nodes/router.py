import asyncio

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.agent.nodes.log_utils import log_node, _insert_prompt_log


_SYSTEM_PROMPT = """You are a financial assistant router.
Classify the user's message into one of these intents:
- ASSET: asset/spending analysis, financial advice, investment comparisons or recommendations (e.g. "삼성전자 살까 SK하이닉스 살까", "어떤 주식이 좋아?"), distribution settings, applying or confirming recommendations (적용, 설정 적용, 반영, 그대로 해줘)
- STOCK: clear buy/sell orders (e.g. "삼성전자 10주 매수해줘", "팔아줘") OR specific stock price inquiries (e.g. "삼성전자 현재가", "주가 얼마야", "시세 알려줘") OR holdings/portfolio queries (e.g. "보유종목", "내 주식 보여줘", "보유 현황", "어떤 주식 갖고 있어")
- TRANSFER: money transfers between accounts
- UNKNOWN: anything else

Respond with only one word: ASSET, STOCK, TRANSFER, or UNKNOWN."""


@log_node("Router")
async def router_node(state: ChatAgentState) -> dict:
    last_message = state["messages"][-1]["content"]

    response = await asyncio.to_thread(
        client.chat.completions.create,
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

    asyncio.create_task(
        _insert_prompt_log(
            user_id=state.get("user_id"),
            session_id=state.get("session_id"),
            prompt_type="ROUTER",
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=last_message,
            ai_response=intent,
        )
    )

    return {"intent": intent}
