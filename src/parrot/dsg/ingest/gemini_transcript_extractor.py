"""DEPRECATED alias module — use ``parrot.dsg.ingest.transcript_extractor``.

Sprint 4 Phase 5+ Line B (2026-05-04) renamed
``gemini_transcript_extractor`` → ``transcript_extractor`` because the
extractor is pipeline-agnostic (works with both Line A Gemini Live and
Line B STT-LLM-TTS). This shim preserves the old module path so any
external scripts / in-flight chats that import the old names keep working;
NEW code should import from ``parrot.dsg.ingest.transcript_extractor``.

The old class name ``GeminiTranscriptExtractor`` and factory
``get_gemini_transcript_extractor`` remain available here as aliases of
the new ``TranscriptExtractor`` / ``get_transcript_extractor``.
"""

from __future__ import annotations

from parrot.dsg.ingest.transcript_extractor import (
    GeminiTranscriptExtractor,
    TranscriptExtractor,
    get_gemini_transcript_extractor,
    get_transcript_extractor,
)

__all__ = [
    "GeminiTranscriptExtractor",
    "TranscriptExtractor",
    "get_gemini_transcript_extractor",
    "get_transcript_extractor",
]
