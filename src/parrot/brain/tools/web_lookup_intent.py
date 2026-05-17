"""T1 web lookup tool for GOSLO Intent/Thinking turns.

This is a short-budget, read-only helper.  It gives GOSLO an explicit function
tool for grounded web lookup when the native Gemini provider search tool is not
enough or when we want an auditable fallback path to Nanobot research.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
from typing import Any, Awaitable, Callable

from livekit.agents import RunContext, function_tool

logger = logging.getLogger(__name__)

GroundedLookup = Callable[..., Awaitable[dict[str, Any]] | dict[str, Any]]
TaskDispatcher = Callable[[str, dict | None, str], Awaitable[str]]

_DEFAULT_MODEL = "gemini-2.5-flash"


@function_tool()
async def web_lookup_intent(
    context: RunContext,
    query: str,
    purpose: str = "quick_fact_check",
    context_hint: str = "",
    allow_t3_fallback: bool = True,
) -> str:
    """Run a quick, read-only web lookup for an Intent/Thinking turn.

    Use this for fast T1 context that GOSLO needs before deciding what to say or
    which Plan/Task to draft.  It is especially useful after visual perception:
    first use the live video stream or identify_object to extract visible text,
    logos, colors, packaging, or product hints, then call this tool with those
    hints to check current web information such as a milk-tea brand.

    This tool does not click pages, write files, mutate Calendar, mutate
    Graphiti, or update L2-B.  If the lookup cannot finish within the short T1
    budget, it can dispatch a T3 Nanobot research task so conversation can
    continue instead of stalling.

    Args:
        query: Natural language web query.
        purpose: Why GOSLO needs the lookup, for the audit trail.
        context_hint: Optional visual/user/context hint to ground the query.
        allow_t3_fallback: If true, dispatch a background research task when T1
            lookup times out or cannot run.
    """

    return await do_web_lookup_intent(
        query=query,
        purpose=purpose,
        context_hint=context_hint,
        allow_t3_fallback=allow_t3_fallback,
    )


async def do_web_lookup_intent(
    *,
    query: str,
    purpose: str = "quick_fact_check",
    context_hint: str = "",
    allow_t3_fallback: bool = True,
    thinking_budget_s: float = 4.0,
    grounded_lookup: GroundedLookup | None = None,
    task_dispatcher: TaskDispatcher | None = None,
    model: str = "",
) -> str:
    """Core implementation for tests and the function tool wrapper."""

    selected_query = _compact(query, 500)
    selected_hint = _compact(context_hint, 500)
    selected_purpose = _compact(purpose or "quick_fact_check", 100)
    if not selected_query:
        return (
            "web_lookup_intent needs a query. No web lookup, task dispatch, "
            "Calendar write, Graphiti write, or L2-B mutation occurred."
        )

    lookup = grounded_lookup or _grounded_search_once
    try:
        result = await asyncio.wait_for(
            _maybe_await(
                lookup(
                    query=selected_query,
                    purpose=selected_purpose,
                    context_hint=selected_hint,
                    model=model or _lookup_model(),
                )
            ),
            timeout=max(0.5, min(float(thinking_budget_s or 4.0), 8.0)),
        )
        return _format_lookup_result(
            result,
            query=selected_query,
            purpose=selected_purpose,
            context_hint=selected_hint,
        )
    except Exception as exc:
        logger.info("web_lookup_intent: T1 lookup unavailable", exc_info=True)
        if not allow_t3_fallback:
            return (
                "T1 web_lookup_intent could not finish "
                f"({type(exc).__name__}: {_compact(str(exc), 160)}). "
                "No T3 task was dispatched because allow_t3_fallback=false. "
                "No external mutation occurred."
            )
        return await _format_t3_fallback(
            query=selected_query,
            purpose=selected_purpose,
            context_hint=selected_hint,
            error=f"{type(exc).__name__}: {_compact(str(exc), 180)}",
            task_dispatcher=task_dispatcher,
        )


async def _grounded_search_once(
    *,
    query: str,
    purpose: str,
    context_hint: str = "",
    model: str = "",
) -> dict[str, Any]:
    """Call Gemini generate_content with the Google Search grounding tool."""

    def _call() -> dict[str, Any]:
        from google import genai
        from google.genai import types

        api_key = _google_api_key()
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY/GEMINI_API_KEY is not configured")

        client = genai.Client(api_key=api_key)
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            temperature=0.2,
            max_output_tokens=700,
        )
        prompt = _lookup_prompt(query=query, purpose=purpose, context_hint=context_hint)
        response = client.models.generate_content(
            model=model or _DEFAULT_MODEL,
            contents=prompt,
            config=config,
        )
        return {
            "model": model or _DEFAULT_MODEL,
            "text": _response_text(response),
            "sources": _grounding_sources(response),
            "queries": _grounding_queries(response),
        }

    return await asyncio.to_thread(_call)


def _lookup_prompt(*, query: str, purpose: str, context_hint: str) -> str:
    hint_line = f"\nContext hint: {context_hint}" if context_hint else ""
    return (
        "You are a short-budget grounded lookup helper for a realtime voice "
        "agent. Answer only what is needed for the agent's immediate decision. "
        "If this is a product or brand lookup from visual hints, distinguish "
        "confirmed facts from guesses.\n"
        f"Purpose: {purpose}\n"
        f"Query: {query}{hint_line}\n"
        "Return a concise answer with any useful source cues."
    )


async def _format_t3_fallback(
    *,
    query: str,
    purpose: str,
    context_hint: str,
    error: str,
    task_dispatcher: TaskDispatcher | None,
) -> str:
    dispatcher = task_dispatcher
    if dispatcher is None:
        from parrot.brain.tools.dispatch_task import do_dispatch_task

        dispatcher = do_dispatch_task
    payload = {
        "query": query,
        "purpose": purpose,
        "context_hint": context_hint,
        "source": "web_lookup_intent_t1_fallback",
        "result_channel": "research_result",
        "requested_return": "concise grounded answer with sources",
    }
    try:
        task_id = await dispatcher("research", payload, "high")
    except Exception as dispatch_exc:
        return (
            "T1 web_lookup_intent could not finish "
            f"({error}), and T3 fallback dispatch also failed "
            f"({type(dispatch_exc).__name__}: {_compact(str(dispatch_exc), 160)}). "
            "No external mutation occurred."
        )

    return (
        "T1 web_lookup_intent could not finish inside the thinking budget "
        f"({error}). T3 research task dispatched: {task_id}. "
        "GOSLO can continue the conversation and check the research_result "
        "channel later. No Calendar write, Graphiti write, L2-B mutation, or "
        "file mutation occurred."
    )


def _format_lookup_result(
    result: dict[str, Any],
    *,
    query: str,
    purpose: str,
    context_hint: str,
) -> str:
    text = _compact(str(result.get("text") or ""), 1200)
    sources = result.get("sources") if isinstance(result.get("sources"), list) else []
    queries = result.get("queries") if isinstance(result.get("queries"), list) else []
    model = str(result.get("model") or _DEFAULT_MODEL)
    if not text:
        text = "No grounded answer text was returned."

    source_lines = []
    for row in sources[:4]:
        if not isinstance(row, dict):
            continue
        title = _compact(str(row.get("title") or "source"), 80)
        uri = _compact(str(row.get("uri") or ""), 180)
        if uri:
            source_lines.append(f"- {title}: {uri}")
    source_block = "\nSources:\n" + "\n".join(source_lines) if source_lines else ""
    query_block = ""
    if queries:
        query_block = "\nSearch queries: " + "; ".join(_compact(str(q), 80) for q in queries[:3])
    hint_block = f"\nContext hint: {context_hint}" if context_hint else ""
    return (
        "T1 web_lookup_intent grounded result "
        f"(Google Search, read-only, model={model}).\n"
        f"Purpose: {purpose}\nQuery: {query}{hint_block}\n"
        f"Answer: {text}{query_block}{source_block}\n"
        "No external mutation occurred. For visual brand identification, pair "
        "this with live video or identify_object evidence before trusting the "
        "brand guess."
    )


def _response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text).strip()
    candidates = getattr(response, "candidates", None) or []
    chunks: list[str] = []
    for candidate in candidates:
        content = _field(candidate, "content")
        parts = _field(content, "parts") or []
        for part in parts:
            value = _field(part, "text")
            if value:
                chunks.append(str(value))
    return "\n".join(chunks).strip()


def _grounding_metadata(response: Any) -> Any:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    return _field(candidates[0], "grounding_metadata", "groundingMetadata")


def _grounding_sources(response: Any) -> list[dict[str, str]]:
    metadata = _grounding_metadata(response)
    chunks = _field(metadata, "grounding_chunks", "groundingChunks") or []
    sources: list[dict[str, str]] = []
    seen: set[str] = set()
    for chunk in chunks:
        web = _field(chunk, "web")
        if not web:
            continue
        uri = str(_field(web, "uri") or "").strip()
        if not uri or uri in seen:
            continue
        seen.add(uri)
        sources.append(
            {
                "title": str(_field(web, "title") or "source").strip(),
                "uri": uri,
            }
        )
    return sources


def _grounding_queries(response: Any) -> list[str]:
    metadata = _grounding_metadata(response)
    values = _field(metadata, "web_search_queries", "webSearchQueries") or []
    return [str(item) for item in values if str(item).strip()]


def _field(obj: Any, *names: str) -> Any:
    if obj is None:
        return None
    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        value = getattr(obj, name, None)
        if value is not None:
            return value
    return None


async def _maybe_await(value: Awaitable[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    if inspect.isawaitable(value):
        return await value
    return value


def _lookup_model() -> str:
    return (
        os.getenv("PARROT_GEMINI_GROUNDING_MODEL", "").strip()
        or os.getenv("GEMINI_GROUNDING_MODEL", "").strip()
        or _DEFAULT_MODEL
    )


def _google_api_key() -> str:
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        value = os.getenv(name, "").strip()
        if value:
            return value
    try:
        from parrot.shared.config import ParrotConfig

        return (ParrotConfig().google_api_key or "").strip()
    except Exception:
        return ""


def _compact(value: str, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


__all__ = ["web_lookup_intent", "do_web_lookup_intent"]
