from __future__ import annotations

import asyncio
import io
import time
from types import SimpleNamespace

import py_trees

from parrot.brain.intent_workspace import (
    IntentWorkspace,
    get_intent_workspace,
    set_intent_workspace_for_test,
)
from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    EvidenceStatus,
    SampleRegion,
    TimebaseStamp,
    get_evidence_ledger,
    resolve_identify_evidence,
)
from parrot.brain.vision.evidence_awareness import (
    latest_evidence_awareness_notice,
    stage_attention_threshold_for_goslo,
    stage_evidence_for_goslo,
)
from parrot.brain.vision.evidence_image import prepare_evidence_image
from parrot.brain.vision.frame_cache import (
    get_frame_cache,
    record_livekit_frame_bytes,
    reset_frame_cache_for_tests,
)
from parrot.brain.vision.livekit_sampler import (
    LiveKitFrameSampler,
    LiveKitFrameSamplerConfig,
    encode_livekit_video_frame_to_jpeg,
    read_livekit_frame_sampler_status,
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


def test_identify_evidence_prefers_bbox_ref_asset_over_unrelated_frame() -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    now_ms = int(time.time() * 1000)

    unrelated_frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=now_ms,
            source_id="room-track",
        ),
        asset_path="data/frame-cache/room/latest.jpg",
    )
    focused_asset = ledger.record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.UNITY,
            wall_time_ms=now_ms - 5_000,
            source_id="bbox-tool",
        ),
        asset_path="data/photos/focused-region.jpg",
        bbox_refs=("bbox-red-mug",),
    )

    resolved = asyncio.run(resolve_identify_evidence(bbox_ref_id="bbox-red-mug"))

    assert resolved == focused_asset
    assert resolved != unrelated_frame


def test_identify_evidence_uses_bbox_anchor_time_when_asset_is_not_linked() -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    now_ms = int(time.time() * 1000)

    unrelated_frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=now_ms,
            source_id="room-track",
        ),
        asset_path="data/frame-cache/room/latest.jpg",
    )
    anchor = ledger.record_sample(
        kind=EvidenceKind.BBOX_FOCUS,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.UNITY,
            wall_time_ms=now_ms - 9_000,
            source_id="bbox-tool",
        ),
        bbox_refs=("bbox-blue-mug",),
        description="user boxed the blue mug",
    )
    nearby_frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=anchor.timebase.wall_time_ms + 80,
            source_id="room-track",
        ),
        asset_path="data/frame-cache/room/near-bbox.jpg",
    )

    resolved = asyncio.run(resolve_identify_evidence(bbox_ref_id="bbox-blue-mug"))

    assert resolved == nearby_frame
    assert resolved != unrelated_frame


def test_identify_evidence_missing_bbox_ref_does_not_use_unrelated_latest_frame() -> None:
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    now_ms = int(time.time() * 1000)

    unrelated_frame = ledger.record_sample(
        kind=EvidenceKind.VIDEO_FRAME,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(
            clock_domain=ClockDomain.LIVEKIT_TRACK,
            wall_time_ms=now_ms,
            source_id="room-track",
        ),
        asset_path="data/frame-cache/room/latest.jpg",
    )

    resolved = asyncio.run(resolve_identify_evidence(bbox_ref_id="missing-bbox"))
    requests = ledger.timeline(kind=EvidenceKind.EVIDENCE_REQUEST)

    assert resolved is None
    assert requests
    assert requests[0] != unrelated_frame
    assert requests[0].bbox_refs == ("missing-bbox",)
    assert requests[0].meta["missing_focus_anchor"] is True


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
    cache_status = get_frame_cache().status()
    assert cache_status["frame_count"] == 1
    assert cache_status["latest_frame"]["evidence_id"] == sample.evidence_id
    assert cache_status["tracks"]["track-vision"]["sequence"] == 12
    assert cache_status["tracks"]["track-vision"]["asset_exists"] is True
    assert isinstance(cache_status["latest_frame_fresh"], bool)
    assert ledger.nearest(
        target_time_ms=1_700_000_010_001,
        kinds=(EvidenceKind.VIDEO_FRAME,),
        require_asset=True,
    ) == sample


def test_livekit_frame_encoder_preserves_rgb_pixels() -> None:
    from PIL import Image
    from livekit.rtc import VideoFrame
    from livekit.rtc.video_frame import proto_video

    frame = VideoFrame(
        width=2,
        height=1,
        type=proto_video.VideoBufferType.RGB24,
        data=bytes([255, 0, 0, 0, 255, 0]),
    )

    encoded = encode_livekit_video_frame_to_jpeg(frame, quality=90, max_dimension=16)

    decoded = Image.open(io.BytesIO(encoded))
    assert decoded.size == (2, 1)
    assert decoded.mode == "RGB"


