import os

import httpx

_BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
_TRANSACTION_URL = os.getenv("TRANSACTION_URL", "http://localhost:8083")
_TIMEOUT = 10.0


def _headers(token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def get(path: str, token: str | None = None, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=_BACKEND_URL, timeout=_TIMEOUT) as client:
        response = await client.get(path, headers=_headers(token), params=params)
        response.raise_for_status()
        return response.json()


async def post(path: str, token: str | None = None, body: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=_BACKEND_URL, timeout=_TIMEOUT) as client:
        response = await client.post(path, headers=_headers(token), json=body)
        response.raise_for_status()
        return response.json()


async def patch(path: str, token: str | None = None, body: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=_BACKEND_URL, timeout=_TIMEOUT) as client:
        response = await client.patch(path, headers=_headers(token), json=body)
        response.raise_for_status()
        return response.json()


async def transaction_get(path: str, token: str | None = None, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=_TRANSACTION_URL, timeout=_TIMEOUT) as client:
        response = await client.get(path, headers=_headers(token), params=params)
        response.raise_for_status()
        return response.json()
