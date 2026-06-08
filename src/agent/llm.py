import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30.0,
)

MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

