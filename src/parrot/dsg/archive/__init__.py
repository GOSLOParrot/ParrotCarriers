"""DSG Archive subpackage — three-phase delayed conversation archive.

DSG-ARCHIVE-V1.

Phase 1 (Hot)   : conversation runs; L2-B + L1.5 metadata + IntentWorkspace
                  in memory; ``archive`` does NOT write Graphiti.
Phase 2 (Cold)  : on ConversationBoundary, serialize to disk under
                  ``data/conversations/{conv_id}/``.
Phase 3 (Idle)  : nanobot worker (idle-detected) reads the disk queue
                  and pushes through unified_filter + LLM → Graphiti.

Public API:
    ConversationArchive / get_conversation_archive / set_archive_for_test
    ConversationBoundaryDetector / ConversationBoundary
    ArchiveRequest / ArchiveTarget / ArchiveRequestKind / dispatch_archive_request
    enqueue_episode_for_idle_archive
"""

from __future__ import annotations

from parrot.dsg.archive.boundary import (
    ConversationBoundary,
    ConversationBoundaryDetector,
    ConversationBoundaryEvent,
    get_boundary_detector,
    set_boundary_detector_for_test,
)
from parrot.dsg.archive.conversation import (
    ArchiveOutcome,
    ArchivePath,
    ArchiveRequest,
    ArchiveRequestKind,
    ArchiveTarget,
    ConversationArchive,
    PendingArchive,
    UnifiedArchiveFilter,
    KeepAllFilter,
    FilterDecision,
    dispatch_archive_request,
    enqueue_episode_for_idle_archive,
    get_conversation_archive,
    set_archive_for_test,
)

__all__ = [
    "ArchiveOutcome",
    "ArchivePath",
    "ArchiveRequest",
    "ArchiveRequestKind",
    "ArchiveTarget",
    "ConversationArchive",
    "ConversationBoundary",
    "ConversationBoundaryDetector",
    "ConversationBoundaryEvent",
    "FilterDecision",
    "KeepAllFilter",
    "PendingArchive",
    "UnifiedArchiveFilter",
    "dispatch_archive_request",
    "enqueue_episode_for_idle_archive",
    "get_boundary_detector",
    "get_conversation_archive",
    "set_archive_for_test",
    "set_boundary_detector_for_test",
]
