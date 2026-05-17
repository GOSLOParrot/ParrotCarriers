"""Static-source guard: fly_to / animate / set_video_tier import and call
attach_state_header (Phase 4 W3 selection-C).

Why static source instead of running the tool through livekit's FunctionTool:
    livekit-agents `function_tool()` replaces the underlying function with
    a FunctionTool instance whose invocation API is private (`_func`,
    `_invoke`, etc.) and bound to RunContext + LLM tool-call plumbing. We
    don't want to depend on private internals or stand up a FunctionTool
    runtime just to verify two-line tool wrapping is in place. The
    behavioural correctness of `attach_state_header` itself is covered
    by `test_state_context.py`; here we only catch the regression where
    someone removes the wrapper call from a tool.

If the LLM-facing tool result format is later restructured (e.g. switch to
typed pydantic returns), this test will need rewriting — which is the
intended signal that the protocol contract is changing.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "src" / "parrot" / "brain" / "tools"


def _read(name: str) -> str:
    return (TOOLS_DIR / name).read_text(encoding="utf-8")


def test_fly_to_imports_and_calls_attach_state_header():
    src = _read("fly_to.py")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    assert "attach_state_header(result)" in src


def test_animate_imports_and_calls_attach_state_header():
    src = _read("animate.py")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    assert "attach_state_header(result)" in src


def test_perch_to_finger_uses_ecp_rpc_and_state_header():
    src = _read("perch_to_finger.py")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    assert "EcpCommandKind.PERCH_TO_FINGER" in src
    assert 'method="perchToFinger"' in src
    assert '"anchor": "index_finger_middle_segment"' in src
    assert "attach_state_header(result)" in src


def test_return_to_view_uses_ecp_rpc_and_state_header():
    src = _read("return_to_view.py")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    assert "EcpCommandKind.RETURN_TO_VIEW" in src
    assert 'method="returnToView"' in src
    assert '"anchor": "camera_view_center"' in src
    assert "attach_state_header(result)" in src


def test_set_video_tier_imports_and_calls_attach_state_header():
    src = _read("set_video_tier.py")
    assert "from parrot.brain.tools._state_context import attach_state_header" in src
    # set_video_tier wraps both the failure-path and success-path return
    # values; assert the symbol is referenced in at least 2 places.
    assert src.count("attach_state_header(") >= 2
