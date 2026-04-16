"""Tests for DataChannel telemetry message format."""

from parrot.shared.telemetry import TelemetryEvent, TelemetryFrame, Vec3


def test_telemetry_frame_roundtrip():
    frame = TelemetryFrame(behavior_state="flying", anim_clip="fly")
    frame.pose.position = Vec3(x=1.0, y=2.0, z=3.0)
    raw = frame.to_json()
    parsed = TelemetryFrame.from_json(raw)
    assert parsed.behavior_state == "flying"
    assert parsed.anim_clip == "fly"
    assert parsed.pose.position.x == 1.0
    assert parsed.pose.position.y == 2.0
    assert parsed.pose.position.z == 3.0


def test_telemetry_frame_size_budget():
    """Lossy DataChannel frame must be ≤1300 bytes."""
    frame = TelemetryFrame(behavior_state="dancing", anim_clip="dance")
    raw = frame.to_json()
    assert len(raw.encode("utf-8")) <= 1300


def test_telemetry_event_roundtrip():
    event = TelemetryEvent(
        type="arrived",
        payload={"target": [1.0, 2.0, 3.0]},
    )
    raw = event.to_json()
    parsed = TelemetryEvent.from_json(raw)
    assert parsed.type == "arrived"
    assert parsed.payload["target"] == [1.0, 2.0, 3.0]


def test_telemetry_frame_from_json_defaults():
    """Missing fields should fall back to defaults."""
    parsed = TelemetryFrame.from_json("{}")
    assert parsed.behavior_state == "idle"
    assert parsed.pose.position.x == 0.0
