import asyncio
import re

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.agent.nodes.log_utils import log_node, _insert_prompt_log, run_in_background


_SYSTEM_PROMPT = """You are a financial assistant router.
Classify the user's message into one of these intents:
- ASSET: asset/spending analysis, financial advice, virtual salary (가상월급) distribution recommendations or settings (e.g. "가상월급 분배 추천해줘", "분배 비율 어떻게 해야 해", "얼마씩 나눠야 해", "월급 배분 추천", "비상금 얼마가 적당해"), investment comparisons or advice (e.g. "삼성전자 살까 SK하이닉스 살까", "어떤 주식이 좋아?"), applying or confirming AI recommendations (e.g. "적용할래", "그대로 해줘", "설정 반영해줘")
- STOCK: clear buy/sell orders (e.g. "삼성전자 10주 매수해줘", "팔아줘") OR specific stock price inquiries (e.g. "삼성전자 현재가", "주가 얼마야", "시세 알려줘") OR holdings/portfolio queries (e.g. "보유종목", "내 주식 보여줘", "보유 현황", "어떤 주식 갖고 있어")
- TRANSFER: money transfers between accounts
- UNKNOWN: anything else

Respond with only one word: ASSET, STOCK, TRANSFER, or UNKNOWN."""


@log_node("Router")
async def router_node(state: ChatAgentState) -> dict:
    if not state.get("info_complete") and (state.get("stock_info") or {}).get("has_order_intent"):
        return {"intent": "STOCK"}

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

    content = (response.choices[0].message.content or "").strip()
    # Gemini may prepend explanation text; try last word first
    last_word = re.split(r"\s+", content)[-1].upper().strip(".,!?:") if content else ""
    if last_word in {"ASSET", "STOCK", "TRANSFER"}:
        intent = last_word
    else:
        # Fallback: search for any valid intent keyword in the full response
        content_upper = content.upper()
        found = next(
            (c for c in ["STOCK", "TRANSFER", "ASSET"] if re.search(rf"\b{c}\b", content_upper)),
            None,
        )
        intent = found if found else "UNKNOWN"

    run_in_background(
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
