"""Simulate a Unity client in the LiveKit room — full verification tool.

This script replaces Unity for local testing. It:
  1. Joins parrot-main room as "unity-sim" (matches _rpc_bridge.py prefix check)
  2. Registers RPC handlers for flyTo / animate (logs + returns OK)
  3. Auto-dispatches the Brain Agent if not already in the room
  4. Optionally publishes microphone audio (--mic) for real Gemini voice chat
  5. Plays the agent's voice (TTS) to the default output device — same role as Unity AudioSource + AudioStream
  6. Logs user + parrot transcripts to the console (lk.transcription + transcription_received)
  7. Optionally starts Scheduler + NanobotConsumer in-process (--full)

Usage:
    python src/scripts/sim_unity_client.py              # join + listen only
    python src/scripts/sim_unity_client.py --mic        # join + microphone → Gemini voice
    python src/scripts/sim_unity_client.py --mic --full # join + mic + scheduler + nanobot
    python src/scripts/sim_unity_client.py --text       # join + text chat (type to Gemini)
    python src/scripts/sim_unity_client.py --mic --video # voice + webcam → Gemini sees + hears

Requires: pip install livekit sounddevice numpy opencv-python
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import queue as std_queue
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parrot.shared.config import ParrotConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("sim-unity")

try:
    from livekit import rtc
except ImportError:
    logger.error("Need livekit Python client SDK: pip install livekit")
    sys.exit(1)

from livekit.api import AccessToken, RoomAgentDispatch, VideoGrants
from livekit.protocol.room import RoomConfiguration

# Empty means the default unnamed @server.rtc_session() Brain entrypoint.
# Older local experiments can still pass --agent-name parrot-brain explicitly.
AGENT_NAME = ""
# LiveKit Agents 通过文本流下发同步转写（与 livekit.agents.types.TOPIC_TRANSCRIPTION 一致）
TRANSCRIPTION_TOPIC = "lk.transcription"
# Mic publish rate (LiveKit / sim常用 48k)
SAMPLE_RATE = 48000
# Agent TTS：Google Realtime 输出为 24k（livekit.plugins.google.realtime.realtime_api）
AGENT_PLAYBACK_SAMPLE_RATE = 24000
NUM_CHANNELS = 1
FRAME_DURATION_MS = 20
SAMPLES_PER_FRAME = SAMPLE_RATE * FRAME_DURATION_MS // 1000


def _make_token(
    identity: str,
    room: str,
    cfg: ParrotConfig,
    *,
    include_agent_dispatch: bool | None = None,
    agent_name: str = AGENT_NAME,
) -> str:
    """If include_agent_dispatch is None: only identities starting with 'unity' request agent dispatch.

    Use a non-unity identity (e.g. voice-user) when Unity Editor is already in the room as unity-*
    so Brain RPC stays pinned to Unity while this client only publishes mic audio.
    """
    if include_agent_dispatch is None:
        include_agent_dispatch = identity.startswith("unity")

    b = (
        AccessToken(cfg.livekit.api_key, cfg.livekit.api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .with_ttl(timedelta(hours=1))
    )
    if include_agent_dispatch:
        dispatch = (
            RoomAgentDispatch(agent_name=agent_name)
            if agent_name
            else RoomAgentDispatch()
        )
        room_config = RoomConfiguration(agents=[dispatch])
        b = b.with_room_config(room_config)
    return b.to_jwt()


async def _dispatch_agent(cfg: ParrotConfig, room_name: str, agent_name: str = AGENT_NAME) -> None:
    from livekit.api import CreateAgentDispatchRequest, LiveKitAPI

    lk = LiveKitAPI(
        cfg.livekit.url.replace("ws://", "http://").replace("wss://", "https://"),
        cfg.livekit.api_key,
        cfg.livekit.api_secret,
    )
    try:
        req = CreateAgentDispatchRequest(room=room_name)
        if agent_name:
            req.agent_name = agent_name
        dispatch = await lk.agent_dispatch.create_dispatch(
            req
        )
        logger.info("Agent dispatched: %s", dispatch.id)
    finally:
        await lk.aclose()


def _is_brain_identity(identity: str) -> bool:
    identity = (identity or "").strip().lower()
    return identity == "brain" or identity.startswith("agent-")


def _find_brain_participant(room: rtc.Room) -> str:
    for participant in room.remote_participants.values():
        if _is_brain_identity(participant.identity):
            return participant.identity
    return ""


async def _wait_for_brain_participant(room: rtc.Room, timeout_s: float) -> str:
    deadline = asyncio.get_running_loop().time() + max(0.0, timeout_s)
    while asyncio.get_running_loop().time() < deadline:
        identity = _find_brain_participant(room)
        if identity:
            return identity
        await asyncio.sleep(0.25)
    return _find_brain_participant(room)


def _parse_rpc_json(method: str, payload: str) -> dict:
    try:
        parsed = json.loads(payload or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{method} returned non-JSON payload: {exc}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"{method} returned {type(parsed).__name__}, expected object")
    return parsed


def _assert_business_ok(method: str, parsed: dict) -> None:
    if parsed.get("status") == "error":
        raise RuntimeError(f"{method} business status=error: {parsed}")
    result = parsed.get("result")
    if isinstance(result, dict) and result.get("success") is False:
        raise RuntimeError(f"{method} result.success=false: {result}")


async def _perform_startup_rpc(
    room: rtc.Room,
    brain_identity: str,
    method: str,
    payload: dict,
) -> dict:
    response = await room.local_participant.perform_rpc(
        destination_identity=brain_identity,
        method=method,
        payload=json.dumps(payload, ensure_ascii=False),
        response_timeout=5.0,
    )
    parsed = _parse_rpc_json(method, response)
    _assert_business_ok(method, parsed)
    logger.info(
        "START RPC business-ok: %s keys=%s",
        method,
        ",".join(sorted(parsed.keys())),
    )
    return parsed


async def _run_startup_rpc_check(room: rtc.Room, brain_identity: str) -> None:
    snapshot = await _perform_startup_rpc(
        room,
        brain_identity,
        "getRoomSettingSnapshot",
        {"compact": True},
    )
    active_room = (
        (snapshot.get("snapshot") or {}).get("active_room")
        if isinstance(snapshot.get("snapshot"), dict)
        else None
    )
    if not isinstance(active_room, dict):
        raise RuntimeError("getRoomSettingSnapshot returned no snapshot.active_room")

    experience_mode = str(active_room.get("experience_mode") or "ar_companion")
    await _perform_startup_rpc(
        room,
        brain_identity,
        "applyRoomProfile",
        {
            "room_profile_id": active_room.get("room_profile_id") or "default",
            "room_profile": active_room,
            "experience_mode": experience_mode,
        },
    )
    await _perform_startup_rpc(
        room,
        brain_identity,
        "setAppCapabilityMode",
        {"mode": "FullARCompanion"},
    )
    logger.info(
        "START RPC check passed: active_room=%s experience_mode=%s brain=%s",
        active_room.get("room_profile_id"),
        experience_mode,
        brain_identity,
    )


def _print_sound_devices() -> None:
    import sounddevice as sd

    print(sd.query_devices())
    di, do = sd.default.device
    print(f"Default input device index: {di}")
    print(f"Default output device index: {do}")


def _play_selftest_tone(output_device: int | None, samplerate: int = 48000) -> None:
    """Short beep to verify Windows/sounddevice can reach the chosen headphones."""
    import sounddevice as sd

    duration_s = 0.45
    t = np.linspace(0.0, duration_s, int(samplerate * duration_s), dtype=np.float32)
    tone = (0.2 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.float32)
    logger.info(
        "AUDIO SELF-TEST: playing 440 Hz tone (%.1fs @ %d Hz) — you should hear a beep.",
        duration_s,
        samplerate,
    )
    kwargs: dict = {"samplerate": samplerate, "device": output_device}
    if output_device is None:
        kwargs.pop("device")
    sd.play(tone, **kwargs)
    sd.wait()


async def _play_remote_agent_audio(
    track: rtc.Track,
    participant_identity: str,
    output_device: int | None,
    playback_sample_rate: int,
) -> None:
    """Decode agent TTS from LiveKit and play via sounddevice (Unity does this with AudioSource)."""
    import sounddevice as sd

    logger.info(
        "Speaker: playing agent audio from %s (playback %d Hz)",
        participant_identity,
        playback_sample_rate,
    )
    audio_stream = rtc.AudioStream.from_track(
        track=track,
        sample_rate=playback_sample_rate,
        num_channels=NUM_CHANNELS,
    )
    sync_q: std_queue.Queue[np.ndarray] = std_queue.Queue(maxsize=400)
    buf = np.zeros(0, dtype=np.float32)
    frame_count = 0
    peak_logged = 0.0

    block = max(int(playback_sample_rate * 0.02), 1)

    def out_cb(outdata: np.ndarray, frames: int, _t, status) -> None:
        nonlocal buf
        try:
            if status:
                logger.warning("playback sounddevice: %s", status)
            need = frames
            while len(buf) < need:
                try:
                    buf = np.concatenate([buf, sync_q.get_nowait()])
                except std_queue.Empty:
                    buf = np.concatenate([buf, np.zeros(need - len(buf), dtype=np.float32)])
                    break
            chunk = buf[:need]
            buf = buf[need:]
            if outdata.ndim == 1:
                outdata[:] = chunk
            else:
                outdata[:, 0] = chunk
        except Exception:
            logger.exception("playback output callback failed")

    out_kw: dict = dict(
        samplerate=playback_sample_rate,
        channels=1,
        dtype="float32",
        blocksize=block,
        callback=out_cb,
        latency="high",
    )
    if output_device is not None:
        out_kw["device"] = output_device
    out = sd.OutputStream(**out_kw)
    out.start()
    try:
        async for event in audio_stream:
            f = event.frame
            if not f.data:
                continue
            samples = np.frombuffer(f.data, dtype=np.int16).astype(np.float32) / 32768.0
            nch = f.num_channels or 1
            if nch > 1:
                samples = samples.reshape(-1, nch).mean(axis=1)
            peak = float(np.max(np.abs(samples))) if samples.size else 0.0
            frame_count += 1
            if peak > peak_logged:
                peak_logged = peak
            if frame_count <= 3 or frame_count % 250 == 0:
                logger.info(
                    "Speaker: frame #%d sr=%d ch=%d samples=%d peak=%.4f",
                    frame_count,
                    f.sample_rate,
                    f.num_channels,
                    f.samples_per_channel,
                    peak,
                )
            try:
                sync_q.put_nowait(samples)
            except std_queue.Full:
                try:
                    sync_q.get_nowait()
                except std_queue.Empty:
                    pass
                try:
                    sync_q.put_nowait(samples)
                except std_queue.Full:
                    pass
    except asyncio.CancelledError:
        raise
    finally:
        out.stop()
        out.close()
        await audio_stream.aclose()
        logger.info(
            "Speaker: stopped playback for %s (frames=%d peak=%.4f)",
            participant_identity,
            frame_count,
            peak_logged,
        )


def _enqueue_mic_frame(mic_q: asyncio.Queue[rtc.AudioFrame], frame: rtc.AudioFrame) -> None:
    """Runs on the asyncio loop thread — bounded queue so capture_frame cannot flood the loop."""
    try:
        mic_q.put_nowait(frame)
    except asyncio.QueueFull:
        try:
            mic_q.get_nowait()
        except asyncio.QueueEmpty:
            pass
        try:
            mic_q.put_nowait(frame)
        except asyncio.QueueFull:
            pass


async def _publish_microphone(room: rtc.Room, input_device: int | None) -> tuple[object, asyncio.Task]:
    """Capture microphone audio and publish to LiveKit room.

    Uses a single writer task + bounded queue. The old pattern scheduled one
    ``ensure_future(capture_frame)`` per audio block with no backpressure, which
    could starve the event loop after a few minutes and look like a freeze.
    """
    import sounddevice as sd

    source = rtc.AudioSource(SAMPLE_RATE, NUM_CHANNELS)
    track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    await room.local_participant.publish_track(track, options)
    logger.info(
        "Microphone published to room (rate=%d, channels=%d, device=%s)",
        SAMPLE_RATE,
        NUM_CHANNELS,
        input_device if input_device is not None else "default",
    )

    loop = asyncio.get_running_loop()
    mic_q: asyncio.Queue[rtc.AudioFrame] = asyncio.Queue(maxsize=50)

    async def mic_writer() -> None:
        try:
            while True:
                frame = await mic_q.get()
                await source.capture_frame(frame)
        except asyncio.CancelledError:
            raise

    writer_task = asyncio.create_task(mic_writer())

    def audio_callback(indata, frames, time_info, status):
        if status:
            logger.warning("sounddevice status: %s", status)
        mono = np.asarray(indata)
        if mono.ndim > 1:
            mono = mono[:, 0]
        audio_data = (mono * 32767.0).astype(np.int16)
        frame = rtc.AudioFrame(
            data=audio_data.tobytes(),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
            samples_per_channel=len(audio_data),
        )
        loop.call_soon_threadsafe(_enqueue_mic_frame, mic_q, frame)

    in_kw: dict = dict(
        samplerate=SAMPLE_RATE,
        channels=NUM_CHANNELS,
        dtype="float32",
        blocksize=SAMPLES_PER_FRAME,
        callback=audio_callback,
    )
    if input_device is not None:
        in_kw["device"] = input_device
    stream = sd.InputStream(**in_kw)
    stream.start()
    logger.info("Microphone capture started — speak to chat with Gemini!")
    return stream, writer_task


async def _publish_video(room: rtc.Room, camera_index: int = 0) -> tuple:
    """Capture webcam video and publish to LiveKit room — simulates ARVideoPublisher.

    Returns (video_source, capture_task) for cleanup.
    """
    import cv2

    WIDTH, HEIGHT, FPS = 1280, 720, 30

    source = rtc.VideoSource(WIDTH, HEIGHT)
    track = rtc.LocalVideoTrack.create_video_track("sim-camera", source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_CAMERA)
    options.video_encoding = rtc.VideoEncoding(max_bitrate=1_500_000, max_framerate=FPS)
    await room.local_participant.publish_track(track, options)
    logger.info("Video track published (%dx%d @%dfps, cam=%d)", WIDTH, HEIGHT, FPS, camera_index)

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if not cap.isOpened():
        logger.error("Failed to open camera %d", camera_index)
        return None, None

    async def _capture_loop() -> None:
        interval = 1.0 / FPS
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    await asyncio.sleep(0.1)
                    continue
                rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                video_frame = rtc.VideoFrame(
                    width=rgba.shape[1],
                    height=rgba.shape[0],
                    type=rtc.VideoBufferType.RGBA,
                    data=rgba.tobytes(),
                )
                source.capture_frame(video_frame)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        finally:
            cap.release()

    task = asyncio.create_task(_capture_loop())
    return cap, task


async def _start_services() -> tuple:
    """Start Scheduler + NanobotConsumer in-process."""
    from parrot.scheduler.service import SchedulerService
    from parrot.bus.nanobot_consumer import NanobotConsumer

    scheduler = SchedulerService()
    await scheduler.start()
    logger.info("Scheduler started in-process")

    nanobot = NanobotConsumer()
    await nanobot.start()
    logger.info("NanobotConsumer started in-process")

    return scheduler, nanobot


def _register_conversation_transcripts(
    room: rtc.Room,
    loop: asyncio.AbstractEventLoop,
    local_identity: str,
) -> None:
    """在控制台打印「你说什么 / 鹦鹉回复什么」（依赖 Agent 发布的转写流与 transcription 事件）。"""

    def on_text_stream(reader: rtc.TextStreamReader, participant_identity: str) -> None:
        async def _run() -> None:
            try:
                text = (await reader.read_all()).strip()
                if not text:
                    return
                if participant_identity.startswith("agent-"):
                    label = "鹦鹉"
                elif participant_identity == local_identity:
                    label = "你"
                else:
                    label = participant_identity
                line = f"[转写·流] {label}: {text}"
                logger.info("%s", line)
                print(f"\n{line}\n", flush=True)
            except Exception:
                logger.exception("读取 lk.transcription 文本流失败")

        loop.create_task(_run())

    room.register_text_stream_handler(TRANSCRIPTION_TOPIC, on_text_stream)

    def on_transcription_received(segments, participant, publication) -> None:
        if not segments:
            return
        parts: list[str] = []
        for s in segments:
            t = getattr(s, "text", None) or ""
            if t:
                parts.append(t)
        text = " ".join(parts).strip()
        if not text:
            return
        pid = participant.identity if participant is not None else "?"
        if pid.startswith("agent-"):
            label = "鹦鹉"
        elif pid == local_identity:
            label = "你"
        else:
            label = pid
        line = f"[转写·段] {label}: {text}"
        logger.info("%s", line)
        print(f"\n{line}\n", flush=True)

    room.on("transcription_received", on_transcription_received)
    logger.info(
        "Conversation transcript logging enabled (%s + transcription_received)",
        TRANSCRIPTION_TOPIC,
    )


async def _monitor_nanobot_results() -> None:
    """Listen to Nanobot results and print them."""
    from parrot.shared.constants import CH_NANOBOT_RESULTS
    from parrot.shared.redis_client import get_redis

    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(CH_NANOBOT_RESULTS)
    logger.info("Monitoring Nanobot results on %s", CH_NANOBOT_RESULTS)

    async for message in pubsub.listen():
        if message["type"] == "message":
            result = json.loads(message["data"])
            logger.info(
                ">>> NANOBOT RESULT: task=%s type=%s status=%s",
                result.get("task_id"),
                result.get("type"),
                result.get("status"),
            )


async def main(
    use_mic: bool = False,
    use_text: bool = False,
    use_video: bool = False,
    full_stack: bool = False,
    input_device: int | None = None,
    output_device: int | None = None,
    camera_device: int = 0,
    playback_sample_rate: int = AGENT_PLAYBACK_SAMPLE_RATE,
    audio_selftest: bool = False,
    identity: str = "unity-sim",
    agent_playback: bool = True,
    startup_rpc_check: bool = False,
    brain_wait_seconds: float = 30.0,
    agent_name: str = AGENT_NAME,
) -> None:
    cfg = ParrotConfig()
    room_name = cfg.livekit.room_name

    token = _make_token(identity, room_name, cfg, agent_name=agent_name)
    logger.info(
        "Identity: %s  Room: %s  (agent_dispatch_in_token=%s, agent_name=%s, agent_playback=%s)",
        identity,
        room_name,
        identity.startswith("unity"),
        agent_name or "<unnamed>",
        agent_playback,
    )

    scheduler = nanobot = None
    if full_stack:
        scheduler, nanobot = await _start_services()

    result_monitor = asyncio.create_task(_monitor_nanobot_results())

    loop = asyncio.get_running_loop()
    playback_tasks: list[asyncio.Task] = []
    playback_started: set[str] = set()
    room = rtc.Room()

    @room.on("track_subscribed")
    def on_track(track, publication, participant):
        logger.info(
            "Track from %s: sid=%s kind=%s name=%s",
            participant.identity,
            track.sid,
            track.kind,
            getattr(publication, "name", "") or "",
        )
        if not agent_playback:
            return
        if not participant.identity.startswith("agent-"):
            return
        if publication.kind != rtc.TrackKind.KIND_AUDIO:
            return
        if track.sid in playback_started:
            logger.info("Speaker: skip duplicate track sid=%s", track.sid)
            return
        playback_started.add(track.sid)
        fut = asyncio.ensure_future(
            _play_remote_agent_audio(
                track,
                participant.identity,
                output_device,
                playback_sample_rate,
            ),
            loop=loop,
        )
        playback_tasks.append(fut)

    @room.on("participant_connected")
    def on_join(participant):
        logger.info("+ %s joined", participant.identity)

    @room.on("participant_disconnected")
    def on_leave(participant):
        logger.info("- %s left", participant.identity)

    _register_conversation_transcripts(room, loop, identity)

    if audio_selftest:
        _play_selftest_tone(output_device, samplerate=48000)
        _play_selftest_tone(output_device, samplerate=playback_sample_rate)

    url = cfg.livekit.url
    logger.info("Connecting to %s ...", url)
    await room.connect(url, token)
    logger.info("Connected to room '%s'", room.name)

    @room.local_participant.register_rpc_method("flyTo")
    async def handle_fly_to(data):
        payload = json.loads(data.payload)
        logger.info(">>> RPC flyTo from %s: %s", data.caller_identity, payload)
        return json.dumps({"status": "ok", "action": "flyTo", "target": payload})

    @room.local_participant.register_rpc_method("animate")
    async def handle_animate(data):
        payload = json.loads(data.payload)
        logger.info(">>> RPC animate from %s: %s", data.caller_identity, payload)
        return json.dumps({"status": "ok", "action": "animate", "animation": payload.get("animation")})

    logger.info("RPC handlers registered: flyTo, animate")

    # Join token may already include RoomAgentDispatch; the worker joins shortly after us.
    # If we dispatch immediately, we often spawn a duplicate job (Redis/asyncio issues + wasted work).
    brain_identity = await _wait_for_brain_participant(room, 15.0)
    if not brain_identity:
        logger.info("No agent in room after wait — dispatching %s ...", agent_name or "<unnamed>")
        await _dispatch_agent(cfg, room_name, agent_name=agent_name)
        brain_identity = await _wait_for_brain_participant(room, brain_wait_seconds)

    if startup_rpc_check:
        try:
            if not brain_identity:
                raise RuntimeError(
                    f"START RPC check failed: Brain participant not present after {brain_wait_seconds:.1f}s"
                )
            await _run_startup_rpc_check(room, brain_identity)
        finally:
            for pt in playback_tasks:
                pt.cancel()
            if playback_tasks:
                await asyncio.gather(*playback_tasks, return_exceptions=True)
            result_monitor.cancel()
            await asyncio.gather(result_monitor, return_exceptions=True)
            if nanobot:
                await nanobot.stop()
            if scheduler:
                await scheduler.stop()
            await room.disconnect()
            logger.info("Disconnected.")
        return

    mic_stream = None
    mic_writer_task: asyncio.Task | None = None
    if use_mic:
        import sounddevice as sd

        di, do = sd.default.device
        logger.info(
            "sounddevice default input=%s output=%s (use --list-audio-devices to pick --input-device / --output-device)",
            di,
            do,
        )
        logger.info(
            "Agent TTS playback sample rate=%d Hz (override with --playback-sample-rate if needed)",
            playback_sample_rate,
        )
        mic_stream, mic_writer_task = await _publish_microphone(room, input_device)

    video_cap = None
    video_task: asyncio.Task | None = None
    if use_video:
        video_cap, video_task = await _publish_video(room, camera_device)
        if video_task is None:
            logger.warning("Video publishing failed — continuing without video")

    print()
    print("=" * 60)
    if use_mic:
        print("  VOICE MODE: Speak into your microphone to chat with Parrot")
    elif use_text:
        print("  TEXT MODE: Type messages below (not yet routed to Gemini)")
        print("  (Text-to-Gemini requires text-mode LLM, voice is recommended)")
    else:
        print("  LISTEN MODE: Watching for Brain Agent interactions")
    if use_video:
        print("  VIDEO: Webcam publishing to LiveKit (Gemini can see)")
    if full_stack:
        print("  FULL STACK: Scheduler + NanobotConsumer running in-process")
    print("  Press Ctrl+C to quit")
    print("=" * 60)
    print()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        for pt in playback_tasks:
            pt.cancel()
        if playback_tasks:
            await asyncio.gather(*playback_tasks, return_exceptions=True)
        if mic_stream:
            mic_stream.stop()
            mic_stream.close()
        if mic_writer_task:
            mic_writer_task.cancel()
            await asyncio.gather(mic_writer_task, return_exceptions=True)
        if video_task:
            video_task.cancel()
            await asyncio.gather(video_task, return_exceptions=True)
        result_monitor.cancel()
        if nanobot:
            await nanobot.stop()
        if scheduler:
            await scheduler.stop()
        await room.disconnect()
        logger.info("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulate Unity client — full ParrotCarriers verification tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mic              Voice chat with Gemini via microphone
  %(prog)s --mic --full       Voice + Scheduler + Nanobot (full stack)
  %(prog)s                    Listen-only mode (watch RPC calls)

  With Unity Editor already in the room as unity-* (RPC + on-screen audio):
  %(prog)s --identity voice-user --mic --no-agent-playback
        """,
    )
    parser.add_argument(
        "--identity",
        default="unity-sim",
        metavar="ID",
        help='LiveKit participant identity (default: unity-sim). Use a non-unity-* id (e.g. voice-user) '
        "plus Unity as the only unity-* client so Brain RPC targets Unity while you speak from this process.",
    )
    parser.add_argument(
        "--no-agent-playback",
        action="store_true",
        help="Do not play agent TTS via sounddevice (use with Unity playing audio to avoid double playback).",
    )
    parser.add_argument(
        "--startup-rpc-check",
        action="store_true",
        help="After joining, verify getRoomSettingSnapshot/applyRoomProfile/setAppCapabilityMode business-ok and exit.",
    )
    parser.add_argument(
        "--brain-wait-seconds",
        type=float,
        default=30.0,
        metavar="S",
        help="Seconds to wait for Brain after dispatch before failing --startup-rpc-check.",
    )
    parser.add_argument(
        "--agent-name",
        default=AGENT_NAME,
        metavar="NAME",
        help="LiveKit Agents dispatch name. Default is empty for the unnamed @server.rtc_session entrypoint.",
    )
    parser.add_argument("--mic", action="store_true", help="Enable microphone → Gemini voice chat")
    parser.add_argument("--video", action="store_true", help="Publish webcam video (simulates ARVideoPublisher)")
    parser.add_argument("--text", action="store_true", help="Enable text input mode")
    parser.add_argument("--full", action="store_true", help="Also start Scheduler + NanobotConsumer in-process")
    parser.add_argument(
        "--list-audio-devices",
        action="store_true",
        help="Print sounddevice indices and exit (for --input-device / --output-device)",
    )
    parser.add_argument(
        "--input-device",
        type=int,
        default=None,
        metavar="N",
        help="sounddevice input index (default: system default)",
    )
    parser.add_argument(
        "--output-device",
        type=int,
        default=None,
        metavar="N",
        help="sounddevice output index for agent TTS (default: system default)",
    )
    parser.add_argument(
        "--playback-sample-rate",
        type=int,
        default=AGENT_PLAYBACK_SAMPLE_RATE,
        metavar="HZ",
        help=f"Output stream rate for agent audio (default {AGENT_PLAYBACK_SAMPLE_RATE}, try 48000 if silent)",
    )
    parser.add_argument(
        "--camera-device",
        type=int,
        default=0,
        metavar="N",
        help="OpenCV camera index for --video (default: 0)",
    )
    parser.add_argument(
        "--audio-selftest",
        action="store_true",
        help="Before connecting, play test beeps on the output device (480 Hz + playback rate)",
    )
    args = parser.parse_args()
    if args.list_audio_devices:
        _print_sound_devices()
        sys.exit(0)
    asyncio.run(
        main(
            use_mic=args.mic,
            use_text=args.text,
            use_video=args.video,
            full_stack=args.full,
            input_device=args.input_device,
            output_device=args.output_device,
            camera_device=args.camera_device,
            playback_sample_rate=args.playback_sample_rate,
            audio_selftest=args.audio_selftest,
            identity=args.identity,
            agent_playback=not args.no_agent_playback,
            startup_rpc_check=args.startup_rpc_check,
            brain_wait_seconds=args.brain_wait_seconds,
            agent_name=args.agent_name,
        )
    )
