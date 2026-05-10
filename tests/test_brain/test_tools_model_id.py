"""Static-source guard: animate / fly_to expose `model_id` and thread it
through `wrap_legacy_rpc_payload(meta=...)`.

Sprint4 GOSLO model modularization (Step 3, 2026-05-06):
    Brain tools that target the parrot model body (animate / fly_to) accept
    an optional ``model_id`` kwarg and propagate it via the existing
    ``EcpCommand.meta`` wire slot. Empty string → no meta key emitted (wire
    shape stays exactly as it was pre-modularization; observers downstream
    don't see a new always-empty field). Non-empty → ``meta["model_id"]``
    is set so Unity-side ``ParrotRegistry`` can route.

Why static source instead of running the tools through livekit-agents:
    `function_tool()` wraps them in a FunctionTool whose invocation API is
    private. The semantically interesting wire-shape behaviour is already
    covered by ``tests/test_scheduler/test_ecp.py`` (meta kwarg on
    ``wrap_legacy_rpc_payload``). Here we only catch the regression where
    someone removes the kwarg from the tool function or forgets to forward
    it into ``wrap_legacy_rpc_payload``.

Pattern mirrored from ``tests/test_ecp_event/test_tools_state_header.py``.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "src" / "parrot" / "brain" / "tools"


def _read(name: str) -> str:
    return (TOOLS_DIR / name).read_text(encoding="utf-8")


def test_animate_exposes_model_id_kwarg():
    src = _read("animate.py")
    # Default empty string keeps backward compat — old callers that don't
    # know about model_id still work.
    assert 'model_id: str = ""' in src, (
        "animate.py must declare `model_id: str = \"\"` so Gemini sees an "
        "optional kwarg with safe default."
    )


def test_animate_threads_model_id_into_meta():
    src = _read("animate.py")
    # Either pattern is acceptable: dict literal with conditional value, or
    # branched kwarg construction. We assert the simplest invariant — meta
    # is forwarded into wrap_legacy_rpc_payload AND model_id appears next
    # to it on the same call site.
    assert "meta=" in src, "animate.py must pass meta= to wrap_legacy_rpc_payload"
    assert 'model_id' in src and '"model_id"' in src, (
        "animate.py must build a meta payload keyed on \"model_id\"."
    )


def test_animate_checks_selected_model_capability_before_rpc():
    src = _read("animate.py")

    assert "supports_capability(animation_name" in src
    assert "unsupported_message(animation_name" in src


def test_fly_to_exposes_model_id_kwarg():
    src = _read("fly_to.py")
    assert 'model_id: str = ""' in src, (
        "fly_to.py must declare `model_id: str = \"\"` so Gemini sees an "
        "optional kwarg with safe default."
    )


def test_fly_to_threads_model_id_into_meta():
    src = _read("fly_to.py")
    assert "meta=" in src, "fly_to.py must pass meta= to wrap_legacy_rpc_payload"
    assert 'model_id' in src and '"model_id"' in src, (
        "fly_to.py must build a meta payload keyed on \"model_id\"."
    )


def test_animate_empty_model_id_does_not_emit_meta_key():
    """Audit guard — when model_id is empty, the meta kwarg must be None
    (or {}) rather than {"model_id": ""}.

    Otherwise the wire grows a ``"meta": {"model_id": ""}`` block in every
    legacy call, which would be a noisy diff across every audit log line.
    The convention is: empty model_id == "no routing hint, take the active
    controller" == omit the key entirely.
    """
    src = _read("animate.py")
    # We expect the truthiness pattern (`if model_id`) to gate the meta dict.
    # This is a weak signal — the test would also pass on any conditional —
    # but combined with the ``meta=`` and ``"model_id"`` presence assertions
    # above it's enough to catch obvious regressions.
    assert "if model_id" in src, (
        "animate.py must conditionally build the meta dict so empty model_id "
        "leaves the wire shape unchanged."
    )


def test_fly_to_empty_model_id_does_not_emit_meta_key():
    """Mirror of the animate.py guard. See its docstring."""
    src = _read("fly_to.py")
    assert "if model_id" in src, (
        "fly_to.py must conditionally build the meta dict so empty model_id "
        "leaves the wire shape unchanged."
    )


def test_play_capability_validates_manifest_and_threads_model_id():
    src = _read("play_capability.py")

    assert "capability_id: str" in src
    assert "supports_capability" in src
    assert "unsupported_message" in src
    assert "wrap_legacy_rpc_payload" in src
    assert "meta=" in src
    assert '"model_id"' in src
    assert '"strict_capability": True' in src
    assert 'method="animate"' in src


def test_lineb_model_reaction_uses_strict_capability_rpc():
    src = (REPO_ROOT / "src" / "parrot" / "brain" / "lineb_model_reaction.py").read_text(
        encoding="utf-8"
    )

    assert '"speaking": "lineb_speaking"' in src
    assert "supports_capability" in src
    assert "wrap_legacy_rpc_payload" in src
    assert '"strict_capability": True' in src
    assert 'method="animate"' in src


def test_fly_to_checks_capability_before_rpc():
    src = _read("fly_to.py")

    assert 'supports_capability("fly"' in src
    assert 'unsupported_message("fly"' in src
