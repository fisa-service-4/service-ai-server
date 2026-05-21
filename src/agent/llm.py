import os

from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",
)

MODEL = os.getenv("LLM_MODEL", "qwen3:8b")
