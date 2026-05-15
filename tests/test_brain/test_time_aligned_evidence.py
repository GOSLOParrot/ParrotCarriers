from __future__ import annotations

import asyncio

from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    TimebaseStamp,
    get_evidence_ledger,
    resolve_identify_evidence,
)
from parrot.brain.vision.frame_cache import (
    record_livekit_frame_bytes,
    reset_frame_cache_for_tests,
)
from parrot.shared.ecp import EcpCommand, EcpCommandKind
from parrot.shared.ecp_event import EcpEvent, EcpEventSource, EcpEventType


def test_timebase_stamp_prefers_payload_timebase_over_envelope_time() -> None:
    event = EcpEvent.build(
        event_type=EcpEventType.SNAPSHOT_CAPTURED,
        source=EcpEventSource.UNITY,
        payload={
            "timebase": {
                "clock_domain": "livekit_track",
                "wall_time_ms": 1_700_000_000_123,
                "media_time_us": 123_456,
                "sequence": 7,
                "source_id": "track-1",
            }
        },
        created_at=1,
    )

    stamp = TimebaseStamp.from_payload(
        event.payload,
        default_domain=ClockDomain.UNITY,
        envelope_created_at_ms=event.created_at,
    )

    assert stamp.clock_domain == "livekit_track"
    assert stamp.wall_time_ms == 1_700_000_000_123
    assert stamp.media_time_us == 123_456
    assert stamp.sequence == 7
    assert stamp.estimated is False


def test_timebase_stamp_marks_envelope_fallback_as_estimated() -> None:
    stamp = TimebaseStamp.from_payload(
        {},
        default_domain=ClockDomain.UNITY,
        envelope_created_at_ms=1_700_000_000_999,
    )

    assert stamp.clock_domain == "unity"
    assert stamp.wall_time_ms == 1_700_000_000_999
    assert stamp.estimated is True


def test_timebase_stamp_prefers_ecp_command_meta_timebase() -> None:
    command = EcpCommand(
        kind=EcpCommandKind.SET_VIDEO_TIER,
        issued_at=1_700_000_001.5,
        meta={
            "timebase": {
                "clock_domain": "livekit_track",
                "wall_time_ms": 1_700_000_000_321,
                "media_time_us": 654_321,
                "source_id": "track-cmd",
            }
        },
    )

    stamp = TimebaseStamp.from_command_meta(
        command.meta,
        default_domain=ClockDomain.BRAIN,
        command_issued_at_s=command.issued_at,
    )

    assert stamp.clock_domain == "livekit_track"
    assert stamp.wall_time_ms == 1_700_000_000_321
    assert stamp.media_time_us == 654_321
    assert stamp.source_id == "track-cmd"
    assert stamp.estimated is False


def test_timebase_stamp_marks_ecp_command_issued_at_fallback_estimated() -> None:
    command = EcpCommand(
        kind=EcpCommandKind.SET_VIDEO_TIER,
        issued_at=1_700_000_001.5,
    )

    stamp = TimebaseStamp.from_command_meta(
        command.meta,
        default_domain=ClockDomain.BRAIN,
        default_source_id="brain-command",
        command_issued_at_s=command.issued_at,
    )

    assert stamp.clock_domain == "brain"
    assert stamp.wall_time_ms == 1_700_000_001_500
    assert stamp.source_id == "brain-command"
    assert stamp.estimated is True


def test_evidence_ledger_latest_nearest_and_status() -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()

    old = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.WEB,
            wall_time_ms=1_700_000_000_000,
            source_id="test",
        ),
        asset_path="data/photos/2026-05-15/old.jpg",
    )
    new = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.WEB,
            wall_time_ms=1_700_000_002_000,
            source_id="test",
        ),
        asset_path="data/photos/2026-05-15/new.jpg",
    )

    assert ledger.get(old.evidence_id) == old
    assert ledger.nearest(target_time_ms=1_700_000_001_900, require_asset=True) == new
    status = ledger.status()
    assert status["sample_count"] == 2
    assert status["by_kind"]["image_asset"] == 2


def test_identify_evidence_prefers_ready_video_frame_before_image_asset() -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()

    image = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.WEB,
            wall_time_ms=1_700_000_000_000,
            source_id="http-upload",
        ),
        asset_path="data/photos/2026-05-15/close.jpg",
    )
    frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=1_700_000_004_000,
            source_id="track-1",
        ),
        asset_path="data/frame-cache/track-1/frame.jpg",
    )

    resolved = asyncio.run(
        resolve_identify_evidence(target_time_ms=1_700_000_000_100)
    )

    assert resolved == frame
    assert resolved != image


def test_frame_cache_records_livekit_frame_as_video_evidence(tmp_path) -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)

    sample = record_livekit_frame_bytes(
        b"\x89PNG\r\n\x1a\nweb-frame",
        mime_type="image/png",
        room_id="parrot-test-room",
        track_sid="track-vision",
        participant_id="unity-app",
        wall_time_ms=1_700_000_010_000,
        media_time_us=44_000,
        sequence=12,
        description="pytest cached frame",
    )

    assert sample.kind == "video_frame"
    assert sample.mime_type == "image/png"
    assert sample.room_id == "parrot-test-room"
    assert sample.track_sid == "track-vision"
    assert sample.timebase.clock_domain == "livekit_track"
    assert sample.timebase.wall_time_ms == 1_700_000_010_000
    assert sample.timebase.media_time_us == 44_000
    assert sample.timebase.sequence == 12
    assert sample.timebase.estimated is False
    assert sample.asset_path.endswith(".png")
    assert sample.as_json()["asset_exists"] is True
    assert ledger.nearest(
        target_time_ms=1_700_000_010_001,
        kinds=(EvidenceKind.VIDEO_FRAME,),
        require_asset=True,
    ) == sample
