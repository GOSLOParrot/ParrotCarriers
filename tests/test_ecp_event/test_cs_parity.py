"""Cross-language parity guard for `EcpEventType` enum (Python ↔ C#).

Entry doc §8.5 #2 + §8.4: event_type registry MUST be in lockstep between
``src/parrot/shared/ecp_event.py:EcpEventType`` and
``unity/ArSpike/Assets/Scripts/ParrotApp/Ecp/EcpEventDto.cs:EcpEventTypeNames``.

This test parses the C# file as text (the alternative — compile + reflect —
needs a full Unity toolchain; we don't want CI to depend on that). It looks
for ``public const string Foo = "x.y";`` lines inside the
``EcpEventTypeNames`` static class.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from parrot.shared.ecp_event import EcpEventSource, EcpEventType


REPO_ROOT = Path(__file__).resolve().parents[2]
CS_DTO_PATH = REPO_ROOT / "unity" / "ArSpike" / "Assets" / "Scripts" / "ParrotApp" / "Ecp" / "EcpEventDto.cs"


def _extract_const_strings(cs_text: str, class_name: str) -> set[str]:
    """Parse `public const string X = "value";` lines from a named static
    class. Tolerant of // comments inside the class body."""
    # Find the `static class <name> { ... }` block
    pattern = re.compile(
        rf"public\s+static\s+class\s+{class_name}\s*{{(?P<body>.*?)^\s*}}",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(cs_text)
    if not m:
        pytest.fail(f"Could not find `public static class {class_name}` in {CS_DTO_PATH}")
    body = m.group("body")
    # Strip // comments to avoid `// "fake"` matches
    body_stripped = re.sub(r"//.*?$", "", body, flags=re.MULTILINE)
    return set(re.findall(r'public\s+const\s+string\s+\w+\s*=\s*"([^"]+)"\s*;', body_stripped))


def test_cs_dto_file_exists():
    assert CS_DTO_PATH.is_file(), f"Missing C# DTO at {CS_DTO_PATH}"


def test_event_type_names_match_python_enum():
    cs_text = CS_DTO_PATH.read_text(encoding="utf-8")
    cs_values = _extract_const_strings(cs_text, "EcpEventTypeNames")
    py_values = {member.value for member in EcpEventType}

    assert cs_values == py_values, (
        f"Python ↔ C# EcpEventType drift:\n"
        f"  in Python only: {py_values - cs_values}\n"
        f"  in C# only:     {cs_values - py_values}\n"
        f"  Update both atomically per entry doc §8.5 #2."
    )


def test_event_source_names_match_python_enum():
    cs_text = CS_DTO_PATH.read_text(encoding="utf-8")
    cs_values = _extract_const_strings(cs_text, "EcpEventSourceNames")
    py_values = {member.value for member in EcpEventSource}

    assert cs_values == py_values, (
        f"Python ↔ C# EcpEventSource drift:\n"
        f"  in Python only: {py_values - cs_values}\n"
        f"  in C# only:     {cs_values - py_values}"
    )


def test_topic_constants_match_python():
    """`EcpEventConsts.Topic*` in C# must equal the Python topic constants."""
    from parrot.shared.ecp_event import (
        TOPIC_ECP_EVENT,
        TOPIC_ECP_STATE,
        TOPIC_ECP_TICK,
    )

    cs_text = CS_DTO_PATH.read_text(encoding="utf-8")
    cs_topics = _extract_const_strings(cs_text, "EcpEventConsts")
    expected = {TOPIC_ECP_EVENT, TOPIC_ECP_STATE, TOPIC_ECP_TICK}
    # EcpEventConsts has SchemaVersion / PayloadLimitBytes too (int constants
    # that don't match our regex), so we only assert the topic strings appear.
    assert expected.issubset(cs_topics), (
        f"Topic drift Python ↔ C#:\n"
        f"  Python expected: {expected}\n"
        f"  C# const strings: {cs_topics}\n"
        f"  Missing in C#: {expected - cs_topics}"
    )
