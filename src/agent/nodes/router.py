from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL


_SYSTEM_PROMPT = """You are a financial assistant router.
Classify the user's message into one of these intents:
- ASSET: questions about assets, spending analysis, consumption patterns, financial advice, distribution settings
- STOCK: buying or selling stocks, stock prices, portfolio inquiries
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

    intent = response.choices[0].message.content.strip().upper()
    if intent not in {"ASSET", "STOCK", "TRANSFER"}:
        intent = "UNKNOWN"

    return {"intent": intent}
