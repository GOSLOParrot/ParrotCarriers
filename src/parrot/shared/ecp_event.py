"""Sprint4 Phase 4 cross-language wire envelope — `EcpEvent`.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §8.1`` (L2 / L3
/ L4) and §8.3 (event_type registry).

NAMING (read first — easy to footgun)
-------------------------------------
There is **another** ``EventEnvelope`` in ``parrot.shared.event_log``. That class
is the **L0 Redis Stream** internal envelope (Sprint 0, ratified, untouched).

Phase 4 introduces a *separate* wire envelope for Unity ↔ Brain LiveKit
DataChannel transport with cross-language round-trip + dedup + size-cap
guarantees. It is named ``EcpEvent`` (no "Envelope" suffix) **on purpose** to
avoid the import-time ambiguity that nuked us during Sprint 1 with the
``soul_constraints`` BB key dual-identity (see ``bb_schema.py`` history).

    | Use case                       | Class           | Module                     | Channel                                             |
    |--------------------------------|-----------------|----------------------------|-----------------------------------------------------|
    | L0 Redis Stream internal       | EventEnvelope   | parrot.shared.event_log    | Redis Stream ``parrot.events.log`` (Brain-only)     |
    | Phase 4 cross-language wire    | EcpEvent        | parrot.shared.ecp_event    | LiveKit reliable DataChannel ``parrot.ecp.event``   |

Both are Pydantic; both are immutable. Don't import the wrong one.

CONTRACT (locked in §8 of the entry doc)
----------------------------------------
* Topic on the wire: ``parrot.ecp.event`` (NOT ``ecp.event.v1`` — aligned with
  existing ``parrot.ecp.state`` / ``parrot.ecp.health`` namespace).
* ``event_type`` MUST come from :class:`EcpEventType` — free strings rejected.
* ``source`` MUST come from :class:`EcpEventSource` — free strings rejected.
* ``payload`` JSON encoded MUST stay under :data:`ECP_EVENT_PAYLOAD_LIMIT_BYTES`
  (8 KB). Larger blobs go through HTTP upload + ``asset_ref`` (see §8 L8).
* ``event_id`` is time-sortable: ``evt_<ts_ms_hex>_<rand_hex>`` — Brain dedupes
  by event_id with a 60s sliding window.
* ``schema_version`` starts at 1; bump only on field-set change (payload schema
  evolution stays inside the per-event-type payload dict).
"""

from __future__ import annotations

import json
import os
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


SCHEMA_VERSION: int = 1

# Locked in §8.1 L3. Computed against the JSON-encoded payload bytes; the
# envelope's other fields are negligible relative to this cap. Brain-side
# `event_ingest` enforces it on receive; Unity-side caller MUST pre-check
# before publishing (otherwise the event is silently dropped after dedup).
ECP_EVENT_PAYLOAD_LIMIT_BYTES: int = 8 * 1024

# Topic constants — keep them as module-level so callers don't typo. Aligned
# with the existing ``parrot.ecp.state`` / ``parrot.ecp.health`` namespace
# already used by ``LiveKitDataChannelHeartbeatTransport``.
TOPIC_ECP_EVENT: str = "parrot.ecp.event"
TOPIC_ECP_STATE: str = "parrot.ecp.state"  # existing, declared here for one-stop reference
TOPIC_ECP_TICK: str = "parrot.ecp.tick"  # Phase 4 lossy gesture / pose / focus drag


class EcpEventSource(str, Enum):
    """Producer of the event.

    Locked in §8.1 L2 + §8.5 #5: ``unity`` / ``brain`` for Phase 4; ``nanobot``
    reserved as a placeholder so multi-agent extension does not break the
    enum's wire format. Adding a value is backward compatible; removing one is
    a schema_version bump.
    """

    UNITY = "unity"
    BRAIN = "brain"
    NANOBOT = "nanobot"  # reserved — no Phase 4 producer


