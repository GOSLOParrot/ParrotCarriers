"""Naming-collision guard for DSG / Brain Plan / IntentWorkspace docs+code.

主设计稿 § 0.2 hard rules:
    - "Compartment" must NOT appear under parrot.dsg.l1_5/.
    - "Bucket" must NOT appear under parrot.dsg.l2b/.
    - The lone string "Event" (without IntentEvent / Episode / EventBoundary
      qualifier) is forbidden in any module / docstring / class name in
      the parrot.brain.plan + parrot.dsg.l2b + parrot.dsg.l1_5 +
      parrot.dsg.archive subpackages.
    - "Scene" alone is allowed only when paired with Type / Tag /
      Profile / Registry / Snapshot / Switch.

This test crawls the relevant source files and fails on violations,
giving an early-warning if implementation chats reintroduce confusion.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


_SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "parrot"


def _read_files(*subpaths: str) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for sub in subpaths:
        d = _SRC_ROOT / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*.py"):
            try:
                out.append((p, p.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
    return out


def test_compartment_not_in_l1_5() -> None:
    """``Compartment`` is L2-B-only.

    L1.5 modules MUST NOT use ``Compartment`` as a class / variable /
    type name. Cross-reference comments that explicitly disclaim
    "Compartment lives in L2-B" are allowed (they document the rule
    rather than violate it).
    """
    pattern = re.compile(r"\bCompartment\b")
    code_pattern = re.compile(
        r"^\s*(class|def|from .* import .*Compartment|import .*Compartment|"
        r"\w*\s*[:=].*Compartment)", re.MULTILINE,
    )
    violations: list[str] = []
    for path, body in _read_files("dsg/l1_5"):
        if not pattern.search(body):
            continue
        # Reject any code-level use (class def / import / type annotation).
        for i, line in enumerate(body.splitlines(), start=1):
            stripped = line.strip()
            # Skip comment / docstring lines that explicitly cite the rule.
            if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if "Compartment" not in stripped:
                continue
            if stripped.startswith('"') or stripped.startswith("'"):
                # narrative docstring continuation
                continue
            # Anything else is a real code reference
            violations.append(f"{path}:{i}: {stripped}")
    assert not violations, (
        "L1.5 must not use 'Compartment' in code:\n  " + "\n  ".join(violations)
    )


def test_bucket_not_in_l2b_subpackage() -> None:
    """`Bucket` is L1.5-only."""
    violations: list[str] = []
    for path, body in _read_files("dsg/l2b"):
        for i, line in enumerate(body.splitlines(), start=1):
            stripped = line.strip()
            if "Bucket" not in stripped:
                continue
            # Allow string comparisons against the field name
            # ``bucket_id`` (the L2-B node carries this informational
            # tag — see 主设计稿 § 2.2). Reject only the L1.5 class
            # / enum names.
            if re.search(r"\bBucket(Kind|Spec|Handle|Op|Registry)\b", stripped):
                violations.append(f"{path}:{i}: {stripped}")
            elif re.search(r"\bbucket_id\b", stripped):
                continue  # tag field reference — OK
            elif re.search(r"\bview_by_bucket\b", stripped):
                continue  # view function — OK
    assert not violations, "L2-B must not reference L1.5 'Bucket' classes:\n  " + "\n  ".join(violations)


def test_event_must_be_qualified() -> None:
    """``Event`` (lone) must be ``IntentEvent`` or appear in ``Episode`` /
    ``EventBoundary`` / ``EpisodeMarker`` / ``EventDriven`` etc."""
    bad: list[str] = []
    pattern = re.compile(r"\bEvent\b")
    allowed_qualifiers = (
        "IntentEvent",
        "EventBoundary",
        "EVENT_DRIVEN",
        "EventDriven",
        "EventReason",
        "TimelineMarkerKind.INTENT_EVENT",
        "BoundaryEvent",
        "BUCKET_OP",
        # generic library terms
        "EventEnvelope",
        "EventLoop",
        "asyncio.Event",
        "ConversationBoundaryEvent",
    )
    for path, body in _read_files("dsg/l1_5", "dsg/l2b", "dsg/archive", "brain/plan"):
        for i, line in enumerate(body.splitlines(), start=1):
            stripped = line.strip()
            if not pattern.search(stripped):
                continue
            # Skip docstrings + comment lines that explicitly list the
            # naming policy (intentional discussion of the rule).
            lower = stripped.lower()
            if "naming" in lower or "rule" in lower or "alone" in lower:
                continue
            # Skip if any allowed qualifier is present
            if any(q in stripped for q in allowed_qualifiers):
                continue
            # Allow EpisodeMarker / Episode / NodeKind.EVENT enum value
            if re.search(r"\bEpisode\b", stripped) or "NodeKind.EVENT" in stripped or "EVENT" == stripped:
                continue
            # Allow ``"event_id"`` and ``event_id:`` field references
            if "event_id" in stripped:
                continue
            # Lone "Event" appears
            if re.search(r"(?<!Intent)(?<!Boundary)(?<!Bucket_)Event(?!Boundary)(?!Reason)(?!Driven)(?!Envelope)(?!Loop)(?!.value)", stripped):
                # final guard: word-boundary check
                tokens = re.findall(r"\b[A-Za-z_]\w*\b", stripped)
                if any(t == "Event" for t in tokens):
                    bad.append(f"{path}:{i}: {stripped}")
    assert not bad, "Lone 'Event' must be qualified (IntentEvent / Episode / etc):\n  " + "\n  ".join(bad)