def test_prepare_evidence_image_uses_normalized_crop(tmp_path) -> None:
    from PIL import Image

    asset = tmp_path / "evidence.png"
    image = Image.new("RGB", (4, 4), color=(0, 0, 0))
    image.putpixel((2, 1), (255, 0, 0))
    image.putpixel((3, 1), (0, 255, 0))
    image.save(asset)

    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        status=EvidenceStatus.READY,
        timebase=TimebaseStamp(clock_domain=ClockDomain.WEB, wall_time_ms=1),
        asset_path=str(asset),
        region=SampleRegion(x=0.5, y=0.25, width=0.5, height=0.25),
    )

    prepared = prepare_evidence_image(sample)

    assert prepared is not None
    assert prepared.cropped is True
    assert prepared.width == 2
    assert prepared.height == 1
    assert prepared.b64_jpeg


def test_stage_evidence_for_goslo_writes_intent_workspace_and_notice() -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()

    try:
        sample = ledger.record_sample(
            kind=EvidenceKind.IMAGE_ASSET,
            status=EvidenceStatus.READY,
            timebase=TimebaseStamp(clock_domain=ClockDomain.WEB, wall_time_ms=1),
            description="red mug",
        )

        decision = asyncio.run(
            stage_evidence_for_goslo(
                evidence_id=sample.evidence_id,
                description="red mug near keyboard",
                source="pytest",
            )
        )

        assert decision.staged_ref_id
        assert decision.notify_goslo is True
        # Check the real singleton rather than a fresh workspace.
        from parrot.brain.intent_workspace import get_intent_workspace

        staged = get_intent_workspace().list_active(role="visual_evidence_hint")
        notice = latest_evidence_awareness_notice()
        assert len(staged) == 1
        assert staged[0].ref_id == decision.staged_ref_id
        assert notice["staged_ref_id"] == decision.staged_ref_id
        assert notice["allow_interrupt"] is False
    finally:
        set_intent_workspace_for_test(None)


def test_attention_threshold_bridge_stages_nearest_frame_for_goslo(tmp_path) -> None:
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_intent_workspace_for_test(IntentWorkspace())
    ledger = get_evidence_ledger()
    ledger.reset_for_tests()

    try:
        frame_path = tmp_path / "threshold-frame.jpg"
        frame_path.write_bytes(b"fake-jpeg")
        anchor_time_ms = 1_700_000_030_000
        ledger.record_sample(
            kind=EvidenceKind.BBOX_FOCUS,
            status=EvidenceStatus.READY,
            timebase=TimebaseStamp(
                clock_domain=ClockDomain.UNITY,
                wall_time_ms=anchor_time_ms,
            ),
            related_refs=("ref-bbox-threshold",),
            bbox_refs=("ref-bbox-threshold",),
            description="threshold bbox anchor",
        )
        frame = ledger.record_sample(
            kind=EvidenceKind.VIDEO_FRAME,
            status=EvidenceStatus.READY,
            timebase=TimebaseStamp(
                clock_domain=ClockDomain.LIVEKIT_TRACK,
                wall_time_ms=anchor_time_ms + 3,
                source_id="screen-share-track",
            ),
            asset_path=str(frame_path),
            mime_type="image/jpeg",
            description="nearby screen-share frame",
        )

        decision = asyncio.run(
            stage_attention_threshold_for_goslo(
                {
                    "ref_id": "ref-bbox-threshold",
                    "subject_kind": "bbox",
                    "subject_id": "bbox-threshold",
                    "label": "threshold bbox",
                    "weight": 1.0,
                    "ts_ms": anchor_time_ms,
                }
            )
        )

        assert decision.evidence_id == frame.evidence_id
        assert decision.staged_ref_id
        assert decision.allow_interrupt is False
        assert decision.notify_goslo is True
        staged = get_intent_workspace().list_active(role="visual_evidence_hint")
        notice = latest_evidence_awareness_notice()
        assert staged[0].ref_id == decision.staged_ref_id
        assert notice["staged_ref_id"] == decision.staged_ref_id
        assert "attention threshold crossed" in notice["message"]
    finally:
        set_intent_workspace_for_test(None)