class EcpEventType(str, Enum):
    """Event type registry — locked in §8.3.

    Naming convention: ``<domain>.<verb_or_state>`` lowercase; multi-word
    domains use snake_case (e.g. ``photo.taken_preview``). Adding a new value
    is backward compatible; renaming or removing is a schema_version bump.

    Phase 4 starter set — adding a value here MUST also:
      1. Update §8.3 in the entry doc (the human-facing registry)
      2. Add a payload TypedDict / Pydantic submodel under §8.3 if one doesn't
         exist yet (Phase 4 keeps payloads as dict[str, Any] for speed; payload
         schemas can promote to typed models once the producer / consumer pair
         is stable)
    """

    # Tool ② — identify_object full chain
    SNAPSHOT_CAPTURED = "snapshot.captured"
    SIGHTING_MATCHED = "sighting.matched"
    SIGHTING_UNMATCHED = "sighting.unmatched"

    # Tool ③ — Focus / BBox attention
    BBOX_PLACED = "bbox.placed"
    BBOX_REMOVED = "bbox.removed"
    FOCUS_ANCHORED = "focus.anchored"
    FOCUS_RELEASED = "focus.released"
    VISUAL_TOOL_LIFECYCLE = "visual_tool.lifecycle"
    ATTENTION_THRESHOLD_CROSSED = "attention.threshold.crossed"

    # Tool ④ — camera / photo
    PHOTO_TAKEN_PREVIEW = "photo.taken_preview"
    PHOTO_ASSET_UPLOADED = "photo.asset_uploaded"

    # Tool ① — gesture (optional Phase 4)
    GESTURE_RECOGNIZED = "gesture.recognized"

    # Tool ③ — config Echo (Phase 4 W6-7, F-05 fix). Unity ScriptableObject
    # `ParrotAttentionConfig` is the source of truth for Δ_focus / Δ_bbox /
    # threshold / target_ttl_s; Unity publishes this on Room.OnConnected (incl.
    # reconnect / Brain pipeline switch) so Brain `attention_config_handler`
    # writes BB `global/attention_thresholds`. payload schema (locked in
    # entry doc §8.1 L9 + bb_schema.py global/attention_thresholds comment):
    #   {"delta_focus": float, "delta_bbox": float, "threshold": float,
    #    "target_ttl_s": float, "schema_version": int = 1}
    ATTENTION_CONFIG_ECHO = "attention.config.echo"

    # Defensive — emitted by `event_ingest` when an inbound EcpEvent fails the
    # 8KB payload cap (so observers / metrics see the rejection instead of a
    # silent drop). Brain-only producer.
    EVENT_REJECTED_OVERSIZE = "event.rejected.oversize"


def generate_event_id() -> str:
    """Generate a time-sortable event_id.

    Format: ``evt_<ts_ms_hex>_<rand_hex>``. The 12-char hex prefix is the Unix
    epoch milliseconds at construction time, so a lexicographic sort over
    event_ids matches insertion-time ordering (good for dedup window scans
    and audit queries). The 8-char random suffix is collision-resistance for
    same-millisecond events.

    UUID v7 (RFC 9562) would be the spec-aligned choice, but Python stdlib
    doesn't ship a v7 generator. This format is purpose-built for our wire +
    dedup-window use case and is intentionally NOT a UUID — it's a string ID
    with the same time-sortable property. Promotion to v7 is a Phase 5+ option
    and would only require the dedup window logic to keep treating event_id
    as opaque (no fields are parsed from it).
    """
    ts_ms = int(time.time() * 1000)
    ts_hex = format(ts_ms, "012x")
    rand_hex = os.urandom(4).hex()
    return f"evt_{ts_hex}_{rand_hex}"


