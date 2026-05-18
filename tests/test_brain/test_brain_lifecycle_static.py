from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / "src" / "parrot" / "brain" / "agent.py"
PHOTO_UPLOAD = ROOT / "src" / "parrot" / "brain" / "photo_upload_server.py"
TRIGGER_LISTENER = ROOT / "src" / "parrot" / "dsg" / "trigger_listener.py"


def test_brain_room_job_tracks_and_cancels_background_tasks() -> None:
    text = AGENT.read_text(encoding="utf-8")

    assert "background_tasks: list[asyncio.Task[Any]]" in text
    assert "def _track_background_task" in text
    assert "async def _stop_room_scoped_background" in text
    assert 'await start_trigger_listener()' in text
    assert "asyncio.create_task(start_trigger_listener())" not in text
    assert 'name="scheduler_result_listener"' in text
    assert 'name="l2b_trigger_boot"' in text
    assert 'os.getenv("PARROT_BRAIN_AGENT_NAME", "")' in text
    assert "@server.rtc_session(agent_name=_BRAIN_AGENT_NAME)" in text
    assert 'await pubsub.unsubscribe(CH_SCHEDULER_TO_BRAIN)' in text
    assert '_stop_room_scoped_background("room_disconnected")' in text
    assert "stop_photo_upload_server(photo_upload_server)" in text


def test_photo_upload_server_has_cooperative_stop_handle() -> None:
    text = PHOTO_UPLOAD.read_text(encoding="utf-8")

    assert "async def _serve_guarded" in text
    assert 'asyncio.create_task(_serve_guarded(), name="photo_upload_server")' in text
    assert "except SystemExit as exc" in text
    assert 'setattr(server, "_parrot_task", task)' in text
    assert "async def stop_photo_upload_server" in text
    assert "server.should_exit = True" in text
    # FIX (2026-05-11 audit Round 5, Bug L): cooperative-first, then
    # cancel-on-timeout. The previous assertion locked in a bug-y
    # ``asyncio.shield(task)`` shape that prevented the timeout from
    # cancelling a stuck uvicorn shutdown. Now we still rely on
    # ``shield`` to wait politely, but a hung task must be cancelled
    # so the next session's ``start_photo_upload_server`` can rebind
    # the port.
    assert "task.cancel()" in text
    assert "asyncio.wait_for(asyncio.shield(task)" in text


def test_dsg_trigger_listener_closes_pubsub_on_cancel() -> None:
    text = TRIGGER_LISTENER.read_text(encoding="utf-8")

    assert "pubsub = None" in text
    assert "except asyncio.CancelledError" in text
    assert "await pubsub.unsubscribe(CH_DSG_EVENTS, CH_DSG_SCENE_UPDATE)" in text
    assert "await pubsub.close()" in text