def test_livekit_frame_sampler_scans_existing_video_track(tmp_path, monkeypatch) -> None:
    from livekit.rtc import VideoFrame
    from livekit.rtc._proto import track_pb2
    from livekit.rtc.video_frame import proto_video

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "sampler-status.json"),
    )

    frame = VideoFrame(
        width=1,
        height=1,
        type=proto_video.VideoBufferType.RGB24,
        data=bytes([20, 40, 80]),
    )
    stream = _FakeFrameStream(
        [SimpleNamespace(frame=frame, timestamp_us=987_654, rotation=0)]
    )
    track = SimpleNamespace(
        sid="track-auto",
        name="ar-camera",
        kind=track_pb2.TrackKind.KIND_VIDEO,
        muted=False,
    )
    publication = _FakePublication(
        track=track,
        sid="pub-auto",
        name="ar-camera",
        kind=track_pb2.TrackKind.KIND_VIDEO,
        source=track_pb2.TrackSource.SOURCE_CAMERA,
    )
    participant = SimpleNamespace(
        identity="unity-phone",
        sid="participant-auto",
        track_publications={"pub-auto": publication},
    )
    room = _FakeRoom(name="parrot-test-room", participants={"unity-phone": participant})
    sampler = LiveKitFrameSampler(
        room,
        config=LiveKitFrameSamplerConfig(fps=10, max_dimension=16, jpeg_quality=70),
        stream_factory=lambda _track, _capacity: stream,
    )

    async def run() -> None:
        sampler.start()
        await asyncio.sleep(0.05)
        await sampler.stop()

    asyncio.run(run())

    status = sampler.status()
    persisted_status = read_livekit_frame_sampler_status()
    rows = ledger.timeline(kind=EvidenceKind.VIDEO_FRAME, limit=1)
    latest = rows[0] if rows else None
    assert publication.subscribed is True
    assert stream.closed is True
    assert status["recorded_frames"] == 1
    assert status["latest_frame_fresh"] is True
    assert status["latest_frame"]["evidence_id"] == latest.evidence_id
    assert status["tracks"]["track-auto"]["fresh"] is True
    assert persisted_status["available"] is True
    assert persisted_status["recorded_frames"] == 1
    assert persisted_status["latest_frame_fresh"] is True
    assert persisted_status["tracks"]["track-auto"]["sequence"] == 1
    assert persisted_status["room_id"] == "parrot-test-room"
    assert latest is not None
    assert latest.kind == "video_frame"
    assert latest.track_sid == "track-auto"
    assert latest.room_id == "parrot-test-room"
    assert latest.timebase.media_time_us == 987_654
    assert latest.timebase.sequence == 1
    assert latest.meta["source"] == "livekit_frame_sampler"
    assert latest.as_json()["asset_exists"] is True


def test_livekit_frame_sampler_accepts_screen_share_source_name(tmp_path, monkeypatch) -> None:
    from livekit.rtc import VideoFrame
    from livekit.rtc._proto import track_pb2
    from livekit.rtc.video_frame import proto_video

    ledger = get_evidence_ledger()
    ledger.reset_for_tests()
    reset_frame_cache_for_tests(root=tmp_path)
    monkeypatch.setenv(
        "PARROT_LIVEKIT_FRAME_SAMPLER_STATUS_PATH",
        str(tmp_path / "sampler-status.json"),
    )

    frame = VideoFrame(
        width=1,
        height=1,
        type=proto_video.VideoBufferType.RGB24,
        data=bytes([80, 40, 20]),
    )
    stream = _FakeFrameStream(
        [SimpleNamespace(frame=frame, timestamp_us=111_222, rotation=0)]
    )
    track = SimpleNamespace(
        sid="track-screen",
        name="web-console",
        kind=track_pb2.TrackKind.KIND_VIDEO,
        muted=False,
    )
    publication = _FakePublication(
        track=track,
        sid="pub-screen",
        name="browser",
        kind=track_pb2.TrackKind.KIND_VIDEO,
        source="SOURCE_SCREEN_SHARE",
    )
    participant = SimpleNamespace(
        identity="web-console",
        sid="participant-screen",
        track_publications={"pub-screen": publication},
    )
    room = _FakeRoom(name="parrot-test-room", participants={"web-console": participant})
    sampler = LiveKitFrameSampler(
        room,
        config=LiveKitFrameSamplerConfig(fps=10, max_dimension=16, jpeg_quality=70),
        stream_factory=lambda _track, _capacity: stream,
    )

    async def run() -> None:
        sampler.start()
        await asyncio.sleep(0.05)
        await sampler.stop()

    asyncio.run(run())

    status = sampler.status()
    latest = ledger.timeline(kind=EvidenceKind.VIDEO_FRAME, limit=1)[0]
    assert publication.subscribed is True
    assert status["recorded_frames"] == 1
    assert status["latest_frame"]["track_sid"] == "track-screen"
    assert status["latest_frame"]["publication_source"] == "SOURCE_SCREEN_SHARE"
    assert latest.track_sid == "track-screen"
    assert latest.meta["publication_source"] == "SOURCE_SCREEN_SHARE"


class _FakeFrameStream:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self._events = list(events)
        self.closed = False

    def __aiter__(self) -> "_FakeFrameStream":
        return self

    async def __anext__(self) -> SimpleNamespace:
        if not self._events:
            raise StopAsyncIteration
        return self._events.pop(0)

    async def aclose(self) -> None:
        self.closed = True


class _FakePublication:
    def __init__(
        self,
        *,
        track: SimpleNamespace,
        sid: str,
        name: str,
        kind: int,
        source: int,
    ) -> None:
        self.track = track
        self.sid = sid
        self.name = name
        self.kind = kind
        self.source = source
        self.muted = False
        self.subscribed = False

    def set_subscribed(self, subscribed: bool) -> None:
        self.subscribed = subscribed


class _FakeRoom:
    def __init__(self, *, name: str, participants: dict[str, SimpleNamespace]) -> None:
        self.name = name
        self.remote_participants = participants
        self.handlers: dict[str, set] = {}

    def on(self, event: str, handler) -> None:
        self.handlers.setdefault(event, set()).add(handler)

    def off(self, event: str, handler) -> None:
        self.handlers.get(event, set()).discard(handler)
