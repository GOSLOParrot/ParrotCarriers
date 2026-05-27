from __future__ import annotations

import py_trees
import pytest

from parrot.brain.context_injector import ContextInjector


class _FakeChatContext:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    def copy(self) -> "_FakeChatContext":
        clone = _FakeChatContext()
        clone.messages = list(self.messages)
        return clone

    def add_message(self, *, role: str, content: list[str]) -> None:
        self.messages.append({"role": role, "content": content})


class _FakeSession:
    def __init__(self) -> None:
        self.chat_ctx = _FakeChatContext()
        self.update_count = 0
        self.generated_replies: list[str] = []

    async def update_chat_ctx(self, chat_ctx: _FakeChatContext) -> None:
        self.chat_ctx = chat_ctx
        self.update_count += 1

    async def generate_reply(self, *, instructions: str) -> None:
        self.generated_replies.append(instructions)


@pytest.fixture(autouse=True)
def _reset_blackboard() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}


@pytest.mark.asyncio
async def test_evidence_awareness_notice_routes_to_c3_without_speech() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/evidence_awareness_notice",
        {},
        {
            "evidence_id": "ev_123",
            "staged_ref_id": "ref_456",
            "notify_goslo": True,
            "allow_react": True,
            "reason": "staged_notify_allowed",
            "message": "Visual evidence ready for inspection.",
        },
    )

    assert session.update_count == 1
    assert session.generated_replies == []
    assert session.chat_ctx.messages
    pushed = session.chat_ctx.messages[-1]
    assert pushed["role"] == "user"
    assert "Visual evidence ready" in pushed["content"][0]
    assert "evidence_id=ev_123" in pushed["content"][0]
    assert "do not interrupt" in pushed["content"][0]


@pytest.mark.asyncio
async def test_silent_evidence_awareness_notice_stays_layer_one() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/evidence_awareness_notice",
        {},
        {
            "evidence_id": "ev_123",
            "staged_ref_id": "ref_456",
            "notify_goslo": False,
            "allow_react": False,
            "reason": "staged_silent",
            "message": "Visual evidence ready for inspection.",
        },
    )

    assert session.update_count == 0
    assert session.generated_replies == []
    assert session.chat_ctx.messages == []


@pytest.mark.asyncio
async def test_photo_awareness_notice_routes_to_c3_without_speech() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/photo_awareness_notice",
        {},
        {
            "photo_id": "photo_123",
            "policy": "AWARE_SILENT",
            "notify_goslo": True,
            "allow_react": False,
            "allow_interrupt": False,
            "preview_ref_id": "ref_photo_456",
            "reason": "preview_ref_staged",
        },
    )

    assert session.update_count == 1
    assert session.generated_replies == []
    pushed = session.chat_ctx.messages[-1]
    assert pushed["role"] == "user"
    assert "Photo preview is staged" in pushed["content"][0]
    assert "photo_id=photo_123" in pushed["content"][0]
    assert "preview_ref_id=ref_photo_456" in pushed["content"][0]
    assert "do not interrupt" in pushed["content"][0]


@pytest.mark.asyncio
async def test_obsidian_context_notice_routes_to_c3_without_speech() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/obsidian_context_notice",
        {},
        {
            "source_pack_uuid": "pack_123",
            "staged_ref_ids": ["ref_obsidian_456"],
            "item_count": 1,
            "notify_goslo": True,
            "allow_react": False,
            "priority": "c3_high_context",
            "message": "Obsidian diary/context source pack is staged.",
        },
    )

    assert session.update_count == 1
    assert session.generated_replies == []
    pushed = session.chat_ctx.messages[-1]
    assert pushed["role"] == "user"
    assert "Obsidian diary/context source pack is staged" in pushed["content"][0]
    assert "staged_ref_ids=ref_obsidian_456" in pushed["content"][0]
    assert "source_pack_uuid=pack_123" in pushed["content"][0]
    assert "do not interrupt" in pushed["content"][0]


@pytest.mark.asyncio
async def test_photo_awareness_pending_notice_waits_for_staged_ref() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/photo_awareness_notice",
        {},
        {
            "photo_id": "photo_123",
            "policy": "AWARE_REACT",
            "notify_goslo": True,
            "allow_react": True,
            "allow_interrupt": False,
            "reason": "preview_ref_pending",
        },
    )

    assert session.update_count == 0
    assert session.generated_replies == []
    assert session.chat_ctx.messages == []


@pytest.mark.asyncio
async def test_unaware_photo_notice_stays_layer_one() -> None:
    session = _FakeSession()
    injector = ContextInjector(session)  # type: ignore[arg-type]

    await injector._dispatch(
        "transient/photo_awareness_notice",
        {},
        {
            "photo_id": "photo_123",
            "policy": "UNAWARE_RECORDED",
            "notify_goslo": False,
            "allow_react": False,
            "allow_interrupt": False,
            "reason": "awareness_disabled_or_unaware",
        },
    )

    assert session.update_count == 0
    assert session.generated_replies == []
    assert session.chat_ctx.messages == []
