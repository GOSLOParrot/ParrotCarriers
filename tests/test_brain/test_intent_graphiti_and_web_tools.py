from __future__ import annotations

import asyncio
import importlib

import parrot.brain.tools as tools_mod
from parrot.brain.tools.message_check_request import do_message_check_request
from parrot.brain.tools.query_etiquette_memory import do_query_etiquette_memory
from parrot.brain.tools.query_memory import do_query_memory
from parrot.brain.tools.reminder_request import do_reminder_request
from parrot.brain.tools.web_lookup_intent import do_web_lookup_intent
from parrot.memory.graphiti_client import PARTITIONS


def _tool_ids(tools):
    return {getattr(tool, "id", "") for tool in tools}


def test_goslo_intent_tools_are_registered(monkeypatch) -> None:
    monkeypatch.setattr(tools_mod, "_active_pipeline_hint", lambda: "line_a")

    ids = _tool_ids(tools_mod.tools_for_active_model())

    assert "gemini_google_search" in ids
    assert "web_lookup_intent" in ids
    assert "query_memory" in ids
    assert "query_etiquette_memory" in ids
    assert "message_check_request" in ids
    assert "reminder_request" in ids
    assert "identify_object" not in ids


def test_gemini_provider_search_is_skipped_for_line_b(monkeypatch) -> None:
    monkeypatch.setattr(tools_mod, "_active_pipeline_hint", lambda: "line_b")

    ids = _tool_ids(tools_mod.tools_for_active_model())

    assert "gemini_google_search" not in ids
    assert "web_lookup_intent" in ids


def test_identify_object_env_gate_survives_module_reload(monkeypatch) -> None:
    monkeypatch.delenv("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", raising=False)
    reloaded = importlib.reload(tools_mod)

    try:
        ids = _tool_ids(reloaded.tools_for_active_model())

        assert "identify_object" not in ids
        monkeypatch.setenv("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", "1")
        reloaded = importlib.reload(tools_mod)
        ids = _tool_ids(reloaded.tools_for_active_model())
        assert "identify_object" in ids
    finally:
        monkeypatch.setenv("PARROT_ENABLE_IDENTIFY_OBJECT_TOOL", "0")
        importlib.reload(tools_mod)


def test_query_etiquette_memory_uses_noble_partition_and_multihop_strategy() -> None:
    captured = {}

    async def fake_searcher(**kwargs):
        captured.update(kwargs)
        return {
            "success": True,
            "message": "1 hit",
            "data": {
                "hits": [
                    {
                        "text": "A calling card should be left after a formal visit.",
                        "uuid": "fact-uuid-123456",
                        "source_node_uuid": "src-abc",
                        "target_node_uuid": "dst-def",
                    }
                ],
                "subgraph": {"nodes": [{"id": "src"}], "edges": [{"id": "edge"}]},
                "graphiti_bundle": {"raw_envelopes": [{"uuid": "fact-uuid-123456"}]},
                "search_plan": [{"query": "calling cards"}],
            },
        }

    text = asyncio.run(
        do_query_etiquette_memory(
            query="calling card visit",
            depth=9,
            limit=20,
            searcher=fake_searcher,
        )
    )

    assert captured["partition"] == PARTITIONS.NOBLE_ETIQUETTE
    assert captured["strategy"] == "iterative_hybrid"
    assert captured["depth"] == 3
    assert captured["limit"] == 10
    assert "noble_etiquette Graphiti result" in text
    assert "calling card should be left" in text
    assert "No Graphiti write" in text
    assert "L2-B materialization" in text


def test_query_memory_is_fixed_to_laptop_profile_partition() -> None:
    captured = {}

    async def fake_searcher(**kwargs):
        captured.update(kwargs)
        return {
            "success": True,
            "data": {
                "hits": [
                    {
                        "text": "Logitech G504 is the user's mouse.",
                        "uuid": "fact-mouse-123456",
                    }
                ],
                "subgraph": {"nodes": [{"id": "mouse"}], "edges": []},
                "strategy": "iterative_hybrid",
            },
        }

    text = asyncio.run(
        do_query_memory(
            query="用户的鼠标是什么",
            depth=9,
            searcher=fake_searcher,
        )
    )

    assert captured["partition"] == PARTITIONS.LAPTOP_PROFILE_TEST
    assert captured["strategy"] == "iterative_hybrid"
    assert captured["depth"] == 3
    assert captured["limit"] == 8
    assert "laptop_profile_test" in text
    assert "Logitech G504" in text


def test_message_check_request_dispatches_nanobot_message_check() -> None:
    dispatched = []

    async def fake_dispatch(task_type, params, priority):
        dispatched.append((task_type, params, priority))
        return "msg-task"

    text = asyncio.run(
        do_message_check_request(
            query="Check important Gmail",
            account="gosloparrot@gmail.com",
            max_messages=99,
            priority="high",
            reason="demo",
            task_dispatcher=fake_dispatch,
        )
    )

    assert "msg-task" in text
    assert dispatched
    task_type, params, priority = dispatched[0]
    assert task_type == "message_check"
    assert priority == "high"
    assert params["result_channel"] == "message_result"
    assert params["max_messages"] == 20
    assert "Do not send mail" in params["instructions"]


def test_reminder_request_dispatches_nanobot_remind() -> None:
    dispatched = []

    async def fake_dispatch(task_type, params, priority):
        dispatched.append((task_type, params, priority))
        return "rem-task"

    text = asyncio.run(
        do_reminder_request(
            reminder_text="drink water",
            when="in 20 minutes",
            priority="reflex",
            task_dispatcher=fake_dispatch,
        )
    )

    assert "rem-task" in text
    assert dispatched
    task_type, params, priority = dispatched[0]
    assert task_type == "remind"
    assert priority == "reflex"
    assert params["result_channel"] == "reminder_result"
    assert params["reminder_text"] == "drink water"


def test_web_lookup_intent_formats_grounded_result() -> None:
    async def fake_lookup(**kwargs):
        return {
            "model": "fake-grounded",
            "text": "The visible logo most likely belongs to Example Tea.",
            "queries": ["Example Tea logo milk tea"],
            "sources": [
                {"title": "Example Tea", "uri": "https://example.test/tea"},
            ],
        }

    text = asyncio.run(
        do_web_lookup_intent(
            query="what milk tea brand has this green crown logo",
            purpose="visual_brand_check",
            context_hint="green crown logo on cup",
            grounded_lookup=fake_lookup,
        )
    )

    assert "T1 web_lookup_intent grounded result" in text
    assert "Example Tea" in text
    assert "https://example.test/tea" in text
    assert "No external mutation occurred" in text


def test_web_lookup_intent_falls_back_to_t3_research_on_timeout() -> None:
    dispatched = []

    async def slow_lookup(**kwargs):
        await asyncio.sleep(0.6)
        return {"text": "too late"}

    async def fake_dispatch(task_type, params, priority):
        dispatched.append((task_type, params, priority))
        return "task-web-1"

    text = asyncio.run(
        do_web_lookup_intent(
            query="identify a milk tea brand from visual hints",
            purpose="visual_brand_check",
            context_hint="brown cup, cursive logo",
            grounded_lookup=slow_lookup,
            task_dispatcher=fake_dispatch,
            thinking_budget_s=0.001,
        )
    )

    assert "T3 research task dispatched: task-web-1" in text
    assert dispatched
    task_type, params, priority = dispatched[0]
    assert task_type == "research"
    assert priority == "high"
    assert params["source"] == "web_lookup_intent_t1_fallback"
    assert params["context_hint"] == "brown cup, cursive logo"
