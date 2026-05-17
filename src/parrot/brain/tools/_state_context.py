"""Sprint4 Phase 4 W3 — selection-C state context helper.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L10).

LLM 注入路径 C: 执行类 tool (fly_to / animate / set_video_tier) 在 execute
时把当前 GOSLO body / head / cognitive 三态 + active_locks + active_command_id
作为一个紧凑前缀附在 tool 返回值上，让 Gemini 在生成下一个语音回合前能看
到 "我现在身体在做什么 / 大脑在做什么"，避免 GOSLO 跳舞时说 "咱们出门散步
吧" 这种状态分叉的体感事故 (entry doc §3.4 的硬要求)。

为什么不走选项 A (system prompt 末段刷新)：会侵入 LLM 上下文 + 烧 token
+ 跨 turn 持久化难。
为什么不走选项 B (query_my_state tool)：LLM 会学会"先查再决定"，多一个
turn 浪费 token；而且无法保证 LLM 真的会记得查。

选项 C 把 "状态 attach 在执行类 tool 的返回值" 变成 LLM **必然看到** 的输
入 (因为 tool result 紧跟在 tool call 后面)，没有遗漏空间，token 成本
~30 字符/次。

Format
------
单行 ASCII 前缀，最大 ~140 字符；followed by 真正的 RPC response::

    [GOSLO state] body=DANCING head=HEAD_FORWARD cognitive=SPEAKING locks=body active_cmd=cmd_abc12345
    {actual RPC JSON or text}

省略默认值字段以减少噪声 — body=IDLE / head=HEAD_FORWARD / cognitive=IDLE_MIND /
no locks / no active cmd 都不打印。当全部都是默认时，前缀完全不附加 (LLM
看到的就是裸 RPC response)。

NOT
---
本 helper **不** 做决策 / 不 reason / 不裁剪 LLM 行为；只 surface 客观状态。
LLM 看到 body=DANCING 就会自己推导 "现在不是说出门散步的时机"。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from parrot.scheduler.blackboard import open_bb_client
from parrot.shared.parrot_actions import CognitiveState, ParrotBodyState

if TYPE_CHECKING:
    import py_trees


logger = logging.getLogger(__name__)


_READER_NAME = "tools._state_context"

# Default values that are NOT worth surfacing to the LLM. These are the
# "everything is normal" values per parrot_behavior_rules.md §1.
_DEFAULT_BODY = ParrotBodyState.IDLE
_DEFAULT_HEAD = "HEAD_FORWARD"  # parrot_behavior_rules §1.2 default
_DEFAULT_COGNITIVE = CognitiveState.IDLE_MIND


_bb: "py_trees.blackboard.Client | None" = None


def _ensure_bb() -> "py_trees.blackboard.Client":
    """Open a read-only-style BB client. We declare a writer string so the
    py-trees Blackboard can audit; we never actually write.
    """
    global _bb
    if _bb is None:
        _bb = open_bb_client(name="state_context", writer=_READER_NAME)
    return _bb


def _safe_get(key: str) -> Any:
    """Read a BB key, returning None on KeyError without noisy logging.

    Phase 4 W3 stage: head_state has no producer yet (Unity-side W3.A.2);
    cognitive_state may be empty during the first ~100ms after agent boot
    before agent_state_changed fires; active_locks ditto. Empty reads are
    expected, not errors.
    """
    try:
        return _ensure_bb().get(key)
    except KeyError:
        return None


def get_state_snapshot() -> dict[str, Any]:
    """Read the four BB keys this helper cares about. Returns a dict with
    None values for missing producers.
    """
    return {
        "body_state": _safe_get("tick/body_state"),
        "head_state": _safe_get("tick/head_state"),
        "cognitive_state": _safe_get("tick/cognitive_state"),
        # session/ecp_state is the place active_locks / active_command_id
        # eventually live (entry doc §8.1 L1 — Phase 4 EcpState upload).
        # Until that producer exists, this read returns None and we skip
        # those fields in the header.
        "ecp_state": _safe_get("session/ecp_state"),
    }


def _stringify(value: Any) -> str:
    """Render an enum or plain value as a stable wire string."""
    if value is None:
        return ""
    # str-mixin enums (ParrotBodyState, CognitiveState, etc.) repr as
    # "ClassName.MEMBER" but str() returns the value cleanly.
    return str(value.value) if hasattr(value, "value") else str(value)


def format_state_header(snapshot: dict[str, Any] | None = None) -> str:
    """Return a single-line ASCII state header, or empty string if all
    fields are at their defaults.

    Empty-string return is the "no header attached" signal — callers
    should skip the header concat entirely in that case to avoid a stray
    leading newline in the LLM-facing tool result.
    """
    snap = snapshot if snapshot is not None else get_state_snapshot()

    parts: list[str] = []

    ecp_state = snap.get("ecp_state")

    body = snap.get("body_state")
    if isinstance(ecp_state, dict):
        ecp_body = ecp_state.get("body_state")
        if ecp_body and (body is None or _stringify(body).lower() == _DEFAULT_BODY.value):
            body = ecp_body
    body_str = _stringify(body).lower()
    # Emit body unless it equals IDLE (default). We compare on string value
    # so unknown raw strings (defensive — e.g. Unity sends a future state
    # before backend enum updates) still surface.
    if body is not None and body_str and body_str != _DEFAULT_BODY.value:
        parts.append(f"body={body_str}")
    if body_str == "perched_on_hand":
        parts.append("mode=ON_HAND")

    head = snap.get("head_state")
    if isinstance(ecp_state, dict):
        ecp_head = ecp_state.get("head_state")
        if ecp_head and (head is None or _stringify(head) == _DEFAULT_HEAD):
            head = ecp_head
    head_str = _stringify(head)
    if head is not None and head_str and head_str != _DEFAULT_HEAD:
        parts.append(f"head={head_str}")

    cognitive = snap.get("cognitive_state")
    cognitive_str = _stringify(cognitive)
    if cognitive is not None and cognitive_str and cognitive_str != _DEFAULT_COGNITIVE.value:
        parts.append(f"cognitive={cognitive_str}")

    if isinstance(ecp_state, dict):
        locks = ecp_state.get("active_locks") or ()
        if locks:
            # active_locks may arrive as list or tuple; render comma-separated
            locks_str = ",".join(str(l) for l in locks)
            parts.append(f"locks={locks_str}")
        active_cmd = ecp_state.get("active_command_id") or ""
        if active_cmd:
            parts.append(f"active_cmd={active_cmd}")

    if not parts:
        return ""
    return "[GOSLO state] " + " ".join(parts)


def attach_state_header(rpc_response: str) -> str:
    """Convenience wrapper for tools: prepend the header (if any) to an
    RPC response string. Returns the response unchanged when no
    interesting state exists.
    """
    header = format_state_header()
    if not header:
        return rpc_response
    # Single newline separator — LLMs handle this far better than literal
    # "\\n\\n" or fancy formatting.
    return f"{header}\n{rpc_response}"


__all__ = [
    "attach_state_header",
    "format_state_header",
    "get_state_snapshot",
]