class EcpEvent(BaseModel):
    """Cross-language wire envelope for Phase 4 Unity ↔ Brain events.

    Immutable on purpose — events are append-only by L0-style design. Producers
    construct, hand off to transport, and never mutate. Consumers may copy
    fields out but must not rewrite them.

    See module docstring for the EventEnvelope vs EcpEvent naming distinction
    (this class is the wire one).
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        # Use enum values on serialization so JSON / C# JsonUtility round-trip
        # cleanly (Unity's JsonUtility cannot deserialize Python Enum reprs).
        use_enum_values=True,
    )

    schema_version: int = Field(default=SCHEMA_VERSION, ge=1, le=255)
    event_id: str = Field(default_factory=generate_event_id, min_length=1, max_length=64)
    event_type: EcpEventType
    created_at: int = Field(..., ge=0)  # Unix epoch ms; caller computes
    source: EcpEventSource

    # Routing / audit metadata — kept top-level (not nested in source) so a
    # cheap consumer can route by these fields without parsing source first.
    unity_identity: str = Field(default="", max_length=128)
    room_id: str = Field(default="", max_length=128)
    correlation_id: str = Field(default="", max_length=64)

    # Caller computes payload_bytes against the JSON-serialized payload. We
    # store + validate it on construction so consumers can reject oversize
    # payloads without re-serializing. The match is enforced in
    # :meth:`with_computed_payload_bytes` (the recommended factory).
    payload_bytes: int = Field(..., ge=0, le=ECP_EVENT_PAYLOAD_LIMIT_BYTES * 4)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_id")
    @classmethod
    def _event_id_format(cls, v: str) -> str:
        # Loose validation — tolerate the time-prefixed format AND raw UUIDs
        # (in case Phase 5+ migrates to UUID v7). Only rule: must not contain
        # whitespace / commas / control chars (would break Redis Stream IDs +
        # JSON safety).
        for bad in (" ", "\t", "\n", ",", "\0"):
            if bad in v:
                raise ValueError(f"event_id contains illegal char {bad!r}: {v!r}")
        return v

    @classmethod
    def build(
        cls,
        *,
        event_type: EcpEventType,
        source: EcpEventSource,
        payload: dict[str, Any] | None = None,
        unity_identity: str = "",
        room_id: str = "",
        correlation_id: str = "",
        created_at: int | None = None,
    ) -> "EcpEvent":
        """Recommended factory: computes payload_bytes + created_at + event_id.

        Raises :class:`ValueError` if the JSON-encoded payload exceeds
        :data:`ECP_EVENT_PAYLOAD_LIMIT_BYTES`. Callers with payloads that may
        be large MUST handle the exception (typically by uploading the blob
        via HTTP and replacing it with an ``asset_ref``).
        """
        body = payload or {}
        encoded = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        size = len(encoded)
        if size > ECP_EVENT_PAYLOAD_LIMIT_BYTES:
            raise ValueError(
                f"EcpEvent payload {size}B exceeds 8KB limit; "
                f"use HTTP upload + asset_ref instead (see entry doc §8 L8)."
            )
        return cls(
            event_type=event_type,
            source=source,
            created_at=created_at if created_at is not None else int(time.time() * 1000),
            unity_identity=unity_identity,
            room_id=room_id,
            correlation_id=correlation_id,
            payload_bytes=size,
            payload=body,
        )

    def to_wire_json(self) -> str:
        """Serialize to the exact bytes that go on the DataChannel.

        Uses compact separators so payload_bytes stays the source of truth for
        the encoded size. ``ensure_ascii=False`` matches Unity's UTF-8
        ``Encoding.UTF8.GetBytes`` path used by
        :class:`LiveKitDataChannelHeartbeatTransport`.
        """
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
        )


__all__ = [
    "ECP_EVENT_PAYLOAD_LIMIT_BYTES",
    "EcpEvent",
    "EcpEventSource",
    "EcpEventType",
    "SCHEMA_VERSION",
    "TOPIC_ECP_EVENT",
    "TOPIC_ECP_STATE",
    "TOPIC_ECP_TICK",
    "generate_event_id",
]
