"""Obsidian three-profile ingest filter.

App V1 treats Obsidian as three distinct source profiles, not as one
UUID-bound lane:

* ``profile=ref`` is a binding/strengthening note. It must carry
  ``obsidian_uuid`` because it points at an existing L2-B / Graphiti node and
  must not create a new setting node. Operator imports may set
  ``ref_mode=direct_context`` to lift a UUID-free ref diary as a setting/source
  context node instead of a RefBinding.
* ``profile=daily`` and ``profile=roleplay`` are setting-source notes. They
  may omit ``obsidian_uuid`` and use ``obsidian_note_key`` / path / title as
  local provenance.

This distinction is intentionally repeated here because menu-canvas Obsidian
settings, roleplay packs, and UUID-bound reference notes have different
write paths and must not be collapsed during future refactors.

Input shape (from ssot_enrichment_trigger):
    {
        "label": "user's backpack",
        "obsidian_uuid": "...",        # required only for profile=ref
        "obsidian_note_key": "...",    # path/key for daily/roleplay provenance
        "profile": "daily",            # ref | daily | roleplay
        "description": "...",          # optional, from note body
        "tags": ["..."],               # optional
    }

Missing uuid means rejection only for ``profile=ref``. Daily/roleplay setting
notes can use obsidian_note_key/path as provenance.
"""

from __future__ import annotations

import logging
from typing import Any

from parrot.dsg.ingest.base import (
    IngestFilter,
    IngestOutcome,
    Observation,
    ObservationSource,
)
from parrot.dsg.l1_5_protocol import SensorFrame
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind

logger = logging.getLogger(__name__)

_MAX_LABEL_LEN = 128
_VALID_PROFILES = frozenset({"ref", "daily", "roleplay"})
_PROFILE_ALIASES = {
    "setting": "daily",
    "setting_daily": "daily",
    "daily_setting": "daily",
    "setting_roleplay": "roleplay",
    "roleplay_setting": "roleplay",
    "rp": "roleplay",
    "reference": "ref",
    "ref_reinforce": "ref",
}


class UserTagFilter(IngestFilter):
    """Converts Obsidian tag-sync payloads to CONFIRMED Observations."""

    name = "user_tag_filter"

    def process_frame(self, frame: SensorFrame) -> IngestOutcome:
        return IngestOutcome(filter_name=self.name)

    def process_text(
        self,
        text: str,
        *,
        source: ObservationSource,
        provenance_stream_id: str = "",
        meta: dict[str, Any] | None = None,
    ) -> IngestOutcome:
        # text-path not used
        return IngestOutcome(filter_name=self.name)

    def process_tag(
        self,
        payload: dict[str, Any],
        *,
        provenance_stream_id: str = "",
    ) -> IngestOutcome:
        if not isinstance(payload, dict):
            return IngestOutcome(
                filter_name=self.name, rejected=1, reason="not_a_dict"
            )
        label = str(payload.get("label", "")).strip()[:_MAX_LABEL_LEN]
        uuid = str(payload.get("obsidian_uuid", "")).strip()
        if not label:
            return IngestOutcome(
                filter_name=self.name,
                rejected=1,
                reason="missing_label",
            )

        profile = _normalize_profile(payload.get("profile", "daily"))
        if profile not in _VALID_PROFILES:
            return IngestOutcome(
                filter_name=self.name,
                rejected=1,
                reason="invalid_profile",
            )
        ref_mode = str(payload.get("ref_mode") or "").strip().lower().replace("-", "_")
        uuid_free_ref_direct = (
            profile == "ref"
            and not uuid
            and ref_mode == "direct_context"
            and bool(payload.get("allow_uuid_free_ref", True))
        )
        # Only normal ref notes require an Obsidian UUID. Daily/roleplay notes
        # are setting sources for the menu and can be identified by path/title;
        # the operator-only direct-context ref lane intentionally behaves like
        # those source notes while preserving profile=ref metadata.
        if profile == "ref" and not uuid and not uuid_free_ref_direct:
            return IngestOutcome(
                filter_name=self.name,
                rejected=1,
                reason="missing_ref_uuid",
            )

        kind = _normalize_node_kind(payload.get("kind", NodeKind.OBJECT.value))
        tags = [str(tag) for tag in list(payload.get("tags", []))[:10]]
        meta = {
            "profile": profile,
            "tags": tags,
        }
        # These fields are operational metadata for vault reconciliation and
        # source health views. They stay in Observation.meta/source_meta instead
        # of becoming new SemanticNode top-level fields.
        for key in (
            "obsidian_path",
            "obsidian_note_key",
            "file_mtime",
            "double_link_count",
            "target_node_uuid",
            "ref_mode",
            "context_role",
            "ascent_channel",
        ):
            if key in payload:
                meta[key] = payload[key]

        obs = Observation(
            source=ObservationSource.USER_TAG_OBSIDIAN,
            provenance_stream_id=provenance_stream_id,
            obsidian_uuid=uuid,
            graphiti_uuid=str(payload.get("graphiti_uuid", "") or ""),
            label=label,
            kind=kind,
            description=str(payload.get("description", ""))[:400],
            confidence=1.0,
            confirmation=ConfirmationStatus.CONFIRMED,
            meta=meta,
        )
        return IngestOutcome(
            filter_name=self.name,
            accepted=1,
            observations=(obs,),
        )


def _normalize_profile(raw: Any) -> str:
    """Normalize Obsidian's three agreed profiles to canonical names."""
    value = str(raw or "daily").strip().lower().replace("-", "_")
    return _PROFILE_ALIASES.get(value, value)


def _normalize_node_kind(raw: Any) -> NodeKind:
    """Parse optional Obsidian node kind without letting bad input crash sync."""
    try:
        return NodeKind(str(raw or NodeKind.OBJECT.value).strip().lower())
    except ValueError:
        logger.debug("user_tag_filter: unknown node kind %r, defaulting to object", raw)
        return NodeKind.OBJECT


__all__ = ["UserTagFilter"]
