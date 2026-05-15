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
