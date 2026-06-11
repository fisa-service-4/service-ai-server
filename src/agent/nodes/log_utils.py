import asyncio
import functools
import json
import logging
import time
from typing import Callable

from src.pipeline.db import get_log_pool

logger = logging.getLogger(__name__)

_background_tasks: set = set()


def run_in_background(coro) -> None:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def _insert_langgraph_log(
    session_id: int | None,
    graph_name: str,
    node_name: str,
    execution_time_ms: int,
    execution_result: str | None,
) -> None:
    try:
        pool = await get_log_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO langgraph_execution_log
                    (session_id, graph_name, node_name, execution_order,
                     execution_result, execution_time_ms, executed_at)
                VALUES ($1, $2, $3, 0, $4, $5, NOW())
                """,
                session_id,
                graph_name,
                node_name,
                execution_result,
                execution_time_ms,
            )
    except Exception:
        logger.debug("[LogUtils] langgraph_execution_log 저장 실패 node=%s", node_name)


async def _insert_prompt_log(
    user_id: str | None,
    session_id: int | None,
    prompt_type: str,
    system_prompt: str | None,
    user_prompt: str | None,
    ai_response: str | None,
) -> None:
    try:
        uid = int(user_id) if user_id else None
    except (ValueError, TypeError):
        uid = None
    try:
        pool = await get_log_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ai_prompt_log
                    (user_id, session_id, prompt_type, system_prompt,
                     user_prompt, ai_response, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                uid,
                session_id,
                prompt_type,
                system_prompt,
                user_prompt,
                ai_response,
            )
    except Exception:
        logger.debug("[LogUtils] ai_prompt_log 저장 실패 type=%s", prompt_type)


async def _insert_action_log(
    user_id: str | None,
    action_type: str,
    action_payload: dict | None,
    approved_yn: bool,
    executed_yn: bool,
    result_message: str | None,
) -> None:
    try:
        uid = int(user_id) if user_id else None
    except (ValueError, TypeError):
        uid = None
    if uid is None:
        return
    try:
        pool = await get_log_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ai_action_log
                    (user_id, action_type, action_payload, approved_yn,
                     executed_yn, result_message, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                uid,
                action_type,
                json.dumps(action_payload) if action_payload else None,
                approved_yn,
                executed_yn,
                result_message,
            )
    except Exception:
        logger.debug("[LogUtils] ai_action_log 저장 실패 type=%s", action_type)


def log_node(node_name: str, graph_name: str = "chat_graph") -> Callable:
    def decorator(fn: Callable) -> Callable:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(state, *args, **kwargs):
                start = time.monotonic()
                execution_result = "SUCCESS"
                try:
                    result = await fn(state, *args, **kwargs)
                    return result
                except Exception:
                    execution_result = "FAILURE"
                    raise
                finally:
                    elapsed_ms = int((time.monotonic() - start) * 1000)
                    session_id = state.get("session_id")
                    run_in_background(
                        _insert_langgraph_log(
                            session_id=session_id,
                            graph_name=graph_name,
                            node_name=node_name,
                            execution_time_ms=elapsed_ms,
                            execution_result=execution_result,
                        )
                    )
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(state, *args, **kwargs):
                start = time.monotonic()
                execution_result = "SUCCESS"
                try:
                    result = fn(state, *args, **kwargs)
                    return result
                except Exception:
                    execution_result = "FAILURE"
                    raise
                finally:
                    elapsed_ms = int((time.monotonic() - start) * 1000)
                    session_id = state.get("session_id")
                    try:
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(
                            _insert_langgraph_log(
                                session_id=session_id,
                                graph_name=graph_name,
                                node_name=node_name,
                                execution_time_ms=elapsed_ms,
                                execution_result=execution_result,
                            )
                        )
                        _background_tasks.add(task)
                        task.add_done_callback(_background_tasks.discard)
                    except RuntimeError:
                        pass
            return sync_wrapper
    return decorator
